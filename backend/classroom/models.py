from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from django.db.models import Avg
from users.models import User, School

class Classroom(models.Model):
    class Subject(models.TextChoices):
        MATH = 'MATH', 'Mathematics'
        SCIENCE = 'SCIENCE', 'Science'
        ENGLISH = 'ENGLISH', 'English'
        HISTORY = 'HISTORY', 'History'
        GEOGRAPHY = 'GEOGRAPHY', 'Geography'
        PHYSICS = 'PHYSICS', 'Physics'
        CHEMISTRY = 'CHEMISTRY', 'Chemistry'
        BIOLOGY = 'BIOLOGY', 'Biology'
        COMPUTER_SCIENCE = 'COMPUTER_SCIENCE', 'Computer Science'
        ART = 'ART', 'Art'
        MUSIC = 'MUSIC', 'Music'
        PHYSICAL_EDUCATION = 'PE', 'Physical Education'
        OTHER = 'OTHER', 'Other'

    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=50, choices=Subject.choices)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    section = models.CharField(max_length=10, blank=True)
    
    # Relationships
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_classes', limit_choices_to={'role': User.Role.TEACHER})
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classrooms')
    students = models.ManyToManyField(User, through='Enrollment', related_name='enrolled_classes', limit_choices_to={'role': User.Role.STUDENT})
    
    # Settings
    is_active = models.BooleanField(default=True)
    allow_student_posts = models.BooleanField(default=True)
    allow_student_comments = models.BooleanField(default=True)
    max_students = models.IntegerField(default=40, validators=[MinValueValidator(1), MaxValueValidator(100)])
    is_public = models.BooleanField(default=False)
    
    # Schedule
    schedule_days = ArrayField(models.CharField(max_length=10), default=list, blank=True) 
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'classrooms'
        ordering = ['subject', 'name']
        unique_together = ['teacher', 'name', 'section']
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()} ({self.section})"
    
    def student_count(self):
        return self.students.count()
    
    def is_enrolled(self, user):
        return self.students.filter(id=user.id).exists()
    
    def generate_class_code(self):
        # Generate a unique class code
        import random
        import string
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        while Classroom.objects.filter(code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return code
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_class_code()
        super().save(*args, **kwargs)

class Enrollment(models.Model):
    class EnrollmentStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        DROPPED = 'DROPPED', 'Dropped'
        SUSPENDED = 'SUSPENDED', 'Suspended'

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=EnrollmentStatus.choices, default=EnrollmentStatus.ACTIVE)
    joined_via_code = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'enrollments'
        unique_together = ['student', 'classroom']

class Assignment(models.Model):
    class AssignmentType(models.TextChoices):
        HOMEWORK = 'HOMEWORK', 'Homework'
        PROJECT = 'PROJECT', 'Project'
        QUIZ = 'QUIZ', 'Quiz'
        EXAM = 'EXAM', 'Exam'
        ESSAY = 'ESSAY', 'Essay'
        PRESENTATION = 'PRESENTATION', 'Presentation'
        DISCUSSION = 'DISCUSSION', 'Discussion'

    class AssignmentStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        CLOSED = 'CLOSED', 'Closed'

    title = models.CharField(max_length=200)
    description = models.TextField()
    assignment_type = models.CharField(max_length=20, choices=AssignmentType.choices)
    points = models.IntegerField(default=100, validators=[MinValueValidator(1), MaxValueValidator(1000)])
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.DRAFT)
    
    # Relationships
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assignments')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    
    # Dates
    assigned_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    allow_late_submission = models.BooleanField(default=False)
    late_submission_days = models.IntegerField(default=0)
    
    # Settings
    attachments = models.JSONField(default=list, blank=True)
    instructions = models.TextField(blank=True)
    rubric = models.JSONField(default=dict, blank=True)
    allowed_file_types = ArrayField(models.CharField(max_length=10), default=list, blank=True)
    max_file_size = models.IntegerField(default=10)  # in MB
    
    # Gamification
    xp_reward = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    bonus_xp = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Analytics
    total_submissions = models.IntegerField(default=0)
    average_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ai_clarity_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    ai_difficulty_level = models.CharField(max_length=20, blank=True)
    ai_suggestions = models.JSONField(default=list, blank=True)


    class Meta:
        db_table = 'assignments'
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.title} - {self.classroom.name}"
    
    def is_past_due(self):
        return timezone.now() > self.due_date
    
    def submission_count(self):
        return self.submissions.filter(is_submitted=True).count()
    
    def update_analytics(self):
        # Update assignment analytics
        submissions = self.submissions.filter(is_submitted=True, grade__isnull=False)
        if submissions.exists():
            self.total_submissions = submissions.count()
            self.average_grade = submissions.aggregate(avg=Avg('grade'))['avg']
        else:
            self.total_submissions = 0
            self.average_grade = None
        self.save()

class Submission(models.Model):
    class SubmissionStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        LATE = 'LATE', 'Late'
        GRADED = 'GRADED', 'Graded'
        RETURNED = 'RETURNED', 'Returned'

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    status = models.CharField(max_length=20, choices=SubmissionStatus.choices, default=SubmissionStatus.DRAFT)
    
    # Submission content
    content = models.TextField(blank=True)
    attachments = models.JSONField(default=list, blank=True)
    submission_notes = models.TextField(blank=True)
    word_count = models.IntegerField(default=0)
    
    # Status
    submitted_at = models.DateTimeField(null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    # Grading
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)
    rubric_scores = models.JSONField(default=dict, blank=True)
    
    # XP Tracking
    xp_earned = models.IntegerField(default=0)
    is_xp_awarded = models.BooleanField(default=False)
    bonus_xp = models.IntegerField(default=0)
    
    # AI Features
    ai_feedback = models.TextField(blank=True)
    similarity_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'submissions'
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.get_display_name()} - {self.assignment.title}"
    
    def save(self, *args, **kwargs):
        # Update word count for text submissions
        if self.content:
            self.word_count = len(self.content.split())
        
        # Handle submission status
        if self.submitted_at and not self.grade:
            self.status = self.SubmissionStatus.SUBMITTED
            if self.assignment.due_date and self.submitted_at > self.assignment.due_date:
                self.status = self.SubmissionStatus.LATE
        elif self.grade:
            self.status = self.SubmissionStatus.GRADED
            
        super().save(*args, **kwargs)
    
    @property
    def is_late(self):
        return (self.submitted_at and self.assignment.due_date and 
                self.submitted_at > self.assignment.due_date)
    
    @property
    def grade_percentage(self):
        if self.grade and self.assignment.points:
            return (self.grade / self.assignment.points) * 100
        return 0

class ClassMaterial(models.Model):
    class MaterialType(models.TextChoices):
        DOCUMENT = 'DOCUMENT', 'Document'
        VIDEO = 'VIDEO', 'Video'
        LINK = 'LINK', 'External Link'
        PRESENTATION = 'PRESENTATION', 'Presentation'
        WORKSHEET = 'WORKSHEET', 'Worksheet'
        AUDIO = 'AUDIO', 'Audio'
        IMAGE = 'IMAGE', 'Image'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    material_type = models.CharField(max_length=20, choices=MaterialType.choices)
    
    # Content
    file_url = models.URLField(blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    content = models.TextField(blank=True)
    thumbnail = models.URLField(blank=True, null=True)
    
    # Relationships
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='materials')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_materials')
    
    # Metadata
    is_published = models.BooleanField(default=True)
    download_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    # Organization
    folder = models.CharField(max_length=100, blank=True)
    tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'class_materials'
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.classroom.name}"

class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        LATE = 'LATE', 'Late'
        EXCUSED = 'EXCUSED', 'Excused'
        EARLY_DISMISSAL = 'EARLY_DISMISSAL', 'Early Dismissal'

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    notes = models.TextField(blank=True)
    
    # Time tracking
    check_in = models.TimeField(blank=True, null=True)
    check_out = models.TimeField(blank=True, null=True)
    
    # XP Impact
    xp_deduction = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'attendance'
        unique_together = ['classroom', 'student', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.get_display_name()} - {self.date} - {self.status}"

class ClassPost(models.Model):
    class PostType(models.TextChoices):
        ANNOUNCEMENT = 'ANNOUNCEMENT', 'Announcement'
        DISCUSSION = 'DISCUSSION', 'Discussion'
        QUESTION = 'QUESTION', 'Question'
        RESOURCE = 'RESOURCE', 'Resource'
        POLL = 'POLL', 'Poll'

    title = models.CharField(max_length=200)
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=PostType.choices, default=PostType.ANNOUNCEMENT)
    
    # Relationships
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_posts')
    toxicity_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    # Engagement
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    
    # Poll fields 
    poll_options = models.JSONField(default=list, blank=True)
    poll_end_date = models.DateTimeField(blank=True, null=True)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'class_posts'
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.classroom.name}"
    
    @property
    def net_votes(self):
        return self.upvotes - self.downvotes
    
    @property
    def total_votes(self):
        return self.upvotes + self.downvotes

class Comment(models.Model):
    post = models.ForeignKey(ClassPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_comments')
    content = models.TextField()
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    toxicity_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    # Engagement
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.get_display_name()} on {self.post.title}"

class PollVote(models.Model):
    post = models.ForeignKey(ClassPost, on_delete=models.CASCADE, related_name='poll_votes')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_votes')
    selected_option = models.IntegerField()  # Index of the selected option
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'poll_votes'
        unique_together = ['post', 'student']

class Gradebook(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='gradebook_entries')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gradebook_entries')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='gradebook_entries')
    
    # Grades
    points_earned = models.DecimalField(max_digits=5, decimal_places=2)
    points_possible = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    letter_grade = models.CharField(max_length=5)
    
    # Metadata
    is_excused = models.BooleanField(default=False)
    is_missing = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'gradebook'
        unique_together = ['classroom', 'student', 'assignment']

class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_records')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='student_progress')
    
    # Progress metrics
    assignments_completed = models.IntegerField(default=0)
    assignments_total = models.IntegerField(default=0)
    average_grade = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    xp_earned = models.IntegerField(default=0)
    
    # Engagement metrics
    posts_created = models.IntegerField(default=0)
    comments_made = models.IntegerField(default=0)
    materials_viewed = models.IntegerField(default=0)
    
    # Timestamps
    last_activity = models.DateTimeField(auto_now=True)
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_progress'
        unique_together = ['student', 'classroom']