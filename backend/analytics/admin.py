from django.contrib import admin
from .models import *

@admin.register(MetricDefinition)
class MetricDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'metric_type', 'is_active']
    list_filter = ['metric_type', 'is_active']

@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'time_spent_minutes', 'assignments_completed']
    list_filter = ['date']

@admin.register(PredictiveModel)
class PredictiveModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'version', 'is_active']
    list_filter = ['model_type', 'is_active']