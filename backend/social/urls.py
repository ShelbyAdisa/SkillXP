from django.urls import path, include
from . import views

app_name = 'social'

urlpatterns = [
    # Communities
    path('communities/', views.CommunityListCreateView.as_view(), name='community-list'),
    path('communities/<int:pk>/', views.CommunityDetailView.as_view(), name='community-detail'),
    path('communities/<int:community_id>/members/', views.CommunityMembershipView.as_view(), name='community-members'),
    
    # Posts
    path('posts/', views.PostListCreateView.as_view(), name='post-list'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='post-comments'),
    
    # Voting
    path('posts/<int:post_id>/vote/', views.toggle_vote, name='post-vote'),
    path('comments/<int:comment_id>/vote/', views.toggle_vote, name='comment-vote'),
    
    # Messaging
    path('messages/', views.DirectMessageListCreateView.as_view(), name='message-list'),
    path('threads/', views.MessageThreadListView.as_view(), name='thread-list'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark-notifications-read'),
    
    # User Interactions
    path('users/<int:user_id>/follow/', views.UserFollowView.as_view(), name='user-follow'),
    path('bookmarks/', views.BookmarkListCreateView.as_view(), name='bookmark-list'),
    
    # Reports
    path('reports/', views.ReportCreateView.as_view(), name='report-create'),
    
    # Feeds & Discovery
    path('feed/personal/', views.PersonalFeedView.as_view(), name='personal-feed'),
    path('trending/', views.TrendingTopicsView.as_view(), name='trending-topics'),
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Utility endpoints
    path('feed/school/', views.PostListCreateView.as_view(), name='school-feed'),  # School-wide posts
]