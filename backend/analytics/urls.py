from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'user-analytics', views.UserAnalyticsViewSet)
router.register(r'classroom-analytics', views.ClassroomAnalyticsViewSet)
router.register(r'dashboard', views.AnalyticsDashboardViewSet, basename='analytics-dashboard')
router.register(r'predictive', views.PredictiveAnalyticsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]