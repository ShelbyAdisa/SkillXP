"""
URL configuration for SkillNexus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/classroom/', include('classroom.urls')),
    path('api/elibrary/', include('elibrary.urls')),
    path('api/wellbeing/', include('wellbeing.urls')),
    path('api/social/', include('social.urls')),
    path('api/rewards/', include('rewards.urls')),
    path('api/ai-engine/', include('ai_engine.urls')),
    path('api/notifications/', include('notifications.urls')),
]
