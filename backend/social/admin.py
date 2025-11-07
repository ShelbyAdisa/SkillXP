from django.contrib import admin
from .models import (
    Community, CommunityMembership, Post, Comment, Vote,
    DirectMessage, MessageThread, Notification, UserFollow,
    Bookmark, Report, TrendingTopic
)

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'community_type', 'school', 'is_public', 'member_count', 'post_count', 'created_at')
    list_filter = ('community_type', 'is_public', 'school', 'created_at')
    search_fields = ('name', 'description', 'school__name')
    filter_horizontal = ('moderators', 'banned_users')
    readonly_fields = ('member_count', 'post_count', 'created_at', 'updated_at')

@admin.register(CommunityMembership)
class CommunityMembershipAdmin(admin.ModelAdmin):
    list_display = ('community', 'user', 'role', 'is_approved', 'joined_at')
    list_filter = ('role', 'is_approved', 'joined_at')
    search_fields = ('community__name', 'user__email', 'user__first_name', 'user__last_name')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'community', 'post_type', 'status', 'upvotes', 'comment_count', 'created_at')
    list_filter = ('post_type', 'status', 'is_anonymous', 'is_pinned', 'is_locked', 'created_at')
    search_fields = ('title', 'content', 'author__email', 'community__name')
    readonly_fields = ('upvotes', 'downvotes', 'view_count', 'comment_count', 'created_at', 'updated_at')
    actions = ['approve_posts', 'pin_posts', 'lock_posts']

    def approve_posts(self, request, queryset):
        queryset.update(status=Post.PostStatus.PUBLISHED)
    approve_posts.short_description = "Approve selected posts"

    def pin_posts(self, request, queryset):
        for post in queryset:
            post.is_pinned = not post.is_pinned
            post.save()
    pin_posts.short_description = "Toggle pin status"

    def lock_posts(self, request, queryset):
        for post in queryset:
            post.is_locked = not post.is_locked
            post.save()
    lock_posts.short_description = "Toggle lock status"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content_preview', 'post', 'author', 'is_anonymous', 'upvotes', 'is_removed', 'created_at')
    list_filter = ('is_anonymous', 'is_removed', 'created_at')
    search_fields = ('content', 'post__title', 'author__email')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content_preview', 'is_read', 'is_flagged', 'created_at')
    list_filter = ('is_read', 'is_flagged', 'created_at')
    search_fields = ('content', 'sender__email', 'receiver__email')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'participants_list', 'last_activity', 'created_at')
    filter_horizontal = ('participants',)
    
    def participants_list(self, obj):
        return ", ".join([user.get_display_name() for user in obj.participants.all()])
    participants_list.short_description = 'Participants'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'is_sent', 'created_at')
    list_filter = ('notification_type', 'is_read', 'is_sent', 'created_at')
    search_fields = ('user__email', 'title', 'message')

@admin.register(UserFollow)
class UserFollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__email', 'followed__email')

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'post__title')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'report_type', 'is_resolved', 'created_at')
    list_filter = ('report_type', 'is_resolved', 'created_at')
    search_fields = ('reporter__email', 'description')

@admin.register(TrendingTopic)
class TrendingTopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'post_count', 'score', 'created_at')
    list_filter = ('school', 'created_at')
    search_fields = ('name', 'school__name')
    readonly_fields = ('post_count', 'score', 'created_at')

# Inline admins for better UX
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('upvotes', 'downvotes', 'created_at')
    classes = ['collapse']

class VoteInline(admin.TabularInline):
    model = Vote
    extra = 0
    readonly_fields = ('created_at',)
    classes = ['collapse']

# Add inlines to PostAdmin
PostAdmin.inlines = [CommentInline, VoteInline]