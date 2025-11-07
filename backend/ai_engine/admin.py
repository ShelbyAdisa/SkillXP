from django.contrib import admin
from .models import AIModelConfig, AIRequestLog

@admin.register(AIModelConfig)
class AIModelConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'provider', 'temperature', 'max_tokens', 'is_active', 'updated_at')
    list_filter = ('model_type', 'provider', 'is_active')
    search_fields = ('name', 'provider')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('name', 'model_type', 'provider', 'is_active')}),
        ('API Details', {'fields': ('api_key_env',)}),
        ('Parameters', {'fields': ('temperature', 'max_tokens')}),
    )

@admin.register(AIRequestLog)
class AIRequestLogAdmin(admin.ModelAdmin):
    list_display = (
        'created_at', 'model_config', 'target_app', 'user', 
        'was_successful', 'latency_ms', 'cost_usd'
    )
    list_filter = ('target_app', 'model_config__model_type', 'was_successful')
    search_fields = ('prompt_text', 'error_message', 'user__email')
    readonly_fields = [
        'model_config', 'user', 'target_app', 'prompt_text', 'response_text', 
        'input_tokens', 'output_tokens', 'cost_usd', 'latency_ms', 
        'was_successful', 'error_message', 'created_at'
    ]
    date_hierarchy = 'created_at'