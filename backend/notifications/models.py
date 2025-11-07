from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey  
from django.contrib.contenttypes.models import ContentType  
User = get_user_model()

class Notification(models.Model):
    class Type(models.TextChoices):
        # General/User Notifications
        ACCOUNT_ALERT = 'ACCOUNT_ALERT', 'Account Alert'
        SYSTEM_MESSAGE = 'SYSTEM_MESSAGE', 'System Message'
        
        # Classroom/LMS Notifications
        ASSIGNMENT_DUE = 'ASSIGNMENT_DUE', 'Assignment Due'
        ASSIGNMENT_GRADED = 'ASSIGNMENT_GRADED', 'Assignment Graded'
        NEW_POST = 'NEW_POST', 'New Classroom Post'
        RESOURCE_APPROVED = 'RESOURCE_APPROVED', 'Resource Approved'
        
        # Social Notifications (duplicates social/models.py but centralized here)
        POST_REPLY = 'POST_REPLY', 'Post Reply'
        COMMENT_REPLY = 'COMMENT_REPLY', 'Comment Reply'
        NEW_FOLLOWER = 'NEW_FOLLOWER', 'New Follower'
        MENTION = 'MENTION', 'Mention'
        NEW_MESSAGE = 'NEW_MESSAGE', 'New Message'
        
        # Wellbeing Notifications
        CRISIS_ALERT = 'CRISIS_ALERT', 'Crisis Alert'
        TICKET_RESPONSE = 'TICKET_RESPONSE', 'Support Ticket Response'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=Type.choices)
    message = models.TextField()
    
    # Target object identifiers (generic foreign key implementation)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent_push = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]
    
    def __str__(self):
        return f"[{self.notification_type}] for {self.user.get_display_name()} - {self.message[:30]}..."

# Since the social app already defines its own Notification model for social events, 
# for a simple centralized notification list, we will rely on signals copying or linking 
# into this central model. For now, we only need this single centralized model.