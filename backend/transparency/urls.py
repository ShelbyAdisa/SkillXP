from django.urls import path, include
from . import views

app_name = 'transparency'

urlpatterns = [
    # Budget Categories
    path('categories/', views.BudgetCategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.BudgetCategoryDetailView.as_view(), name='category-detail'),
    
    # Financial Transactions
    path('transactions/', views.FinancialTransactionListCreateView.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', views.FinancialTransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/<int:transaction_id>/approve/', views.approve_transaction, name='approve-transaction'),
    
    # Budgets
    path('budgets/', views.BudgetListCreateView.as_view(), name='budget-list'),
    path('budgets/<int:pk>/', views.BudgetDetailView.as_view(), name='budget-detail'),
    
    # Voting Issues
    path('voting/issues/', views.VotingIssueListCreateView.as_view(), name='voting-issue-list'),
    path('voting/issues/<int:pk>/', views.VotingIssueDetailView.as_view(), name='voting-issue-detail'),
    path('voting/issues/<int:issue_id>/publish/', views.publish_voting_issue, name='publish-voting-issue'),
    
    # Votes
    path('voting/votes/', views.VoteCreateView.as_view(), name='vote-create'),
    path('voting/my-votes/', views.UserVotesListView.as_view(), name='user-votes'),
    
    # Financial Reports
    path('reports/', views.FinancialReportListCreateView.as_view(), name='report-list'),
    path('reports/<int:pk>/', views.FinancialReportDetailView.as_view(), name='report-detail'),
    path('reports/<int:report_id>/publish/', views.publish_financial_report, name='publish-report'),
    
    # Comments
    path('comments/', views.CommentListCreateView.as_view(), name='comment-list'),
    
    # Audit Logs
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit-log-list'),
    
    # Notification Subscriptions
    path('subscriptions/', views.NotificationSubscriptionListCreateView.as_view(), name='subscription-list'),
    
    # Dashboard & Analytics
    path('dashboard/', views.TransparencyDashboardView.as_view(), name='dashboard'),
    path('analytics/financial/', views.FinancialAnalyticsView.as_view(), name='financial-analytics'),
]