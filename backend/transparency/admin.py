from django.contrib import admin
from django.utils import timezone
from .models import (
    BudgetCategory, FinancialTransaction, Budget, VotingIssue,
    Vote, FinancialReport, Comment, AuditLog, NotificationSubscription
)

@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'parent_category', 'color', 'icon', 'get_created_at')
    list_filter = ('school', 'parent_category')
    search_fields = ('name', 'description', 'school__name')
    readonly_fields = ('get_created_at', 'get_updated_at')  # CHANGED: Use methods instead of direct fields

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Updated At'

@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'category', 'amount', 'transaction_type', 'status', 'transaction_date', 'submitted_by')
    list_filter = ('transaction_type', 'status', 'school', 'category')  # REMOVED: 'transaction_date'
    search_fields = ('title', 'description', 'invoice_number', 'vendor_name', 'submitted_by__email')
    readonly_fields = ('get_created_at', 'get_updated_at', 'approved_date')  # CHANGED: Use methods
    actions = ['approve_transactions', 'reject_transactions']

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Updated At'

    def approve_transactions(self, request, queryset):
        updated = queryset.filter(status=FinancialTransaction.Status.PENDING).update(
            status=FinancialTransaction.Status.APPROVED,
            approved_by=request.user,
            approved_date=timezone.now().date()
        )
        self.message_user(request, f'{updated} transactions approved.')
    approve_transactions.short_description = "Approve selected transactions"

    def reject_transactions(self, request, queryset):
        updated = queryset.filter(status=FinancialTransaction.Status.PENDING).update(
            status=FinancialTransaction.Status.REJECTED
        )
        self.message_user(request, f'{updated} transactions rejected.')
    reject_transactions.short_description = "Reject selected transactions"

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'category', 'period', 'allocated_amount', 'spent_amount', 'utilization_percentage', 'is_active')
    list_filter = ('period', 'is_active', 'school', 'category')
    search_fields = ('name', 'description', 'school__name')
    readonly_fields = ('spent_amount', 'get_created_at', 'get_updated_at')  # CHANGED: Use methods
    
    def utilization_percentage(self, obj):
        return f"{obj.utilization_percentage:.1f}%"
    utilization_percentage.short_description = 'Utilization'

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Updated At'

@admin.register(VotingIssue)
class VotingIssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'issue_type', 'status', 'voting_method', 'voting_starts_at', 'voting_ends_at', 'total_votes')
    list_filter = ('issue_type', 'status', 'voting_method', 'school')  # REMOVED: 'voting_starts_at'
    search_fields = ('title', 'description', 'school__name')
    readonly_fields = ('total_votes', 'get_created_at', 'get_updated_at')  # CHANGED: Use methods
    actions = ['open_voting', 'close_voting']

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Updated At'

    def open_voting(self, request, queryset):
        updated = queryset.filter(status=VotingIssue.Status.DRAFT).update(
            status=VotingIssue.Status.OPEN
        )
        self.message_user(request, f'{updated} voting issues opened.')
    open_voting.short_description = "Open selected voting issues"

    def close_voting(self, request, queryset):
        updated = queryset.filter(status=VotingIssue.Status.OPEN).update(
            status=VotingIssue.Status.CLOSED,
            results_published_at=timezone.now()
        )
        self.message_user(request, f'{updated} voting issues closed.')
    close_voting.short_description = "Close selected voting issues"

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('issue', 'voter', 'selected_option', 'is_abstained', 'get_created_at')
    list_filter = ('is_abstained', 'issue__school')  # REMOVED: 'created_at'
    search_fields = ('issue__title', 'voter__email', 'comments')
    readonly_fields = ('get_created_at',)  # CHANGED: Use method

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'report_type', 'start_date', 'end_date', 'is_published', 'published_at')
    list_filter = ('report_type', 'is_published', 'school')  # REMOVED: 'start_date'
    search_fields = ('title', 'description', 'school__name')
    readonly_fields = ('published_at', 'get_created_at', 'get_updated_at')  # CHANGED: Use methods
    actions = ['publish_reports']

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

    def get_updated_at(self, obj):
        return obj.updated_at
    get_updated_at.short_description = 'Updated At'

    def publish_reports(self, request, queryset):
        updated = queryset.filter(is_published=False).update(
            is_published=True,
            published_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports published.')
    publish_reports.short_description = "Publish selected reports"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'comment_type', 'content_preview', 'is_approved', 'get_created_at')
    list_filter = ('comment_type', 'is_approved')  # REMOVED: 'created_at'
    search_fields = ('content', 'author__email')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'description_preview', 'get_created_at')
    list_filter = ('action_type',)  # REMOVED: 'created_at'
    search_fields = ('user__email', 'description', 'changes')
    readonly_fields = ('get_created_at',)  # CHANGED: Use method
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

@admin.register(NotificationSubscription)
class NotificationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'is_active', 'get_created_at')
    list_filter = ('notification_type', 'is_active')  # REMOVED: 'created_at'
    search_fields = ('user__email',)
    filter_horizontal = ()  # REMOVED: 'categories' - might use custom through model

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'

# Inline admins for better UX
class FinancialTransactionInline(admin.TabularInline):
    model = FinancialTransaction
    extra = 0
    readonly_fields = ('amount', 'status', 'transaction_date')
    classes = ['collapse']

class VoteInline(admin.TabularInline):
    model = Vote
    extra = 0
    readonly_fields = ('voter', 'selected_option', 'created_at')
    classes = ['collapse']

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'content', 'created_at')
    classes = ['collapse']

# Add inlines to relevant admins
BudgetCategoryAdmin.inlines = [FinancialTransactionInline]
VotingIssueAdmin.inlines = [VoteInline, CommentInline]
FinancialReportAdmin.inlines = [CommentInline]