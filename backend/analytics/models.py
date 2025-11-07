from django.db import models
from django.conf import settings
from django.utils import timezone

class MetricDefinition(models.Model):
    METRIC_TYPES = (
        ('engagement', 'Engagement'),
        ('academic', 'Academic'),
        ('wellbeing', 'Wellbeing'),
        ('operational', 'Operational'),
        ('social', 'Social'),
        ('transport', 'Transport'),
    )
    
    name = models.CharField(max_length=100)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    description = models.TextField()
    calculation_query = models.TextField(blank=True)
    target_value = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class UserAnalytics(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    
    # Engagement Metrics (from multiple apps)
    login_count = models.IntegerField(default=0)
    time_spent_minutes = models.IntegerField(default=0)
    
    # Classroom Metrics
    assignments_completed = models.IntegerField(default=0)
    average_grade = models.FloatField(null=True, blank=True)
    attendance_rate = models.FloatField(default=0)
    
    # eLibrary Metrics
    resources_accessed = models.IntegerField(default=0)
    study_time_minutes = models.IntegerField(default=0)
    
    # Social Metrics
    posts_created = models.IntegerField(default=0)
    comments_made = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    
    # Wellbeing Metrics
    mood_average = models.FloatField(null=True, blank=True)
    wellbeing_posts = models.IntegerField(default=0)
    
    # Transport Metrics
    transport_attendance = models.FloatField(default=0)
    
    # Gamification
    xp_earned = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'date']

class ClassroomAnalytics(models.Model):
    classroom = models.ForeignKey('classroom.Classroom', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    
    total_students = models.IntegerField(default=0)
    active_students = models.IntegerField(default=0)
    average_engagement = models.FloatField(default=0)
    assignment_completion_rate = models.FloatField(default=0)
    average_grade = models.FloatField(default=0)
    post_activity = models.IntegerField(default=0)

class SchoolAnalytics(models.Model):
    school = models.ForeignKey('users.School', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    average_engagement = models.FloatField(default=0)
    wellbeing_index = models.FloatField(default=0)
    transport_punctuality = models.FloatField(default=0)
    social_activity = models.IntegerField(default=0)
    financial_health = models.FloatField(default=0)

class PredictiveModel(models.Model):
    MODEL_TYPES = (
        ('dropout_risk', 'Dropout Risk'),
        ('performance', 'Performance Prediction'),
        ('engagement', 'Engagement Trend'),
        ('wellbeing', 'Wellbeing Risk'),
    )
    
    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    version = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accuracy_score = models.FloatField(null=True, blank=True)

class PredictionResult(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    model = models.ForeignKey(PredictiveModel, on_delete=models.CASCADE)
    prediction_value = models.FloatField()
    confidence = models.FloatField()
    factors = models.JSONField()
    generated_at = models.DateTimeField(auto_now_add=True)