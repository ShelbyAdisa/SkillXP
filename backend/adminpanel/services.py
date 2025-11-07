from .models import AdminAuditLog

class AdminService:
    @staticmethod
    def log_admin_action(admin, action_type, description, resource_id="", resource_type=""):
        return AdminAuditLog.objects.create(
            admin=admin,
            action_type=action_type,
            description=description,
            resource_id=resource_id,
            resource_type=resource_type
        )
    
    @staticmethod
    def create_system_admin(user):
        from .models import SystemAdmin
        return SystemAdmin.objects.create(user=user)
    
    @staticmethod
    def create_school_admin(user, school, permissions=None):
        from .models import SchoolAdmin
        if permissions is None:
            permissions = {
                'can_manage_users': True,
                'can_moderate_content': True,
                'can_view_analytics': True
            }
        return SchoolAdmin.objects.create(user=user, school=school, permissions=permissions)