from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from .models import (
    WellbeingPost, PostComment, PostReaction, SupportTicket, TicketMessage,
    CounselorAssignment, WellbeingResource, MoodCheck, WellbeingGoal,
    CrisisAlert, ContentReport, ModerationAction
)
from .serializers import (
    WellbeingPostSerializer, PostCommentSerializer, PostReactionSerializer,
    SupportTicketSerializer, TicketMessageSerializer, CounselorAssignmentSerializer,
    WellbeingResourceSerializer, MoodCheckSerializer, WellbeingGoalSerializer,
    CrisisAlertSerializer, ContentReportSerializer, ModerationActionSerializer
)
from .permissions import (
    IsStudent, IsTeacherOrCounselor, IsOwnerOrCounselor, 
    CanCreatePost, CanAccessAnonymousData, CanModerateContent
)
from users.permissions import IsSchoolAdmin

User = get_user_model()

# Wellbeing Posts Views
class WellbeingPostListCreateView(generics.ListCreateAPIView):
    serializer_class = WellbeingPostSerializer
    permission_classes = [permissions.IsAuthenticated, CanCreatePost]
    
    def get_queryset(self):
        queryset = WellbeingPost.objects.filter(is_approved=True)
        
        # Filter by post type if provided
        post_type = self.request.query_params.get('post_type')
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        
        # Filter by urgency
        is_urgent = self.request.query_params.get('is_urgent')
        if is_urgent:
            queryset = queryset.filter(is_urgent=True)
        
        return queryset.select_related('author').prefetch_related('comments', 'reactions')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class WellbeingPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WellbeingPostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrCounselor]
    queryset = WellbeingPost.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)

class PostCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return PostComment.objects.filter(post_id=post_id, is_approved=True).select_related('author')
    
    def perform_create(self, serializer):
        post = WellbeingPost.objects.get(id=self.kwargs['post_id'])
        serializer.save(post=post, author=self.request.user)

# Support Tickets Views
class SupportTicketListCreateView(generics.ListCreateAPIView):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.STUDENT:
            return SupportTicket.objects.filter(student=user)
        elif user.role in [User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return SupportTicket.objects.filter(
                Q(counselor=user) | Q(counselor__isnull=True)
            )
        
        return SupportTicket.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class SupportTicketDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrCounselor]
    queryset = SupportTicket.objects.all()

class TicketMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrCounselor]
    
    def get_queryset(self):
        ticket_id = self.kwargs['ticket_id']
        return TicketMessage.objects.filter(ticket_id=ticket_id).select_related('sender')
    
    def perform_create(self, serializer):
        ticket = SupportTicket.objects.get(id=self.kwargs['ticket_id'])
        serializer.save(ticket=ticket, sender=self.request.user)

# Counselor Assignment Views
class CounselorAssignmentListCreateView(generics.ListCreateAPIView):
    serializer_class = CounselorAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrCounselor]
    
    def get_queryset(self):
        return CounselorAssignment.objects.filter(is_active=True).select_related('counselor', 'student')

class MyStudentAssignmentsView(generics.ListAPIView):
    serializer_class = CounselorAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrCounselor]
    
    def get_queryset(self):
        return CounselorAssignment.objects.filter(
            counselor=self.request.user, is_active=True
        ).select_related('student')

# Wellbeing Resources Views
class WellbeingResourceListView(generics.ListAPIView):
    serializer_class = WellbeingResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_role = self.request.user.role
        return WellbeingResource.objects.filter(
            is_published=True,
            target_roles__contains=[user_role]
        ).select_related('created_by')

class WellbeingResourceCreateView(generics.CreateAPIView):
    serializer_class = WellbeingResourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrCounselor]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# Mood Tracking Views
class MoodCheckListCreateView(generics.ListCreateAPIView):
    serializer_class = MoodCheckSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MoodCheck.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MoodAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrCounselor]
    
    def get(self, request):
        # Get mood analytics for the counselor's assigned students
        if request.user.role == User.Role.TEACHER:
            assigned_students = User.objects.filter(
                counselor_assignments__counselor=request.user,
                counselor_assignments__is_active=True
            )
        else:
            assigned_students = User.objects.filter(role=User.Role.STUDENT)
        
        # Calculate average mood for last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        mood_data = MoodCheck.objects.filter(
            user__in=assigned_students,
            created_at__gte=week_ago
        ).values('user').annotate(
            avg_mood=Avg('mood_level'),
            check_count=Count('id')
        )
        
        return Response(mood_data)

# Wellbeing Goals Views
class WellbeingGoalListCreateView(generics.ListCreateAPIView):
    serializer_class = WellbeingGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WellbeingGoal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WellbeingGoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WellbeingGoalSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrCounselor]
    queryset = WellbeingGoal.objects.all()

# Crisis Alert Views
class CrisisAlertListCreateView(generics.ListCreateAPIView):
    serializer_class = CrisisAlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrCounselor]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return CrisisAlert.objects.all()
        return CrisisAlert.objects.filter(assigned_counselor=user)
    
    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

# Content Report Views
class ContentReportCreateView(generics.CreateAPIView):
    serializer_class = ContentReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

# Moderation Views
class ModerationActionListCreateView(generics.ListCreateAPIView):
    serializer_class = ModerationActionSerializer
    permission_classes = [permissions.IsAuthenticated, CanModerateContent]
    
    def get_queryset(self):
        return ModerationAction.objects.all().select_related('moderator', 'target_user')
    
    def perform_create(self, serializer):
        serializer.save(moderator=self.request.user)

# Dashboard and Analytics Views
class WellbeingDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        data = {}
        
        if user.role == User.Role.STUDENT:
            # Student dashboard
            data.update({
                'recent_posts': WellbeingPostSerializer(
                    WellbeingPost.objects.filter(author=user)[:5], many=True, context={'request': request}
                ).data,
                'active_tickets': SupportTicketSerializer(
                    SupportTicket.objects.filter(student=user, status__in=['OPEN', 'IN_PROGRESS']), 
                    many=True, context={'request': request}
                ).data,
                'mood_trend': MoodCheckSerializer(
                    MoodCheck.objects.filter(user=user)[:7], many=True
                ).data,
            })
        
        elif user.role in [User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            # Counselor/Admin dashboard
            data.update({
                'pending_tickets': SupportTicketSerializer(
                    SupportTicket.objects.filter(status='OPEN'), 
                    many=True, context={'request': request}
                ).data,
                'crisis_alerts': CrisisAlertSerializer(
                    CrisisAlert.objects.filter(status='PENDING'), 
                    many=True, context={'request': request}
                ).data,
                'unresolved_reports': ContentReportSerializer(
                    ContentReport.objects.filter(is_resolved=False), 
                    many=True, context={'request': request}
                ).data,
            })
        
        return Response(data)

# Reaction Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_post_reaction(request, post_id):
    try:
        post = WellbeingPost.objects.get(id=post_id)
        reaction_type = request.data.get('reaction_type')
        
        # Check if user already reacted
        existing_reaction = PostReaction.objects.filter(post=post, user=request.user).first()
        
        if existing_reaction:
            if existing_reaction.reaction_type == reaction_type:
                # Remove reaction if same type
                existing_reaction.delete()
                post.upvotes -= 1
                post.save()
                return Response({'message': 'Reaction removed'})
            else:
                # Update reaction type
                existing_reaction.reaction_type = reaction_type
                existing_reaction.save()
                return Response({'message': 'Reaction updated'})
        else:
            # Create new reaction
            PostReaction.objects.create(
                post=post,
                user=request.user,
                reaction_type=reaction_type
            )
            post.upvotes += 1
            post.save()
            return Response({'message': 'Reaction added'})
            
    except WellbeingPost.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

# Admin Views
class WellbeingAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    
    def get(self, request):
        school = request.user.school
        
        # Basic analytics
        analytics = {
            'total_posts': WellbeingPost.objects.filter(author__school=school).count(),
            'total_tickets': SupportTicket.objects.filter(student__school=school).count(),
            'active_tickets': SupportTicket.objects.filter(
                student__school=school, status__in=['OPEN', 'IN_PROGRESS']
            ).count(),
            'avg_mood_score': MoodCheck.objects.filter(
                user__school=school, 
                created_at__gte=timezone.now() - timedelta(days=30)
            ).aggregate(Avg('mood_level'))['mood_level__avg'],
            'crisis_alerts': CrisisAlert.objects.filter(
                reported_by__school=school,
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
        }
        
        return Response(analytics)