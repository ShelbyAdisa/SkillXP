from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from users.serializers import UserSerializer 
from .models import (
    Classroom, Enrollment, Assignment, Submission, ClassMaterial, 
    Attendance, ClassPost, Comment, PollVote, Gradebook, StudentProgress
)
from .serializers import (
    ClassroomSerializer, EnrollmentSerializer, AssignmentSerializer,
    SubmissionSerializer, ClassMaterialSerializer, AttendanceSerializer,
    ClassPostSerializer, CommentSerializer, JoinClassroomSerializer,
    GradeSubmissionSerializer, GradebookSerializer, StudentProgressSerializer,
    PollVoteSerializer
)
from .permissions import (
    IsClassroomTeacher, IsEnrolledStudent, CanJoinClassroom,
    CanCreateAssignment, CanSubmitAssignment, CanViewClassroom, CanPostInClassroom
)
from .utils import ClassroomAnalytics, GradeCalculator
from .tasks import send_assignment_notification, send_grade_notification
from users.models import User

class ClassroomViewSet(ModelViewSet):
    serializer_class = ClassroomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'subject', 'description']
    filterset_fields = ['subject', 'is_active']
    ordering_fields = ['name', 'subject', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.TEACHER:
            return Classroom.objects.filter(teacher=user)
        elif user.role == User.Role.STUDENT:
            return Classroom.objects.filter(students=user, is_active=True)
        elif user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return Classroom.objects.filter(school=user.school)
        else:
            return Classroom.objects.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user, school=self.request.user.school)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get classroom analytics"""
        classroom = self.get_object()
        stats = ClassroomAnalytics.get_classroom_stats(classroom)
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get enrolled students"""
        classroom = self.get_object()
        students = classroom.students.all()
        serializer = UserSerializer(students, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generate_invite(self, request, pk=None):
        """Generate invite link/code"""
        classroom = self.get_object()
        return Response({
            'invite_code': classroom.code,
            'invite_link': f"/join/{classroom.code}"
        })
    
    @action(detail=True, methods=['get'])
    def materials(self, request, pk=None):
        """Get classroom materials"""
        classroom = self.get_object()
        materials = classroom.materials.filter(is_published=True)
        serializer = ClassMaterialSerializer(materials, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Get classroom attendance records"""
        classroom = self.get_object()
        attendance = classroom.attendance_records.all()
        serializer = AttendanceSerializer(attendance, many=True, context={'request': request})
        return Response(serializer.data)

class AssignmentViewSet(ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    filterset_fields = ['assignment_type', 'status', 'classroom']
    ordering_fields = ['due_date', 'assigned_date', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.STUDENT:
            return Assignment.objects.filter(
                Q(classroom__students=user) | Q(classroom__teacher=user),
                status='PUBLISHED'
            ).distinct()
        else:
            return Assignment.objects.filter(
                Q(classroom__teacher=user) | 
                Q(classroom__school=user.school)
            ).distinct()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish an assignment"""
        assignment = self.get_object()
        assignment.status = Assignment.AssignmentStatus.PUBLISHED
        assignment.save()
        
        # Trigger notifications
        send_assignment_notification(assignment.id)
        
        return Response({'status': 'Assignment published'})
    
    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Get all submissions for this assignment"""
        assignment = self.get_object()
        submissions = assignment.submissions.all()
        serializer = SubmissionSerializer(submissions, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get assignment analytics"""
        assignment = self.get_object()
        submissions = assignment.submissions.filter(is_submitted=True)
        
        stats = {
            'total_submissions': submissions.count(),
            'submitted_count': submissions.filter(status__in=['SUBMITTED', 'LATE', 'GRADED']).count(),
            'graded_count': submissions.filter(status='GRADED').count(),
            'average_grade': submissions.aggregate(avg=Avg('grade'))['avg'] or 0,
            'late_submissions': submissions.filter(status='LATE').count(),
        }
        
        return Response(stats)

class SubmissionViewSet(ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.STUDENT:
            return Submission.objects.filter(student=user)
        else:
            return Submission.objects.filter(assignment__classroom__teacher=user)
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit an assignment"""
        submission = self.get_object()
        submission.status = Submission.SubmissionStatus.SUBMITTED
        submission.submitted_at = timezone.now()
        submission.save()
        
        return Response({'status': 'Assignment submitted'})
    
    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        """Grade a submission"""
        submission = self.get_object()
        serializer = GradeSubmissionSerializer(data=request.data, context={'submission': submission})
        serializer.is_valid(raise_exception=True)
        
        submission.grade = serializer.validated_data['grade']
        submission.feedback = serializer.validated_data.get('feedback', '')
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        submission.status = Submission.SubmissionStatus.GRADED
        
        # Award XP if not already awarded
        if not submission.is_xp_awarded and submission.grade:
            percentage = submission.grade_percentage
            xp_earned = GradeCalculator.calculate_xp_reward(
                submission.assignment, 
                percentage, 
                submission.is_late
            )
            
            submission.xp_earned = xp_earned
            submission.is_xp_awarded = True
            
            # Update student's total XP
            submission.student.xp_points += xp_earned
            submission.student.save()
        
        submission.save()
        
        # Send grade notification
        send_grade_notification(submission.id)
        
        return Response(SubmissionSerializer(submission, context={'request': request}).data)

class ClassMaterialViewSet(ModelViewSet):
    serializer_class = ClassMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['material_type', 'is_published']
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        return ClassMaterial.objects.filter(
            classroom__students=self.request.user,
            is_published=True
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def record_view(self, request, pk=None):
        """Record when a student views material"""
        material = self.get_object()
        material.view_count += 1
        material.save()
        return Response({'status': 'View recorded'})

class AttendanceViewSet(ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.STUDENT:
            return Attendance.objects.filter(student=user)
        else:
            return Attendance.objects.filter(classroom__teacher=user)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple attendance records at once"""
        classroom_id = request.data.get('classroom_id')
        date = request.data.get('date')
        records = request.data.get('records', [])
        
        try:
            classroom = Classroom.objects.get(id=classroom_id)
            
            # Verify user has permission
            if classroom.teacher != request.user and request.user.role not in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
                return Response(
                    {"detail": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            created_count = 0
            for record in records:
                student_id = record.get('student_id')
                status = record.get('status', 'PRESENT')
                notes = record.get('notes', '')
                
                attendance, created = Attendance.objects.update_or_create(
                    classroom=classroom,
                    student_id=student_id,
                    date=date,
                    defaults={
                        'status': status,
                        'notes': notes
                    }
                )
                
                if created:
                    created_count += 1
            
            return Response({
                "detail": f"Created {created_count} attendance records.",
                "total_records": len(records)
            })
            
        except Classroom.DoesNotExist:
            return Response(
                {"detail": "Classroom not found."},
                status=status.HTTP_404_NOT_FOUND
            )

class ClassPostViewSet(ModelViewSet):
    serializer_class = ClassPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['post_type', 'is_pinned']
    search_fields = ['title', 'content']
    
    def get_queryset(self):
        return ClassPost.objects.filter(
            classroom__students=self.request.user,
            is_approved=True
        )
    
    def perform_create(self, serializer):
        classroom = serializer.validated_data['classroom']
        is_approved = self.request.user.role != User.Role.STUDENT
        
        serializer.save(author=self.request.user, is_approved=is_approved)
    
    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        """Upvote a post"""
        post = self.get_object()
        post.upvotes += 1
        post.save()
        return Response({'upvotes': post.upvotes, 'downvotes': post.downvotes})
    
    @action(detail=True, methods=['post'])
    def downvote(self, request, pk=None):
        """Downvote a post"""
        post = self.get_object()
        post.downvotes += 1
        post.save()
        return Response({'upvotes': post.upvotes, 'downvotes': post.downvotes})
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Pin/unpin a post"""
        post = self.get_object()
        post.is_pinned = not post.is_pinned
        post.save()
        return Response({'is_pinned': post.is_pinned})

class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.filter(
            post__classroom__students=self.request.user,
            is_approved=True
        )
    
    def perform_create(self, serializer):
        post = serializer.validated_data['post']
        is_approved = self.request.user.role != User.Role.STUDENT
        
        serializer.save(author=self.request.user, is_approved=is_approved)

class GradebookView(generics.ListAPIView):
    serializer_class = GradebookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        classroom_id = self.kwargs.get('classroom_id')
        user = self.request.user
        
        if user.role == User.Role.STUDENT:
            return Gradebook.objects.filter(
                classroom_id=classroom_id,
                student=user
            )
        else:
            return Gradebook.objects.filter(classroom_id=classroom_id)

class StudentProgressView(generics.RetrieveAPIView):
    serializer_class = StudentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        classroom_id = self.kwargs.get('classroom_id')
        student_id = self.kwargs.get('student_id', self.request.user.id)
        
        try:
            return StudentProgress.objects.get(
                classroom_id=classroom_id,
                student_id=student_id
            )
        except StudentProgress.DoesNotExist:
            # Create progress record if it doesn't exist
            classroom = Classroom.objects.get(id=classroom_id)
            student = User.objects.get(id=student_id)
            return StudentProgress.objects.create(
                classroom=classroom,
                student=student
            )

# List Views for API endpoints
class ClassMaterialListView(generics.ListCreateAPIView):
    serializer_class = ClassMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        classroom_id = self.kwargs.get('classroom_id')
        return ClassMaterial.objects.filter(
            classroom_id=classroom_id,
            is_published=True
        )
    
    def perform_create(self, serializer):
        classroom_id = self.kwargs.get('classroom_id')
        classroom = Classroom.objects.get(id=classroom_id)
        serializer.save(created_by=self.request.user, classroom=classroom)

class AttendanceListView(generics.ListCreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        classroom_id = self.kwargs.get('classroom_id')
        return Attendance.objects.filter(classroom_id=classroom_id)
    
    def perform_create(self, serializer):
        classroom_id = self.kwargs.get('classroom_id')
        classroom = Classroom.objects.get(id=classroom_id)
        serializer.save(classroom=classroom)

class CommentListView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id, is_approved=True)
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = ClassPost.objects.get(id=post_id)
        is_approved = self.request.user.role != User.Role.STUDENT
        
        serializer.save(author=self.request.user, post=post, is_approved=is_approved)

# Additional API Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def teacher_dashboard(request):
    """Get teacher dashboard data"""
    user = request.user
    
    if user.role not in [User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
        return Response({"detail": "For teachers and admins only."}, status=status.HTTP_403_FORBIDDEN)
    
    # Teacher's classrooms
    classrooms = Classroom.objects.filter(teacher=user, is_active=True)
    classroom_data = []
    
    for classroom in classrooms:
        stats = ClassroomAnalytics.get_classroom_stats(classroom)
        classroom_data.append({
            'classroom': ClassroomSerializer(classroom, context={'request': request}).data,
            'stats': stats
        })
    
    # Recent assignments to grade
    assignments_to_grade = Assignment.objects.filter(
        classroom__teacher=user,
        submissions__status='SUBMITTED',
        submissions__grade__isnull=True
    ).distinct()[:5]
    
    # Upcoming assignments
    upcoming_assignments = Assignment.objects.filter(
        classroom__teacher=user,
        due_date__gte=timezone.now(),
        status='PUBLISHED'
    ).order_by('due_date')[:5]
    
    return Response({
        'classrooms': classroom_data,
        'assignments_to_grade': AssignmentSerializer(assignments_to_grade, many=True, context={'request': request}).data,
        'upcoming_assignments': AssignmentSerializer(upcoming_assignments, many=True, context={'request': request}).data,
        'total_students': sum(classroom.student_count() for classroom in classrooms),
        'total_assignments': Assignment.objects.filter(classroom__teacher=user).count()
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def vote_poll(request, post_id):
    """Vote on a poll"""
    try:
        post = ClassPost.objects.get(id=post_id, post_type='POLL')
        
        # Check if student is enrolled
        if not post.classroom.students.filter(id=request.user.id).exists():
            return Response({"detail": "Not enrolled in this classroom."}, status=status.HTTP_403_FORBIDDEN)
        
        selected_option = request.data.get('selected_option')
        
        if selected_option is None or selected_option >= len(post.poll_options):
            return Response({"detail": "Invalid option selected."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already voted
        existing_vote = PollVote.objects.filter(post=post, student=request.user).first()
        if existing_vote:
            return Response({"detail": "Already voted on this poll."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if poll is still active
        if post.poll_end_date and timezone.now() > post.poll_end_date:
            return Response({"detail": "Poll has ended."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create vote
        PollVote.objects.create(
            post=post,
            student=request.user,
            selected_option=selected_option
        )
        
        return Response({"detail": "Vote recorded successfully."})
        
    except ClassPost.DoesNotExist:
        return Response({"detail": "Poll not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanJoinClassroom])
def join_classroom(request):
    """Join a classroom using code"""
    serializer = JoinClassroomSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    code = serializer.validated_data['code']
    
    try:
        classroom = Classroom.objects.get(code=code, is_active=True)
        
        if classroom.students.filter(id=request.user.id).exists():
            return Response(
                {"detail": "Already enrolled in this classroom."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if classroom has space
        if classroom.student_count() >= classroom.max_students:
            return Response(
                {"detail": "Classroom is full."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Enroll student
        Enrollment.objects.create(
            student=request.user, 
            classroom=classroom,
            joined_via_code=True
        )
        
        return Response({
            "detail": "Successfully joined classroom.",
            "classroom": ClassroomSerializer(classroom, context={'request': request}).data
        })
        
    except Classroom.DoesNotExist:
        return Response(
            {"detail": "Invalid classroom code."},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_dashboard(request):
    """Get student dashboard data"""
    user = request.user
    
    if user.role != User.Role.STUDENT:
        return Response({"detail": "For students only."}, status=status.HTTP_403_FORBIDDEN)
    
    # Recent assignments (due soon)
    recent_assignments = Assignment.objects.filter(
        classroom__students=user,
        status='PUBLISHED',
        due_date__gte=timezone.now()
    ).order_by('due_date')[:5]
    
    # Recent submissions
    recent_submissions = Submission.objects.filter(
        student=user
    ).order_by('-submitted_at')[:5]
    
    # Recent grades
    recent_grades = Submission.objects.filter(
        student=user,
        grade__isnull=False
    ).order_by('-graded_at')[:5]
    
    # Classroom progress
    classrooms = Classroom.objects.filter(students=user, is_active=True)
    classroom_progress = []
    
    for classroom in classrooms:
        progress = ClassroomAnalytics.get_student_progress(user, classroom)
        classroom_progress.append({
            'classroom': ClassroomSerializer(classroom, context={'request': request}).data,
            'progress': progress
        })
    
    # Overall stats
    total_xp = user.xp_points
    total_assignments = Assignment.objects.filter(classroom__students=user, status='PUBLISHED').count()
    completed_assignments = Submission.objects.filter(student=user, status__in=['SUBMITTED', 'LATE', 'GRADED']).count()
    
    return Response({
        'recent_assignments': AssignmentSerializer(recent_assignments, many=True, context={'request': request}).data,
        'recent_submissions': SubmissionSerializer(recent_submissions, many=True, context={'request': request}).data,
        'recent_grades': SubmissionSerializer(recent_grades, many=True, context={'request': request}).data,
        'classroom_progress': classroom_progress,
        'overall_stats': {
            'total_xp': total_xp,
            'completion_rate': round((completed_assignments / total_assignments * 100) if total_assignments > 0 else 0, 2),
            'level': user.level,
            'total_classrooms': classrooms.count()
        }
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_classrooms(request):
    """Search for classrooms"""
    query = request.GET.get('q', '')
    subject = request.GET.get('subject', '')
    
    classrooms = Classroom.objects.filter(
        school=request.user.school,
        is_active=True,
        is_public=True
    )
    
    if query:
        classrooms = classrooms.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(teacher__first_name__icontains=query) |
            Q(teacher__last_name__icontains=query)
        )
    
    if subject:
        classrooms = classrooms.filter(subject=subject)
    
    serializer = ClassroomSerializer(classrooms, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_grade_submissions(request, assignment_id):
    """Bulk grade submissions for an assignment"""
    try:
        assignment = Assignment.objects.get(id=assignment_id)
        
        # Verify user has permission
        if assignment.classroom.teacher != request.user and request.user.role not in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        grades_data = request.data.get('grades', [])
        graded_count = 0
        
        for grade_data in grades_data:
            submission_id = grade_data.get('submission_id')
            grade_value = grade_data.get('grade')
            feedback = grade_data.get('feedback', '')
            
            try:
                submission = Submission.objects.get(
                    id=submission_id,
                    assignment=assignment
                )
                
                submission.grade = grade_value
                submission.feedback = feedback
                submission.graded_by = request.user
                submission.graded_at = timezone.now()
                submission.status = Submission.SubmissionStatus.GRADED
                
                # Award XP
                if not submission.is_xp_awarded and submission.grade:
                    percentage = submission.grade_percentage
                    xp_earned = GradeCalculator.calculate_xp_reward(
                        assignment, 
                        percentage, 
                        submission.is_late
                    )
                    
                    submission.xp_earned = xp_earned
                    submission.is_xp_awarded = True
                    
                    # Update student's total XP
                    submission.student.xp_points += xp_earned
                    submission.student.save()
                
                submission.save()
                graded_count += 1
                
                # Send grade notification
                send_grade_notification(submission.id)
                
            except Submission.DoesNotExist:
                continue
        
        return Response({
            "detail": f"Successfully graded {graded_count} submissions.",
            "graded_count": graded_count
        })
        
    except Assignment.DoesNotExist:
        return Response(
            {"detail": "Assignment not found."},
            status=status.HTTP_404_NOT_FOUND
        )