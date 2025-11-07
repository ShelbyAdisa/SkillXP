from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'ai_engine'

router = DefaultRouter()
router.register(r'configs', views.AIModelConfigViewSet)
router.register(r'logs', views.AIRequestLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]