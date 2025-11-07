from rest_framework import permissions
from users.models import User

class IsSchoolAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN])
class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role == User.Role.TEACHER)

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role == User.Role.STUDENT)

class IsParent(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role == User.Role.PARENT)

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if user is admin
        if request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'id'):
            return obj.id == request.user.id
        
        return False

class CanToggleAnonymous(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if school allows anonymity
        if not request.user.school.is_anonymous_allowed:
            return False
        
        # Only students and teachers can use anonymous mode
        return request.user.role in [User.Role.STUDENT, User.Role.TEACHER]