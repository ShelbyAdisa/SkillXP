from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile, School

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'code', 'address', 'phone', 'email', 'website', 
                 'is_anonymous_allowed', 'theme_color']
        read_only_fields = ['id', 'code']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['date_of_birth', 'phone', 'avatar', 'parent_email', 
                 'emergency_contact', 'email_notifications', 'push_notifications', 
                 'sms_notifications', 'show_email', 'show_phone']
        
    def validate_parent_email(self, value):
        user = self.context['request'].user
        if user.role != User.Role.STUDENT and value:
            raise serializers.ValidationError("Parent email is only for students.")
        return value

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    school_details = SchoolSerializer(source='school', read_only=True)
    display_name = serializers.CharField(source='get_display_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'school_id', 'first_name', 'last_name', 'role',
                 'school', 'school_details', 'grade_level', 'subjects', 'is_anonymous',
                 'anonymous_username', 'xp_points', 'level', 'is_verified',
                 'date_joined', 'last_login', 'profile', 'display_name']
        read_only_fields = ['id', 'date_joined', 'last_login', 'xp_points', 'level']
        extra_kwargs = {
            'password': {'write_only': True},
            'school': {'write_only': True}
        }
    
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        
        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)
        else:
            UserProfile.objects.create(user=user)
        
        return user
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile fields
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance

from rest_framework import serializers
from .models import User, School

class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    school_code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'user_id', 'first_name', 'last_name', 'role',
            'password', 'password_confirm', 'school_code', 'grade_level'
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        school_code = validated_data.pop('school_code')

        # find the school
        try:
            school = School.objects.get(code=school_code)
        except School.DoesNotExist:
            raise serializers.ValidationError({"school_code": "Invalid school code."})

        # attach the school to the user
        user = User.objects.create_user(
            **validated_data,
            school_id=school.id if school else None,
        )
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Verify school
      
        
        # Authenticate user
        user = authenticate(request=self.context.get('request'),
                          email=email, password=password)
        
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        
        # Verify user belongs to this school
        # if user.school != school:
        #     raise serializers.ValidationError("User does not belong to this school.")
        
        attrs['user'] = user
        return attrs

class AnonymousModeSerializer(serializers.Serializer):
    is_anonymous = serializers.BooleanField()
    anonymous_username = serializers.CharField(max_length=50, required=False)
    
    def validate_anonymous_username(self, value):
        if value and User.objects.filter(anonymous_username=value).exists():
            raise serializers.ValidationError("This anonymous username is already taken.")
        return value