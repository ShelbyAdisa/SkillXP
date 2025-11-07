from django.contrib import admin
from .models import *

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'teacher', 'section', 'student_count', 'is_active', 'created_at']
    list_filter = ['subject', 'is_active', 'created_at']
    search_fields = ['name', 'teacher__first_name', 'teacher__last_name', 'code']
    readonly_fields = ['code', 'created_at', 'updated_at']
    filter_horizontal = []  # REMOVE 'students' from here

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'classroom', 'assignment_type', 'status', 'due_date', 'points', 'xp_reward']
    list_filter = ['assignment_type', 'status', 'assigned_date']
    search_fields = ['title', 'classroom__name']
    readonly_fields = ['total_submissions', 'average_grade']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'status', 'submitted_at', 'grade', 'xp_earned']
    list_filter = ['status', 'submitted_at', 'is_xp_awarded']
    search_fields = ['student__first_name', 'student__last_name', 'assignment__title']
    readonly_fields = ['submitted_at', 'last_modified']

@admin.register(ClassPost)
class ClassPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'classroom', 'author', 'post_type', 'is_pinned', 'is_approved', 'created_at']
    list_filter = ['post_type', 'is_pinned', 'is_approved']
    search_fields = ['title', 'classroom__name', 'author__first_name']

# Register other models...
admin.site.register(Enrollment)
admin.site.register(ClassMaterial)
admin.site.register(Attendance)
admin.site.register(Comment)
admin.site.register(PollVote)
admin.site.register(Gradebook)
admin.site.register(StudentProgress)