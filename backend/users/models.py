from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager
# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    # Role Choices
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        TEACHER = 'TEACHER', 'Teacher'
        PARENT = 'PARENT', 'Parent'
        ADMIN = 'ADMIN', 'Admin'
        SCHOOL_ADMIN = 'SCHOOL_ADMIN', 'School Administrator'

    # Basic Information
    email = models.EmailField(unique=True)
    user_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    
    # Role and Permissions
    role = models.CharField(max_length=20, choices=Role.choices)
    is_anonymous = models.BooleanField(default=False)
    anonymous_username = models.CharField(max_length=50, blank=True, null=True)
    
    # School Information
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='users')
    grade_level = models.CharField(max_length=20, blank=True, null=True)  # For students
    subjects = models.JSONField(default=list, blank=True)  # For teachers
    
    # Status Flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    
    # Gamification
    xp_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_id', 'first_name', 'last_name', 'role']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user_id})"

    def get_display_name(self):
        # Returns anonymous username if anonymous mode is enabled
        if self.is_anonymous and self.anonymous_username:
            return self.anonymous_username
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class School(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    
    # School Configuration
    is_anonymous_allowed = models.BooleanField(default=True)
    max_students = models.IntegerField(default=1000)
    theme_color = models.CharField(max_length=7, default='#3B82F6')  
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'schools'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Academic Information (for students)
    parent_email = models.EmailField(blank=True, null=True)  
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Privacy Settings
    show_email = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Profile of {self.user.get_display_name()}"
    
    class Meta:
        db_table = 'user_profiles'