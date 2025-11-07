from django.urls import path, include
from . import views

app_name = 'wellbeing'

urlpatterns = [
    # Wellbeing Posts
    path('posts/', views.WellbeingPostListCreateView.as_view(), name='post-list'),
    path('posts/<int:pk>/', views.WellbeingPostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', views.PostCommentListCreateView.as_view(), name='post-comments'),
    path('posts/<int:post_id>/react/', views.toggle_post_reaction, name='post-reaction'),
    
    # Support Tickets
    path('tickets/', views.SupportTicketListCreateView.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', views.SupportTicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/<int:ticket_id>/messages/', views.TicketMessageListCreateView.as_view(), name='ticket-messages'),
    
    # Counselor Assignments
    path('counselors/assignments/', views.CounselorAssignmentListCreateView.as_view(), name='counselor-assignments'),
    path('counselors/my-students/', views.MyStudentAssignmentsView.as_view(), name='my-students'),
    
    # Wellbeing Resources
    path('resources/', views.WellbeingResourceListView.as_view(), name='resource-list'),
    path('resources/create/', views.WellbeingResourceCreateView.as_view(), name='resource-create'),
    
    # Mood Tracking
    path('mood-checks/', views.MoodCheckListCreateView.as_view(), name='mood-list'),
    path('mood/analytics/', views.MoodAnalyticsView.as_view(), name='mood-analytics'),
    
    # Wellbeing Goals
    path('goals/', views.WellbeingGoalListCreateView.as_view(), name='goal-list'),
    path('goals/<int:pk>/', views.WellbeingGoalDetailView.as_view(), name='goal-detail'),
    
    # Crisis Management
    path('crisis-alerts/', views.CrisisAlertListCreateView.as_view(), name='crisis-list'),
    
    # Content Reporting
    path('reports/', views.ContentReportCreateView.as_view(), name='report-create'),
    
    # Moderation
    path('moderation/actions/', views.ModerationActionListCreateView.as_view(), name='moderation-list'),
    
    # Dashboard & Analytics
    path('dashboard/', views.WellbeingDashboardView.as_view(), name='dashboard'),
    path('analytics/', views.WellbeingAnalyticsView.as_view(), name='analytics'),
]