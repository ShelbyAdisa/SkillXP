from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    BudgetCategory, FinancialTransaction, Budget, VotingIssue,
    Vote, FinancialReport, Comment, AuditLog, NotificationSubscription
)

User = get_user_model()

class BudgetCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    transaction_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = BudgetCategory
        fields = [
            'id', 'name', 'description', 'school', 'parent_category',
            'color', 'icon', 'subcategories', 'transaction_count', 'total_amount'
        ]
        read_only_fields = ['school']
    
    def get_subcategories(self, obj):
        return BudgetCategorySerializer(
            obj.subcategories.all(), many=True, context=self.context
        ).data
    
    def get_transaction_count(self, obj):
        return obj.transactions.count()
    
    def get_total_amount(self, obj):
        return sum(t.amount for t in obj.transactions.filter(status=FinancialTransaction.Status.APPROVED))

class FinancialTransactionSerializer(serializers.ModelSerializer):
    submitted_by_display_name = serializers.CharField(source='submitted_by.get_display_name', read_only=True)
    approved_by_display_name = serializers.CharField(source='approved_by.get_display_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialTransaction
        fields = [
            'id', 'school', 'category', 'category_name', 'title', 'description',
            'amount', 'transaction_type', 'status', 'transaction_date', 'due_date',
            'approved_date', 'submitted_by', 'submitted_by_display_name',
            'approved_by', 'approved_by_display_name', 'invoice_number',
            'vendor_name', 'supporting_docs', 'comments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['school', 'submitted_by', 'approved_by', 'approved_date', 'created_at', 'updated_at']
    
    def get_comments_count(self, obj):
        return obj.comment_set.count()
    
    def create(self, validated_data):
        validated_data['submitted_by'] = self.context['request'].user
        validated_data['school'] = self.context['request'].user.school
        return super().create(validated_data)

class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    remaining_amount = serializers.ReadOnlyField()
    utilization_percentage = serializers.ReadOnlyField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = [
            'id', 'school', 'category', 'category_name', 'name', 'description',
            'period', 'allocated_amount', 'spent_amount', 'remaining_amount',
            'utilization_percentage', 'start_date', 'end_date', 'is_active',
            'comments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['school', 'spent_amount', 'created_at', 'updated_at']
    
    def get_comments_count(self, obj):
        return obj.comment_set.count()
    
    def create(self, validated_data):
        validated_data['school'] = self.context['request'].user.school
        return super().create(validated_data)

class VotingIssueSerializer(serializers.ModelSerializer):
    created_by_display_name = serializers.CharField(source='created_by.get_display_name', read_only=True)
    is_voting_active = serializers.ReadOnlyField()
    user_has_voted = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    vote_results = serializers.SerializerMethodField()
    
    class Meta:
        model = VotingIssue
        fields = [
            'id', 'school', 'title', 'description', 'issue_type', 'voting_method',
            'status', 'options', 'allow_abstain', 'min_approval_percentage',
            'voting_starts_at', 'voting_ends_at', 'results_published_at',
            'eligible_roles', 'created_by', 'created_by_display_name',
            'total_votes', 'is_voting_active', 'user_has_voted', 'user_vote',
            'vote_results', 'created_at', 'updated_at'
        ]
        read_only_fields = ['school', 'created_by', 'total_votes', 'created_at', 'updated_at']
    
    def get_user_has_voted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.votes.filter(voter=request.user).exists()
        return False
    
    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(voter=request.user).first()
            if vote:
                return {
                    'selected_option': vote.selected_option,
                    'is_abstained': vote.is_abstained,
                    'comments': vote.comments
                }
        return None
    
    def get_vote_results(self, obj):
        # Only show results if voting is closed and results are published
        if obj.status != VotingIssue.Status.CLOSED or not obj.results_published_at:
            return None
        
        results = {}
        for i, option in enumerate(obj.options):
            vote_count = obj.votes.filter(selected_option=i, is_abstained=False).count()
            results[option['text']] = {
                'votes': vote_count,
                'percentage': (vote_count / obj.total_votes * 100) if obj.total_votes > 0 else 0
            }
        
        abstentions = obj.votes.filter(is_abstained=True).count()
        results['abstentions'] = {
            'votes': abstentions,
            'percentage': (abstentions / obj.total_votes * 100) if obj.total_votes > 0 else 0
        }
        
        return results
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['school'] = self.context['request'].user.school
        return super().create(validated_data)

class VoteSerializer(serializers.ModelSerializer):
    voter_display_name = serializers.CharField(source='voter.get_display_name', read_only=True)
    
    class Meta:
        model = Vote
        fields = [
            'id', 'issue', 'voter', 'voter_display_name', 'selected_option',
            'is_abstained', 'comments', 'ranked_choices', 'created_at'
        ]
        read_only_fields = ['voter', 'created_at']
    
    def validate(self, attrs):
        issue = attrs['issue']
        voter = self.context['request'].user
        
        # Check if voting is active
        if not issue.is_voting_active:
            raise serializers.ValidationError("Voting is not active for this issue.")
        
        # Check if user is eligible to vote
        if voter.role not in issue.eligible_roles:
            raise serializers.ValidationError("You are not eligible to vote on this issue.")
        
        # Check if user has already voted
        if Vote.objects.filter(issue=issue, voter=voter).exists():
            raise serializers.ValidationError("You have already voted on this issue.")
        
        # Validate selected option
        if not attrs.get('is_abstained', False):
            selected_option = attrs.get('selected_option')
            if selected_option is None or selected_option < 0 or selected_option >= len(issue.options):
                raise serializers.ValidationError("Invalid option selected.")
        
        return attrs
    
    def create(self, validated_data):
        validated_data['voter'] = self.context['request'].user
        
        # Update issue vote count
        issue = validated_data['issue']
        issue.total_votes += 1
        issue.save()
        
        return super().create(validated_data)

class FinancialReportSerializer(serializers.ModelSerializer):
    generated_by_display_name = serializers.CharField(source='generated_by.get_display_name', read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialReport
        fields = [
            'id', 'school', 'title', 'report_type', 'description',
            'report_data', 'report_file', 'start_date', 'end_date',
            'is_published', 'published_at', 'generated_by',
            'generated_by_display_name', 'comments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['school', 'generated_by', 'created_at', 'updated_at']
    
    def get_comments_count(self, obj):
        return obj.comment_set.count()
    
    def create(self, validated_data):
        validated_data['generated_by'] = self.context['request'].user
        validated_data['school'] = self.context['request'].user.school
        return super().create(validated_data)

class CommentSerializer(serializers.ModelSerializer):
    author_display_name = serializers.CharField(source='author.get_display_name', read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'author_display_name', 'content', 'comment_type',
            'transaction', 'budget', 'voting_issue', 'financial_report',
            'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        # Ensure only one related object is set
        related_objects = [
            attrs.get('transaction'),
            attrs.get('budget'),
            attrs.get('voting_issue'),
            attrs.get('financial_report')
        ]
        
        if sum(1 for obj in related_objects if obj is not None) != 1:
            raise serializers.ValidationError("Exactly one related object must be specified.")
        
        return attrs
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class AuditLogSerializer(serializers.ModelSerializer):
    user_display_name = serializers.CharField(source='user.get_display_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_display_name', 'action_type', 'description',
            'transaction', 'budget', 'voting_issue', 'financial_report',
            'changes', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['created_at']

class NotificationSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSubscription
        fields = [
            'id', 'user', 'notification_type', 'is_active',
            'categories', 'min_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

# Dashboard Serializers
class FinancialOverviewSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    budget_utilization = serializers.FloatField()
    pending_approvals = serializers.IntegerField()

class VotingOverviewSerializer(serializers.Serializer):
    active_issues = serializers.IntegerField()
    total_votes_cast = serializers.IntegerField()
    user_votes_cast = serializers.IntegerField()
    recent_results = serializers.DictField()