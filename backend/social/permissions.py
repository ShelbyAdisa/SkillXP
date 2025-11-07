from rest_framework import permissions
from users.models import User

class IsSchoolMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class CanPostInCommunity(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if community allows posting
        community_id = request.data.get('community') or view.kwargs.get('community_id')
        if community_id:
            from .models import CommunityMembership
            return CommunityMembership.objects.filter(
                community_id=community_id,
                user=request.user,
                is_approved=True
            ).exists()
        
        return True  # Allow school-wide posts

class IsCommunityModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return True
        
        if hasattr(obj, 'community'):
            return obj.community.moderators.filter(id=request.user.id).exists()
        elif hasattr(obj, 'moderators'):
            return obj.moderators.filter(id=request.user.id).exists()
        
        return False

class IsOwnerOrModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'author'):
            if obj.author == request.user:
                return True
        
        if hasattr(obj, 'user'):
            if obj.user == request.user:
                return True
        
        if hasattr(obj, 'sender'):
            if obj.sender == request.user:
                return True
        
        # Check if user is community moderator
        if hasattr(obj, 'community'):
            return obj.community.moderators.filter(id=request.user.id).exists()
        
        return False

class CanMessageUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Students can only message teachers and other students in their school
        receiver_id = request.data.get('receiver')
        if receiver_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                receiver = User.objects.get(id=receiver_id)
                if receiver.school != request.user.school:
                    return False
                
                # Role-based messaging restrictions
                if request.user.role == User.Role.STUDENT:
                    return receiver.role in [User.Role.STUDENT, User.Role.TEACHER]
                elif request.user.role == User.Role.PARENT:
                    return receiver.role in [User.Role.TEACHER, User.Role.ADMIN]
                
                return True  # Teachers and admins can message anyone
                
            except User.DoesNotExist:
                return False
        
        return True

class CanViewCommunity(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_public:
            return True
        
        # Check if user is a member of private community
        from .models import CommunityMembership
        return CommunityMembership.objects.filter(
            community=obj,
            user=request.user,
            is_approved=True
        ).exists()

class CanModerateContent(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.role in [User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN]