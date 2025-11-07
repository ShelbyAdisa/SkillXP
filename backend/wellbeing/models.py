from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class WellbeingPost(models.Model):
    class PostType(models.TextChoices):
        GENERAL = 'GENERAL', 'General Discussion'
        SUPPORT = 'SUPPORT', 'Seeking Support'
        ADVICE = 'ADVICE', 'Asking for Advice'
        VENT = 'VENT', 'Just Venting'
        SUCCESS = 'SUCCESS', 'Success Story'

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wellbeing_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=PostType.choices, default=PostType.GENERAL)
    is_anonymous = models.BooleanField(default=True)
    
    # Moderation fields
    is_approved = models.BooleanField(default=True)
    is_urgent = models.BooleanField(default=False)
    toxicity_score = models.FloatField(null=True, blank=True)
    
    # Engagement metrics
    upvotes = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wellbeing_posts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.author.get_display_name()}"

class PostComment(models.Model):
    post = models.ForeignKey(WellbeingPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wellbeing_comments')
    content = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    
    # Moderation
    is_approved = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'post_comments'
        ordering = ['created_at']

class PostReaction(models.Model):
    class ReactionType(models.TextChoices):
        LIKE = 'LIKE', 'Like'
        SUPPORT = 'SUPPORT', 'Support'
        THANKS = 'THANKS', 'Thanks'
        CARE = 'CARE', 'Care'
    
    post = models.ForeignKey(WellbeingPost, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wellbeing_reactions')
    reaction_type = models.CharField(max_length=10, choices=ReactionType.choices)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'post_reactions'
        unique_together = ['post', 'user']

class SupportTicket(models.Model):
    class TicketStatus(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'
    
    class PriorityLevel(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    counselor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='assigned_tickets', limit_choices_to={'role': User.Role.TEACHER})
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TicketStatus.choices, default=TicketStatus.OPEN)
    priority = models.CharField(max_length=10, choices=PriorityLevel.choices, default=PriorityLevel.MEDIUM)
    
    # Privacy
    is_anonymous = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']

class TicketMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_messages')
    content = models.TextField()
    is_counselor_response = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'ticket_messages'
        ordering = ['created_at']

class CounselorAssignment(models.Model):
    counselor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_assignments',
                                 limit_choices_to={'role': User.Role.TEACHER})
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='counselor_assignments',
                               limit_choices_to={'role': User.Role.STUDENT})
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'counselor_assignments'
        unique_together = ['counselor', 'student']

class WellbeingResource(models.Model):
    class ResourceType(models.TextChoices):
        ARTICLE = 'ARTICLE', 'Article'
        VIDEO = 'VIDEO', 'Video'
        PODCAST = 'PODCAST', 'Podcast'
        HELPLINE = 'HELPLINE', 'Helpline'
        EXERCISE = 'EXERCISE', 'Exercise'
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices)
    content_url = models.URLField(blank=True, null=True)
    content_file = models.FileField(upload_to='wellbeing/resources/', blank=True, null=True)
    
    # Target audience
    target_roles = models.JSONField(default=list) 
    tags = models.JSONField(default=list)
    
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'wellbeing_resources'
        ordering = ['-created_at']

class MoodCheck(models.Model):
    class MoodLevel(models.IntegerChoices):
        VERY_LOW = 1, 'Very Low'
        LOW = 2, 'Low'
        NEUTRAL = 3, 'Neutral'
        GOOD = 4, 'Good'
        EXCELLENT = 5, 'Excellent'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_checks')
    mood_level = models.IntegerField(choices=MoodLevel.choices, validators=[MinValueValidator(1), MaxValueValidator(5)])
    notes = models.TextField(blank=True, null=True)
    factors = models.JSONField(default=list) 
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'mood_checks'
        ordering = ['-created_at']
        unique_together = ['user', 'created_at']  

class WellbeingGoal(models.Model):
    class GoalStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        ARCHIVED = 'ARCHIVED', 'Archived'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wellbeing_goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    target_date = models.DateField()
    status = models.CharField(max_length=20, choices=GoalStatus.choices, default=GoalStatus.ACTIVE)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wellbeing_goals'
        ordering = ['-created_at']

class CrisisAlert(models.Model):
    class AlertStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        ACKNOWLEDGED = 'ACKNOWLEDGED', 'Acknowledged'
        RESOLVED = 'RESOLVED', 'Resolved'
        ESCALATED = 'ESCALATED', 'Escalated'
    
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_alerts')
    post = models.ForeignKey(WellbeingPost, on_delete=models.CASCADE, null=True, blank=True)
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    severity_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    status = models.CharField(max_length=20, choices=AlertStatus.choices, default=AlertStatus.PENDING)
    
    assigned_counselor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                         limit_choices_to={'role': User.Role.TEACHER})
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crisis_alerts'
        ordering = ['-created_at']

class ContentReport(models.Model):
    class ReportType(models.TextChoices):
        HARASSMENT = 'HARASSMENT', 'Harassment'
        SELF_HARM = 'SELF_HARM', 'Self-harm Content'
        BULLYING = 'BULLYING', 'Bullying'
        INAPPROPRIATE = 'INAPPROPRIATE', 'Inappropriate Content'
        OTHER = 'OTHER', 'Other'
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_reports')
    post = models.ForeignKey(WellbeingPost, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'content_reports'

class ModerationAction(models.Model):
    class ActionType(models.TextChoices):
        POST_REMOVED = 'POST_REMOVED', 'Post Removed'
        COMMENT_REMOVED = 'COMMENT_REMOVED', 'Comment Removed'
        USER_WARNED = 'USER_WARNED', 'User Warned'
        USER_SUSPENDED = 'USER_SUSPENDED', 'User Suspended'
        CONTENT_APPROVED = 'CONTENT_APPROVED', 'Content Approved'
    
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_actions')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_history')
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    reason = models.TextField()
    
    post = models.ForeignKey(WellbeingPost, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'moderation_actions'
        ordering = ['-created_at']