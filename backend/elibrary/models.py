from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.db.models import Max
from users.models import User, School

class ResourceCategory(models.Model):
    # Categories for organizing library resources
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6') 
    icon = models.CharField(max_length=50, default='📚')  
    
    # Organization
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='resource_categories')
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_categories')
    
    class Meta:
        db_table = 'resource_categories'
        verbose_name_plural = 'Resource categories'
        unique_together = ['name', 'school']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.school.name}"
    
    def get_resource_count(self):
        # Get count of published resources in this category
        return self.resources.filter(is_published=True, is_approved=True).count()

class LearningResource(models.Model):
    # Main resource model for eLibrary
    class ResourceType(models.TextChoices):
        DOCUMENT = 'DOCUMENT', 'Document'
        VIDEO = 'VIDEO', 'Video'
        AUDIO = 'AUDIO', 'Audio'
        IMAGE = 'IMAGE', 'Image'
        LINK = 'LINK', 'External Link'
        PRESENTATION = 'PRESENTATION', 'Presentation'
        INTERACTIVE = 'INTERACTIVE', 'Interactive Content'
        EBOOK = 'EBOOK', 'E-Book'
        WORKSHEET = 'WORKSHEET', 'Worksheet'
        QUIZ = 'QUIZ', 'Quiz'

    class AccessLevel(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        SCHOOL = 'SCHOOL', 'School Only'
        CLASSROOM = 'CLASSROOM', 'Classroom Only'
        PRIVATE = 'PRIVATE', 'Private'

    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices)
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices, default=AccessLevel.SCHOOL)
    
    # Content
    file = models.FileField(
        upload_to='elibrary/resources/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator([
                'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx',
                'mp4', 'avi', 'mov', 'mp3', 'wav', 'jpg', 'jpeg', 'png', 'gif'
            ])
        ]
    )
    external_url = models.URLField(blank=True, null=True)
    embed_code = models.TextField(blank=True, null=True)  # For embedded content
    content = models.TextField(blank=True, null=True)  # For text-based resources
    
    # Metadata
    author = models.CharField(max_length=100, blank=True, null=True)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    language = models.CharField(max_length=10, default='en')
    pages = models.IntegerField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)  # For audio/video
    
    # Organization
    categories = models.ManyToManyField(ResourceCategory, related_name='resources', blank=True)
    tags = models.JSONField(default=list, blank=True) 
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('BEGINNER', 'Beginner'),
            ('INTERMEDIATE', 'Intermediate'),
            ('ADVANCED', 'Advanced')
        ],
        default='BEGINNER'
    )
    
    # Relationships
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='library_resources')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_resources')
    classrooms = models.ManyToManyField('classroom.Classroom', related_name='library_resources', blank=True)
    
    # AI Integration
    ai_summary = models.TextField(blank=True, null=True)
    ai_keywords = models.JSONField(default=list, blank=True)
    ai_difficulty_score = models.FloatField(blank=True, null=True)  # 0-1 scale
    
    # Engagement Metrics
    view_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'learning_resources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['resource_type', 'is_published', 'is_approved']),
            models.Index(fields=['school', 'access_level']),
            models.Index(fields=['created_by', 'is_published']),
            models.Index(fields=['is_featured', 'is_published']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"
    
    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_file_size(self):
        # Get human-readable file size
        if self.file and self.file.size:
            size = self.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return "N/A"
    
    def get_engagement_rate(self):
        # Calculate engagement rate
        if self.view_count == 0:
            return 0
        total_interactions = (self.download_count + self.favorite_count + 
                            ResourceInteraction.objects.filter(resource=self, interaction_type='COMPLETE').count())
        return round((total_interactions / self.view_count) * 100, 2)
    
    def can_user_access(self, user):
        # Check if a user can access this resource
        if self.access_level == 'PUBLIC':
            return True
        elif self.access_level == 'SCHOOL':
            return self.school == user.school
        elif self.access_level == 'CLASSROOM':
            return (self.classrooms.filter(students=user).exists() or 
                    self.classrooms.filter(teacher=user).exists())
        elif self.access_level == 'PRIVATE':
            return self.created_by == user
        return False

class ResourceReview(models.Model):
    # User reviews and ratings for resources
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_reviews')
    
    # Rating (1-5 stars)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField(blank=True, null=True)
    
    # Helpfulness
    helpful_votes = models.IntegerField(default=0)
    not_helpful_votes = models.IntegerField(default=0)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resource_reviews'
        unique_together = ['resource', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['resource', 'is_approved']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_display_name()} - {self.resource.title} - {self.rating} stars"
    
    def get_helpfulness_score(self):
        # Calculate helpfulness score
        total_votes = self.helpful_votes + self.not_helpful_votes
        if total_votes == 0:
            return 0
        return round((self.helpful_votes / total_votes) * 100, 2)

class ResourceInteraction(models.Model):
    # Track user interactions with resources
    class InteractionType(models.TextChoices):
        VIEW = 'VIEW', 'View'
        DOWNLOAD = 'DOWNLOAD', 'Download'
        FAVORITE = 'FAVORITE', 'Favorite'
        SHARE = 'SHARE', 'Share'
        COMPLETE = 'COMPLETE', 'Complete'
    
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_interactions')
    interaction_type = models.CharField(max_length=20, choices=InteractionType.choices)
    
    # Additional data
    duration_seconds = models.IntegerField(default=0)  # For viewing time
    progress_percentage = models.FloatField(default=0)  # For completion tracking
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'resource_interactions'
        indexes = [
            models.Index(fields=['resource', 'user', 'interaction_type']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['resource', 'interaction_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_display_name()} - {self.interaction_type} - {self.resource.title}"

class StudyCollection(models.Model):
    # Collections of resources for study purposes
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Organization
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='study_collections')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_collections')
    resources = models.ManyToManyField(LearningResource, through='CollectionItem', related_name='collections')
    
    # Access
    is_public = models.BooleanField(default=False)
    allow_collaboration = models.BooleanField(default=False)
    collaborators = models.ManyToManyField(User, related_name='collaborative_collections', blank=True)
    
    # Metadata
    view_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'study_collections'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', 'is_public']),
            models.Index(fields=['created_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.created_by.get_display_name()}"
    
    def get_resource_count(self):
        return self.resources.count()
    
    def can_user_access(self, user):
        # Check if user can access this collection
        if self.is_public:
            return True
        return (self.created_by == user or 
                self.collaborators.filter(id=user.id).exists())

class CollectionItem(models.Model):
    # Through model for collection resources with ordering
    collection = models.ForeignKey(StudyCollection, on_delete=models.CASCADE)
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'collection_items'
        ordering = ['order', 'added_at']
        unique_together = ['collection', 'resource']
    
    def __str__(self):
        return f"{self.collection.name} - {self.resource.title}"

class AIRecommendation(models.Model):
    # AI-powered resource recommendations
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_recommendations')
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE, related_name='ai_recommendations')
    
    # Recommendation metrics
    confidence_score = models.FloatField()
    reason = models.TextField(blank=True, null=True)  # AI explanation
    recommendation_type = models.CharField(
        max_length=20,
        choices=[
            ('SIMILAR', 'Similar Content'),
            ('PROGRESSION', 'Next in Progression'),
            ('TRENDING', 'Trending'),
            ('PERSONALIZED', 'Personalized')
        ]
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'ai_recommendations'
        unique_together = ['user', 'resource']
        ordering = ['-confidence_score']
        indexes = [
            models.Index(fields=['user', 'expires_at']),
            models.Index(fields=['recommendation_type', 'confidence_score']),
        ]
    
    def __str__(self):
        return f"AI Rec for {self.user.get_display_name()} - {self.resource.title}"
    
    def is_expired(self):
        # Check if recommendation is expired
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

class ReadingList(models.Model):
    # Personal reading lists for users
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_lists')
    resources = models.ManyToManyField(LearningResource, through='ReadingListItem', related_name='reading_lists')
    
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reading_lists'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_public', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.get_display_name()}"
    
    def get_resource_count(self):
        return self.resources.count()
    
    def get_completed_count(self):
        return self.readinglistitem_set.filter(completed=True).count()
    
    def get_progress_percentage(self):
        total = self.get_resource_count()
        completed = self.get_completed_count()
        return round((completed / total * 100) if total > 0 else 0, 2)
    
    def can_user_access(self, user):
        # Check if user can access this reading list
        if self.is_public:
            return True
        return self.user == user

class ReadingListItem(models.Model):
    # Through model for reading list items
    reading_list = models.ForeignKey(ReadingList, on_delete=models.CASCADE)
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'reading_list_items'
        ordering = ['order', 'added_at']
        unique_together = ['reading_list', 'resource']
        indexes = [
            models.Index(fields=['reading_list', 'completed']),
            models.Index(fields=['resource', 'completed']),
        ]
    
    def __str__(self):
        return f"{self.reading_list.name} - {self.resource.title}"
    
    def save(self, *args, **kwargs):
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.completed and self.completed_at:
            self.completed_at = None
        super().save(*args, **kwargs)