from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Q
import threading
import time

from .models import FinancialTransaction, Budget, VotingIssue, NotificationSubscription, AuditLog
from django.contrib.auth import get_user_model

User = get_user_model()

def check_budget_alerts(transaction_id):
    # Check for budget alerts after transaction approval - run in background thread
    def _check():
        try:
            transaction = FinancialTransaction.objects.get(id=transaction_id)
            
            if (transaction.transaction_type == FinancialTransaction.TransactionType.EXPENSE and
                transaction.status == FinancialTransaction.Status.APPROVED):
                
                # Find relevant budget
                budget = Budget.objects.filter(
                    category=transaction.category,
                    start_date__lte=transaction.transaction_date,
                    end_date__gte=transaction.transaction_date,
                    is_active=True
                ).first()
                
                if budget and budget.utilization_percentage >= 80:
                    # Notify budget managers
                    from .models import NotificationSubscription
                    subscribers = NotificationSubscription.objects.filter(
                        notification_type=NotificationSubscription.NotificationType.BUDGET_ALERT,
                        is_active=True,
                        categories=budget.category
                    )
                    
                    subject = f'Budget Utilization Alert: {budget.name}'
                    message = f'''
                                    Budget utilization alert triggered by recent transaction:
                                    
                                    Budget: {budget.name}
                                    Category: {budget.category.name}
                                    Utilization: {budget.utilization_percentage:.1f}%
                                    Recent Transaction: {transaction.title} (${transaction.amount})
                                    
                                    Allocated: ${budget.allocated_amount}
                                    Spent: ${budget.spent_amount}
                                    Remaining: ${budget.remaining_amount}
                                '''
                    
                    for subscription in subscribers:
                        if subscription.user.profile.email_notifications:
                            send_mail(
                                subject,
                                message,
                                settings.DEFAULT_FROM_EMAIL,
                                [subscription.user.email],
                                fail_silently=True,
                            )
                            
        except FinancialTransaction.DoesNotExist:
            pass
    
    thread = threading.Thread(target=_check)
    thread.daemon = True
    thread.start()

def send_voting_reminders(issue_id):
    # Send voting reminders to users who haven't voted - run in background thread
    def _send_reminders():
        try:
            issue = VotingIssue.objects.get(id=issue_id)
            
            if not issue.is_voting_active:
                return
            
            # Find users who haven't voted
            voters_who_voted = set(issue.votes.values_list('voter_id', flat=True))
            eligible_voters = User.objects.filter(
                school=issue.school,
                role__in=issue.eligible_roles
            ).exclude(id__in=voters_who_voted)
            
            subject = f'Voting Reminder: {issue.title}'
            message = f'''
                            Reminder: Voting ends soon!
                            
                            Issue: {issue.title}
                            Description: {issue.description}
                            Voting Ends: {issue.voting_ends_at.strftime("%b %d, %Y at %I:%M %p")}
                            
                            You haven't cast your vote yet. Please vote before the deadline.
                        '''
            
            for voter in eligible_voters:
                if voter.profile.email_notifications:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [voter.email],
                        fail_silently=True,
                    )
                    
        except VotingIssue.DoesNotExist:
            pass
    
    thread = threading.Thread(target=_send_reminders)
    thread.daemon = True
    thread.start()

def generate_monthly_financial_report():
    # Generate monthly financial report - run as scheduled task
    from .models import FinancialReport
    
    last_month = timezone.now() - timedelta(days=30)
    start_date = last_month.replace(day=1)
    end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    for school in User.objects.values_list('school', flat=True).distinct():
        # Calculate financial data
        transactions = FinancialTransaction.objects.filter(
            school=school,
            status=FinancialTransaction.Status.APPROVED,
            transaction_date__range=[start_date, end_date]
        )
        
        income = transactions.filter(
            transaction_type=FinancialTransaction.TransactionType.INCOME
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expenses = transactions.filter(
            transaction_type=FinancialTransaction.TransactionType.EXPENSE
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Category breakdown
        categories = {}
        for transaction in transactions:
            category_name = transaction.category.name
            if category_name not in categories:
                categories[category_name] = {'income': 0, 'expenses': 0}
            
            if transaction.transaction_type == FinancialTransaction.TransactionType.INCOME:
                categories[category_name]['income'] += transaction.amount
            else:
                categories[category_name]['expenses'] += transaction.amount
        
        report_data = {
            'summary': {
                'total_income': float(income),
                'total_expenses': float(expenses),
                'net_balance': float(income - expenses)
            },
            'category_breakdown': categories,
            'transaction_count': transactions.count()
        }
        
        # Create report
        admin_user = User.objects.filter(
            school=school,
            role__in=[User.Role.ADMIN, User.Role.SCHOOL_ADMIN]
        ).first()
        
        if admin_user:
            report = FinancialReport.objects.create(
                school_id=school,
                title=f'Monthly Financial Report - {start_date.strftime("%B %Y")}',
                report_type=FinancialReport.ReportType.MONTHLY,
                description=f'Automated monthly financial report for {start_date.strftime("%B %Y")}',
                report_data=report_data,
                start_date=start_date,
                end_date=end_date,
                generated_by=admin_user,
                is_published=True,
                published_at=timezone.now()
            )
            
            print(f"Generated monthly report for school {school}: {report.title}")

def close_expired_voting_issues():
    # Close voting issues that have passed their end date - run as scheduled task
    expired_issues = VotingIssue.objects.filter(
        status=VotingIssue.Status.OPEN,
        voting_ends_at__lt=timezone.now()
    )
    
    for issue in expired_issues:
        issue.status = VotingIssue.Status.CLOSED
        issue.results_published_at = timezone.now()
        issue.save()
        
        print(f"Closed expired voting issue: {issue.title}")

def cleanup_old_data():
    # Clean up old data - run as scheduled task
    # Archive transactions older than 3 years
    archive_threshold = timezone.now() - timedelta(days=3*365)
    old_transactions = FinancialTransaction.objects.filter(
        transaction_date__lt=archive_threshold
    )
    archived_count = old_transactions.count()
    # In practice, you might move these to an archive table
    
    # Delete very old audit logs
    delete_threshold = timezone.now() - timedelta(days=365)
    deleted_logs = AuditLog.objects.filter(
        created_at__lt=delete_threshold
    ).delete()
    
    print(f"Archived {archived_count} old transactions")
    print(f"Deleted {deleted_logs[0]} old audit logs")

def calculate_voting_results():
    # Calculate and update voting results - run as scheduled task
    closed_issues = VotingIssue.objects.filter(
        status=VotingIssue.Status.CLOSED,
        results_published_at__isnull=True
    )
    
    for issue in closed_issues:
        # Calculate results
        total_votes = issue.votes.count()
        option_counts = {}
        
        for i, option in enumerate(issue.options):
            vote_count = issue.votes.filter(selected_option=i, is_abstained=False).count()
            option_counts[option['text']] = vote_count
        
        abstentions = issue.votes.filter(is_abstained=True).count()
        
        # Determine outcome based on voting method
        if issue.voting_method == VotingIssue.VotingMethod.SIMPLE_MAJORITY:
            max_votes = max(option_counts.values()) if option_counts else 0
            winning_percentage = (max_votes / total_votes * 100) if total_votes > 0 else 0
            
            if winning_percentage >= issue.min_approval_percentage:
                issue.status = VotingIssue.Status.APPROVED
            else:
                issue.status = VotingIssue.Status.REJECTED
        
        issue.results_published_at = timezone.now()
        issue.save()
        
        print(f"Calculated results for voting issue: {issue.title}")

# Management command for scheduled tasks
def run_scheduled_transparency_tasks():
    """Run all scheduled transparency tasks"""
    print("Running scheduled transparency tasks...")
    
    # Generate monthly reports
    if timezone.now().day == 1:
        generate_monthly_financial_report()
    
    # Close expired voting issues
    close_expired_voting_issues()
    
    # Calculate voting results
    calculate_voting_results()
    
    # Cleanup old data 
    if timezone.now().day == 15:
        cleanup_old_data()
    
    print("Scheduled transparency tasks completed!")