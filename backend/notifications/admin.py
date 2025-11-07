from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'notification_type', 'message_preview', 
        'is_read', 'created_at', 'content_object'
    )
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'message')
    date_hierarchy = 'created_at'
    list_editable = ('is_read',)
    
    def message_preview(self, obj):
        return obj.message[:70] + '...' if len(obj.message) > 70 else obj.message
    message_preview.short_description = 'Message'