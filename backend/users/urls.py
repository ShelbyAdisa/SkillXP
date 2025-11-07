from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/change-password/', views.change_password, name='change-password'),
    path('profile/anonymous-mode/', views.ToggleAnonymousView.as_view(), name='toggle-anonymous'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # School Information
    path('school/<str:code>/', views.SchoolDetailView.as_view(), name='school-detail'),
]