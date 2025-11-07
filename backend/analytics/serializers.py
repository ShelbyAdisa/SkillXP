from rest_framework import serializers
from .models import *

class MetricDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricDefinition
        fields = '__all__'

class UserAnalyticsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserAnalytics
        fields = '__all__'

class ClassroomAnalyticsSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    
    class Meta:
        model = ClassroomAnalytics
        fields = '__all__'

class SchoolAnalyticsSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = SchoolAnalytics
        fields = '__all__'

class PredictionResultSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)
    
    class Meta:
        model = PredictionResult
        fields = '__all__'