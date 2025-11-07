from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F, Max
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator, EmptyPage

from .models import (
    ResourceCategory, LearningResource, ResourceReview, 
    ResourceInteraction, StudyCollection, CollectionItem,
    AIRecommendation, ReadingList, ReadingListItem
)
from .serializers import (
    ResourceCategorySerializer, LearningResourceSerializer, ResourceReviewSerializer,
    ResourceInteractionSerializer, StudyCollectionSerializer, CollectionItemSerializer,
    AIRecommendationSerializer, ReadingListSerializer, ReadingListItemSerializer,
    ResourceSearchSerializer, ResourceUploadSerializer
)
from .permissions import (
    CanAccessResource, CanManageResource, CanCreateResource, CanApproveResource,
    IsCollectionOwnerOrCollaborator, CanViewPublicCollections, CanCreateCategory,
    CanReviewResource, CanInteractWithResource, IsReadingListOwner, 
    CanViewPublicReadingLists, ResourceActionPermission, AdminResourcePermission,
    SearchPermission, RecommendationPermission, DashboardPermission
)
from .utils import AIResourceHelper, SearchHelper, ResourceAnalyzer
from users.models import User

class ResourceCategoryViewSet(ModelViewSet):
    serializer_class = ResourceCategorySerializer
    permission_classes = [permissions.IsAuthenticated, CanCreateCategory]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent_category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        return ResourceCategory.objects.filter(school=self.request.user.school, is_active=True)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, school=self.request.user.school)
    
    @action(detail=True, methods=['get'])
    def resources(self, request, pk=None):
        # Get resources in this category
        category = self.get_object()
        resources = category.resources.filter(is_published=True, is_approved=True)
        serializer = LearningResourceSerializer(resources, many=True, context={'request': request})
        return Response(serializer.data)

class LearningResourceViewSet(ModelViewSet):
    serializer_class = LearningResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource_type', 'access_level', 'difficulty_level', 'is_published', 'is_featured']
    search_fields = ['title', 'description', 'author', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'view_count', 'average_rating', 'download_count', 'favorite_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        # Base queryset - resources from user's school
        queryset = LearningResource.objects.filter(school=user.school)
        
        # Filter by access level
        access_filters = Q(access_level='PUBLIC')
        
        if user.school:
            access_filters |= Q(access_level='SCHOOL', school=user.school)
        
        if user.role == User.Role.STUDENT:
            access_filters |= Q(
                access_level='CLASSROOM', 
                classrooms__students=user
            )
        elif user.role == User.Role.TEACHER:
            access_filters |= Q(
                access_level='CLASSROOM',
                classrooms__teacher=user
            )
        
        access_filters |= Q(access_level='PRIVATE', created_by=user)
        
        queryset = queryset.filter(access_filters).distinct()
        
        # Only show published and approved resources for normal users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True, is_approved=True)
        
        return queryset.select_related('created_by', 'school').prefetch_related('categories', 'classrooms')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), CanCreateResource()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), CanManageResource()]
        elif self.action in ['approve', 'reject', 'feature']:
            return [permissions.IsAuthenticated(), AdminResourcePermission()]
        elif self.action in ['record_view', 'record_download', 'toggle_favorite', 'record_completion']:
            return [permissions.IsAuthenticated(), ResourceActionPermission()]
        return [permissions.IsAuthenticated(), CanAccessResource()]
    
    def perform_create(self, serializer):
        resource = serializer.save(created_by=self.request.user, school=self.request.user.school)
        
        # Process resource with AI
        from .tasks import process_new_resource
        process_new_resource(resource.id)
    
    @action(detail=True, methods=['post'])
    def record_view(self, request, pk=None):
        # Record a view interaction
        resource = self.get_object()
        
        ResourceInteraction.objects.create(
            resource=resource,
            user=request.user,
            interaction_type='VIEW'
        )
        
        resource.view_count = F('view_count') + 1
        resource.save()
        resource.refresh_from_db()
        
        return Response({'status': 'View recorded', 'view_count': resource.view_count})
    
    @action(detail=True, methods=['post'])
    def record_download(self, request, pk=None):
        # Record a download interaction
        resource = self.get_object()
        
        ResourceInteraction.objects.create(
            resource=resource,
            user=request.user,
            interaction_type='DOWNLOAD'
        )
        
        resource.download_count = F('download_count') + 1
        resource.save()
        resource.refresh_from_db()
        
        return Response({'status': 'Download recorded', 'download_count': resource.download_count})
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        # Toggle favorite status
        resource = self.get_object()
        
        interaction, created = ResourceInteraction.objects.get_or_create(
            resource=resource,
            user=request.user,
            interaction_type='FAVORITE'
        )
        
        if not created:
            interaction.delete()
            resource.favorite_count = F('favorite_count') - 1
            is_favorited = False
        else:
            resource.favorite_count = F('favorite_count') + 1
            is_favorited = True
        
        resource.save()
        resource.refresh_from_db()
        
        return Response({
            'favorited': is_favorited, 
            'favorite_count': resource.favorite_count
        })
    
    @action(detail=True, methods=['post'])
    def record_completion(self, request, pk=None):
        # Record resource completion
        resource = self.get_object()
        progress = request.data.get('progress_percentage', 100)
        duration = request.data.get('duration_seconds', 0)
        
        ResourceInteraction.objects.create(
            resource=resource,
            user=request.user,
            interaction_type='COMPLETE',
            progress_percentage=progress,
            duration_seconds=duration
        )
        
        return Response({'status': 'Completion recorded'})
    
    @action(detail=True, methods=['get'])
    def similar_resources(self, request, pk=None):
        # Get similar resources
        resource = self.get_object()
        similar = AIResourceHelper.get_similar_resources(resource, request.user)
        serializer = LearningResourceSerializer(similar, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        # Get resource analytics
        resource = self.get_object()
        analytics = ResourceAnalyzer.get_resource_analytics(resource)
        return Response(analytics)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        # Approve a resource
        resource = self.get_object()
        resource.is_approved = True
        resource.requires_approval = False
        resource.save()
        return Response({'status': 'Resource approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        # Reject a resource
        resource = self.get_object()
        resource.is_approved = False
        resource.requires_approval = False
        resource.save()
        return Response({'status': 'Resource rejected'})
    
    @action(detail=True, methods=['post'])
    def feature(self, request, pk=None):
        # Toggle featured status
        resource = self.get_object()
        resource.is_featured = not resource.is_featured
        resource.save()
        return Response({'status': 'Featured status updated', 'is_featured': resource.is_featured})
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        # Get featured resources
        featured_resources = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(featured_resources)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        # Get recently added resources
        recent_resources = self.get_queryset().order_by('-created_at')[:20]
        serializer = self.get_serializer(recent_resources, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        # Get popular resources
        popular_resources = self.get_queryset().order_by('-view_count', '-download_count')[:20]
        serializer = self.get_serializer(popular_resources, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        # Get resources pending approval (admin only)
        if not request.user.is_staff:
            return Response(
                {'detail': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending_resources = LearningResource.objects.filter(
            school=request.user.school,
            requires_approval=True,
            is_approved=False
        )
        serializer = self.get_serializer(pending_resources, many=True, context={'request': request})
        return Response(serializer.data)

class ResourceReviewViewSet(ModelViewSet):
    serializer_class = ResourceReviewSerializer
    permission_classes = [permissions.IsAuthenticated, CanReviewResource]
    
    def get_queryset(self):
        return ResourceReview.objects.filter(
            resource__school=self.request.user.school,
            is_approved=True
        ).select_related('user', 'resource')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        
        # Update resource rating
        resource = review.resource
        reviews = resource.reviews.filter(is_approved=True)
        resource.average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        resource.rating_count = reviews.count()
        resource.save()
    
    @action(detail=True, methods=['post'])
    def vote_helpful(self, request, pk=None):
        # Vote a review as helpful
        review = self.get_object()
        review.helpful_votes = F('helpful_votes') + 1
        review.save()
        review.refresh_from_db()
        return Response({'helpful_votes': review.helpful_votes})
    
    @action(detail=True, methods=['post'])
    def vote_not_helpful(self, request, pk=None):
        # Vote a review as not helpful
        review = self.get_object()
        review.not_helpful_votes = F('not_helpful_votes') + 1
        review.save()
        review.refresh_from_db()
        return Response({'not_helpful_votes': review.not_helpful_votes})
    
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        # Get current user's reviews
        user_reviews = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(user_reviews, many=True, context={'request': request})
        return Response(serializer.data)

class StudyCollectionViewSet(ModelViewSet):
    serializer_class = StudyCollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_public', 'allow_collaboration']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        user = self.request.user
        
        # User can see their own collections, collaborative collections, and public collections
        return StudyCollection.objects.filter(
            Q(created_by=user) | 
            Q(collaborators=user) |
            Q(is_public=True)
        ).distinct().select_related('created_by', 'school').prefetch_related('collaborators')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'add_resource', 'remove_resource']:
            return [permissions.IsAuthenticated(), IsCollectionOwnerOrCollaborator()]
        return [permissions.IsAuthenticated(), CanViewPublicCollections()]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, school=self.request.user.school)
    
    @action(detail=True, methods=['post'])
    def add_resource(self, request, pk=None):
        # Add resource to collection
        collection = self.get_object()
        resource_id = request.data.get('resource_id')
        notes = request.data.get('notes', '')
        
        try:
            resource = LearningResource.objects.get(id=resource_id, school=request.user.school)
            
            # Check if resource is already in collection
            if collection.resources.filter(id=resource_id).exists():
                return Response(
                    {'detail': 'Resource already in collection.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the next order number
            max_order = CollectionItem.objects.filter(collection=collection).aggregate(max_order=Max('order'))['max_order'] or 0
            
            CollectionItem.objects.create(
                collection=collection,
                resource=resource,
                order=max_order + 1,
                notes=notes
            )
            
            return Response({'status': 'Resource added to collection'})
            
        except LearningResource.DoesNotExist:
            return Response(
                {'detail': 'Resource not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_resource(self, request, pk=None):
        # Remove resource from collection
        collection = self.get_object()
        resource_id = request.data.get('resource_id')
        
        try:
            collection_item = CollectionItem.objects.get(
                collection=collection,
                resource_id=resource_id
            )
            collection_item.delete()
            
            # Reorder remaining items
            items = CollectionItem.objects.filter(collection=collection).order_by('order')
            for index, item in enumerate(items):
                item.order = index + 1
                item.save()
            
            return Response({'status': 'Resource removed from collection'})
            
        except CollectionItem.DoesNotExist:
            return Response(
                {'detail': 'Resource not found in collection.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def resources(self, request, pk=None):
        # Get collection resources
        collection = self.get_object()
        items = collection.collectionitem_set.select_related('resource').all()
        serializer = CollectionItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        # Reorder collection resources
        collection = self.get_object()
        resource_order = request.data.get('resource_order', [])
        
        for order_data in resource_order:
            resource_id = order_data.get('resource_id')
            new_order = order_data.get('order')
            
            try:
                item = CollectionItem.objects.get(
                    collection=collection,
                    resource_id=resource_id
                )
                item.order = new_order
                item.save()
            except CollectionItem.DoesNotExist:
                continue
        
        return Response({'status': 'Collection reordered'})

class ReadingListViewSet(ModelViewSet):
    serializer_class = ReadingListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        user = self.request.user
        
        # User can see their own reading lists and public reading lists
        return ReadingList.objects.filter(
            Q(user=user) | Q(is_public=True)
        ).distinct().select_related('user')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'add_resource', 'remove_resource', 'mark_completed']:
            return [permissions.IsAuthenticated(), IsReadingListOwner()]
        return [permissions.IsAuthenticated(), CanViewPublicReadingLists()]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_resource(self, request, pk=None):
        # Add resource to reading list
        reading_list = self.get_object()
        resource_id = request.data.get('resource_id')
        notes = request.data.get('notes', '')
        
        try:
            resource = LearningResource.objects.get(id=resource_id, school=request.user.school)
            
            # Check if resource is already in reading list
            if reading_list.resources.filter(id=resource_id).exists():
                return Response(
                    {'detail': 'Resource already in reading list.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the next order number
            max_order = ReadingListItem.objects.filter(reading_list=reading_list).aggregate(max_order=Max('order'))['max_order'] or 0
            
            ReadingListItem.objects.create(
                reading_list=reading_list,
                resource=resource,
                order=max_order + 1,
                notes=notes
            )
            
            return Response({'status': 'Resource added to reading list'})
            
        except LearningResource.DoesNotExist:
            return Response(
                {'detail': 'Resource not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_resource(self, request, pk=None):
        # Remove resource from reading list
        reading_list = self.get_object()
        resource_id = request.data.get('resource_id')
        
        try:
            reading_item = ReadingListItem.objects.get(
                reading_list=reading_list,
                resource_id=resource_id
            )
            reading_item.delete()
            
            # Reorder remaining items
            items = ReadingListItem.objects.filter(reading_list=reading_list).order_by('order')
            for index, item in enumerate(items):
                item.order = index + 1
                item.save()
            
            return Response({'status': 'Resource removed from reading list'})
            
        except ReadingListItem.DoesNotExist:
            return Response(
                {'detail': 'Resource not found in reading list.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        # Mark reading list item as completed
        reading_list = self.get_object()
        resource_id = request.data.get('resource_id')
        
        try:
            item = ReadingListItem.objects.get(
                reading_list=reading_list,
                resource_id=resource_id
            )
            
            item.completed = True
            item.completed_at = timezone.now()
            item.save()
            
            return Response({'status': 'Resource marked as completed'})
            
        except ReadingListItem.DoesNotExist:
            return Response(
                {'detail': 'Resource not found in reading list.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        # Get reading list progress
        reading_list = self.get_object()
        total_items = reading_list.resources.count()
        completed_items = reading_list.readinglistitem_set.filter(completed=True).count()
        
        progress = (completed_items / total_items * 100) if total_items > 0 else 0
        
        return Response({
            'total_items': total_items,
            'completed_items': completed_items,
            'progress_percentage': round(progress, 2)
        })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanCreateResource])
def upload_resource(request):
    # Upload a new resource with file handling
    serializer = ResourceUploadSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        # Create the resource
        resource = serializer.save(
            created_by=request.user,
            school=request.user.school,
            requires_approval=request.user.role == User.Role.TEACHER  # Teachers need approval
        )
        
        # Process with AI
        from .tasks import process_new_resource
        process_new_resource(resource.id)
        
        return Response(
            LearningResourceSerializer(resource, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([SearchPermission])
def search_resources(request):
    # Advanced search for resources
    serializer = ResourceSearchSerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)
    
    results = SearchHelper.search_resources(
        user=request.user,
        query=serializer.validated_data.get('query'),
        resource_type=serializer.validated_data.get('resource_type'),
        category_id=serializer.validated_data.get('category'),
        difficulty=serializer.validated_data.get('difficulty'),
        tags=serializer.validated_data.get('tags'),
        sort_by=serializer.validated_data.get('sort_by')
    )
    
    # Paginate results
    page = request.GET.get('page', 1)
    page_size = min(int(request.GET.get('page_size', 20)), 100) 
    
    paginator = Paginator(results, page_size)
    try:
        paginated_results = paginator.page(page)
    except EmptyPage:
        paginated_results = paginator.page(paginator.num_pages)
    
    resource_serializer = LearningResourceSerializer(
        paginated_results, 
        many=True, 
        context={'request': request}
    )
    
    # Get available filters for the search
    available_filters = SearchHelper.build_search_filters(request.user)
    
    return Response({
        'results': resource_serializer.data,
        'total_count': paginator.count,
        'page_count': paginator.num_pages,
        'current_page': paginated_results.number,
        'filters': available_filters
    })

@api_view(['GET'])
@permission_classes([RecommendationPermission])
def get_recommendations(request):
    # Get AI-powered resource recommendations
    recommendations = AIRecommendation.objects.filter(
        user=request.user,
        expires_at__gte=timezone.now()
    ).select_related('resource').order_by('-confidence_score')[:10]
    
    serializer = AIRecommendationSerializer(recommendations, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([DashboardPermission])
def dashboard_stats(request):
    # Get eLibrary dashboard statistics
    user = request.user
    
    # Basic stats
    total_resources = LearningResource.objects.filter(school=user.school, is_published=True).count()
    user_favorites = ResourceInteraction.objects.filter(
        user=user, 
        interaction_type='FAVORITE'
    ).count()
    user_completions = ResourceInteraction.objects.filter(
        user=user,
        interaction_type='COMPLETE'
    ).count()
    user_views = ResourceInteraction.objects.filter(
        user=user,
        interaction_type='VIEW'
    ).count()
    
    # Recent activity
    recent_views = ResourceInteraction.objects.filter(
        user=user,
        interaction_type='VIEW'
    ).select_related('resource').order_by('-created_at')[:5]
    
    # Popular resources
    popular_resources = LearningResource.objects.filter(
        school=user.school,
        is_published=True
    ).order_by('-view_count')[:5]
    
    # User's recent uploads (if teacher/admin)
    recent_uploads = []
    if user.role in [User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
        recent_uploads = LearningResource.objects.filter(
            created_by=user
        ).order_by('-created_at')[:5]
    
    return Response({
        'stats': {
            'total_resources': total_resources,
            'user_favorites': user_favorites,
            'user_completions': user_completions,
            'user_views': user_views,
            'reading_lists': ReadingList.objects.filter(user=user).count(),
            'collections': StudyCollection.objects.filter(created_by=user).count(),
            'reviews_written': ResourceReview.objects.filter(user=user).count()
        },
        'recent_activity': ResourceInteractionSerializer(recent_views, many=True).data,
        'popular_resources': LearningResourceSerializer(popular_resources, many=True, context={'request': request}).data,
        'recent_uploads': LearningResourceSerializer(recent_uploads, many=True, context={'request': request}).data if recent_uploads else []
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def global_search(request):
    # Global search across all eLibrary content
    query = request.GET.get('q', '')
    if not query:
        return Response({'results': []})
    
    # Search resources
    resources = SearchHelper.search_resources(
        user=request.user,
        query=query,
        limit=10
    )
    
    # Search collections
    collections = StudyCollection.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        Q(is_public=True) | Q(created_by=request.user) | Q(collaborators=request.user)
    )[:5]
    
    # Search categories
    categories = ResourceCategory.objects.filter(
        school=request.user.school,
        name__icontains=query
    )[:5]
    
    return Response({
        'resources': LearningResourceSerializer(resources, many=True, context={'request': request}).data,
        'collections': StudyCollectionSerializer(collections, many=True, context={'request': request}).data,
        'categories': ResourceCategorySerializer(categories, many=True, context={'request': request}).data
    })