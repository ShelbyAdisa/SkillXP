from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import (
    Trip, LocationUpdate, StudentTransport, AttendanceLog,
    EmergencyAlert, NotificationPreference
)
from .tasks import send_arrival_notifications, check_maintenance_schedule

@receiver(post_save, sender=Trip)
def handle_trip_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Trip.objects.get(pk=instance.pk)
            
            # Trip started
            if (old_instance.status != Trip.TripStatus.IN_PROGRESS and 
                instance.status == Trip.TripStatus.IN_PROGRESS):
                
                # Notify parents that bus has started
                student_assignments = StudentTransport.objects.filter(
                    route=instance.route,
                    is_active=True
                )
                
                for assignment in student_assignments:
                    preferences = NotificationPreference.objects.filter(user=assignment.student).first()
                    if preferences and preferences.bus_arriving:
                        subject = f'Bus {instance.bus.bus_number} Has Started'
                        message = f'''
                                    Your bus has started its route.
                                    
                                    Bus: {instance.bus.bus_number}
                                    Route: {instance.route.name}
                                    Estimated arrival at your stop: {assignment.morning_pickup_time}
                                    
                                    You can track the bus in real-time through the app.
                                '''
                        
                        if preferences.email_notifications:
                            send_mail(
                                subject,
                                message,
                                settings.DEFAULT_FROM_EMAIL,
                                [assignment.student.email],
                                fail_silently=True,
                            )
            
            # Trip completed
            elif (old_instance.status == Trip.TripStatus.IN_PROGRESS and 
                  instance.status == Trip.TripStatus.COMPLETED):
                
                # Schedule maintenance check
                check_maintenance_schedule.delay(instance.bus.id)
                
        except Trip.DoesNotExist:
            pass

@receiver(post_save, sender=LocationUpdate)
def handle_location_update(sender, instance, created, **kwargs):
    if created:
        # Update trip's current location
        instance.trip.current_latitude = instance.latitude
        instance.trip.current_longitude = instance.longitude
        instance.trip.last_location_update = timezone.now()
        
        if instance.speed:
            instance.trip.average_speed = instance.speed
        
        instance.trip.save()
        
        # Check if bus is approaching any stops for notifications
        send_arrival_notifications.delay(instance.trip.id)

@receiver(post_save, sender=StudentTransport)
def handle_student_transport_assignment(sender, instance, created, **kwargs):
    if created:
        # Notify student/parent about transport assignment
        subject = 'Transport Assignment Updated'
        message = f'''
                    Your transport assignment has been updated:
                    
                    Route: {instance.route.name}
                    Bus Stop: {instance.bus_stop.name}
                    Morning Pickup: {instance.morning_pickup_time or 'Not set'}
                    Evening Dropoff: {instance.evening_dropoff_time or 'Not set'}
                    
                    Address: {instance.bus_stop.address}
                '''
        
        # Send to student
        preferences = NotificationPreference.objects.filter(user=instance.student).first()
        if preferences and preferences.route_changes and preferences.email_notifications:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.student.email],
                fail_silently=True,
            )
        
        # Send to parent if available
        if hasattr(instance.student, 'profile') and instance.student.profile.parent_email:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.student.profile.parent_email],
                fail_silently=True,
            )

@receiver(post_save, sender=AttendanceLog)
def handle_attendance_marking(sender, instance, created, **kwargs):
    if created and instance.is_present:
        # Notify parents when attendance is marked
        preferences = NotificationPreference.objects.filter(user=instance.student).first()
        
        if preferences and preferences.attendance_marked:
            action = "picked up" if instance.attendance_type == 'PICKUP' else "dropped off"
            
            subject = f'Student {action} - {instance.student.get_display_name()}'
            message = f'''
            {instance.student.get_display_name()} has been {action} from the bus.
            
            Time: {instance.actual_time.strftime("%I:%M %p") if instance.actual_time else 'Not recorded'}
            Bus Stop: {instance.bus_stop.name}
            Bus: {instance.trip.bus.bus_number}
            '''
            
            if preferences.email_notifications:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.student.email],
                    fail_silently=True,
                )
            
            # Also notify parent
            if hasattr(instance.student, 'profile') and instance.student.profile.parent_email:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.student.profile.parent_email],
                    fail_silently=True,
                )

@receiver(post_save, sender=EmergencyAlert)
def handle_emergency_alert(sender, instance, created, **kwargs):
    if created:
        # Notify all concerned parties about emergency
        school = instance.trip.bus.school
        
        # Get all parents with students on this trip
        student_assignments = StudentTransport.objects.filter(
            route=instance.trip.route,
            is_active=True
        )
        
        subject = f'EMERGENCY ALERT - {instance.get_alert_type_display()}'
        message = f'''
                    EMERGENCY ALERT
                    
                    Type: {instance.get_alert_type_display()}
                    Severity: {instance.get_severity_display()}
                    Bus: {instance.trip.bus.bus_number}
                    Route: {instance.trip.route.name}
                    Description: {instance.description}
                    
                    We will provide updates as more information becomes available.
                '''
        
        for assignment in student_assignments:
            preferences = NotificationPreference.objects.filter(user=assignment.student).first()
            if preferences and preferences.emergency_alerts:
                if preferences.email_notifications:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [assignment.student.email],
                        fail_silently=True,
                    )
                
                if preferences.push_notifications:
                    # This would integrate with your push notification service
                    pass

@receiver(pre_save, sender=Trip)
def check_trip_delays(sender, instance, **kwargs):
    if instance.pk and instance.status == Trip.TripStatus.IN_PROGRESS:
        try:
            old_instance = Trip.objects.get(pk=instance.pk)
            
            # Check if trip is significantly delayed
            if (instance.actual_start and old_instance.actual_start and
                instance.actual_start > old_instance.actual_start + timedelta(minutes=15)):
                
                # Notify about delay
                student_assignments = StudentTransport.objects.filter(
                    route=instance.route,
                    is_active=True
                )
                
                for assignment in student_assignments:
                    preferences = NotificationPreference.objects.filter(user=assignment.student).first()
                    if preferences and preferences.bus_delayed:
                        subject = f'Bus Delay - {instance.bus.bus_number}'
                        message = f'''
                                    Your bus is experiencing a delay.
                                    
                                    Bus: {instance.bus.bus_number}
                                    Route: {instance.route.name}
                                    Current Delay: Approximately 15 minutes
                                    
                                    We apologize for the inconvenience.
                                '''
                        
                        if preferences.email_notifications:
                            send_mail(
                                subject,
                                message,
                                settings.DEFAULT_FROM_EMAIL,
                                [assignment.student.email],
                                fail_silently=True,
                            )
                            
        except Trip.DoesNotExist:
            pass