from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, F
import threading
import time
import requests

from .models import Trip, Bus, MaintenanceLog, StudentTransport, NotificationPreference, GPSDevice, LocationUpdate
from django.contrib.auth import get_user_model

User = get_user_model()

def sync_gps_devices_status(school_id):
    # Sync GPS devices status and update bus locations
    def _sync_devices():
        try:
            gps_devices = GPSDevice.objects.filter(
                bus__school_id=school_id,
                status=GPSDevice.DeviceStatus.ACTIVE
            )
            
            for device in gps_devices:
                # Simulate GPS device communication
                # In production, this would call your GPS provider's API
                device.last_communication = timezone.now()
                
                # Check if device is online (simulated)
                time_since_last_comm = timezone.now() - (device.last_communication or timezone.now())
                if time_since_last_comm.total_seconds() > 300:
                    device.bus.gps_status = 'OFFLINE'
                else:
                    device.bus.gps_status = 'ONLINE'
                
                device.save()
                device.bus.save()
                
                print(f"Synced GPS device {device.device_id} for bus {device.bus.bus_number}")
                
        except Exception as e:
            print(f"Error syncing GPS devices: {e}")
    
    thread = threading.Thread(target=_sync_devices)
    thread.daemon = True
    thread.start()

def check_bus_maintenance():
    # Check and schedule bus maintenance - run as scheduled task
    maintenance_threshold_km = 5000
    maintenance_threshold_months = 6
    
    buses_needing_maintenance = Bus.objects.filter(
        status=Bus.BusStatus.ACTIVE
    ).annotate(
        km_since_maintenance=F('mileage') - F('last_maintenance_date_mileage'),
        months_since_maintenance=(
            timezone.now().date() - F('last_maintenance_date')
        ).days // 30
    ).filter(
        Q(km_since_maintenance__gte=maintenance_threshold_km) |
        Q(months_since_maintenance__gte=maintenance_threshold_months)
    )
    
    for bus in buses_needing_maintenance:
        # Create maintenance log
        MaintenanceLog.objects.create(
            bus=bus,
            maintenance_type=MaintenanceLog.MaintenanceType.ROUTINE,
            description=f"Routine maintenance due - {bus.km_since_maintenance} km since last maintenance",
            mileage=bus.mileage,
            scheduled_date=timezone.now().date() + timedelta(days=7),
            assigned_mechanic="Auto-assigned"
        )
        
        # Notify admin
        admins = User.objects.filter(
            school=bus.school,
            role__in=[User.Role.ADMIN, User.Role.SCHOOL_ADMIN]
        )
        
        subject = f'Maintenance Due - Bus {bus.bus_number}'
        message = f'''
                    Maintenance is due for bus {bus.bus_number}.
                    
                    Current Mileage: {bus.mileage} km
                    Since Last Maintenance: {bus.km_since_maintenance} km
                    Last Maintenance: {bus.last_maintenance_date}
                    
                    A maintenance log has been created and scheduled.
                '''
        
        for admin in admins:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin.email],
                fail_silently=True,
            )
        
        print(f"Scheduled maintenance for bus {bus.bus_number}")

def generate_daily_trips():
    # Generate daily trips for all active routes - run as scheduled task
    today = timezone.now().date()
    
    for school in User.objects.values_list('school', flat=True).distinct():
        active_buses = Bus.objects.filter(
            school=school, 
            status=Bus.BusStatus.ACTIVE,
            current_route__isnull=False,
            current_driver__isnull=False
        )
        
        for bus in active_buses:
            # Create morning trip
            if bus.current_route.morning_start_time:
                morning_start = timezone.make_aware(
                    timezone.datetime.combine(today, bus.current_route.morning_start_time)
                )
                
                Trip.objects.get_or_create(
                    bus=bus,
                    route=bus.current_route,
                    driver=bus.current_driver,
                    trip_type=Trip.TripType.MORNING_PICKUP,
                    scheduled_start=morning_start,
                    defaults={
                        'scheduled_end': morning_start + timedelta(hours=1),
                        'status': Trip.TripStatus.SCHEDULED
                    }
                )
            
            # Create evening trip
            if bus.current_route.evening_start_time:
                evening_start = timezone.make_aware(
                    timezone.datetime.combine(today, bus.current_route.evening_start_time)
                )
                
                Trip.objects.get_or_create(
                    bus=bus,
                    route=bus.current_route,
                    driver=bus.current_driver,
                    trip_type=Trip.TripType.EVENING_DROPOFF,
                    scheduled_start=evening_start,
                    defaults={
                        'scheduled_end': evening_start + timedelta(hours=1),
                        'status': Trip.TripStatus.SCHEDULED
                    }
                )
    
    print(f"Generated daily trips for {timezone.now().date()}")

def auto_end_completed_trips():
    # Automatically end trips that should be completed - run as scheduled task
    overdue_trips = Trip.objects.filter(
        status=Trip.TripStatus.IN_PROGRESS,
        scheduled_end__lt=timezone.now() - timedelta(hours=1)
    )
    
    for trip in overdue_trips:
        trip.status = Trip.TripStatus.COMPLETED
        trip.actual_end = timezone.now()
        trip.save()
        print(f"Auto-ended trip {trip.id} for bus {trip.bus.bus_number}")

def check_insurance_expiry():
    # Check for expiring insurance - run as scheduled task
    expiry_threshold = timezone.now().date() + timedelta(days=30)
    
    expiring_buses = Bus.objects.filter(
        insurance_expiry__lte=expiry_threshold,
        insurance_expiry__gte=timezone.now().date() 
    )
    
    for bus in expiring_buses:
        # Notify admin
        admins = User.objects.filter(
            school=bus.school,
            role__in=[User.Role.ADMIN, User.Role.SCHOOL_ADMIN]
        )
        
        days_until_expiry = (bus.insurance_expiry - timezone.now().date()).days
        
        subject = f'Insurance Expiring Soon - Bus {bus.bus_number}'
        message = f'''
                    Insurance for bus {bus.bus_number} will expire in {days_until_expiry} days.
                    
                    Bus: {bus.bus_number}
                    License Plate: {bus.license_plate}
                    Insurance Expiry: {bus.insurance_expiry}
                    
                    Please renew the insurance before the expiry date.
                '''
        
        for admin in admins:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin.email],
                fail_silently=True,
            )

def cleanup_old_data():
    # Clean up old transport data - run as scheduled task#
    # Archive trips older than 30 days
    archive_threshold = timezone.now() - timedelta(days=30)
    old_trips = Trip.objects.filter(
        scheduled_start__lt=archive_threshold,
        status=Trip.TripStatus.COMPLETED
    )
    archived_count = old_trips.count()
    
    # Delete very old location updates
    delete_threshold = timezone.now() - timedelta(days=7)
    deleted_locations = LocationUpdate.objects.filter(
        created_at__lt=delete_threshold
    ).delete()
    
    print(f"Archived {archived_count} old trips")
    print(f"Deleted {deleted_locations[0]} old location updates")

# Management command for scheduled tasks
def run_scheduled_transport_tasks():
    # Run all scheduled transport tasks
    print("Running scheduled transport tasks...")
    
    # Generate daily trips (run daily at 6 AM)
    generate_daily_trips()
    
    # Auto-end completed trips (run hourly)
    auto_end_completed_trips()
    
    # Check maintenance (run weekly)
    if timezone.now().weekday() == 0:  # Monday
        check_bus_maintenance()
    
    # Check insurance expiry (run weekly)
    if timezone.now().weekday() == 0:  # Monday
        check_insurance_expiry()
    
    # Cleanup old data (run monthly)
    if timezone.now().day == 1:
        cleanup_old_data()
    
    print("Scheduled transport tasks completed!")