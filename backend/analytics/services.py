from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import *
from .serializers import *
from .services import AnalyticsService
from .permissions import *

# Import your actual models
from users.models import User, School
from classroom.models import Classroom, Submission, StudentProgress, ClassPost, Comment as ClassComment
from social.models import Post as SocialPost, Comment as SocialComment, DirectMessage
from elibrary.models import ResourceInteraction, LearningResource
from wellbeing.models import MoodCheck, WellbeingPost, SupportTicket
from transport.models import Trip, AttendanceLog
class AnalyticsService:
    
    @staticmethod
    def get_dashboard_data(user, timeframe='30d'):
        end_date = timezone.now().date()
        if timeframe == '7d':
            start_date = end_date - timedelta(days=7)
        elif timeframe == '30d':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=365)
        
        base_query = Q()
        if hasattr(user, 'schooladmin'):
            school = user.schooladmin.school
            base_query = Q(user__school=school)
        
        # REAL DATA FROM YOUR APPS
        dashboard = {
            'timeframe': timeframe,
            'summary': {
                'total_students': User.objects.filter(role='STUDENT', **base_query).count(),
                'active_students': UserAnalytics.objects.filter(
                    date=end_date, user__role='STUDENT', **base_query
                ).count(),
                'total_teachers': User.objects.filter(role='TEACHER', **base_query).count(),
                'total_classes': Classroom.objects.filter(**base_query).count(),
            },
            'engagement_metrics': AnalyticsService._get_engagement_metrics(base_query, start_date, end_date),
            'academic_metrics': AnalyticsService._get_academic_metrics(base_query, start_date, end_date),
            'wellbeing_metrics': AnalyticsService._get_wellbeing_metrics(base_query, start_date, end_date),
            'transport_metrics': AnalyticsService._get_transport_metrics(base_query, start_date, end_date),
        }
        
        return dashboard
    
    @staticmethod
    def _get_engagement_metrics(base_query, start_date, end_date):
        from classroom.models import ClassPost, Comment as ClassComment
        from social.models import Post as SocialPost, Comment as SocialComment
        from elibrary.models import ResourceInteraction
        
        return {
            'classroom_posts': ClassPost.objects.filter(
                created_at__date__range=[start_date, end_date], **base_query
            ).count(),
            'social_posts': SocialPost.objects.filter(
                created_at__date__range=[start_date, end_date], **base_query
            ).count(),
            'resource_interactions': ResourceInteraction.objects.filter(
                created_at__date__range=[start_date, end_date], **base_query
            ).count(),
            'total_comments': (
                ClassComment.objects.filter(
                    created_at__date__range=[start_date, end_date], **base_query
                ).count() +
                SocialComment.objects.filter(
                    created_at__date__range=[start_date, end_date], **base_query
                ).count()
            )
        }
    
    @staticmethod
    def _get_academic_metrics(base_query, start_date, end_date):
        from classroom.models import Assignment, Submission, StudentProgress
        
        assignments = Assignment.objects.filter(
            assigned_date__date__range=[start_date, end_date], **base_query
        )
        submissions = Submission.objects.filter(
            submitted_at__date__range=[start_date, end_date], **base_query
        )
        
        return {
            'assignments_created': assignments.count(),
            'submissions_received': submissions.count(),
            'average_grade': submissions.aggregate(avg=Avg('grade'))['avg'] or 0,
            'completion_rate': AnalyticsService._calculate_completion_rate(assignments, submissions),
        }
    
    @staticmethod
    def _get_wellbeing_metrics(base_query, start_date, end_date):
        from wellbeing.models import WellbeingPost, MoodCheck, SupportTicket
        
        return {
            'wellbeing_posts': WellbeingPost.objects.filter(
                created_at__date__range=[start_date, end_date], **base_query
            ).count(),
            'mood_checks': MoodCheck.objects.filter(
                created_at__date__range=[start_date, end_date], **base_query
            ).count(),
            'support_tickets': SupportTicket.objects.filter(
                created_at__date__range=[start_date, end_date], **base_query
            ).count(),
            'average_mood': MoodCheck.objects.filter(
                created_at__date__range=[start_date, end_date], **base_query
            ).aggregate(avg=Avg('mood_level'))['avg'] or 0,
        }
    
    @staticmethod
    def _get_transport_metrics(base_query, start_date, end_date):
        from transport.models import Trip, AttendanceLog
        
        trips = Trip.objects.filter(
            scheduled_start__date__range=[start_date, end_date], **base_query
        )
        attendance = AttendanceLog.objects.filter(
            created_at__date__range=[start_date, end_date], **base_query
        )
        
        return {
            'total_trips': trips.count(),
            'completed_trips': trips.filter(status='COMPLETED').count(),
            'on_time_rate': attendance.filter(is_present=True).count() / max(attendance.count(), 1) * 100,
            'average_delay': 0,  # Would calculate from actual vs scheduled times
        }
    
    @staticmethod
    def get_user_engagement_breakdown(user_id):
        from datetime import datetime, timedelta
        
        user_data = {
            'classroom_activity': {
                'posts': 0, 'comments': 0, 'assignments_completed': 0
            },
            'social_activity': {
                'posts': 0, 'comments': 0, 'messages': 0
            },
            'learning_activity': {
                'resources_accessed': 0, 'study_time': 0
            },
            'wellbeing_activity': {
                'posts': 0, 'mood_checks': 0
            }
        }
        
        # Calculate actual metrics from your apps
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Classroom activity
        from classroom.models import ClassPost, Comment as ClassComment, Submission
        user_data['classroom_activity']['posts'] = ClassPost.objects.filter(
            author_id=user_id, created_at__gte=thirty_days_ago
        ).count()
        user_data['classroom_activity']['comments'] = ClassComment.objects.filter(
            author_id=user_id, created_at__gte=thirty_days_ago
        ).count()
        user_data['classroom_activity']['assignments_completed'] = Submission.objects.filter(
            student_id=user_id, submitted_at__gte=thirty_days_ago, status='SUBMITTED'
        ).count()
        
        # Social activity  
        from social.models import Post as SocialPost, Comment as SocialComment, DirectMessage
        user_data['social_activity']['posts'] = SocialPost.objects.filter(
            author_id=user_id, created_at__gte=thirty_days_ago
        ).count()
        user_data['social_activity']['comments'] = SocialComment.objects.filter(
            author_id=user_id, created_at__gte=thirty_days_ago
        ).count()
        user_data['social_activity']['messages'] = DirectMessage.objects.filter(
            sender_id=user_id, created_at__gte=thirty_days_ago
        ).count()
        
        # Learning activity
        from elibrary.models import ResourceInteraction
        interactions = ResourceInteraction.objects.filter(
            user_id=user_id, created_at__gte=thirty_days_ago
        )
        user_data['learning_activity']['resources_accessed'] = interactions.count()
        user_data['learning_activity']['study_time'] = interactions.aggregate(
            total=Sum('duration_seconds')
        )['total'] or 0
        
        # Wellbeing activity
        from wellbeing.models import WellbeingPost, MoodCheck
        user_data['wellbeing_activity']['posts'] = WellbeingPost.objects.filter(
            author_id=user_id, created_at__gte=thirty_days_ago
        ).count()
        user_data['wellbeing_activity']['mood_checks'] = MoodCheck.objects.filter(
            user_id=user_id, created_at__gte=thirty_days_ago
        ).count()
        
        return user_data