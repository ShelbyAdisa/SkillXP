from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import SystemAdmin, SchoolAdmin, AdminAuditLog
from .serializers import *
from .permissions import IsSystemAdmin, IsSchoolAdmin, CanManageUsers
from .mixins import SchoolScopeMixin, AdminActionMixin, PermissionBasedMixin, BulkActionMixin

User = get_user_model()

class SystemAdminViewSet(AdminActionMixin, PermissionBasedMixin, viewsets.ModelViewSet):
    queryset = SystemAdmin.objects.all()
    serializer_class = SystemAdminSerializer

class SchoolAdminViewSet(AdminActionMixin, PermissionBasedMixin, viewsets.ModelViewSet):
    queryset = SchoolAdmin.objects.all()
    serializer_class = SchoolAdminSerializer

class AdminAuditLogViewSet(SchoolScopeMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AdminAuditLogSerializer
    permission_classes = [IsSystemAdmin | IsSchoolAdmin]
    
    def get_queryset(self):
        queryset = AdminAuditLog.objects.all()
        
        # Apply school scope if school admin
        if hasattr(self.request.user, 'schooladmin'):
            school = self.request.user.schooladmin.school
            # This will need to be expanded as we integrate with other apps
            queryset = queryset.filter(admin__schooladmin__school=school)
        
        return queryset
class SystemAdminViewSet(viewsets.ModelViewSet):
    queryset = SystemAdmin.objects.all()
    serializer_class = SystemAdminSerializer
    permission_classes = [IsSystemAdmin]

class SchoolAdminViewSet(viewsets.ModelViewSet):
    queryset = SchoolAdmin.objects.all()
    serializer_class = SchoolAdminSerializer
    permission_classes = [IsSystemAdmin]

class AdminAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AdminAuditLogSerializer
    permission_classes = [IsSystemAdmin | IsSchoolAdmin]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'systemadmin'):
            return AdminAuditLog.objects.all()
        elif hasattr(self.request.user, 'schooladmin'):
            return AdminAuditLog.objects.filter(admin=self.request.user)
        return AdminAuditLog.objects.none()

class AdminDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsSystemAdmin | IsSchoolAdmin]
    
    def list(self, request):
        # Basic dashboard that will expand as other apps are built
        user = request.user
        dashboard_data = {
            'admin_type': 'system' if hasattr(user, 'systemadmin') else 'school',
            'total_users': User.objects.count() if hasattr(user, 'systemadmin') else User.objects.filter(school=user.schooladmin.school).count(),
            'recent_activity': AdminAuditLog.objects.filter(admin=user)[:10].values('action_type', 'description', 'timestamp'),
            'system_status': 'active'
        }
        return Response(dashboard_data)
    
    @action(detail=False, methods=['get'], permission_classes=[CanManageUsers])
    def user_management(self, request):
        # Basic user management - will expand with users app integration
        users = User.objects.all()
        if hasattr(request.user, 'schooladmin'):
            users = users.filter(school=request.user.schooladmin.school)
        
        user_data = [{
            'id': user.id,
            'email': user.email,
            'name': user.get_full_name(),
            'role': user.role,
            'is_active': user.is_active
        } for user in users[:50]]  
        
        return Response(user_data)