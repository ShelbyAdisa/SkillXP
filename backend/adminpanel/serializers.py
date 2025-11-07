from rest_framework import serializers
from .models import SystemAdmin, SchoolAdmin, AdminAuditLog

class SystemAdminSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = SystemAdmin
        fields = ['id', 'user', 'user_email', 'user_name', 'created_at', 'is_active']

class SchoolAdminSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = SchoolAdmin
        fields = ['id', 'user', 'user_email', 'user_name', 'school', 'school_name', 'permissions', 'created_at', 'is_active']

class AdminAuditLogSerializer(serializers.ModelSerializer):
    admin_name = serializers.CharField(source='admin.get_full_name', read_only=True)
    admin_email = serializers.EmailField(source='admin.email', read_only=True)
    
    class Meta:
        model = AdminAuditLog
        fields = ['id', 'admin', 'admin_name', 'admin_email', 'action_type', 'description', 
                 'resource_id', 'resource_type', 'timestamp', 'ip_address']