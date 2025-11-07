from rest_framework import permissions

class CanViewAnalytics(permissions.BasePermission):
    def has_permission(self, request, view):
        # System admins, school admins, and teachers can view analytics
        if hasattr(request.user, 'systemadmin'):
            return True
        if hasattr(request.user, 'schooladmin'):
            return True
        if hasattr(request.user, 'teacher'):
            return True
        return False

class CanViewPredictiveAnalytics(permissions.BasePermission):
    def has_permission(self, request, view):
        # Only admins can view predictive analytics
        return hasattr(request.user, 'systemadmin') or hasattr(request.user, 'schooladmin')