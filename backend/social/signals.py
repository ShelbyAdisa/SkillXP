from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import (
    Post, Comment, DirectMessage, Notification, UserFollow,
    CommunityMembership, Vote, Report, TrendingTopic
)
from ai_engine.services import AIService  # ✅ AI IMPORT

@receiver(post_save, sender=Post)
def handle_new_post(sender, instance, created, **kwargs):
    if created:
        # ✅ AI TOXICITY ANALYSIS
        analyze_post_toxicity(instance)
        
        # Award XP for posting
        if hasattr(instance.author, 'xp_points'):
            instance.author.xp_points += 3
            instance.author.save()
        
        # Update community post count
        if instance.community:
            instance.community.post_count += 1
            instance.community.save()
        
        # Create notification for community members if it's a community post
        if instance.community and instance.community.is_public:
            from .models import CommunityMembership
            members = CommunityMembership.objects.filter(
                community=instance.community,
                is_approved=True
            ).exclude(user=instance.author)
            
            for membership in members:
                Notification.objects.create(
                    user=membership.user,
                    notification_type=Notification.NotificationType.POST_REPLY,
                    title=f'New post in {instance.community.name}',
                    message=f'New post: {instance.title}',
                    post=instance,
                    community=instance.community
                )

@receiver(post_save, sender=Comment)
def handle_new_comment(sender, instance, created, **kwargs):
    if created and not instance.parent_comment:
        # ✅ AI TOXICITY ANALYSIS FOR COMMENTS
        analyze_comment_toxicity(instance)
        
        # Update post comment count
        instance.post.comment_count += 1
        instance.post.save()
        
        # Award XP for commenting
        if hasattr(instance.author, 'xp_points'):
            instance.author.xp_points += 1
            instance.author.save()
        
        # Notify post author (if not the same user)
        if instance.author != instance.post.author:
            Notification.objects.create(
                user=instance.post.author,
                notification_type=Notification.NotificationType.COMMENT_REPLY,
                title='New comment on your post',
                message=f'{instance.author.get_display_name()} commented on your post',
                post=instance.post,
                comment=instance
            )
        
        # Notify parent comment author if this is a reply
        if instance.parent_comment and instance.author != instance.parent_comment.author:
            Notification.objects.create(
                user=instance.parent_comment.author,
                notification_type=Notification.NotificationType.COMMENT_REPLY,
                title='New reply to your comment',
                message=f'{instance.author.get_display_name()} replied to your comment',
                post=instance.post,
                comment=instance
            )

# ✅ AI ANALYSIS FUNCTIONS

def analyze_post_toxicity(post_instance):
    """
    Analyze post content for toxicity using AI engine
    """
    if not post_instance.content or getattr(post_instance, '_ai_processing', False):
        return
    
    try:
        # Prevent recursive signal triggering
        post_instance._ai_processing = True
        
        # Call AI engine for toxicity analysis
        toxicity_result = AIService.analyze_toxicity(post_instance.content, post_instance.author)
        
        if 'error' not in toxicity_result:
            # Update post with toxicity analysis
            toxicity_score = toxicity_result.get('toxicity_score', 0)
            is_toxic = toxicity_result.get('is_toxic', False)
            
            # Update the post without triggering signals again
            Post.objects.filter(id=post_instance.id).update(
                toxicity_score=toxicity_score
            )
            
            # Auto-flag high toxicity content for moderation
            if toxicity_score > 0.7:
                print(f"🚨 High toxicity post flagged (Score: {toxicity_score}): Post #{post_instance.id}")
            elif toxicity_score > 0.4:
                print(f"⚠️ Medium toxicity post (Score: {toxicity_score}): Post #{post_instance.id}")
            else:
                print(f"✅ Low toxicity post (Score: {toxicity_score}): Post #{post_instance.id}")
                
    except Exception as e:
        print(f"❌ Error analyzing post toxicity: {e}")
    finally:
        # Clean up flag
        if hasattr(post_instance, '_ai_processing'):
            delattr(post_instance, '_ai_processing')

def analyze_comment_toxicity(comment_instance):
    """
    Analyze comment content for toxicity using AI engine
    """
    if not comment_instance.content or getattr(comment_instance, '_ai_processing', False):
        return
    
    try:
        # Prevent recursive signal triggering
        comment_instance._ai_processing = True
        
        # Call AI engine for toxicity analysis
        toxicity_result = AIService.analyze_toxicity(comment_instance.content, comment_instance.author)
        
        if 'error' not in toxicity_result:
            # Update comment with toxicity analysis
            toxicity_score = toxicity_result.get('toxicity_score', 0)
            
            # Update the comment without triggering signals again
            Comment.objects.filter(id=comment_instance.id).update(
                toxicity_score=toxicity_score
            )
            
            # Auto-remove high toxicity comments
            if toxicity_score > 0.8:
                print(f"🚨 High toxicity comment removed (Score: {toxicity_score}): Comment #{comment_instance.id}")
                Comment.objects.filter(id=comment_instance.id).update(is_removed=True)
            elif toxicity_score > 0.6:
                print(f"⚠️ High toxicity comment flagged (Score: {toxicity_score}): Comment #{comment_instance.id}")
                
    except Exception as e:
        print(f"❌ Error analyzing comment toxicity: {e}")
    finally:
        # Clean up flag
        if hasattr(comment_instance, '_ai_processing'):
            delattr(comment_instance, '_ai_processing')

# ✅ AI ANALYSIS TO REPORT HANDLING

@receiver(post_save, sender=Report)
def handle_new_report(sender, instance, created, **kwargs):
    if created:
        # ✅ AI ANALYSIS FOR REPORTED CONTENT
        if instance.post:
            analyze_post_toxicity(instance.post)
        elif instance.comment:
            analyze_comment_toxicity(instance.comment)
        
        # Notify moderators and admins
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        moderators = User.objects.filter(
            role__in=[User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN],
            school=instance.reporter.school
        )
        
        subject = f'New Content Report - {instance.report_type}'
        message = f'''
        New content report submitted by {instance.reporter.get_display_name()}
        
        Report Type: {instance.get_report_type_display()}
        Description: {instance.description}
        
        Please review the reported content in the moderation dashboard.
        '''
        
        for moderator in moderators:
            # Create in-app notification
            Notification.objects.create(
                user=moderator,
                notification_type=Notification.NotificationType.MENTION,
                title='New content report',
                message=f'New {instance.report_type} report needs review',
            )
            
            # Send email
            if moderator.profile.email_notifications:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [moderator.email],
                    fail_silently=True,
                )

@receiver(post_save, sender=DirectMessage)
def handle_new_message(sender, instance, created, **kwargs):
    if created:
        from .models import MessageThread

        # Try to find an existing thread between sender and receiver
        thread = (
            MessageThread.objects.filter(participants=instance.sender)
            .filter(participants=instance.receiver)
            .first()
        )

        # If it doesn't exist, create one and add both users
        if not thread:
            thread = MessageThread.objects.create()
            thread.participants.add(instance.sender, instance.receiver)

        # Update thread with the latest message info
        thread.last_message = instance
        thread.last_activity = timezone.now()
        thread.save()

        # Create in-app notification
        Notification.objects.create(
            user=instance.receiver,
            notification_type=Notification.NotificationType.MESSAGE,
            title="New message",
            message=f"New message from {instance.sender.get_display_name()}",
        )

@receiver(post_save, sender=UserFollow)
def handle_new_follow(sender, instance, created, **kwargs):
    if created:
        # Create notification for followed user
        Notification.objects.create(
            user=instance.followed,
            notification_type=Notification.NotificationType.NEW_FOLLOWER,
            title='New follower',
            message=f'{instance.follower.get_display_name()} started following you',
        )

@receiver(post_save, sender=Vote)
def handle_new_vote(sender, instance, created, **kwargs):
    if created:
        target_user = None
        
        if instance.post:
            target_user = instance.post.author
            # Award XP for receiving upvotes
            if instance.vote_type == 'UPVOTE' and hasattr(target_user, 'xp_points'):
                target_user.xp_points += 1
                target_user.save()
        elif instance.comment:
            target_user = instance.comment.author
            # Award XP for receiving upvotes on comments
            if instance.vote_type == 'UPVOTE' and hasattr(target_user, 'xp_points'):
                target_user.xp_points += 0.5
                target_user.save()
        
        # Create notification if it's an upvote and not self-vote
        if (instance.vote_type == 'UPVOTE' and target_user and 
            instance.user != target_user):
            
            if instance.post:
                Notification.objects.create(
                    user=target_user,
                    notification_type=Notification.NotificationType.POST_UPVOTE,
                    title='New upvote on your post',
                    message=f'{instance.user.get_display_name()} upvoted your post',
                    post=instance.post
                )
            elif instance.comment:
                Notification.objects.create(
                    user=target_user,
                    notification_type=Notification.NotificationType.COMMENT_UPVOTE,
                    title='New upvote on your comment',
                    message=f'{instance.user.get_display_name()} upvoted your comment',
                    comment=instance.comment
                )

@receiver(post_save, sender=CommunityMembership)
def handle_new_membership(sender, instance, created, **kwargs):
    if created and instance.is_approved:
        # Update community member count
        instance.community.member_count += 1
        instance.community.save()

# 🚨 REMOVED: update_trending_signal function completely