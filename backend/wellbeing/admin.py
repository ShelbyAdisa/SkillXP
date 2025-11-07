from django.contrib import admin
from .models import (
    WellbeingPost, PostComment, PostReaction, SupportTicket, TicketMessage,
    CounselorAssignment, WellbeingResource, MoodCheck, WellbeingGoal,
    CrisisAlert, ContentReport, ModerationAction
)

@admin.register(WellbeingPost)
class WellbeingPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_type', 'is_anonymous', 'is_approved', 'is_urgent', 'upvotes', 'get_created_at')
    list_filter = ('post_type', 'is_approved', 'is_urgent', 'is_anonymous')  # REMOVED: 'created_at'
    search_fields = ('title', 'content', 'author__email', 'author__first_name', 'author__last_name')
    readonly_fields = ('get_created_at', 'get_updated_at')  # CHANGED: Use methods
    actions = ['approve_posts', 'reject_posts']

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Updated At'

    def approve_posts(self, request, queryset):
        queryset.update(is_approved=True)
    approve_posts.short_description = "Approve selected posts"

    def reject_posts(self, request, queryset):
        queryset.update(is_approved=False)
    reject_posts.short_description = "Reject selected posts"

@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('content_preview', 'post', 'author', 'is_anonymous', 'is_approved', 'get_created_at')
    list_filter = ('is_approved', 'is_anonymous')  # REMOVED: 'created_at'
    search_fields = ('content', 'author__email', 'post__title')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'counselor', 'status', 'priority', 'get_created_at')
    list_filter = ('status', 'priority', 'is_anonymous')  # REMOVED: 'created_at'
    search_fields = ('title', 'description', 'student__email', 'counselor__email')
    readonly_fields = ('get_created_at', 'get_updated_at', 'resolved_at')  # CHANGED: Use methods

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Updated At'

@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'is_counselor_response', 'get_created_at')
    list_filter = ('is_counselor_response',)  # REMOVED: 'created_at'
    search_fields = ('content', 'ticket__title', 'sender__email')

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

@admin.register(CounselorAssignment)
class CounselorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('counselor', 'student', 'is_active', 'assigned_at')
    list_filter = ('is_active',)  # REMOVED: 'assigned_at'
    search_fields = ('counselor__email', 'student__email')

@admin.register(WellbeingResource)
class WellbeingResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'is_published', 'created_by', 'get_created_at')
    list_filter = ('resource_type', 'is_published')  # REMOVED: 'created_at'
    search_fields = ('title', 'description', 'tags')

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

@admin.register(MoodCheck)
class MoodCheckAdmin(admin.ModelAdmin):
    list_display = ('user', 'mood_level', 'get_created_at')
    list_filter = ('mood_level',)  # REMOVED: 'created_at'
    search_fields = ('user__email', 'notes')

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

@admin.register(WellbeingGoal)
class WellbeingGoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'target_date', 'get_created_at')
    list_filter = ('status', 'target_date')  # REMOVED: 'created_at'
    search_fields = ('title', 'user__email')

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

@admin.register(CrisisAlert)
class CrisisAlertAdmin(admin.ModelAdmin):
    list_display = ('reported_by', 'severity_level', 'status', 'assigned_counselor', 'get_created_at')
    list_filter = ('status', 'severity_level')  # REMOVED: 'created_at'
    search_fields = ('description', 'reported_by__email')
    readonly_fields = ('get_created_at', 'get_updated_at')  # CHANGED: Use methods

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Updated At'

@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'reporter', 'is_resolved', 'get_created_at')
    list_filter = ('report_type', 'is_resolved')  # REMOVED: 'created_at'
    search_fields = ('description', 'reporter__email')

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

@admin.register(ModerationAction)
class ModerationActionAdmin(admin.ModelAdmin):
    list_display = ('moderator', 'target_user', 'action_type', 'get_created_at')
    list_filter = ('action_type',)  # REMOVED: 'created_at'
    search_fields = ('moderator__email', 'target_user__email', 'reason')
    readonly_fields = ('get_created_at', 'get_updated_at')  # CHANGED: Use methods

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Updated At'