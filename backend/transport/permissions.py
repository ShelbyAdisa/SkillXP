from rest_framework import permissions
from users.models import User

class IsSchoolMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class CanManageTransport(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # School admins and transport managers can manage transport
        return request.user.role in [
            User.Role.ADMIN, 
            User.Role.SCHOOL_ADMIN
        ]

class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user has a driver profile
        return hasattr(request.user, 'driver_profile') and request.user.driver_profile.is_active

class IsParentOrStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.role in [User.Role.STUDENT, User.Role.PARENT]

class CanViewStudentTransport(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Parents can only view their children's transport info
        if request.user.role == User.Role.PARENT:
            return True
        
        # Students can view their own transport info
        if request.user.role == User.Role.STUDENT:
            return True
        
        # Admins and drivers can view all
        return request.user.role in [
            User.Role.ADMIN, 
            User.Role.SCHOOL_ADMIN,
            User.Role.TEACHER  # Teachers might need to view for attendance
        ]

class CanUpdateLocation(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only drivers can update location
        if not hasattr(request.user, 'driver_profile'):
            return False
        
        # Driver must be assigned to the trip they're updating
        if view.kwargs.get('trip_id'):
            from .models import Trip
            try:
                trip = Trip.objects.get(id=view.kwargs['trip_id'])
                return trip.driver == request.user.driver_profile
            except Trip.DoesNotExist:
                return False
        
        return True

class CanMarkAttendance(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Drivers and teachers can mark attendance
        return (hasattr(request.user, 'driver_profile') or 
                request.user.role in [User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN])

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'student'):
            return obj.student == request.user
        elif hasattr(obj, 'driver'):
            return obj.driver.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False

class CanViewLiveTracking(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Parents can view their children's bus tracking
        if request.user.role == User.Role.PARENT:
            return True
        
        # Students can view their own bus tracking
        if request.user.role == User.Role.STUDENT:
            return True
        
        # Admins and drivers can view all tracking
        return request.user.role in [
            User.Role.ADMIN, 
            User.Role.SCHOOL_ADMIN
        ] or hasattr(request.user, 'driver_profile')

class CanCreateEmergencyAlert(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Drivers and admins can create emergency alerts
        return (hasattr(request.user, 'driver_profile') or 
                request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN])