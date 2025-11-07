from rest_framework import serializers
from django.utils import timezone
from .models import (
    Classroom, Enrollment, Assignment, Submission, ClassMaterial, 
    Attendance, ClassPost, Comment, PollVote, Gradebook, StudentProgress
)
from users.serializers import UserSerializer
from users.models import User

class ClassroomSerializer(serializers.ModelSerializer):
    teacher_details = UserSerializer(source='teacher', read_only=True)
    student_count = serializers.IntegerField(source='student_count', read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = Classroom
        fields = [
            'id', 'name', 'subject', 'code', 'description', 'section',
            'teacher', 'teacher_details', 'school', 'school_name',
            'student_count', 'is_enrolled', 'is_active', 'allow_student_posts', 
            'allow_student_comments', 'max_students', 'is_public',
            'schedule_days', 'start_time', 'end_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'code', 'created_at', 'updated_at', 'teacher_details', 
            'student_count', 'school_name'
        ]
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_enrolled(request.user)
        return False
    
    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Ensure teacher belongs to the same school
            teacher = attrs.get('teacher')
            if teacher and teacher.school != request.user.school:
                raise serializers.ValidationError("Teacher must belong to the same school.")
            
            # Set school from requesting user if not provided
            if not attrs.get('school') and request.user.school:
                attrs['school'] = request.user.school
                
        return attrs

class EnrollmentSerializer(serializers.ModelSerializer):
    student_details = UserSerializer(source='student', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_details', 'classroom', 'classroom_name',
            'enrolled_at', 'status', 'joined_via_code'
        ]
        read_only_fields = ['id', 'enrolled_at']

class AssignmentSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_display_name', read_only=True)
    submission_count = serializers.SerializerMethodField()
    is_submitted = serializers.SerializerMethodField()
    student_submission = serializers.SerializerMethodField()
    is_past_due = serializers.BooleanField(source='is_past_due', read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'assignment_type', 'points', 'status',
            'classroom', 'classroom_name', 'created_by', 'created_by_name',
            'assigned_date', 'due_date', 'allow_late_submission', 'late_submission_days',
            'attachments', 'instructions', 'rubric', 'allowed_file_types', 'max_file_size',
            'xp_reward', 'bonus_xp', 'total_submissions', 'average_grade',
            'submission_count', 'is_submitted', 'student_submission', 'is_past_due'
        ]
        read_only_fields = [
            'id', 'created_by', 'submission_count', 'total_submissions', 
            'average_grade', 'is_past_due'
        ]
    
    def get_submission_count(self, obj):
        return obj.submission_count()
    
    def get_is_submitted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == User.Role.STUDENT:
            return obj.submissions.filter(student=request.user, status=Submission.SubmissionStatus.SUBMITTED).exists()
        return False
    
    def get_student_submission(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == User.Role.STUDENT:
            submission = obj.submissions.filter(student=request.user).first()
            if submission:
                return SubmissionSerializer(submission, context=self.context).data
        return None
    
    def validate_due_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value
    
    def validate(self, attrs):
        assigned_date = attrs.get('assigned_date', getattr(self.instance, 'assigned_date', None))
        due_date = attrs.get('due_date')
        
        if assigned_date and due_date and due_date < assigned_date:
            raise serializers.ValidationError("Due date cannot be before assigned date.")
        
        return attrs

class SubmissionSerializer(serializers.ModelSerializer):
    student_details = UserSerializer(source='student', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    max_points = serializers.IntegerField(source='assignment.points', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.get_display_name', read_only=True)
    grade_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'assignment_title', 'student', 'student_details',
            'status', 'content', 'attachments', 'submission_notes', 'word_count',
            'submitted_at', 'last_modified', 'grade', 'feedback', 'graded_by', 
            'graded_by_name', 'graded_at', 'rubric_scores', 'xp_earned', 
            'is_xp_awarded', 'bonus_xp', 'ai_feedback', 'similarity_score',
            'max_points', 'grade_percentage'
        ]
        read_only_fields = [
            'id', 'submitted_at', 'last_modified', 'graded_by', 'graded_at', 
            'xp_earned', 'is_xp_awarded', 'word_count', 'status', 'grade_percentage'
        ]
    
    def validate(self, attrs):
        assignment = attrs.get('assignment') or self.instance.assignment if self.instance else None
        
        if assignment and assignment.status != Assignment.AssignmentStatus.PUBLISHED:
            raise serializers.ValidationError("Cannot submit to an unpublished assignment.")
        
        # Check if user is enrolled in the classroom
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if not assignment.classroom.is_enrolled(request.user):
                raise serializers.ValidationError("You are not enrolled in this classroom.")
        
        return attrs
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['student'] = request.user
        return super().create(validated_data)

class ClassMaterialSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_display_name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    
    class Meta:
        model = ClassMaterial
        fields = [
            'id', 'title', 'description', 'material_type', 'file_url', 
            'external_link', 'content', 'thumbnail', 'classroom', 'classroom_name',
            'created_by', 'created_by_name', 'is_published', 'download_count', 
            'view_count', 'is_featured', 'folder', 'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'download_count', 'view_count', 
            'created_at', 'updated_at'
        ]

class AttendanceSerializer(serializers.ModelSerializer):
    student_details = UserSerializer(source='student', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'classroom', 'classroom_name', 'student', 'student_details',
            'date', 'status', 'notes', 'check_in', 'check_out', 'xp_deduction'
        ]
        read_only_fields = ['id']

class ClassPostSerializer(serializers.ModelSerializer):
    author_details = UserSerializer(source='author', read_only=True)
    comment_count = serializers.SerializerMethodField()
    net_votes = serializers.IntegerField(read_only=True)
    total_votes = serializers.IntegerField(read_only=True)
    has_voted = serializers.SerializerMethodField()
    poll_results = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassPost
        fields = [
            'id', 'title', 'content', 'post_type', 'classroom', 'author', 'author_details',
            'upvotes', 'downvotes', 'view_count', 'is_pinned', 'allow_comments',
            'poll_options', 'poll_end_date', 'is_approved', 'is_anonymous',
            'comment_count', 'net_votes', 'total_votes', 'has_voted', 'poll_results',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'upvotes', 'downvotes', 'view_count', 'created_at', 
            'updated_at', 'comment_count', 'net_votes', 'total_votes'
        ]
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_has_voted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and obj.post_type == ClassPost.PostType.POLL:
            return PollVote.objects.filter(post=obj, student=request.user).exists()
        return False
    
    def get_poll_results(self, obj):
        if obj.post_type == ClassPost.PostType.POLL and obj.poll_options:
            votes = PollVote.objects.filter(post=obj)
            results = []
            for index, option in enumerate(obj.poll_options):
                vote_count = votes.filter(selected_option=index).count()
                results.append({
                    'option': option,
                    'votes': vote_count,
                    'percentage': round((vote_count / votes.count() * 100) if votes.count() > 0 else 0, 1)
                })
            return results
        return None
    
    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.user.role == User.Role.STUDENT:
            classroom = attrs.get('classroom')
            if classroom and not classroom.allow_student_posts:
                raise serializers.ValidationError("This classroom does not allow student posts.")
            
            # Auto-approve teacher posts, require approval for student posts
            if not attrs.get('is_approved'):
                attrs['is_approved'] = False
        
        # Validate poll fields
        if attrs.get('post_type') == ClassPost.PostType.POLL:
            poll_options = attrs.get('poll_options', [])
            poll_end_date = attrs.get('poll_end_date')
            
            if not poll_options or len(poll_options) < 2:
                raise serializers.ValidationError("Poll must have at least 2 options.")
            
            if poll_end_date and poll_end_date < timezone.now():
                raise serializers.ValidationError("Poll end date cannot be in the past.")
        
        return attrs

class CommentSerializer(serializers.ModelSerializer):
    author_details = UserSerializer(source='author', read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'author_details', 'content', 'parent_comment',
            'upvotes', 'downvotes', 'is_approved', 'is_anonymous', 'replies_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'upvotes', 'downvotes', 'created_at', 'updated_at', 'replies_count'
        ]
    
    def get_replies_count(self, obj):
        return obj.replies.count()
    
    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.user.role == User.Role.STUDENT:
            # Auto-approve teacher comments, require approval for student comments
            if not attrs.get('is_approved'):
                attrs['is_approved'] = False
        return attrs

class PollVoteSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_display_name', read_only=True)
    
    class Meta:
        model = PollVote
        fields = ['id', 'post', 'student', 'student_name', 'selected_option', 'voted_at']
        read_only_fields = ['id', 'student', 'voted_at']

class GradebookSerializer(serializers.ModelSerializer):
    student_details = UserSerializer(source='student', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    
    class Meta:
        model = Gradebook
        fields = [
            'id', 'classroom', 'classroom_name', 'student', 'student_details',
            'assignment', 'assignment_title', 'points_earned', 'points_possible',
            'percentage', 'letter_grade', 'is_excused', 'is_missing', 'notes'
        ]
        read_only_fields = ['id']

class StudentProgressSerializer(serializers.ModelSerializer):
    student_details = UserSerializer(source='student', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    completion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProgress
        fields = [
            'id', 'student', 'student_details', 'classroom', 'classroom_name',
            'assignments_completed', 'assignments_total', 'average_grade',
            'attendance_rate', 'xp_earned', 'posts_created', 'comments_made',
            'materials_viewed', 'completion_rate', 'last_activity', 'calculated_at'
        ]
        read_only_fields = ['id', 'calculated_at']
    
    def get_completion_rate(self, obj):
        if obj.assignments_total > 0:
            return round((obj.assignments_completed / obj.assignments_total) * 100, 2)
        return 0

# Utility Serializers
class JoinClassroomSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
    
    def validate_code(self, value):
        try:
            classroom = Classroom.objects.get(code=value, is_active=True)
        except Classroom.DoesNotExist:
            raise serializers.ValidationError("Invalid classroom code or classroom is not active.")
        
        # Check if classroom has space
        if classroom.student_count() >= classroom.max_students:
            raise serializers.ValidationError("This classroom is full.")
        
        return value

class GradeSubmissionSerializer(serializers.Serializer):
    grade = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0)
    feedback = serializers.CharField(required=False, allow_blank=True)
    rubric_scores = serializers.JSONField(required=False)
    bonus_xp = serializers.IntegerField(min_value=0, required=False, default=0)
    
    def validate_grade(self, value):
        submission = self.context.get('submission')
        if submission and value > submission.assignment.points:
            raise serializers.ValidationError(
                f"Grade cannot exceed assignment points ({submission.assignment.points})"
            )
        return value

class BulkGradeSerializer(serializers.Serializer):
    grades = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

class ClassroomAnalyticsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    total_assignments = serializers.IntegerField()
    average_grade = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    attendance_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    submissions_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    active_students = serializers.IntegerField()

# Dashboard Serializers
class TeacherDashboardSerializer(serializers.Serializer):
    classrooms = serializers.ListField()
    assignments_to_grade = serializers.ListField()
    upcoming_assignments = serializers.ListField()
    total_students = serializers.IntegerField()
    total_assignments = serializers.IntegerField()

class StudentDashboardSerializer(serializers.Serializer):
    recent_assignments = serializers.ListField()
    recent_submissions = serializers.ListField()
    recent_grades = serializers.ListField()
    classroom_progress = serializers.ListField()
    overall_stats = serializers.DictField()

# Search Serializer
class ClassroomSearchSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_display_name', read_only=True)
    student_count = serializers.IntegerField(source='student_count', read_only=True)
    
    class Meta:
        model = Classroom
        fields = [
            'id', 'name', 'subject', 'code', 'description', 'teacher', 'teacher_name',
            'student_count', 'is_public', 'created_at'
        ]