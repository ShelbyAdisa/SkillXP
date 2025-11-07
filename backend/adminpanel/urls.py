from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'system-admins', views.SystemAdminViewSet)
router.register(r'school-admins', views.SchoolAdminViewSet)
router.register(r'audit-logs', views.AdminAuditLogViewSet)
router.register(r'dashboard', views.AdminDashboardViewSet, basename='admin-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]