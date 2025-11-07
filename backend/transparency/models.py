from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class BudgetCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    school = models.ForeignKey('users.School', on_delete=models.CASCADE, related_name='budget_categories')
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    color = models.CharField(max_length=7, default='#3B82F6')  
    icon = models.CharField(max_length=50, default='folder')  
    
    class Meta:
        db_table = 'budget_categories'
        verbose_name_plural = 'Budget Categories'
        unique_together = ['name', 'school']
    
    def __str__(self):
        return f"{self.name} ({self.school.name})"

class FinancialTransaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = 'INCOME', 'Income'
        EXPENSE = 'EXPENSE', 'Expense'
        TRANSFER = 'TRANSFER', 'Transfer'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        PAID = 'PAID', 'Paid'

    school = models.ForeignKey('users.School', on_delete=models.CASCADE, related_name='financial_transactions')
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, related_name='transactions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    
    # Dates
    transaction_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    
    # Approval workflow
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_transactions')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_transactions')
    
    # Supporting documents
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    vendor_name = models.CharField(max_length=200, blank=True, null=True)
    supporting_docs = models.FileField(upload_to='transparency/documents/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financial_transactions'
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.title} - ${self.amount} ({self.get_transaction_type_display()})"

class Budget(models.Model):
    class BudgetPeriod(models.TextChoices):
        MONTHLY = 'MONTHLY', 'Monthly'
        QUARTERLY = 'QUARTERLY', 'Quarterly'
        ANNUAL = 'ANNUAL', 'Annual'

    school = models.ForeignKey('users.School', on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    period = models.CharField(max_length=10, choices=BudgetPeriod.choices, default=BudgetPeriod.ANNUAL)
    
    # Budget amounts
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'budgets'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} - ${self.allocated_amount} ({self.period})"
    
    @property
    def remaining_amount(self):
        return self.allocated_amount - self.spent_amount
    
    @property
    def utilization_percentage(self):
        if self.allocated_amount > 0:
            return (self.spent_amount / self.allocated_amount) * 100
        return 0

class VotingIssue(models.Model):
    class IssueType(models.TextChoices):
        BUDGET_ALLOCATION = 'BUDGET_ALLOCATION', 'Budget Allocation'
        POLICY_CHANGE = 'POLICY_CHANGE', 'Policy Change'
        SCHOOL_IMPROVEMENT = 'SCHOOL_IMPROVEMENT', 'School Improvement'
        EVENT_PLANNING = 'EVENT_PLANNING', 'Event Planning'
        OTHER = 'OTHER', 'Other'

    class VotingMethod(models.TextChoices):
        SIMPLE_MAJORITY = 'SIMPLE_MAJORITY', 'Simple Majority'
        TWO_THIRDS = 'TWO_THIRDS', 'Two-Thirds Majority'
        CONSENSUS = 'CONSENSUS', 'Consensus'
        RANKED_CHOICE = 'RANKED_CHOICE', 'Ranked Choice'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        OPEN = 'OPEN', 'Open for Voting'
        CLOSED = 'CLOSED', 'Voting Closed'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    school = models.ForeignKey('users.School', on_delete=models.CASCADE, related_name='voting_issues')
    title = models.CharField(max_length=200)
    description = models.TextField()
    issue_type = models.CharField(max_length=20, choices=IssueType.choices)
    voting_method = models.CharField(max_length=20, choices=VotingMethod.choices, default=VotingMethod.SIMPLE_MAJORITY)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    
    # Voting parameters
    options = models.JSONField(default=list)  
    allow_abstain = models.BooleanField(default=True)
    min_approval_percentage = models.IntegerField(default=51, validators=[MinValueValidator(1), MaxValueValidator(100)])
    
    # Dates
    voting_starts_at = models.DateTimeField()
    voting_ends_at = models.DateTimeField()
    results_published_at = models.DateTimeField(null=True, blank=True)
    
    # Eligibility
    eligible_roles = models.JSONField(default=list) 
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_voting_issues')
    total_votes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'voting_issues'
        ordering = ['-voting_starts_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    @property
    def is_voting_active(self):
        now = timezone.now()
        return self.status == self.Status.OPEN and self.voting_starts_at <= now <= self.voting_ends_at

class Vote(models.Model):
    issue = models.ForeignKey(VotingIssue, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transparency_votes')
    selected_option = models.IntegerField()  
    is_abstained = models.BooleanField(default=False)
    comments = models.TextField(blank=True)
    
    # For ranked choice voting
    ranked_choices = models.JSONField(default=list, blank=True) 
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'transparency_votes'
        unique_together = ['issue', 'voter']
    
    def __str__(self):
        if self.is_abstained:
            return f"Abstained by {self.voter.get_display_name()} on {self.issue.title}"
        return f"Vote by {self.voter.get_display_name()} on {self.issue.title}"

class FinancialReport(models.Model):
    class ReportType(models.TextChoices):
        MONTHLY = 'MONTHLY', 'Monthly Financial Report'
        QUARTERLY = 'QUARTERLY', 'Quarterly Financial Report'
        ANNUAL = 'ANNUAL', 'Annual Financial Report'
        BUDGET_VS_ACTUAL = 'BUDGET_VS_ACTUAL', 'Budget vs Actual'
        SPECIAL = 'SPECIAL', 'Special Report'

    school = models.ForeignKey('users.School', on_delete=models.CASCADE, related_name='financial_reports')
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    description = models.TextField(blank=True)
    
    # Report data (could be generated or uploaded)
    report_data = models.JSONField(default=dict)  
    report_file = models.FileField(upload_to='transparency/reports/', blank=True, null=True)
    
    # Period covered
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Publication status
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financial_reports'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"

class Comment(models.Model):
    class CommentType(models.TextChoices):
        TRANSACTION = 'TRANSACTION', 'Transaction'
        BUDGET = 'BUDGET', 'Budget'
        VOTING_ISSUE = 'VOTING_ISSUE', 'Voting Issue'
        FINANCIAL_REPORT = 'FINANCIAL_REPORT', 'Financial Report'

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transparency_comments')
    content = models.TextField()
    comment_type = models.CharField(max_length=20, choices=CommentType.choices)
    
    # Polymorphic relationship
    transaction = models.ForeignKey(FinancialTransaction, on_delete=models.CASCADE, null=True, blank=True)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True, blank=True)
    voting_issue = models.ForeignKey(VotingIssue, on_delete=models.CASCADE, null=True, blank=True)
    financial_report = models.ForeignKey(FinancialReport, on_delete=models.CASCADE, null=True, blank=True)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transparency_comments'
        ordering = ['created_at']

class AuditLog(models.Model):
    class ActionType(models.TextChoices):
        CREATE = 'CREATE', 'Create'
        UPDATE = 'UPDATE', 'Update'
        DELETE = 'DELETE', 'Delete'
        APPROVE = 'APPROVE', 'Approve'
        REJECT = 'REJECT', 'Reject'
        VOTE = 'VOTE', 'Vote'
        COMMENT = 'COMMENT', 'Comment'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transparency_audit_logs')
    action_type = models.CharField(max_length=10, choices=ActionType.choices)
    description = models.TextField()
    
    # Related objects
    transaction = models.ForeignKey(FinancialTransaction, on_delete=models.CASCADE, null=True, blank=True)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True, blank=True)
    voting_issue = models.ForeignKey(VotingIssue, on_delete=models.CASCADE, null=True, blank=True)
    financial_report = models.ForeignKey(FinancialReport, on_delete=models.CASCADE, null=True, blank=True)
    
    # Changes (for updates)
    changes = models.JSONField(default=dict, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']

class NotificationSubscription(models.Model):
    class NotificationType(models.TextChoices):
        NEW_TRANSACTION = 'NEW_TRANSACTION', 'New Transaction'
        BUDGET_ALERT = 'BUDGET_ALERT', 'Budget Alert'
        VOTING_START = 'VOTING_START', 'Voting Started'
        VOTING_END = 'VOTING_END', 'Voting Ended'
        NEW_REPORT = 'NEW_REPORT', 'New Financial Report'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transparency_subscriptions')
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    is_active = models.BooleanField(default=True)
    
    # Filters
    categories = models.ManyToManyField(BudgetCategory, blank=True)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_subscriptions'
        unique_together = ['user', 'notification_type']