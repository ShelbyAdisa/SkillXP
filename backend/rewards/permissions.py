from rest_framework import permissions
from users.models import User

class IsStudent(permissions.BasePermission):
    """
    Custom permission to allow access only to users with the STUDENT role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role == User.Role.STUDENT)

class CanManageRewards(permissions.BasePermission):
    """
    Custom permission to allow access for reward management (Admin/School Admin/Teacher).
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN, User.Role.TEACHER])