from django.db import models
from django.conf import settings

class SystemAdmin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class SchoolAdmin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    school = models.ForeignKey('users.School', on_delete=models.CASCADE)
    permissions = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class AdminAuditLog(models.Model):
    ACTION_TYPES = (
        ('user_management', 'User Management'),
        ('content_moderation', 'Content Moderation'),
        ('system_config', 'System Configuration'),
        ('data_export', 'Data Export'),
        ('access_override', 'Access Override'),
    )
    
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    resource_id = models.CharField(max_length=100, blank=True)
    resource_type = models.CharField(max_length=50, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']