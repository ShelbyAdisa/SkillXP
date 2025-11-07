from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import UserAnalytics
from django.db.models import Avg
@receiver(post_save, sender='classroom.Submission')
def update_analytics_on_submission(sender, instance, created, **kwargs):
    if created and instance.status == 'SUBMITTED':
        user_analytics, _ = UserAnalytics.objects.get_or_create(
            user=instance.student,
            date=timezone.now().date()
        )
        user_analytics.assignments_completed += 1
        user_analytics.save()

@receiver(post_save, sender='social.Post')
def update_analytics_on_social_post(sender, instance, created, **kwargs):
    if created:
        user_analytics, _ = UserAnalytics.objects.get_or_create(
            user=instance.author,
            date=timezone.now().date()
        )
        user_analytics.posts_created += 1
        user_analytics.save()

@receiver(post_save, sender='elibrary.ResourceInteraction')
def update_analytics_on_resource_interaction(sender, instance, created, **kwargs):
    if created:
        user_analytics, _ = UserAnalytics.objects.get_or_create(
            user=instance.user,
            date=timezone.now().date()
        )
        user_analytics.resources_accessed += 1
        user_analytics.study_time_minutes += instance.duration_seconds // 60
        user_analytics.save()

@receiver(post_save, sender='wellbeing.WellbeingPost')
def update_analytics_on_wellbeing_post(sender, instance, created, **kwargs):
    if created:
        user_analytics, _ = UserAnalytics.objects.get_or_create(
            user=instance.author,
            date=timezone.now().date()
        )
        user_analytics.wellbeing_posts += 1
        user_analytics.save()

@receiver(post_save, sender='wellbeing.MoodCheck')
def update_analytics_on_mood_check(sender, instance, created, **kwargs):
    if created:
        # Update user's mood average
        from wellbeing.models import MoodCheck
        recent_checks = MoodCheck.objects.filter(
            user=instance.user,
            created_at__date=timezone.now().date()
        )
        avg_mood = recent_checks.aggregate(avg=Avg('mood_level'))['avg']
        
        user_analytics, _ = UserAnalytics.objects.get_or_create(
            user=instance.user,
            date=timezone.now().date()
        )
        user_analytics.mood_average = avg_mood
        user_analytics.save()