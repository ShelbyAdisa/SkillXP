from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User, UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Automatically create user profile when user is created
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Automatically save user profile when user is saved
    instance.profile.save()

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    # Send welcome email when new user registers
    if created and instance.email:
        subject = f'Welcome to {instance.school.name} - SkillXP Nexus'
        message = f'''
        Hello {instance.first_name},
        
        Welcome to SkillXP Nexus! Your account has been successfully created.
        
        School: {instance.school.name}
        Role: {instance.get_role_display()}
        School ID: {instance.school_id}
        
        You can now access all features of our connected school ecosystem.
        
        Best regards,
        {instance.school.name} Team
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=True,
        )