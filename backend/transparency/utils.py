from django.core.cache import cache
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from decimal import Decimal
from .models import Vote, Comment  

def get_financial_summary(school, start_date=None, end_date=None):
    # Get financial summary for a school
    cache_key = f"financial_summary_{school.id}_{start_date}_{end_date}"
    summary = cache.get(cache_key)
    
    if not summary:
        transactions = school.financial_transactions.filter(
            status='APPROVED'
        )
        
        if start_date:
            transactions = transactions.filter(transaction_date__gte=start_date)
        if end_date:
            transactions = transactions.filter(transaction_date__lte=end_date)
        
        income = transactions.filter(transaction_type='INCOME').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        expenses = transactions.filter(transaction_type='EXPENSE').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        summary = {
            'total_income': income,
            'total_expenses': expenses,
            'net_balance': income - expenses,
            'transaction_count': transactions.count()
        }
        cache.set(cache_key, summary, 3600) 
    
    return summary

def get_budget_utilization(school):
    # Get budget utilization statistics
    active_budgets = school.budgets.filter(is_active=True)
    
    if not active_budgets:
        return {'average_utilization': 0, 'over_budget_count': 0}
    
    total_utilization = sum(budget.utilization_percentage for budget in active_budgets)
    average_utilization = total_utilization / len(active_budgets)
    
    over_budget_count = sum(1 for budget in active_budgets if budget.utilization_percentage > 100)
    
    return {
        'average_utilization': average_utilization,
        'over_budget_count': over_budget_count,
        'total_budgets': len(active_budgets)
    }

def can_user_vote(user, voting_issue):
    # Check if a user can vote on a specific issue
    if user.school != voting_issue.school:
        return False
    
    if user.role not in voting_issue.eligible_roles:
        return False
    
    if not voting_issue.is_voting_active:
        return False
    
    # Check if user has already voted
    return not voting_issue.votes.filter(voter=user).exists()

def calculate_voting_results(voting_issue):
    # Calculate voting results for an issue
    votes = voting_issue.votes.all()
    total_votes = votes.count()
    
    if total_votes == 0:
        return {'error': 'No votes cast'}
    
    results = {}
    
    # Count votes for each option
    for i, option in enumerate(voting_issue.options):
        vote_count = votes.filter(selected_option=i, is_abstained=False).count()
        percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
        results[option['text']] = {
            'votes': vote_count,
            'percentage': round(percentage, 1)
        }
    
    # Count abstentions
    abstentions = votes.filter(is_abstained=True).count()
    abstention_percentage = (abstentions / total_votes * 100) if total_votes > 0 else 0
    results['abstentions'] = {
        'votes': abstentions,
        'percentage': round(abstention_percentage, 1)
    }
    
    # Determine winner based on voting method
    if voting_issue.voting_method == 'SIMPLE_MAJORITY':
        valid_votes = total_votes - abstentions
        if valid_votes > 0:
            winning_option = max(
                [(option, data['votes']) for option, data in results.items() if option != 'abstentions'],
                key=lambda x: x[1]
            )
            winning_percentage = (winning_option[1] / valid_votes * 100)
            
            results['winner'] = winning_option[0]
            results['winning_percentage'] = round(winning_percentage, 1)
            results['is_approved'] = winning_percentage >= voting_issue.min_approval_percentage
    
    return results

def format_currency(amount):
    # Format amount as currency
    return f"${amount:,.2f}"

def get_pending_approvals_count(school):
    # Get count of pending approvals
    return school.financial_transactions.filter(status='PENDING').count()

def get_recent_activity(school, days=7):
    # Get recent transparency activity
    since_date = timezone.now() - timedelta(days=days)
    
    activity = {
        'new_transactions': school.financial_transactions.filter(
            created_at__gte=since_date
        ).count(),
        'new_votes': Vote.objects.filter(
            issue__school=school,
            created_at__gte=since_date
        ).count(),
        'new_comments': Comment.objects.filter(
            created_at__gte=since_date,
            transaction__school=school
        ).count(),
        'published_reports': school.financial_reports.filter(
            published_at__gte=since_date
        ).count()
    }
    
    return activity

def validate_budget_period(start_date, end_date, period):
    # Validate budget period consistency
    if start_date >= end_date:
        return False, "End date must be after start date"
    
    if period == 'MONTHLY':
        expected_end = start_date + timedelta(days=30)
        if abs((end_date - start_date).days - 30) > 5:
            return False, "Monthly budget should be approximately 30 days"
    elif period == 'QUARTERLY':
        expected_end = start_date + timedelta(days=90)
        if abs((end_date - start_date).days - 90) > 10:
            return False, "Quarterly budget should be approximately 90 days"
    elif period == 'ANNUAL':
        expected_end = start_date + timedelta(days=365)
        if abs((end_date - start_date).days - 365) > 15:
            return False, "Annual budget should be approximately 365 days"
    
    return True, "Valid period"