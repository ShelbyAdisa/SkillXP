from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import (
    WellbeingPost, SupportTicket, CrisisAlert, ContentReport,
    TicketMessage, MoodCheck
)
from .tasks import analyze_post_sentiment, check_crisis_keywords

@receiver(post_save, sender=WellbeingPost)
def handle_new_post(sender, instance, created, **kwargs):
    if created:
        # Schedule AI analysis for toxicity and sentiment
        analyze_post_sentiment.delay(instance.id)
        
        # Check for crisis keywords
        check_crisis_keywords.delay(instance.id)
        
        # Award XP for posting (if using gamification)
        if hasattr(instance.author, 'xp_points'):
            instance.author.xp_points += 5
            instance.author.save()

@receiver(post_save, sender=SupportTicket)
def handle_new_ticket(sender, instance, created, **kwargs):
    if created:
        # Notify available counselors
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        counselors = User.objects.filter(
            role=User.Role.TEACHER,
            school=instance.student.school
        )
        
        subject = f'New Support Ticket: {instance.title}'
        message = f'''
                    A new support ticket has been created by {instance.student.get_display_name()}.
        
                    Title: {instance.title}
                    Priority: {instance.get_priority_display()}
                    
                    Please review the ticket in the counselor dashboard.
            '''
        
        for counselor in counselors:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [counselor.email],
                fail_silently=True,
            )

@receiver(post_save, sender=TicketMessage)
def handle_new_message(sender, instance, created, **kwargs):
    if created and instance.is_counselor_response:
        # Notify student about counselor response
        subject = 'Response to Your Support Ticket'
        message = f'''
                    Your counselor has responded to your support ticket "{instance.ticket.title}".
                    
                    Message: {instance.content}
                    
                    You can view the full conversation in your support dashboard.
                '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.ticket.student.email],
            fail_silently=True,
        )

@receiver(post_save, sender=CrisisAlert)
def handle_crisis_alert(sender, instance, created, **kwargs):
    if created:
        # Immediate notification to all counselors and admins
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        staff = User.objects.filter(
            role__in=[User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN],
            school=instance.reported_by.school
        )
        
        subject = f'CRISIS ALERT - Severity {instance.severity_level}/10'
        message = f'''
        URGENT: A crisis alert has been reported.
        
        Reported by: {instance.reported_by.get_display_name()}
        Severity: {instance.severity_level}/10
        Description: {instance.description}
        
        Immediate attention required!
        '''
        
        for user in staff:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )

@receiver(pre_save, sender=MoodCheck)
def check_mood_trend(sender, instance, **kwargs):
    if instance.pk: 
        try:
            old_instance = MoodCheck.objects.get(pk=instance.pk)
            if old_instance.mood_level >= 3 and instance.mood_level < 2:
                # Significant drop in mood - might need follow-up
                from .tasks import schedule_wellbeing_checkin
                schedule_wellbeing_checkin.delay(instance.user.id)
        except MoodCheck.DoesNotExist:
            pass