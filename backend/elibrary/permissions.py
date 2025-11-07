from rest_framework import permissions
from users.models import User

class IsSchoolMember(permissions.BasePermission):
    # Check if user belongs to the same school as the resource
    def has_object_permission(self, request, view, obj):
        return obj.school == request.user.school

class CanAccessResource(permissions.BasePermission):
    # Check if user can access a specific resource
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Public resources are accessible to all authenticated users
        if obj.access_level == 'PUBLIC':
            return True
        
        # School resources require same school
        if obj.access_level == 'SCHOOL':
            return obj.school == user.school
        
        # Classroom resources require enrollment
        if obj.access_level == 'CLASSROOM':
            return (obj.classrooms.filter(students=user).exists() or 
                    obj.classrooms.filter(teacher=user).exists())
        
        # Private resources only for creator
        if obj.access_level == 'PRIVATE':
            return obj.created_by == user
        
        return False

class CanManageResource(permissions.BasePermission):
    # Check if user can manage a resource
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Creator can always manage
        if obj.created_by == user:
            return True
        
        # Teachers can manage resources in their classrooms
        if user.role == User.Role.TEACHER:
            return obj.classrooms.filter(teacher=user).exists()
        
        # Admins can manage all resources in their school
        if user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return obj.school == user.school
        
        return False

class CanCreateResource(permissions.BasePermission):
    # Check if user can create resources
    def has_permission(self, request, view):
        user = request.user
        
        # Teachers, admins, and school admins can create resources
        return user.role in [
            User.Role.TEACHER, 
            User.Role.ADMIN, 
            User.Role.SCHOOL_ADMIN
        ]

class CanApproveResource(permissions.BasePermission):
    # Check if user can approve resources
    def has_permission(self, request, view):
        user = request.user
        
        # Only admins and school admins can approve resources
        return user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]
    
    def has_object_permission(self, request, view, obj):
        # Can only approve resources from their school
        return obj.school == request.user.school

class IsCollectionOwnerOrCollaborator(permissions.BasePermission):
    # Check if user owns or can collaborate on a collection
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Owner can always manage
        if obj.created_by == user:
            return True
        if obj.allow_collaboration and obj.collaborators.filter(id=user.id).exists():
            return True
        
        return False

class CanViewPublicCollections(permissions.BasePermission):
    # Check if user can view public collections
    def has_object_permission(self, request, view, obj):
        # Public collections are viewable by all authenticated users
        if obj.is_public:
            return True
        
        # Private collections only for owner and collaborators
        user = request.user
        return (obj.created_by == user or 
                obj.collaborators.filter(id=user.id).exists())

class CanCreateCategory(permissions.BasePermission):
    # Check if user can create resource categories
    def has_permission(self, request, view):
        user = request.user
        
        # Only teachers and admins can create categories
        return user.role in [
            User.Role.TEACHER,
            User.Role.ADMIN,
            User.Role.SCHOOL_ADMIN
        ]

class CanReviewResource(permissions.BasePermission):
    # Check if user can review resources
    def has_permission(self, request, view):
        user = request.user
        
        # All authenticated users can review resources they have access to
        return user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users can only review resources they can access
        user = request.user
        resource = obj.resource
        
        # Check resource access permissions directly
        if resource.access_level == 'PUBLIC':
            return True
        elif resource.access_level == 'SCHOOL':
            return resource.school == user.school
        elif resource.access_level == 'CLASSROOM':
            return (resource.classrooms.filter(students=user).exists() or 
                    resource.classrooms.filter(teacher=user).exists())
        elif resource.access_level == 'PRIVATE':
            return resource.created_by == user
        
        return False

class CanInteractWithResource(permissions.BasePermission):
    # Check if user can interact with resources 
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.access_level == 'PUBLIC':
            return True
        elif obj.access_level == 'SCHOOL':
            return obj.school == user.school
        elif obj.access_level == 'CLASSROOM':
            return (obj.classrooms.filter(students=user).exists() or 
                    obj.classrooms.filter(teacher=user).exists())
        elif obj.access_level == 'PRIVATE':
            return obj.created_by == user
        
        return False

class IsReadingListOwner(permissions.BasePermission):
    # Check if user owns the reading list
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class CanViewPublicReadingLists(permissions.BasePermission):
    # Check if user can view public reading lists
    def has_object_permission(self, request, view, obj):
        # Public reading lists are viewable by all authenticated users
        if obj.is_public:
            return True
        
        # Private reading lists only for owner
        return obj.user == request.user

class ResourceActionPermission(permissions.BasePermission):
    # Permission class for resource-specific actions
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        #  For view/download/similar/analytics actions, user must have access to the resource
        if view.action in ['record_view', 'record_download', 'similar_resources', 'analytics']:
            return CanAccessResource().has_object_permission(request, view, obj)
        
        # For favorite and completion actions, user must have access to the resource
        if view.action in ['toggle_favorite', 'record_completion']:
            return CanAccessResource().has_object_permission(request, view, obj)
        
        return False

class AdminResourcePermission(permissions.BasePermission):
    # Admin-level permissions for resource management
    def has_permission(self, request, view):
        user = request.user
        
        if view.action in ['approve', 'reject', 'feature', 'pending_approval']:
            return user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # Admin actions only on resources from their school
        return obj.school == request.user.school

class SearchPermission(permissions.BasePermission):
    # Permission for search functionality
    def has_permission(self, request, view):
        # All authenticated users can search
        return request.user.is_authenticated

class RecommendationPermission(permissions.BasePermission):
    # Permission for recommendation functionality
    def has_permission(self, request, view):
        # All authenticated users can get recommendations
        return request.user.is_authenticated

class DashboardPermission(permissions.BasePermission):
    # Permission for dashboard access
    def has_permission(self, request, view):
        # All authenticated users can access their dashboard
        return request.user.is_authenticated

class CanUploadResource(permissions.BasePermission):
    # Check if user can upload resources
    def has_permission(self, request, view):
        user = request.user
        
        # Teachers, admins, and school admins can upload resources
        return user.role in [
            User.Role.TEACHER, 
            User.Role.ADMIN, 
            User.Role.SCHOOL_ADMIN
        ]

class CanModerateReviews(permissions.BasePermission):
    # Check if user can moderate reviews
    def has_permission(self, request, view):
        user = request.user
        
        # Only admins and school admins can moderate reviews
        return user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]
    
    def has_object_permission(self, request, view, obj):
        # Can only moderate reviews for resources from their school
        return obj.resource.school == request.user.school

class BulkOperationPermission(permissions.BasePermission):
    # Permission for bulk operations
    def has_permission(self, request, view):
        user = request.user
        
        # Only teachers and admins can perform bulk operations
        return user.role in [
            User.Role.TEACHER,
            User.Role.ADMIN,
            User.Role.SCHOOL_ADMIN
        ]

class AnalyticsPermission(permissions.BasePermission):
    # Permission for analytics access
    def has_permission(self, request, view):
        user = request.user
        
        # Teachers and admins can access analytics
        return user.role in [
            User.Role.TEACHER,
            User.Role.ADMIN,
            User.Role.SCHOOL_ADMIN
        ]

class GlobalSearchPermission(permissions.BasePermission):
    # Permission for global search
    def has_permission(self, request, view):
        # All authenticated users can use global search
        return request.user.is_authenticated