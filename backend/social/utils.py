from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import re

def extract_mentions(text):
    """Extract @mentions from text"""
    mentions = re.findall(r'@(\w+)', text)
    return mentions

def extract_hashtags(text):
    """Extract #hashtags from text"""
    hashtags = re.findall(r'#(\w+)', text)
    return hashtags

def get_user_engagement_stats(user):
    """Get social engagement statistics for a user"""
    cache_key = f"social_engagement_{user.id}"
    stats = cache.get(cache_key)
    
    if not stats:
        week_ago = timezone.now() - timedelta(days=7)
        
        stats = {
            'posts_this_week': user.social_posts.filter(created_at__gte=week_ago).count(),
            'comments_this_week': user.social_comments.filter(created_at__gte=week_ago).count(),
            'upvotes_received': sum(
                list(user.social_posts.values_list('upvotes', flat=True)) +
                list(user.social_comments.values_list('upvotes', flat=True))
            ),
            'followers_count': user.followers.count(),
            'following_count': user.following.count(),
        }
        cache.set(cache_key, stats, 3600)  # Cache for 1 hour
    
    return stats

def get_community_recommendations(user, limit=5):
    """Get community recommendations for a user"""
    from .models import Community, CommunityMembership
    
    # Get user's current communities
    user_communities = CommunityMembership.objects.filter(
        user=user, is_approved=True
    ).values_list('community_id', flat=True)
    
    # Recommend popular public communities user isn't in
    recommendations = Community.objects.filter(
        school=user.school,
        is_public=True
    ).exclude(
        id__in=user_communities
    ).order_by('-member_count')[:limit]
    
    return recommendations

def can_user_message(sender, receiver):
    """Check if a user can message another user"""
    from .models import User

    if sender.school != receiver.school:
        return False
    
    # Role-based messaging restrictions
    if sender.role == User.Role.STUDENT:
        return receiver.role in [User.Role.STUDENT, User.Role.TEACHER]
    elif sender.role == User.Role.PARENT:
        return receiver.role in [User.Role.TEACHER, User.Role.ADMIN]
    
    return True  # Teachers and admins can message anyone

def format_content_with_mentions(text):
    """Format text to highlight mentions and hashtags"""
    # Convert @mentions to links
    text = re.sub(r'@(\w+)', r'<a href="/profile/\1">@\1</a>', text)
    
    # Convert #hashtags to links
    text = re.sub(r'#(\w+)', r'<a href="/search?q=%23\1">#\1</a>', text)
    
    return text

def should_throttle_post(user):
    """Check if user should be throttled from posting"""
    from .models import Post
    
    hour_ago = timezone.now() - timedelta(hours=1)
    recent_posts = Post.objects.filter(author=user, created_at__gte=hour_ago).count()
    
    # Limit to 10 posts per hour
    return recent_posts >= 10

def get_unread_message_count(user):
    """Get count of unread messages for user"""
    from .models import DirectMessage
    return DirectMessage.objects.filter(receiver=user, is_read=False).count()

def get_unread_notification_count(user):
    """Get count of unread notifications for user"""
    from .models import Notification
    return Notification.objects.filter(user=user, is_read=False).count()