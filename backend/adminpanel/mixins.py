from rest_framework.response import Response
from rest_framework.decorators import action
from .permissions import IsSystemAdmin, IsSchoolAdmin

class SchoolScopeMixin:
 
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if hasattr(self.request.user, 'schooladmin'):
            school = self.request.user.schooladmin.school
            
            # Handle different model structures across apps
            if hasattr(queryset.model, 'school'):
                return queryset.filter(school=school)
            elif hasattr(queryset.model, 'user'):
                return queryset.filter(user__school=school)
            elif hasattr(queryset.model, 'classroom'):
                return queryset.filter(classroom__school=school)
        
        return queryset

class AdminActionMixin:
    """
    Mixin to log admin actions automatically
    """
    def perform_create(self, serializer):
        instance = serializer.save()
        self._log_admin_action('create', f"Created {instance._meta.verbose_name}: {instance}")
        return instance
    
    def perform_update(self, serializer):
        instance = serializer.save()
        self._log_admin_action('update', f"Updated {instance._meta.verbose_name}: {instance}")
        return instance
    
    def perform_destroy(self, instance):
        self._log_admin_action('delete', f"Deleted {instance._meta.verbose_name}: {instance}")
        instance.delete()
    
    def _log_admin_action(self, action, description):
        from .services import AdminService
        AdminService.log_admin_action(
            admin=self.request.user,
            action_type='system_config',
            description=description,
            resource_id=str(getattr(self, 'instance', None)),
            resource_type=self.queryset.model._meta.label
        )

class PermissionBasedMixin:
    """
    Mixin to handle different permissions for SystemAdmin vs SchoolAdmin
    """
    def get_permissions(self):
        permissions = []
        
        if self.action in ['create', 'update', 'destroy']:
            permissions.append(IsSystemAdmin())
        elif self.action in ['list', 'retrieve']:
            permissions.append(IsSystemAdmin() | IsSchoolAdmin())
        else:
            permissions = super().get_permissions()
        
        return permissions

class BulkActionMixin:
   
    @action(detail=False, methods=['post'], permission_classes=[IsSystemAdmin | IsSchoolAdmin])
    def bulk_activate(self, request):
        ids = request.data.get('ids', [])
        queryset = self.get_queryset().filter(id__in=ids)
        queryset.update(is_active=True)
        
        from .services import AdminService
        AdminService.log_admin_action(
            admin=request.user,
            action_type='user_management',
            description=f"Bulk activated {len(ids)} {self.queryset.model._meta.verbose_name_plural}"
        )
        
        return Response({'message': f'Successfully activated {len(ids)} items'})
    
    @action(detail=False, methods=['post'], permission_classes=[IsSystemAdmin | IsSchoolAdmin])
    def bulk_deactivate(self, request):
        ids = request.data.get('ids', [])
        queryset = self.get_queryset().filter(id__in=ids)
        queryset.update(is_active=False)
        
        from .services import AdminService
        AdminService.log_admin_action(
            admin=request.user,
            action_type='user_management',
            description=f"Bulk deactivated {len(ids)} {self.queryset.model._meta.verbose_name_plural}"
        )
        
        return Response({'message': f'Successfully deactivated {len(ids)} items'})