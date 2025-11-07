from django.contrib import admin
from .models import RedeemableItem, RewardTransaction
from django.utils.html import format_html
from django.utils import timezone

@admin.register(RedeemableItem)
class RedeemableItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'cost', 'stock_status', 'school', 'is_active', 'created_at')
    list_filter = ('item_type', 'is_active', 'school')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('name', 'description', 'item_type', 'school', 'is_active')}),
        ('Cost & Stock', {'fields': ('cost', 'stock')}),
    )

    def stock_status(self, obj):
        if obj.stock == -1:
            return format_html('<strong>Unlimited</strong>')
        elif obj.stock == 0:
            return format_html('<strong style="color: red;">Out of Stock</strong>')
        else:
            return obj.stock
    stock_status.short_description = 'Stock'

@admin.register(RewardTransaction)
class RewardTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item', 'xp_spent', 'status', 'redeemed_at', 'fulfilled_at')
    list_filter = ('status', 'item__item_type', 'redeemed_at')
    search_fields = ('user__email', 'item__name')
    readonly_fields = ('user', 'item', 'xp_spent', 'redeemed_at')
    list_editable = ('status',)
    
    actions = ['mark_fulfilled', 'mark_canceled']

    def mark_fulfilled(self, request, queryset):
        updated = queryset.filter(status=RewardTransaction.Status.PENDING).update(
            status=RewardTransaction.Status.FULFILLED,
            fulfilled_at=timezone.now()
        )
        self.message_user(request, f'{updated} transactions marked as fulfilled.')
    mark_fulfilled.short_description = "Mark selected pending transactions as fulfilled"

    def mark_canceled(self, request, queryset):
        updated = queryset.filter(status=RewardTransaction.Status.PENDING).update(
            status=RewardTransaction.Status.CANCELED
        )
        self.message_user(request, f'{updated} transactions marked as canceled.')
    mark_canceled.short_description = "Mark selected pending transactions as canceled"