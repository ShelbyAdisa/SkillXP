from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'elibrary'

router = DefaultRouter()
router.register(r'categories', views.ResourceCategoryViewSet, basename='category')
router.register(r'resources', views.LearningResourceViewSet, basename='resource')
router.register(r'reviews', views.ResourceReviewViewSet, basename='review')
router.register(r'collections', views.StudyCollectionViewSet, basename='collection')
router.register(r'reading-lists', views.ReadingListViewSet, basename='readinglist')

urlpatterns = [
    path('', include(router.urls)),
    
    # Search and discovery
    path('search/', views.search_resources, name='search-resources'),
    path('recommendations/', views.get_recommendations, name='get-recommendations'),
    path('global-search/', views.global_search, name='global-search'),
    
    # Dashboard and analytics
    path('dashboard/', views.dashboard_stats, name='dashboard-stats'),
    
    # Upload endpoint
    path('upload/', views.upload_resource, name='upload-resource'),
    
    # Collection specific endpoints
    path('collections/<int:pk>/resources/', views.StudyCollectionViewSet.as_view({'get': 'resources'}), name='collection-resources'),
    path('collections/<int:pk>/add-resource/', views.StudyCollectionViewSet.as_view({'post': 'add_resource'}), name='add-to-collection'),
    path('collections/<int:pk>/remove-resource/', views.StudyCollectionViewSet.as_view({'post': 'remove_resource'}), name='remove-from-collection'),
    path('collections/<int:pk>/reorder/', views.StudyCollectionViewSet.as_view({'post': 'reorder'}), name='reorder-collection'),
    
    # Reading list specific endpoints
    path('reading-lists/<int:pk>/add-resource/', views.ReadingListViewSet.as_view({'post': 'add_resource'}), name='add-to-reading-list'),
    path('reading-lists/<int:pk>/remove-resource/', views.ReadingListViewSet.as_view({'post': 'remove_resource'}), name='remove-from-reading-list'),
    path('reading-lists/<int:pk>/mark-completed/', views.ReadingListViewSet.as_view({'post': 'mark_completed'}), name='mark-reading-completed'),
    path('reading-lists/<int:pk>/progress/', views.ReadingListViewSet.as_view({'get': 'progress'}), name='reading-list-progress'),
    
    # Resource specific endpoints
    path('resources/<int:pk>/view/', views.LearningResourceViewSet.as_view({'post': 'record_view'}), name='record-view'),
    path('resources/<int:pk>/download/', views.LearningResourceViewSet.as_view({'post': 'record_download'}), name='record-download'),
    path('resources/<int:pk>/favorite/', views.LearningResourceViewSet.as_view({'post': 'toggle_favorite'}), name='toggle-favorite'),
    path('resources/<int:pk>/complete/', views.LearningResourceViewSet.as_view({'post': 'record_completion'}), name='record-completion'),
    path('resources/<int:pk>/similar/', views.LearningResourceViewSet.as_view({'get': 'similar_resources'}), name='similar-resources'),
    path('resources/<int:pk>/analytics/', views.LearningResourceViewSet.as_view({'get': 'analytics'}), name='resource-analytics'),
    path('resources/<int:pk>/approve/', views.LearningResourceViewSet.as_view({'post': 'approve'}), name='approve-resource'),
    path('resources/<int:pk>/reject/', views.LearningResourceViewSet.as_view({'post': 'reject'}), name='reject-resource'),
    path('resources/<int:pk>/feature/', views.LearningResourceViewSet.as_view({'post': 'feature'}), name='feature-resource'),
    
    # Review specific endpoints
    path('reviews/my-reviews/', views.ResourceReviewViewSet.as_view({'get': 'my_reviews'}), name='my-reviews'),
    path('reviews/<int:pk>/vote-helpful/', views.ResourceReviewViewSet.as_view({'post': 'vote_helpful'}), name='vote-helpful'),
    path('reviews/<int:pk>/vote-not-helpful/', views.ResourceReviewViewSet.as_view({'post': 'vote_not_helpful'}), name='vote-not-helpful'),
    
    # Category specific endpoints
    path('categories/<int:pk>/resources/', views.ResourceCategoryViewSet.as_view({'get': 'resources'}), name='category-resources'),
    
    # Featured, recent, and popular resources
    path('resources/featured/', views.LearningResourceViewSet.as_view({'get': 'featured'}), name='featured-resources'),
    path('resources/recent/', views.LearningResourceViewSet.as_view({'get': 'recent'}), name='recent-resources'),
    path('resources/popular/', views.LearningResourceViewSet.as_view({'get': 'popular'}), name='popular-resources'),
    path('resources/pending-approval/', views.LearningResourceViewSet.as_view({'get': 'pending_approval'}), name='pending-approval'),
]