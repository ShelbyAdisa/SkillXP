from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Count, F, ExpressionWrapper, FloatField, Q
import threading
import time
import re

from .models import Post, Comment, TrendingTopic, Notification, Vote
from django.contrib.auth import get_user_model

User = get_user_model()

def analyze_post_sentiment(post_id):
    """Analyze post for sentiment and toxicity - run in background thread"""
    def _analyze():
        try:
            time.sleep(1)  # Simulate processing time
            post = Post.objects.get(id=post_id)
            
            # Simple keyword-based analysis (replace with actual AI service)
            negative_keywords = [
                'hate', 'stupid', 'idiot', 'worthless', 'useless', 'terrible',
                'awful', 'horrible', 'disgusting', 'annoying', 'angry', 'mad'
            ]
            
            crisis_keywords = ['suicide', 'self harm', 'kill myself', 'end it all', 'want to die']
            
            content_lower = post.content.lower()
            toxicity_score = 0.0
            
            # Calculate simple toxicity score
            for word in negative_keywords:
                if word in content_lower:
                    toxicity_score += 0.05
            
            toxicity_score = min(toxicity_score, 1.0)  # Cap at 1.0
            
            # Check for crisis keywords
            for keyword in crisis_keywords:
                if keyword in content_lower:
                    # Create urgent report
                    from .models import Report
                    Report.objects.create(
                        reporter=post.author,
                        post=post,
                        report_type=Report.ReportType.HARASSMENT,
                        description=f"Potential crisis content detected: {keyword}",
                    )
                    toxicity_score = max(toxicity_score, 0.8)  # High score for crisis content
            
            # Update post with analysis results
            post.toxicity_score = toxicity_score
            if toxicity_score > 0.7:
                post.status = Post.PostStatus.REMOVED
                
                # Create automatic notification
                Notification.objects.create(
                    user=post.author,
                    notification_type=Notification.NotificationType.MENTION,
                    title='Post removed due to content policy',
                    message='Your post was automatically removed for violating content guidelines.',
                    post=post
                )
            
            post.save()
            
        except Post.DoesNotExist:
            pass
    
    thread = threading.Thread(target=_analyze)
    thread.daemon = True
    thread.start()

def update_trending_topics(school_id):
    """Update trending topics for a school - run in background thread"""
    def _update():
        try:
            # Clear old trending topics
            old_threshold = timezone.now() - timedelta(hours=24)
            TrendingTopic.objects.filter(
                school_id=school_id,
                created_at__lt=old_threshold
            ).delete()
            
            # Calculate trending topics from recent posts
            time_threshold = timezone.now() - timedelta(hours=6)
            
            # Extract hashtags from posts
            recent_posts = Post.objects.filter(
                school_id=school_id,
                created_at__gte=time_threshold,
                status=Post.PostStatus.PUBLISHED
            )
            
            hashtag_counts = {}
            
            for post in recent_posts:
                # Simple hashtag extraction
                hashtags = re.findall(r'#(\w+)', f"{post.title} {post.content}")
                for tag in hashtags:
                    tag_lower = tag.lower()
                    hashtag_counts[tag_lower] = hashtag_counts.get(tag_lower, 0) + 1
            
            # Create or update trending topics
            for tag, count in list(hashtag_counts.items())[:10]:  # Top 10
                topic, created = TrendingTopic.objects.get_or_create(
                    name=tag,
                    school_id=school_id,
                    defaults={'post_count': count, 'score': count}
                )
                
                if not created:
                    topic.post_count = count
                    topic.score = count  # Simple score based on frequency
                    topic.save()
            
        except Exception as e:
            print(f"Error updating trending topics: {e}")
    
    thread = threading.Thread(target=_update)
    thread.daemon = True
    thread.start()

def send_digest_notifications():
    """Send daily digest notifications - run as scheduled task"""
    yesterday = timezone.now() - timedelta(days=1)
    
    for school in User.objects.values_list('school', flat=True).distinct():
        school_users = User.objects.filter(school=school)
        
        for user in school_users:
            if not user.profile.email_notifications:
                continue
            
            # Get user's daily activity summary
            new_followers = user.followers.filter(created_at__gte=yesterday).count()
            new_upvotes = Vote.objects.filter(
                Q(post__author=user) | Q(comment__author=user),
                vote_type='UPVOTE',
                created_at__gte=yesterday
            ).count()
            new_comments = Comment.objects.filter(
                post__author=user,
                created_at__gte=yesterday
            ).count()
            
            # Only send digest if there was activity
            if new_followers > 0 or new_upvotes > 0 or new_comments > 0:
                subject = f'SkillXP Nexus - Your Daily Digest'
                message = f"""
                Hello {user.first_name},
                
                Here's your daily activity summary:
                
                New Followers: {new_followers}
                New Upvotes: {new_upvotes}
                New Comments: {new_comments}
                
                Check your dashboard for more details!
                
                - SkillXP Nexus Team
                """
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Failed to send digest to {user.email}: {e}")

def cleanup_old_data():
    """Clean up old data - run as scheduled task"""
    # Archive posts older than 1 year
    archive_threshold = timezone.now() - timedelta(days=365)
    old_posts = Post.objects.filter(created_at__lt=archive_threshold)
    archived_count = old_posts.update(status=Post.PostStatus.ARCHIVED)
    
    # Delete very old notifications
    delete_threshold = timezone.now() - timedelta(days=30)
    deleted_notifications = Notification.objects.filter(
        created_at__lt=delete_threshold,
        is_read=True
    ).delete()
    
    print(f"Archived {archived_count} old posts")
    print(f"Deleted {deleted_notifications[0]} old notifications")

def calculate_user_engagement():
    """Calculate and update user engagement scores"""
    time_threshold = timezone.now() - timedelta(days=7)
    
    # Calculate engagement scores for all users
    users = User.objects.filter(
        social_posts__created_at__gte=time_threshold
    ).annotate(
        post_count=Count('social_posts'),
        comment_count=Count('social_comments'),
        vote_count=Count('social_votes'),
        engagement_score=ExpressionWrapper(
            F('post_count') * 3 + F('comment_count') * 2 + F('vote_count') * 1,
            output_field=FloatField()
        )
    )
    
    # Update user profiles or store in cache
    for user in users:
        # You could store this in user profile or cache for recommendations
        pass
    
    print(f"Calculated engagement for {users.count()} users")

# Management command for scheduled tasks
def run_scheduled_social_tasks():
    """Run all scheduled social tasks"""
    print("Running scheduled social tasks...")
    
    # Send daily digests (run in morning)
    send_digest_notifications()
    
    # Cleanup old data (run weekly)
    if timezone.now().weekday() == 0:  # Monday
        cleanup_old_data()
        calculate_user_engagement()
    
    print("Scheduled social tasks completed!")
def send_push_notification(user, title, message):
    """
    Placeholder push notification function.
    Later you can connect this to Firebase Cloud Messaging (FCM),
    OneSignal, or Expo Push.
    """
    print(f"Sending push notification to {user}: {title} - {message}")
