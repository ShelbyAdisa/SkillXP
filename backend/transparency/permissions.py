from rest_framework import permissions
from users.models import User

class IsSchoolMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class CanViewFinancialData(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # All school members can view basic financial data
        return request.user.role in [
            User.Role.STUDENT, User.Role.TEACHER, User.Role.PARENT,
            User.Role.ADMIN, User.Role.SCHOOL_ADMIN
        ]

class CanSubmitTransaction(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Teachers and admins can submit transactions
        return request.user.role in [
            User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN
        ]

class CanApproveTransaction(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only admins and school admins can approve transactions
        return request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]

class CanManageBudgets(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only admins and school admins can manage budgets
        return request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]

class CanCreateVotingIssue(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Teachers and admins can create voting issues
        return request.user.role in [
            User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN
        ]

class CanVote(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user can vote on specific issue
        if view.kwargs.get('pk'):
            from .models import VotingIssue
            try:
                issue = VotingIssue.objects.get(pk=view.kwargs['pk'])
                return request.user.role in issue.eligible_roles
            except VotingIssue.DoesNotExist:
                return False
        
        return True

class CanViewAuditLogs(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only admins and school admins can view audit logs
        return request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'submitted_by'):
            return obj.submitted_by == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'generated_by'):
            return obj.generated_by == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'voter'):
            return obj.voter == request.user
        
        return False

class CanGenerateReports(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only admins and school admins can generate financial reports
        return request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]