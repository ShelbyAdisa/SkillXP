from rest_framework import permissions

class IsSystemAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'systemadmin') and request.user.systemadmin.is_active

class IsSchoolAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'schooladmin') and request.user.schooladmin.is_active

class CanManageUsers(permissions.BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, 'systemadmin'):
            return True
        if hasattr(request.user, 'schooladmin'):
            return request.user.schooladmin.permissions.get('can_manage_users', False)
        return False