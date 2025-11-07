from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'classrooms', views.ClassroomViewSet, basename='classroom')
router.register(r'assignments', views.AssignmentViewSet, basename='assignment')
router.register(r'submissions', views.SubmissionViewSet, basename='submission')
router.register(r'materials', views.ClassMaterialViewSet, basename='material')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
router.register(r'posts', views.ClassPostViewSet, basename='post')
router.register(r'comments', views.CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    
    # Additional endpoints
    path('join/', views.join_classroom, name='join-classroom'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher-dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student-dashboard'),
    path('search/', views.search_classrooms, name='search-classrooms'),
    path('posts/<int:post_id>/vote/', views.vote_poll, name='vote-poll'),
    
    # Classroom-specific endpoints
    path('classrooms/<int:classroom_id>/gradebook/', views.GradebookView.as_view(), name='classroom-gradebook'),
    path('classrooms/<int:classroom_id>/progress/<int:student_id>/', views.StudentProgressView.as_view(), name='student-progress'),
    path('classrooms/<int:classroom_id>/progress/', views.StudentProgressView.as_view(), name='current-student-progress'),
    
    # Nested endpoints
    path('classrooms/<int:classroom_id>/materials/', views.ClassMaterialListView.as_view(), name='classroom-materials'),
    path('classrooms/<int:classroom_id>/attendance/', views.AttendanceListView.as_view(), name='classroom-attendance'),
    path('posts/<int:post_id>/comments/', views.CommentListView.as_view(), name='post-comments'),
    
    # Bulk operations
    path('assignments/<int:assignment_id>/bulk-grade/', views.bulk_grade_submissions, name='bulk-grade-submissions'),
]