from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    WellbeingPost, PostComment, PostReaction, SupportTicket, TicketMessage,
    CounselorAssignment, WellbeingResource, MoodCheck, WellbeingGoal,
    CrisisAlert, ContentReport, ModerationAction
)

User = get_user_model()

class WellbeingPostSerializer(serializers.ModelSerializer):
    author_display_name = serializers.CharField(source='author.get_display_name', read_only=True)
    comment_count = serializers.SerializerMethodField()
    user_has_reacted = serializers.SerializerMethodField()
    
    class Meta:
        model = WellbeingPost
        fields = [
            'id', 'title', 'content', 'post_type', 'is_anonymous', 'is_approved',
            'is_urgent', 'upvotes', 'view_count', 'author_display_name',
            'comment_count', 'user_has_reacted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'upvotes', 'view_count', 'created_at', 'updated_at']
    
    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()
    
    def get_user_has_reacted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.reactions.filter(user=request.user).exists()
        return False
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class PostCommentSerializer(serializers.ModelSerializer):
    author_display_name = serializers.CharField(source='author.get_display_name', read_only=True)
    
    class Meta:
        model = PostComment
        fields = [
            'id', 'post', 'content', 'is_anonymous', 'is_approved',
            'author_display_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ['id', 'post', 'reaction_type', 'created_at']
        read_only_fields = ['user', 'created_at']

class SupportTicketSerializer(serializers.ModelSerializer):
    student_display_name = serializers.CharField(source='student.get_display_name', read_only=True)
    counselor_display_name = serializers.CharField(source='counselor.get_display_name', read_only=True)
    message_count = serializers.SerializerMethodField()
    unread_messages = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'is_anonymous',
            'student_display_name', 'counselor_display_name', 'message_count',
            'unread_messages', 'created_at', 'updated_at', 'resolved_at'
        ]
        read_only_fields = ['student', 'counselor', 'created_at', 'updated_at', 'resolved_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_unread_messages(self, obj):
        # Implementation depends on your read status tracking
        return 0
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)

class TicketMessageSerializer(serializers.ModelSerializer):
    sender_display_name = serializers.CharField(source='sender.get_display_name', read_only=True)
    
    class Meta:
        model = TicketMessage
        fields = [
            'id', 'ticket', 'content', 'is_counselor_response',
            'sender_display_name', 'created_at'
        ]
        read_only_fields = ['sender', 'created_at']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        ticket = validated_data['ticket']
        
        # Auto-assign counselor if this is the first counselor response
        if (not ticket.counselor and 
            self.context['request'].user.role in [User.Role.TEACHER, User.Role.ADMIN]):
            ticket.counselor = self.context['request'].user
            ticket.save()
        
        # Mark as counselor response if sender is teacher/admin
        if self.context['request'].user.role in [User.Role.TEACHER, User.Role.ADMIN]:
            validated_data['is_counselor_response'] = True
        
        return super().create(validated_data)

class CounselorAssignmentSerializer(serializers.ModelSerializer):
    counselor_display_name = serializers.CharField(source='counselor.get_display_name', read_only=True)
    student_display_name = serializers.CharField(source='student.get_display_name', read_only=True)
    
    class Meta:
        model = CounselorAssignment
        fields = [
            'id', 'counselor', 'student', 'counselor_display_name',
            'student_display_name', 'is_active', 'assigned_at'
        ]

class WellbeingResourceSerializer(serializers.ModelSerializer):
    created_by_display_name = serializers.CharField(source='created_by.get_display_name', read_only=True)
    
    class Meta:
        model = WellbeingResource
        fields = [
            'id', 'title', 'description', 'resource_type', 'content_url',
            'content_file', 'target_roles', 'tags', 'is_published',
            'created_by_display_name', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']

class MoodCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodCheck
        fields = ['id', 'mood_level', 'notes', 'factors', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class WellbeingGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellbeingGoal
        fields = [
            'id', 'title', 'description', 'target_date', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class CrisisAlertSerializer(serializers.ModelSerializer):
    reported_by_display_name = serializers.CharField(source='reported_by.get_display_name', read_only=True)
    assigned_counselor_display_name = serializers.CharField(source='assigned_counselor.get_display_name', read_only=True)
    
    class Meta:
        model = CrisisAlert
        fields = [
            'id', 'reported_by', 'post', 'ticket', 'description', 'severity_level',
            'status', 'assigned_counselor', 'reported_by_display_name',
            'assigned_counselor_display_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['reported_by', 'created_at', 'updated_at']

class ContentReportSerializer(serializers.ModelSerializer):
    reporter_display_name = serializers.CharField(source='reporter.get_display_name', read_only=True)
    
    class Meta:
        model = ContentReport
        fields = [
            'id', 'reporter', 'post', 'comment', 'report_type', 'description',
            'is_resolved', 'reporter_display_name', 'created_at'
        ]
        read_only_fields = ['reporter', 'created_at']

class ModerationActionSerializer(serializers.ModelSerializer):
    moderator_display_name = serializers.CharField(source='moderator.get_display_name', read_only=True)
    target_user_display_name = serializers.CharField(source='target_user.get_display_name', read_only=True)
    
    class Meta:
        model = ModerationAction
        fields = [
            'id', 'moderator', 'target_user', 'action_type', 'reason',
            'post', 'comment', 'moderator_display_name', 'target_user_display_name',
            'created_at'
        ]
        read_only_fields = ['moderator', 'created_at']