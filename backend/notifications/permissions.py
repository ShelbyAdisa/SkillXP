from rest_framework import permissions

class IsNotificationOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of a notification to view/delete it.
    """
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            return obj.user == request.user
        return False