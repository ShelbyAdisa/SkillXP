from rest_framework import permissions
from users.models import User

class IsClassroomTeacher(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj can be Classroom, Assignment, etc.
        if hasattr(obj, 'teacher'):
            return obj.teacher == request.user
        elif hasattr(obj, 'classroom'):
            return obj.classroom.teacher == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        return False

class IsEnrolledStudent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role != User.Role.STUDENT:
            return False
            
        if hasattr(obj, 'classroom'):
            return obj.classroom.students.filter(id=request.user.id).exists()
        elif hasattr(obj, 'students'):
            return obj.students.filter(id=request.user.id).exists()
        return False

class CanJoinClassroom(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.STUDENT

class CanCreateAssignment(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in [User.Role.TEACHER, User.Role.ADMIN]

class CanSubmitAssignment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role != User.Role.STUDENT:
            return False
        
        # Check if student is enrolled in the assignment's classroom
        return obj.classroom.students.filter(id=request.user.id).exists()

class CanViewClassroom(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Teachers can view their own classrooms
        if obj.teacher == request.user:
            return True
        
        # Students can view if enrolled
        if request.user.role == User.Role.STUDENT:
            return obj.students.filter(id=request.user.id).exists()
        
        # Admins can view all classrooms in their school
        if request.user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return obj.school == request.user.school
            
        return False

class CanPostInClassroom(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Teachers can always post
        if obj.teacher == request.user:
            return True
        
        # Students can post if allowed and enrolled
        if request.user.role == User.Role.STUDENT:
            return (obj.allow_student_posts and 
                   obj.students.filter(id=request.user.id).exists())
        
        return False