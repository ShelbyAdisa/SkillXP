from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, school_id, first_name, last_name, role, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        if not school_id:
            raise ValueError(_('The School ID must be set'))
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            school_id=school_id,
            first_name=first_name,
            last_name=last_name,
            role=role,
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, role='ADMIN', password=None, **extra_fields):
        # Auto-create school for superuser if not provided
        school_id = extra_fields.pop('school_id', None)
        
        if not school_id:
            from .models import School
            school, created = School.objects.get_or_create(
                name="System Admin School",
                defaults={
                    'code': 'SYSADMIN',
                    'address': 'System Address',
                    'phone': '+0000000000', 
                    'email': 'admin@system.com'
                }
            )
            school_id = school.id
        
        # Generate user_id if not provided
        if 'user_id' not in extra_fields:
            extra_fields['user_id'] = f"admin_{email.split('@')[0]}"
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        
        return self.create_user(
            email=email,
            school_id=school_id,
            first_name=first_name, 
            last_name=last_name,
            role=role,
            password=password,
            **extra_fields
        )
    def create_student(self, email, school_id, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('role', 'STUDENT')
        return self.create_user(email, school_id, first_name, last_name, 'STUDENT', password, **extra_fields)

    def create_teacher(self, email, school_id, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('role', 'TEACHER')
        return self.create_user(email, school_id, first_name, last_name, 'TEACHER', password, **extra_fields)

    def create_parent(self, email, school_id, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('role', 'PARENT')
        return self.create_user(email, school_id, first_name, last_name, 'PARENT', password, **extra_fields)
