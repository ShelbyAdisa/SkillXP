from celery import shared_task
from datetime import date
from .models import UserAnalytics, ClassroomAnalytics, SchoolAnalytics
from .services import AnalyticsService

@shared_task
def update_daily_analytics():
    """Task to update all analytics metrics daily"""
    AnalyticsService.calculate_daily_metrics()
    return "Daily analytics updated"

@shared_task
def run_predictive_models():
    """Task to run predictive models overnight"""
    AnalyticsService.run_all_prediction_models()
    return "Predictive models executed"