from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import json

def get_wellbeing_stats(user):
    """Get wellbeing statistics for a user"""
    cache_key = f"wellbeing_stats_{user.id}"
    stats = cache.get(cache_key)
    
    if not stats:
        stats = {
            'weekly_mood_avg': calculate_weekly_mood_avg(user),
            'post_count': user.wellbeing_posts.count(),
            'goal_progress': calculate_goal_progress(user),
            'support_sessions': user.support_tickets.count(),
        }
        cache.set(cache_key, stats, 3600)  # Cache for 1 hour
    
    return stats

def calculate_weekly_mood_avg(user):
    """Calculate average mood for the past week"""
    week_ago = timezone.now() - timedelta(days=7)
    mood_checks = user.mood_checks.filter(created_at__gte=week_ago)
    
    if mood_checks.exists():
        return round(sum(check.mood_level for check in mood_checks) / mood_checks.count(), 2)
    return None

def calculate_goal_progress(user):
    """Calculate progress on wellbeing goals"""
    goals = user.wellbeing_goals.all()
    if not goals.exists():
        return 0
    
    completed = goals.filter(status='COMPLETED').count()
    return round((completed / goals.count()) * 100)

def should_escalate_alert(alert):
    """Determine if a crisis alert should be escalated"""
    from .models import CrisisAlert
    escalation_threshold = 8
    
    if alert.severity_level >= escalation_threshold:
        return True
    
    # Check for multiple alerts from same user
    recent_alerts = CrisisAlert.objects.filter(
        reported_by=alert.reported_by,
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    return recent_alerts >= 3

def get_recommended_resources(user, mood_level=None):
    """Get wellbeing resources recommended for user"""
    from .models import WellbeingResource
    
    resources = WellbeingResource.objects.filter(
        is_published=True,
        target_roles__contains=[user.role]
    )
    
    if mood_level:
        # Filter resources based on mood
        if mood_level <= 2:
            # Low mood - show supportive resources
            resources = resources.filter(tags__contains=['support', 'coping', 'emergency'])
        elif mood_level >= 4:
            # Good mood - show growth resources
            resources = resources.filter(tags__contains=['growth', 'happiness', 'productivity'])
    
    return resources[:5]  # Return top 5 recommendations

def validate_anonymous_username(username):
    """Validate anonymous username"""
    from .models import User
    
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if User.objects.filter(anonymous_username=username).exists():
        return False, "This anonymous username is already taken"
    
    # Check for inappropriate words
    inappropriate_words = ['admin', 'moderator', 'counselor', 'teacher']
    if any(word in username.lower() for word in inappropriate_words):
        return False, "Username contains inappropriate words"
    
    return True, "Username is valid"