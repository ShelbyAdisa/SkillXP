from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from .models import (
    ResourceCategory, LearningResource, ResourceReview, 
    ResourceInteraction, StudyCollection, CollectionItem,
    AIRecommendation, ReadingList, ReadingListItem
)
from users.serializers import UserSerializer
from classroom.serializers import ClassroomSerializer

class ResourceCategorySerializer(serializers.ModelSerializer):
    resource_count = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = ResourceCategory
        fields = [
            'id', 'name', 'description', 'color', 'icon', 
            'parent_category', 'school', 'is_active', 'created_by',
            'resource_count', 'subcategories'
        ]
        read_only_fields = ['id', 'created_by', 'resource_count', 'school']
    
    def get_resource_count(self, obj):
        return obj.resources.filter(is_published=True, is_approved=True).count()
    
    def get_subcategories(self, obj):
        subcategories = obj.subcategories.filter(is_active=True)
        return ResourceCategorySerializer(subcategories, many=True, context=self.context).data

class LearningResourceSerializer(serializers.ModelSerializer):
    created_by_details = UserSerializer(source='created_by', read_only=True)
    categories_details = ResourceCategorySerializer(source='categories', many=True, read_only=True)
    classrooms_details = ClassroomSerializer(source='classrooms', many=True, read_only=True)
    file_size = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    user_favorited = serializers.SerializerMethodField()
    interaction_stats = serializers.SerializerMethodField()
    can_manage = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningResource
        fields = [
            'id', 'title', 'description', 'resource_type', 'access_level',
            'file', 'external_url', 'embed_code', 'content',
            'author', 'publisher', 'publication_date', 'isbn', 'language',
            'pages', 'duration', 'categories', 'categories_details', 'tags',
            'difficulty_level', 'school', 'created_by', 'created_by_details',
            'classrooms', 'classrooms_details', 'ai_summary', 'ai_keywords',
            'ai_difficulty_score', 'view_count', 'download_count',
            'average_rating', 'rating_count', 'favorite_count',
            'is_published', 'is_featured', 'requires_approval', 'is_approved',
            'created_at', 'updated_at', 'published_at', 'file_size',
            'user_rating', 'user_favorited', 'interaction_stats', 'can_manage'
        ]
        read_only_fields = [
            'id', 'created_by', 'school', 'view_count', 'download_count', 
            'average_rating', 'rating_count', 'favorite_count', 'created_at', 
            'updated_at', 'published_at', 'ai_summary', 'ai_keywords', 'ai_difficulty_score'
        ]
        extra_kwargs = {
            'file': {'required': False},
            'external_url': {'required': False},
            'content': {'required': False}
        }
    
    def get_file_size(self, obj):
        return obj.get_file_size()
    
    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            review = obj.reviews.filter(user=request.user).first()
            return review.rating if review else None
        return None
    
    def get_user_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.interactions.filter(
                user=request.user, 
                interaction_type='FAVORITE'
            ).exists()
        return False
    
    def get_interaction_stats(self, obj):
        return {
            'views': obj.interactions.filter(interaction_type='VIEW').count(),
            'downloads': obj.interactions.filter(interaction_type='DOWNLOAD').count(),
            'favorites': obj.interactions.filter(interaction_type='FAVORITE').count(),
            'completions': obj.interactions.filter(interaction_type='COMPLETE').count(),
        }
    
    def get_can_manage(self, obj):
        # Check if current user can manage this resource
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        from .permissions import CanManageResource
        return CanManageResource().has_object_permission(request, None, obj)
    
    def validate(self, attrs):
        # Validate that either file, external_url, or content is provided
        has_file = attrs.get('file') or (self.instance and self.instance.file)
        has_url = attrs.get('external_url') or (self.instance and self.instance.external_url)
        has_content = attrs.get('content') or (self.instance and self.instance.content)
        
        if not any([has_file, has_url, has_content]):
            raise serializers.ValidationError(
                "At least one of file, external_url, or content must be provided."
            )
        
        # Validate file type if file is provided
        if has_file and not self.instance:  # Only on creation
            file = attrs.get('file')
            allowed_extensions = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx',
                                 'mp4', 'avi', 'mov', 'mp3', 'wav', 'jpg', 'jpeg', 'png', 'gif']
            validator = FileExtensionValidator(allowed_extensions)
            validator(file)
        
        return attrs
    
    def create(self, validated_data):
        # Extract many-to-many fields
        categories = validated_data.pop('categories', [])
        classrooms = validated_data.pop('classrooms', [])
        
        # Create resource
        resource = LearningResource.objects.create(**validated_data)
        
        # Set many-to-many relationships
        if categories:
            resource.categories.set(categories)
        if classrooms:
            resource.classrooms.set(classrooms)
        
        return resource
    
    def update(self, instance, validated_data):
        # Handle many-to-many fields
        categories = validated_data.pop('categories', None)
        classrooms = validated_data.pop('classrooms', None)
        
        # Update instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update many-to-many relationships if provided
        if categories is not None:
            instance.categories.set(categories)
        if classrooms is not None:
            instance.classrooms.set(classrooms)
        
        return instance

class ResourceReviewSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    resource_title = serializers.CharField(source='resource.title', read_only=True)
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = ResourceReview
        fields = [
            'id', 'resource', 'resource_title', 'user', 'user_details',
            'rating', 'review_text', 'helpful_votes', 'not_helpful_votes',
            'is_approved', 'created_at', 'updated_at', 'can_edit'
        ]
        read_only_fields = [
            'id', 'user', 'helpful_votes', 'not_helpful_votes', 
            'is_approved', 'created_at', 'updated_at'
        ]
    
    def get_can_edit(self, obj):
        # Check if current user can edit this review
        request = self.context.get('request')
        return request and request.user.is_authenticated and obj.user == request.user
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def create(self, validated_data):
        # Ensure user can only have one review per resource
        resource = validated_data['resource']
        user = self.context['request'].user
        
        if ResourceReview.objects.filter(resource=resource, user=user).exists():
            raise serializers.ValidationError("You have already reviewed this resource.")
        
        validated_data['user'] = user
        return super().create(validated_data)

class ResourceInteractionSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    resource_title = serializers.CharField(source='resource.title', read_only=True)
    
    class Meta:
        model = ResourceInteraction
        fields = [
            'id', 'resource', 'resource_title', 'user', 'user_details',
            'interaction_type', 'duration_seconds', 'progress_percentage',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

class StudyCollectionSerializer(serializers.ModelSerializer):
    created_by_details = UserSerializer(source='created_by', read_only=True)
    resource_count = serializers.SerializerMethodField()
    collaborators_details = UserSerializer(source='collaborators', many=True, read_only=True)
    can_manage = serializers.SerializerMethodField()
    
    class Meta:
        model = StudyCollection
        fields = [
            'id', 'name', 'description', 'school', 'created_by', 'created_by_details',
            'is_public', 'allow_collaboration', 'collaborators', 'collaborators_details',
            'view_count', 'favorite_count', 'resource_count', 'created_at', 'updated_at', 'can_manage'
        ]
        read_only_fields = [
            'id', 'created_by', 'school', 'view_count', 'favorite_count', 
            'created_at', 'updated_at'
        ]
    
    def get_resource_count(self, obj):
        return obj.resources.count()
    
    def get_can_manage(self, obj):
        # Check if current user can manage this collection
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        from .permissions import IsCollectionOwnerOrCollaborator
        return IsCollectionOwnerOrCollaborator().has_object_permission(request, None, obj)
    
    def create(self, validated_data):
        collaborators = validated_data.pop('collaborators', [])
        collection = StudyCollection.objects.create(**validated_data)
        
        if collaborators:
            collection.collaborators.set(collaborators)
        
        return collection
    
    def update(self, instance, validated_data):
        collaborators = validated_data.pop('collaborators', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if collaborators is not None:
            instance.collaborators.set(collaborators)
        
        return instance

class CollectionItemSerializer(serializers.ModelSerializer):
    resource_details = LearningResourceSerializer(source='resource', read_only=True)
    
    class Meta:
        model = CollectionItem
        fields = ['id', 'collection', 'resource', 'resource_details', 'order', 'added_at', 'notes']
        read_only_fields = ['id', 'added_at']

class AIRecommendationSerializer(serializers.ModelSerializer):
    resource_details = LearningResourceSerializer(source='resource', read_only=True)
    
    class Meta:
        model = AIRecommendation
        fields = [
            'id', 'user', 'resource', 'resource_details', 'confidence_score',
            'reason', 'recommendation_type', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at']

class ReadingListSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    resource_count = serializers.SerializerMethodField()
    completed_count = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = ReadingList
        fields = [
            'id', 'name', 'description', 'user', 'user_details', 'is_public',
            'resource_count', 'completed_count', 'progress_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_resource_count(self, obj):
        return obj.resources.count()
    
    def get_completed_count(self, obj):
        return obj.readinglistitem_set.filter(completed=True).count()
    
    def get_progress_percentage(self, obj):
        total = self.get_resource_count(obj)
        completed = self.get_completed_count(obj)
        return round((completed / total * 100) if total > 0 else 0, 2)

class ReadingListItemSerializer(serializers.ModelSerializer):
    resource_details = LearningResourceSerializer(source='resource', read_only=True)
    
    class Meta:
        model = ReadingListItem
        fields = [
            'id', 'reading_list', 'resource', 'resource_details', 'order',
            'added_at', 'completed', 'completed_at', 'notes'
        ]
        read_only_fields = ['id', 'added_at']

class ResourceSearchSerializer(serializers.Serializer):
    # Serializer for resource search parameters
    query = serializers.CharField(required=False, allow_blank=True)
    resource_type = serializers.CharField(required=False, allow_blank=True)
    category = serializers.IntegerField(required=False, allow_null=True)
    difficulty = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50), 
        required=False, 
        default=list
    )
    sort_by = serializers.ChoiceField(
        choices=['relevance', 'popular', 'rating', 'newest', 'oldest'],
        default='relevance'
    )
    page = serializers.IntegerField(min_value=1, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=20)

class ResourceUploadSerializer(serializers.ModelSerializer):
    # Serializer for resource upload with additional validation
    class Meta:
        model = LearningResource
        fields = [
            'title', 'description', 'resource_type', 'file', 
            'external_url', 'content', 'categories', 'tags', 
            'difficulty_level', 'access_level'
        ]
        extra_kwargs = {
            'file': {'required': False},
            'external_url': {'required': False},
            'content': {'required': False}
        }
    
    def validate(self, attrs):
        # Validate that at least one content field is provided
        has_file = attrs.get('file')
        has_url = attrs.get('external_url')
        has_content = attrs.get('content')
        
        if not any([has_file, has_url, has_content]):
            raise serializers.ValidationError(
                "At least one of file, external_url, or content must be provided."
            )
        
        # Validate file type and size
        if has_file:
            # Check file size (max 100MB)
            max_size = 100 * 1024 * 1024  # 100MB
            if has_file.size > max_size:
                raise serializers.ValidationError("File size must be less than 100MB.")
            
            # Validate file extension
            allowed_extensions = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx',
                                 'mp4', 'avi', 'mov', 'mp3', 'wav', 'jpg', 'jpeg', 'png', 'gif']
            validator = FileExtensionValidator(allowed_extensions)
            validator(has_file)
        
        return attrs

class BulkOperationSerializer(serializers.Serializer):
    # Serializer for bulk operations
    resource_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=100
    )

class ResourceAnalyticsSerializer(serializers.Serializer):
    # Serializer for resource analytics data
    total_views = serializers.IntegerField()
    total_downloads = serializers.IntegerField()
    total_favorites = serializers.IntegerField()
    total_completions = serializers.IntegerField()
    engagement_rate = serializers.FloatField()
    average_completion_time = serializers.FloatField()
    user_demographics = serializers.JSONField()
    average_rating = serializers.FloatField()
    rating_count = serializers.IntegerField()