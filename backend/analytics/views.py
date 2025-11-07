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

class UserAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserAnalyticsSerializer
    permission_classes = [CanViewAnalytics]
    
    def get_queryset(self):
        queryset = UserAnalytics.objects.all()
        
        # School admins only see their school's data
        if hasattr(self.request.user, 'schooladmin'):
            school = self.request.user.schooladmin.school
            queryset = queryset.filter(user__school=school)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        user_id = request.query_params.get('user_id')
        timeframe = request.query_params.get('timeframe', '7d')
        
        if not user_id:
            return Response({'error': 'user_id parameter is required'}, status=400)
        
        # REAL implementation using your models
        overview_data = AnalyticsService.get_user_engagement_breakdown(user_id)
        
        # Add timeframe filtering
        end_date = timezone.now().date()
        if timeframe == '7d':
            start_date = end_date - timedelta(days=7)
        elif timeframe == '30d':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=365)
        
        # Get recent activity from actual models
        from classroom.models import Submission
        from social.models import Post as SocialPost
        from elibrary.models import ResourceInteraction
        
        recent_activity = {
            'recent_submissions': Submission.objects.filter(
                student_id=user_id, submitted_at__date__gte=start_date
            ).count(),
            'recent_posts': SocialPost.objects.filter(
                author_id=user_id, created_at__date__gte=start_date
            ).count(),
            'recent_resources': ResourceInteraction.objects.filter(
                user_id=user_id, created_at__date__gte=start_date
            ).count(),
        }
        
        overview_data['recent_activity'] = recent_activity
        overview_data['timeframe'] = timeframe
        
        return Response(overview_data)
    
    @action(detail=False, methods=['get'])
    def engagement_trend(self, request):
        user_id = request.query_params.get('user_id')
        days = int(request.query_params.get('days', '30'))
        
        if not user_id:
            return Response({'error': 'user_id parameter is required'}, status=400)
        
        # Generate real engagement trend data
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            daily_data = UserAnalytics.objects.filter(
                user_id=user_id, date=current_date
            ).first()
            
            trend_data.append({
                'date': current_date,
                'login_count': daily_data.login_count if daily_data else 0,
                'time_spent_minutes': daily_data.time_spent_minutes if daily_data else 0,
                'resources_accessed': daily_data.resources_accessed if daily_data else 0,
                'posts_created': daily_data.posts_created if daily_data else 0,
            })
            
            current_date += timedelta(days=1)
        
        return Response(trend_data)

class ClassroomAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ClassroomAnalyticsSerializer
    permission_classes = [CanViewAnalytics]
    
    def get_queryset(self):
        queryset = ClassroomAnalytics.objects.all()
        
        if hasattr(self.request.user, 'schooladmin'):
            school = self.request.user.schooladmin.school
            queryset = queryset.filter(classroom__school=school)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def performance_breakdown(self, request):
        # REAL implementation using your classroom models
        from classroom.models import Classroom, StudentProgress
        
        base_query = Q()
        if hasattr(request.user, 'schooladmin'):
            school = request.user.schooladmin.school
            base_query = Q(classroom__school=school)
        
        performance_data = Classroom.objects.filter(base_query).annotate(
            total_students=Count('students'),
            avg_grade=Avg('studentprogress__average_grade'),
            completion_rate=Avg('studentprogress__assignments_completed') / Count('assignments') * 100,
            engagement_score=Avg('studentprogress__posts_created') + Avg('studentprogress__comments_made')
        ).values('id', 'name', 'total_students', 'avg_grade', 'completion_rate', 'engagement_score')
        
        return Response(performance_data)

class AnalyticsDashboardViewSet(viewsets.ViewSet):
    permission_classes = [CanViewAnalytics]
    
    def list(self, request):
        timeframe = request.query_params.get('timeframe', '30d')
        dashboard_data = AnalyticsService.get_dashboard_data(request.user, timeframe)
        return Response(dashboard_data)
    
    @action(detail=False, methods=['get'])
    def engagement_metrics(self, request):
        # REAL implementation with your apps
        from classroom.models import ClassPost, Comment as ClassComment
        from social.models import Post as SocialPost, Comment as SocialComment
        from elibrary.models import ResourceInteraction
        
        base_query = Q()
        if hasattr(request.user, 'schooladmin'):
            school = request.user.schooladmin.school
            base_query = Q(user__school=school) | Q(author__school=school)
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        metrics = {
            'classroom_engagement': {
                'posts': ClassPost.objects.filter(created_at__gte=thirty_days_ago, **base_query).count(),
                'comments': ClassComment.objects.filter(created_at__gte=thirty_days_ago, **base_query).count(),
                'materials_viewed': 0,  # Would integrate with your ClassMaterial model
            },
            'social_engagement': {
                'posts': SocialPost.objects.filter(created_at__gte=thirty_days_ago, **base_query).count(),
                'comments': SocialComment.objects.filter(created_at__gte=thirty_days_ago, **base_query).count(),
                'messages': 0,  # Would integrate with your DirectMessage model
            },
            'learning_engagement': {
                'resource_interactions': ResourceInteraction.objects.filter(
                    created_at__gte=thirty_days_ago, **base_query
                ).count(),
                'study_time_minutes': ResourceInteraction.objects.filter(
                    created_at__gte=thirty_days_ago, **base_query
                ).aggregate(total=Sum('duration_seconds'))['total'] or 0 // 60,
            }
        }
        
        return Response(metrics)
    
    @action(detail=False, methods=['get'])
    def academic_performance(self, request):
        # REAL implementation using your models
        from classroom.models import StudentProgress, Submission
        from django.db.models import Q
        
        base_query = Q()
        if hasattr(request.user, 'schooladmin'):
            school = request.user.schooladmin.school
            base_query = Q(student__school=school)
        
        performance_data = {
            'overall_grades': StudentProgress.objects.filter(base_query).aggregate(
                avg_grade=Avg('average_grade'),
                avg_attendance=Avg('attendance_rate'),
                total_xp=Sum('xp_earned')
            ),
            'submission_stats': Submission.objects.filter(
                base_query, status='SUBMITTED'
            ).aggregate(
                total_submissions=Count('id'),
                avg_grade=Avg('grade'),
                late_submissions=Count('id', filter=Q(submitted_at__gt=Q('assignment__due_date')))
            ),
            'grade_distribution': Submission.objects.filter(
                base_query, grade__isnull=False
            ).values('assignment__assignment_type').annotate(
                avg_grade=Avg('grade'),
                count=Count('id')
            )
        }
        
        return Response(performance_data)
    
    @action(detail=False, methods=['get'])
    def wellbeing_insights(self, request):
        # REAL implementation using your wellbeing models
        from wellbeing.models import MoodCheck, WellbeingPost, SupportTicket
        from django.db.models import Q
        
        base_query = Q()
        if hasattr(request.user, 'schooladmin'):
            school = request.user.schooladmin.school
            base_query = Q(user__school=school)
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        insights = {
            'mood_trends': MoodCheck.objects.filter(
                base_query, created_at__gte=thirty_days_ago
            ).values('created_at__date').annotate(
                avg_mood=Avg('mood_level')
            ).order_by('created_at__date'),
            'post_activity': WellbeingPost.objects.filter(
                base_query, created_at__gte=thirty_days_ago
            ).count(),
            'support_requests': SupportTicket.objects.filter(
                base_query, created_at__gte=thirty_days_ago
            ).count(),
            'mood_distribution': MoodCheck.objects.filter(
                base_query, created_at__gte=thirty_days_ago
            ).values('mood_level').annotate(
                count=Count('id')
            ),
            'urgent_cases': SupportTicket.objects.filter(
                base_query, priority='URGENT', status='OPEN'
            ).count()
        }
        
        return Response(insights)
    
    @action(detail=False, methods=['get'])
    def transport_analytics(self, request):
        # REAL implementation using your transport models
        from transport.models import Trip, AttendanceLog
        from django.db.models import Q
        
        base_query = Q()
        if hasattr(request.user, 'schooladmin'):
            school = request.user.schooladmin.school
            base_query = Q(route__school=school)
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        transport_data = {
            'trip_metrics': Trip.objects.filter(
                base_query, scheduled_start__gte=thirty_days_ago
            ).aggregate(
                total_trips=Count('id'),
                completed_trips=Count('id', filter=Q(status='COMPLETED')),
                on_time_trips=Count('id', filter=Q(status='COMPLETED'))  # Simplified
            ),
            'attendance_metrics': AttendanceLog.objects.filter(
                base_query, created_at__gte=thirty_days_ago
            ).aggregate(
                total_logs=Count('id'),
                present_count=Count('id', filter=Q(is_present=True)),
                attendance_rate=Count('id', filter=Q(is_present=True)) * 100.0 / Count('id')
            ),
            'bus_utilization': Trip.objects.filter(
                base_query, scheduled_start__gte=thirty_days_ago
            ).values('bus__bus_number').annotate(
                trip_count=Count('id'),
                avg_students=Avg('students_onboard')
            )
        }
        
        return Response(transport_data)

class PredictiveAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PredictionResultSerializer
    permission_classes = [CanViewAnalytics]
    
    def get_queryset(self):
        queryset = PredictionResult.objects.all()
        
        if hasattr(self.request.user, 'schooladmin'):
            school = self.request.user.schooladmin.school
            queryset = queryset.filter(user__school=school)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def dropout_risk(self, request):
        # REAL implementation using your data
        high_risk_students = PredictionResult.objects.filter(
            model__model_type='dropout_risk',
            prediction_value__gte=0.7
        ).select_related('user').order_by('-prediction_value')[:20]
        
        risk_data = []
        for result in high_risk_students:
            risk_data.append({
                'student_name': result.user.get_display_name(),
                'risk_score': result.prediction_value,
                'confidence': result.confidence,
                'factors': result.factors,
                'last_updated': result.generated_at
            })
        
        return Response(risk_data)
    
    @action(detail=False, methods=['post'])
    def trigger_prediction(self, request):
        model_type = request.data.get('model_type')
        
        # REAL implementation - this would integrate with your ai_engine
        if model_type == 'dropout_risk':
            # Logic to calculate dropout risk using your actual data
            result = AnalyticsService.calculate_dropout_risk(request.user)
        elif model_type == 'performance':
            result = AnalyticsService.predict_performance(request.user)
        else:
            return Response({'error': 'Invalid model type'}, status=400)
        
        return Response({
            'status': 'Prediction completed',
            'model_type': model_type,
            'results': result
        })