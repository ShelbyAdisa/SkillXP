from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Community(models.Model):
    class CommunityType(models.TextChoices):
        SCHOOL_WIDE = 'SCHOOL_WIDE', 'School Wide'
        GRADE_LEVEL = 'GRADE_LEVEL', 'Grade Level'
        SUBJECT = 'SUBJECT', 'Subject Based'
        INTEREST = 'INTEREST', 'Interest Based'
        CLUB = 'CLUB', 'Club/Organization'

    name = models.CharField(max_length=100)
    description = models.TextField()
    community_type = models.CharField(max_length=20, choices=CommunityType.choices)
    school = models.ForeignKey('users.School', on_delete=models.CASCADE, related_name='communities')
    
    # Membership settings
    is_public = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    
    # Moderation
    moderators = models.ManyToManyField(User, related_name='moderated_communities', blank=True)
    banned_users = models.ManyToManyField(User, related_name='banned_from_communities', blank=True)
    
    # Metadata
    member_count = models.IntegerField(default=0)
    post_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'communities'
        verbose_name_plural = 'Communities'
        unique_together = ['name', 'school']
    
    def __str__(self):
        return f"{self.name} ({self.school.name})"

class CommunityMembership(models.Model):
    class MemberRole(models.TextChoices):
        MEMBER = 'MEMBER', 'Member'
        MODERATOR = 'MODERATOR', 'Moderator'
        ADMIN = 'ADMIN', 'Admin'

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_memberships')
    role = models.CharField(max_length=10, choices=MemberRole.choices, default=MemberRole.MEMBER)
    joined_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'community_memberships'
        unique_together = ['community', 'user']

class Post(models.Model):
    class PostType(models.TextChoices):
        DISCUSSION = 'DISCUSSION', 'Discussion'
        QUESTION = 'QUESTION', 'Question'
        ANNOUNCEMENT = 'ANNOUNCEMENT', 'Announcement'
        RESOURCE = 'RESOURCE', 'Resource'
        POLL = 'POLL', 'Poll'

    class PostStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        ARCHIVED = 'ARCHIVED', 'Archived'
        REMOVED = 'REMOVED', 'Removed'

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_posts')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    post_type = models.CharField(max_length=15, choices=PostType.choices, default=PostType.DISCUSSION)
    status = models.CharField(max_length=10, choices=PostStatus.choices, default=PostStatus.PUBLISHED)
    
    # Anonymity
    is_anonymous = models.BooleanField(default=False)
    
    # Engagement metrics
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    
    # Poll fields (if post_type is POLL)
    poll_question = models.TextField(blank=True, null=True)
    poll_options = models.JSONField(default=list, blank=True)  # [{"text": "Option1", "votes": 0}]
    poll_ends_at = models.DateTimeField(null=True, blank=True)
    
    # Moderation
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    toxicity_score = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'social_posts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.author.get_display_name()}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    
    # Anonymity
    is_anonymous = models.BooleanField(default=False)
    
    # Engagement
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    # Moderation
    is_removed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'social_comments'
        ordering = ['created_at']

class Vote(models.Model):
    class VoteType(models.TextChoices):
        UPVOTE = 'UPVOTE', 'Upvote'
        DOWNVOTE = 'DOWNVOTE', 'Downvote'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_votes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    vote_type = models.CharField(max_length=8, choices=VoteType.choices)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'social_votes'
        unique_together = [
            ['user', 'post'],
            ['user', 'comment']
        ]

class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    
    # Read status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Moderation
    is_flagged = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'direct_messages'
        ordering = ['created_at']

class MessageThread(models.Model):
    participants = models.ManyToManyField(User, related_name='message_threads')
    last_message = models.ForeignKey(DirectMessage, on_delete=models.SET_NULL, null=True, blank=True)
    last_activity = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'message_threads'
        ordering = ['-last_activity']

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        POST_REPLY = 'POST_REPLY', 'Post Reply'
        COMMENT_REPLY = 'COMMENT_REPLY', 'Comment Reply'
        POST_UPVOTE = 'POST_UPVOTE', 'Post Upvote'
        COMMENT_UPVOTE = 'COMMENT_UPVOTE', 'Comment Upvote'
        NEW_FOLLOWER = 'NEW_FOLLOWER', 'New Follower'
        MENTION = 'MENTION', 'Mention'
        MESSAGE = 'MESSAGE', 'New Message'
        COMMUNITY_INVITE = 'COMMUNITY_INVITE', 'Community Invite'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_notifications')
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'social_notifications'
        ordering = ['-created_at']

class UserFollow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'user_follows'
        unique_together = ['follower', 'followed']

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'social_bookmarks'
        unique_together = ['user', 'post']

class Report(models.Model):
    class ReportType(models.TextChoices):
        SPAM = 'SPAM', 'Spam'
        HARASSMENT = 'HARASSMENT', 'Harassment'
        HATE_SPEECH = 'HATE_SPEECH', 'Hate Speech'
        INAPPROPRIATE = 'INAPPROPRIATE', 'Inappropriate Content'
        OTHER = 'OTHER', 'Other'

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_reports')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    message = models.ForeignKey(DirectMessage, on_delete=models.CASCADE, null=True, blank=True)
    report_type = models.CharField(max_length=15, choices=ReportType.choices)
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'social_reports'

class TrendingTopic(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey('users.School', on_delete=models.CASCADE, related_name='trending_topics')
    post_count = models.IntegerField(default=0)
    score = models.FloatField(default=0.0)  # Trending score based on engagement
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'trending_topics'
        unique_together = ['name', 'school']