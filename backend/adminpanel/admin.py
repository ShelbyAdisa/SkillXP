from django.contrib import admin
from .models import SystemAdmin, SchoolAdmin, AdminAuditLog

@admin.register(SystemAdmin)
class SystemAdminAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']

@admin.register(SchoolAdmin)
class SchoolAdminAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'created_at', 'is_active']
    list_filter = ['is_active', 'school', 'created_at']

@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ['admin', 'action_type', 'resource_type', 'timestamp']
    list_filter = ['action_type', 'timestamp']
    search_fields = ['admin__email', 'description']
    readonly_fields = ['timestamp']