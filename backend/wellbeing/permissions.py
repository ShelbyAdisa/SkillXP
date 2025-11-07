from rest_framework import permissions
from users.models import User

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role == User.Role.STUDENT)

class IsTeacherOrCounselor(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.role in [User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN])

class IsCounselorAssigned(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return True
        
        if hasattr(obj, 'counselor'):
            return obj.counselor == request.user
        elif hasattr(obj, 'assigned_counselor'):
            return obj.assigned_counselor == request.user
        elif hasattr(obj, 'ticket'):
            return obj.ticket.counselor == request.user
        
        return False

class IsOwnerOrCounselor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'student'):
            return obj.student == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'reporter'):
            return obj.reporter == request.user
        
        # Check if user is assigned counselor
        if hasattr(obj, 'counselor') and obj.counselor == request.user:
            return True
        
        return False

class CanCreatePost(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only students and teachers can create wellbeing posts
        return request.user.role in [User.Role.STUDENT, User.Role.TEACHER]

class CanAccessAnonymousData(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admins and counselors can see behind anonymity
        return request.user.role in [User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN]

class CanModerateContent(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only teachers and admins can moderate
        return request.user.role in [User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN]