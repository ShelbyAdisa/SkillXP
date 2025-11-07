from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import (
    FinancialTransaction, VotingIssue, Vote, FinancialReport,
    Comment, AuditLog, NotificationSubscription, Budget
)
from .tasks import check_budget_alerts, send_voting_reminders

@receiver(post_save, sender=FinancialTransaction)
def handle_transaction_creation(sender, instance, created, **kwargs):
    if created:
        # Create audit log
        AuditLog.objects.create(
            user=instance.submitted_by,
            action_type=AuditLog.ActionType.CREATE,
            description=f"Submitted transaction: {instance.title}",
            transaction=instance
        )
        
        # Notify approvers about new pending transaction
        if instance.status == FinancialTransaction.Status.PENDING:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            approvers = User.objects.filter(
                school=instance.school,
                role__in=[User.Role.ADMIN, User.Role.SCHOOL_ADMIN]
            )
            
            subject = f'New Transaction Pending Approval - {instance.title}'
            message = f'''
                        A new transaction requires your approval:
                        
                        Title: {instance.title}
                        Amount: ${instance.amount}
                        Category: {instance.category.name}
                        Submitted by: {instance.submitted_by.get_display_name()}
                        
                        Please review and approve in the transparency dashboard.
                        '''
            
            for approver in approvers:
                if approver.profile.email_notifications:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [approver.email],
                        fail_silently=True,
                    )

@receiver(pre_save, sender=FinancialTransaction)
def handle_transaction_approval(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = FinancialTransaction.objects.get(pk=instance.pk)
            
            # Check if status changed to APPROVED
            if (old_instance.status != FinancialTransaction.Status.APPROVED and 
                instance.status == FinancialTransaction.Status.APPROVED):
                
                # Check for budget alerts
                check_budget_alerts.delay(instance.id)
                
                # Notify subscriber about large transactions
                if instance.amount >= 1000:  
                    from .models import NotificationSubscription
                    subscribers = NotificationSubscription.objects.filter(
                        notification_type=NotificationSubscription.NotificationType.NEW_TRANSACTION,
                        is_active=True,
                        categories=instance.category
                    ).exclude(user=instance.submitted_by)
                    
                    for subscription in subscribers:
                        if (subscription.min_amount is None or 
                            instance.amount >= subscription.min_amount):
                            
                            subject = f'Large Transaction Approved - {instance.title}'
                            message = f'''
                                            A large transaction has been approved:
                                            
                                            Title: {instance.title}
                                            Amount: ${instance.amount}
                                            Category: {instance.category.name}
                                            Approved by: {instance.approved_by.get_display_name()}
                                            
                                            View details in the transparency dashboard.
                                         '''
                            
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

@receiver(post_save, sender=VotingIssue)
def handle_voting_issue_publish(sender, instance, **kwargs):
    if instance.status == VotingIssue.Status.OPEN:
        # Notify eligible voters
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        eligible_voters = User.objects.filter(
            school=instance.school,
            role__in=instance.eligible_roles
        )
        
        subject = f'New Voting Issue: {instance.title}'
        message = f'''
                        A new voting issue is now open:
                        
                        Title: {instance.title}
                        Description: {instance.description}
                        Voting Period: {instance.voting_starts_at.strftime("%b %d, %Y")} to {instance.voting_ends_at.strftime("%b %d, %Y")}
                        
                        Please cast your vote in the transparency dashboard.
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
        
        # Schedule voting reminder
        reminder_time = instance.voting_ends_at - timedelta(hours=24)
        send_voting_reminders.apply_async((instance.id,), eta=reminder_time)

@receiver(post_save, sender=Vote)
def handle_new_vote(sender, instance, created, **kwargs):
    if created:
        # Create audit log
        AuditLog.objects.create(
            user=instance.voter,
            action_type=AuditLog.ActionType.VOTE,
            description=f"Voted on issue: {instance.issue.title}",
            voting_issue=instance.issue
        )
        
        # Check if voting should close 
        if instance.issue.is_voting_active:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            total_eligible_voters = User.objects.filter(
                school=instance.issue.school,
                role__in=instance.issue.eligible_roles
            ).count()
            
            votes_cast = instance.issue.votes.count()
            
            # Auto-close if all eligible voters have voted
            if votes_cast >= total_eligible_voters:
                instance.issue.status = VotingIssue.Status.CLOSED
                instance.issue.results_published_at = timezone.now()
                instance.issue.save()

@receiver(post_save, sender=FinancialReport)
def handle_report_publish(sender, instance, **kwargs):
    if instance.is_published:
        # Notify subscribers
        from .models import NotificationSubscription
        subscribers = NotificationSubscription.objects.filter(
            notification_type=NotificationSubscription.NotificationType.NEW_REPORT,
            is_active=True
        )
        
        subject = f'New Financial Report Published: {instance.title}'
        message = f'''
                        A new financial report has been published:
                        
                        Title: {instance.title}
                        Report Type: {instance.get_report_type_display()}
                        Period: {instance.start_date.strftime("%b %d, %Y")} to {instance.end_date.strftime("%b %d, %Y")}
                        
                        View the report in the transparency dashboard.
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

@receiver(post_save, sender=Comment)
def handle_new_comment(sender, instance, created, **kwargs):
    if created:
        # Create audit log
        AuditLog.objects.create(
            user=instance.author,
            action_type=AuditLog.ActionType.COMMENT,
            description=f"Commented on {instance.comment_type}",
            **{instance.comment_type.lower(): instance.get_related_object()}
        )

# Budget monitoring signal
@receiver(post_save, sender=Budget)
def handle_budget_update(sender, instance, **kwargs):
    # Check for budget utilization alerts
    if instance.utilization_percentage >= 90:
        from .models import NotificationSubscription
        subscribers = NotificationSubscription.objects.filter(
            notification_type=NotificationSubscription.NotificationType.BUDGET_ALERT,
            is_active=True,
            categories=instance.category
        )
        
        subject = f'Budget Alert: {instance.name}'
        message = f'''
                        Budget utilization alert:
                        
                        Budget: {instance.name}
                        Category: {instance.category.name}
                        Allocated: ${instance.allocated_amount}
                        Spent: ${instance.spent_amount}
                        Utilization: {instance.utilization_percentage:.1f}%
                        
                        This budget is approaching its limit.
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