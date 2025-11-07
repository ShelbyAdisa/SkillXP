from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, School

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'school_id', 'first_name', 'last_name', 'role', 'school', 'is_active', 'date_joined')
    list_filter = ('role', 'school', 'is_active', 'is_anonymous')
    search_fields = ('email', 'school_id', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'school_id', 'school')}),
        ('Role & Permissions', {'fields': ('role', 'is_anonymous', 'anonymous_username', 'is_active', 'is_staff', 'is_superuser')}),
        ('Academic Info', {'fields': ('grade_level', 'subjects')}),
        ('Gamification', {'fields': ('xp_points', 'level')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'school_id', 'first_name', 'last_name', 'role', 'school', 'password1', 'password2'),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'phone')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'email', 'phone', 'created_at')
    search_fields = ('name', 'code', 'email')
    readonly_fields = ('created_at', 'updated_at')