from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from django.urls import reverse
from django.utils.http import urlencode
from .models import *

class ResourceCategoryInline(admin.TabularInline):
    # Inline for subcategories
    model = ResourceCategory
    fields = ['name', 'is_active', 'resource_count']
    readonly_fields = ['resource_count']
    extra = 0
    show_change_link = True

    def resource_count(self, obj):
        return obj.resources.count()
    resource_count.short_description = 'Resources'

@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'parent_category', 'resource_count', 'is_active', 'created_by', 'get_created_at']
    list_filter = ['school', 'is_active', 'parent_category']  # REMOVED: 'created_at'
    search_fields = ['name', 'description']
    readonly_fields = ['get_created_at']  # CHANGED: Use method instead of direct field
    list_editable = ['is_active']
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'color', 'icon')
        }),
        ('Organization', {
            'fields': ('school', 'parent_category')
        }),
        ('Status', {
            'fields': ('is_active', 'created_by')
        }),
        ('Metadata', {
            'fields': ('get_created_at', 'updated_fields'),  # CHANGED: Use method
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ResourceCategoryInline]

    def resource_count(self, obj):
        count = obj.resources.count()
        url = (
            reverse('admin:elibrary_learningresource_changelist')
            + '?'
            + urlencode({'categories__id': f'{obj.id}'})
        )
        return format_html('<a href="{}">{}</a>', url, count)
    resource_count.short_description = 'Resources'

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def updated_fields(self, obj):
        if obj.id:
            return format_html(
                '<strong>Subcategories:</strong> {}<br>'
                '<strong>Total Resources:</strong> {}',
                obj.subcategories.count(),
                obj.resources.count()
            )
        return "Save first to see statistics"
    updated_fields.short_description = 'Statistics'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(resource_count=Count('resources'))

class ResourceReviewInline(admin.TabularInline):
    # Inline for resource reviews
    model = ResourceReview
    fields = ['user', 'rating', 'review_text', 'is_approved', 'created_at']
    readonly_fields = ['created_at']
    extra = 0
    show_change_link = True

class CollectionItemInline(admin.TabularInline):
    # Inline for collection items
    model = CollectionItem
    fields = ['resource', 'order', 'notes', 'added_at']
    readonly_fields = ['added_at']
    extra = 1
    show_change_link = True

@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'resource_type', 'school', 'created_by', 
        'is_published', 'is_approved', 'view_count', 
        'average_rating', 'engagement_rate', 'get_created_at'
    ]
    list_filter = [
        'resource_type', 'access_level', 'is_published', 
        'is_approved', 'school', 'difficulty_level'
    ]
    search_fields = ['title', 'description', 'author', 'tags']
    readonly_fields = [
        'get_created_at', 'updated_at', 'published_at',
        'view_count', 'download_count', 'favorite_count',
        'rating_count', 'engagement_rate', 'file_size'
    ]
    list_editable = ['is_published', 'is_approved']
    filter_horizontal = ['categories']  # REMOVED: 'tags' - it's likely not a ManyToManyField
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'resource_type', 'access_level')
        }),
        ('Content', {
            'fields': ('file', 'external_url', 'embed_code', 'content')
        }),
        ('Metadata', {
            'fields': ('author', 'publisher', 'publication_date', 'isbn', 'language', 'pages', 'duration')
        }),
        ('Organization', {
            'fields': ('categories', 'tags', 'difficulty_level')  # 'tags' can stay here as a regular field
        }),
        ('AI Integration', {
            'fields': ('ai_summary', 'ai_keywords', 'ai_difficulty_score'),
            'classes': ('collapse',)
        }),
        ('Engagement Metrics', {
            'fields': (
                'view_count', 'download_count', 'favorite_count',
                'average_rating', 'rating_count', 'engagement_rate'
            )
        }),
        ('File Information', {
            'fields': ('file_size',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_published', 'is_featured', 'requires_approval', 'is_approved')
        }),
        ('Relationships', {
            'fields': ('school', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('get_created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ResourceReviewInline]

    def engagement_rate(self, obj):
        rate = obj.get_engagement_rate()
        color = 'green' if rate > 50 else 'orange' if rate > 25 else 'red'
        return format_html('<span style="color: {};">{}%</span>', color, rate)
    engagement_rate.short_description = 'Engagement Rate'

    def file_size(self, obj):
        return obj.get_file_size()
    file_size.short_description = 'File Size'

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(school=request.user.school)

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['publish_resources', 'unpublish_resources', 'approve_resources']

    def publish_resources(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} resources published successfully.')
    publish_resources.short_description = "Publish selected resources"

    def unpublish_resources(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} resources unpublished.')
    unpublish_resources.short_description = "Unpublish selected resources"

    def approve_resources(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} resources approved.')
    approve_resources.short_description = "Approve selected resources"
@admin.register(ResourceReview)
class ResourceReviewAdmin(admin.ModelAdmin):
    list_display = [
        'resource', 'user', 'rating', 'helpfulness_score', 
        'is_approved', 'get_created_at', 'review_preview'
    ]
    list_filter = ['rating', 'is_approved']  # REMOVED: 'created_at'
    search_fields = [
        'resource__title', 'user__first_name', 
        'user__last_name', 'review_text'
    ]
    readonly_fields = ['get_created_at', 'updated_at', 'helpfulness_score']  # CHANGED: Use method
    list_editable = ['is_approved']
    list_per_page = 25
    
    fieldsets = (
        ('Review Content', {
            'fields': ('resource', 'user', 'rating', 'review_text')
        }),
        ('Helpfulness', {
            'fields': ('helpful_votes', 'not_helpful_votes', 'helpfulness_score')
        }),
        ('Moderation', {
            'fields': ('is_approved',)
        }),
        ('Timestamps', {
            'fields': ('get_created_at', 'updated_at'),  # CHANGED: Use method
            'classes': ('collapse',)
        }),
    )

    def review_preview(self, obj):
        if obj.review_text:
            preview = obj.review_text[:50] + '...' if len(obj.review_text) > 50 else obj.review_text
            return format_html('<span title="{}">{}</span>', obj.review_text, preview)
        return "-"
    review_preview.short_description = 'Review Preview'

    def helpfulness_score(self, obj):
        score = obj.get_helpfulness_score()
        color = 'green' if score > 70 else 'orange' if score > 40 else 'red'
        return format_html('<span style="color: {};">{}%</span>', color, score)
    helpfulness_score.short_description = 'Helpfulness Score'

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(resource__school=request.user.school)

    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews approved.')
    approve_reviews.short_description = "Approve selected reviews"

    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews disapproved.')
    disapprove_reviews.short_description = "Disapprove selected reviews"

@admin.register(StudyCollection)
class StudyCollectionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'school', 'created_by', 'is_public', 
        'resource_count', 'view_count', 'get_created_at'
    ]
    list_filter = ['is_public', 'school', 'allow_collaboration']  # REMOVED: 'created_at'
    search_fields = ['name', 'description', 'created_by__first_name', 'created_by__last_name']
    readonly_fields = ['get_created_at', 'updated_at', 'view_count', 'favorite_count']  # CHANGED: Use method
    list_editable = ['is_public']
    filter_horizontal = ['collaborators']  # REMOVED: 'resources' - uses through model (CollectionItem)
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Organization', {
            'fields': ('school', 'created_by')  # REMOVED: 'resources' from here too
        }),
        ('Access & Collaboration', {
            'fields': ('is_public', 'allow_collaboration', 'collaborators')
        }),
        ('Engagement', {
            'fields': ('view_count', 'favorite_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('get_created_at', 'updated_at'),  # CHANGED: Use method
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CollectionItemInline]

    def resource_count(self, obj):
        count = obj.resources.count()
        url = (
            reverse('admin:elibrary_learningresource_changelist')
            + '?'
            + urlencode({'collections__id': f'{obj.id}'})
        )
        return format_html('<a href="{}">{}</a>', url, count)
    resource_count.short_description = 'Resources'

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(resource_count=Count('resources'))

# ... rest of your admin classes remain the same (ResourceInteraction, CollectionItem, AIRecommendation, ReadingList, ReadingListItem)
@admin.register(ResourceInteraction)
class ResourceInteractionAdmin(admin.ModelAdmin):
    list_display = ['resource', 'user', 'interaction_type', 'duration_seconds', 'progress_percentage', 'get_created_at']
    list_filter = ['interaction_type']  # REMOVED: 'created_at'
    search_fields = ['resource__title', 'user__first_name', 'user__last_name']
    readonly_fields = ['get_created_at']  # CHANGED: Use method
    list_per_page = 50
    date_hierarchy = 'created_at'

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(resource__school=request.user.school)

@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ['collection', 'resource', 'order', 'added_at']
    list_filter = ['collection__school']  # REMOVED: 'added_at'
    search_fields = ['collection__name', 'resource__title']
    list_editable = ['order']
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(collection__school=request.user.school)

@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'recommendation_type', 'confidence_score', 'is_expired', 'get_created_at']
    list_filter = ['recommendation_type']  # REMOVED: 'created_at'
    search_fields = ['user__first_name', 'user__last_name', 'resource__title']
    readonly_fields = ['get_created_at', 'is_expired']  # CHANGED: Use method
    list_per_page = 25

    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(resource__school=request.user.school)

@admin.register(ReadingList)
class ReadingListAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'is_public', 'resource_count', 
        'progress_percentage', 'get_created_at'
    ]
    list_filter = ['is_public']  # REMOVED: 'created_at'
    search_fields = ['name', 'user__first_name', 'user__last_name']
    readonly_fields = ['get_created_at', 'updated_at', 'progress_percentage']  # CHANGED: Use method
    list_editable = ['is_public']
    list_per_page = 25

    def resource_count(self, obj):
        return obj.get_resource_count()
    resource_count.short_description = 'Total Resources'

    def progress_percentage(self, obj):
        progress = obj.get_progress_percentage()
        color = 'green' if progress > 75 else 'orange' if progress > 50 else 'red'
        return format_html('<span style="color: {};">{}%</span>', color, progress)
    progress_percentage.short_description = 'Progress'

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

@admin.register(ReadingListItem)
class ReadingListItemAdmin(admin.ModelAdmin):
    list_display = ['reading_list', 'resource', 'order', 'completed', 'completed_at', 'added_at']
    list_filter = ['completed', 'reading_list__user']  # REMOVED: 'added_at'
    search_fields = ['reading_list__name', 'resource__title']
    list_editable = ['order', 'completed']
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(reading_list__user__school=request.user.school)