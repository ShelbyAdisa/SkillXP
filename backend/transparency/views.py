from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum, Count, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from .models import (
    BudgetCategory, FinancialTransaction, Budget, VotingIssue,
    Vote, FinancialReport, Comment, AuditLog, NotificationSubscription
)
from .serializers import (
    BudgetCategorySerializer, FinancialTransactionSerializer, BudgetSerializer,
    VotingIssueSerializer, VoteSerializer, FinancialReportSerializer,
    CommentSerializer, AuditLogSerializer, NotificationSubscriptionSerializer,
    FinancialOverviewSerializer, VotingOverviewSerializer
)
from .permissions import (
    IsSchoolMember, CanViewFinancialData, CanSubmitTransaction,
    CanApproveTransaction, CanManageBudgets, CanCreateVotingIssue,
    CanVote, CanViewAuditLogs, IsOwnerOrAdmin, CanGenerateReports
)

User = get_user_model()

# Budget Categories Views
class BudgetCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = BudgetCategorySerializer
    permission_classes = [permissions.IsAuthenticated, CanViewFinancialData]
    
    def get_queryset(self):
        return BudgetCategory.objects.filter(school=self.request.user.school)
    
    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class BudgetCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetCategorySerializer
    permission_classes = [permissions.IsAuthenticated, CanViewFinancialData]
    queryset = BudgetCategory.objects.all()

# Financial Transactions Views
class FinancialTransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = FinancialTransactionSerializer
    permission_classes = [permissions.IsAuthenticated, CanSubmitTransaction]
    
    def get_queryset(self):
        user = self.request.user
        queryset = FinancialTransaction.objects.filter(school=user.school)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by type if provided
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(transaction_type=type_filter)
        
        # Filter by category if provided
        category_filter = self.request.query_params.get('category')
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        # Non-admins can only see their own submissions or approved transactions
        if user.role not in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            queryset = queryset.filter(
                Q(submitted_by=user) | Q(status=FinancialTransaction.Status.APPROVED)
            )
        
        return queryset.select_related('category', 'submitted_by', 'approved_by')
    
    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user, school=self.request.user.school)

class FinancialTransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FinancialTransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = FinancialTransaction.objects.all()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanApproveTransaction])
def approve_transaction(request, transaction_id):
    try:
        transaction = FinancialTransaction.objects.get(id=transaction_id)
        
        if transaction.status != FinancialTransaction.Status.PENDING:
            return Response(
                {'error': 'Transaction is not pending approval'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction.status = FinancialTransaction.Status.APPROVED
        transaction.approved_by = request.user
        transaction.approved_date = timezone.now().date()
        transaction.save()
        
        # Update related budget spent amount
        if transaction.transaction_type == FinancialTransaction.TransactionType.EXPENSE:
            budget = Budget.objects.filter(
                category=transaction.category,
                start_date__lte=transaction.transaction_date,
                end_date__gte=transaction.transaction_date,
                is_active=True
            ).first()
            
            if budget:
                budget.spent_amount = F('spent_amount') + transaction.amount
                budget.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action_type=AuditLog.ActionType.APPROVE,
            description=f"Approved transaction: {transaction.title}",
            transaction=transaction
        )
        
        return Response({'message': 'Transaction approved successfully'})
        
    except FinancialTransaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

# Budget Views
class BudgetListCreateView(generics.ListCreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageBudgets]
    
    def get_queryset(self):
        return Budget.objects.filter(school=self.request.user.school).select_related('category')
    
    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageBudgets]
    queryset = Budget.objects.all()

# Voting Issues Views
class VotingIssueListCreateView(generics.ListCreateAPIView):
    serializer_class = VotingIssueSerializer
    permission_classes = [permissions.IsAuthenticated, CanCreateVotingIssue]
    
    def get_queryset(self):
        user = self.request.user
        queryset = VotingIssue.objects.filter(school=user.school)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by type if provided
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(issue_type=type_filter)
        
        return queryset.select_related('created_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, school=self.request.user.school)

class VotingIssueDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VotingIssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = VotingIssue.objects.all()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanCreateVotingIssue])
def publish_voting_issue(request, issue_id):
    try:
        issue = VotingIssue.objects.get(id=issue_id)
        
        if issue.status != VotingIssue.Status.DRAFT:
            return Response(
                {'error': 'Only draft issues can be published'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        issue.status = VotingIssue.Status.OPEN
        issue.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action_type=AuditLog.ActionType.UPDATE,
            description=f"Published voting issue: {issue.title}",
            voting_issue=issue
        )
        
        return Response({'message': 'Voting issue published successfully'})
        
    except VotingIssue.DoesNotExist:
        return Response({'error': 'Voting issue not found'}, status=status.HTTP_404_NOT_FOUND)

# Vote Views
class VoteCreateView(generics.CreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated, CanVote]
    
    def perform_create(self, serializer):
        serializer.save(voter=self.request.user)

class UserVotesListView(generics.ListAPIView):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Vote.objects.filter(voter=self.request.user).select_related('issue')

# Financial Reports Views
class FinancialReportListCreateView(generics.ListCreateAPIView):
    serializer_class = FinancialReportSerializer
    permission_classes = [permissions.IsAuthenticated, CanGenerateReports]
    
    def get_queryset(self):
        user = self.request.user
        queryset = FinancialReport.objects.filter(school=user.school)
        
        # Non-admins can only see published reports
        if user.role not in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            queryset = queryset.filter(is_published=True)
        
        return queryset.select_related('generated_by')
    
    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user, school=self.request.user.school)

class FinancialReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FinancialReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = FinancialReport.objects.all()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanGenerateReports])
def publish_financial_report(request, report_id):
    try:
        report = FinancialReport.objects.get(id=report_id)
        
        if report.is_published:
            return Response(
                {'error': 'Report is already published'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report.is_published = True
        report.published_at = timezone.now()
        report.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action_type=AuditLog.ActionType.UPDATE,
            description=f"Published financial report: {report.title}",
            financial_report=report
        )
        
        return Response({'message': 'Financial report published successfully'})
        
    except FinancialReport.DoesNotExist:
        return Response({'error': 'Financial report not found'}, status=status.HTTP_404_NOT_FOUND)

# Comment Views
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolMember]
    
    def get_queryset(self):
        # Filter by object type and ID from query params
        object_type = self.request.query_params.get('object_type')
        object_id = self.request.query_params.get('object_id')
        
        if object_type and object_id:
            filter_kwargs = {f'{object_type.lower()}__id': object_id}
            return Comment.objects.filter(**filter_kwargs, is_approved=True).select_related('author')
        
        return Comment.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# Audit Log Views
class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewAuditLogs]
    
    def get_queryset(self):
        return AuditLog.objects.filter(
            user__school=self.request.user.school
        ).select_related('user').order_by('-created_at')

# Notification Subscription Views
class NotificationSubscriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = NotificationSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NotificationSubscription.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Dashboard Views
class TransparencyDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanViewFinancialData]
    
    def get(self, request):
        school = request.user.school
        user = request.user
        
        # Financial Overview
        current_year = timezone.now().year
        financial_data = FinancialTransaction.objects.filter(
            school=school,
            status=FinancialTransaction.Status.APPROVED,
            transaction_date__year=current_year
        ).aggregate(
            total_income=Sum('amount', filter=Q(transaction_type=FinancialTransaction.TransactionType.INCOME)),
            total_expenses=Sum('amount', filter=Q(transaction_type=FinancialTransaction.TransactionType.EXPENSE))
        )
        
        total_income = financial_data['total_income'] or 0
        total_expenses = financial_data['total_expenses'] or 0
        net_balance = total_income - total_expenses
        
        # Budget utilization
        active_budgets = Budget.objects.filter(school=school, is_active=True)
        total_allocated = sum(budget.allocated_amount for budget in active_budgets)
        total_spent = sum(budget.spent_amount for budget in active_budgets)
        budget_utilization = (total_spent / total_allocated * 100) if total_allocated > 0 else 0
        
        # Pending approvals
        pending_approvals = FinancialTransaction.objects.filter(
            school=school,
            status=FinancialTransaction.Status.PENDING
        ).count()
        
        financial_overview = FinancialOverviewSerializer({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
            'budget_utilization': budget_utilization,
            'pending_approvals': pending_approvals
        }).data
        
        # Voting Overview
        active_issues = VotingIssue.objects.filter(
            school=school,
            status=VotingIssue.Status.OPEN,
            voting_starts_at__lte=timezone.now(),
            voting_ends_at__gte=timezone.now()
        ).count()
        
        total_votes_cast = Vote.objects.filter(
            issue__school=school,
            created_at__year=current_year
        ).count()
        
        user_votes_cast = Vote.objects.filter(
            voter=user,
            created_at__year=current_year
        ).count()
        
        # Recent voting results
        recent_closed_issues = VotingIssue.objects.filter(
            school=school,
            status=VotingIssue.Status.CLOSED,
            results_published_at__isnull=False
        ).order_by('-results_published_at')[:3]
        
        recent_results = {}
        for issue in recent_closed_issues:
            results = {}
            for i, option in enumerate(issue.options):
                vote_count = issue.votes.filter(selected_option=i, is_abstained=False).count()
                results[option['text']] = vote_count
            
            recent_results[issue.title] = results
        
        voting_overview = VotingOverviewSerializer({
            'active_issues': active_issues,
            'total_votes_cast': total_votes_cast,
            'user_votes_cast': user_votes_cast,
            'recent_results': recent_results
        }).data
        
        # Recent transactions
        recent_transactions = FinancialTransactionSerializer(
            FinancialTransaction.objects.filter(
                school=school,
                status=FinancialTransaction.Status.APPROVED
            ).order_by('-transaction_date')[:5],
            many=True,
            context={'request': request}
        ).data
        
        # Recent reports
        recent_reports = FinancialReportSerializer(
            FinancialReport.objects.filter(
                school=school,
                is_published=True
            ).order_by('-created_at')[:3],
            many=True,
            context={'request': request}
        ).data
        
        return Response({
            'financial_overview': financial_overview,
            'voting_overview': voting_overview,
            'recent_transactions': recent_transactions,
            'recent_reports': recent_reports
        })

# Analytics Views
class FinancialAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanViewFinancialData]
    
    def get(self, request):
        school = request.user.school
        year = request.query_params.get('year', timezone.now().year)
        
        # Monthly breakdown
        monthly_data = []
        for month in range(1, 13):
            monthly_transactions = FinancialTransaction.objects.filter(
                school=school,
                status=FinancialTransaction.Status.APPROVED,
                transaction_date__year=year,
                transaction_date__month=month
            ).aggregate(
                income=Sum('amount', filter=Q(transaction_type=FinancialTransaction.TransactionType.INCOME)),
                expenses=Sum('amount', filter=Q(transaction_type=FinancialTransaction.TransactionType.EXPENSE))
            )
            
            monthly_data.append({
                'month': month,
                'income': monthly_transactions['income'] or 0,
                'expenses': monthly_transactions['expenses'] or 0,
                'net': (monthly_transactions['income'] or 0) - (monthly_transactions['expenses'] or 0)
            })
        
        # Category breakdown
        category_data = BudgetCategory.objects.filter(school=school).annotate(
            total_amount=Sum('transactions__amount', filter=Q(
                transactions__status=FinancialTransaction.Status.APPROVED,
                transactions__transaction_date__year=year
            ))
        ).values('name', 'total_amount')
        
        return Response({
            'monthly_breakdown': monthly_data,
            'category_breakdown': list(category_data)
        })