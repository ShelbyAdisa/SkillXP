from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Community, CommunityMembership, Post, Comment, Vote,
    DirectMessage, MessageThread, Notification, UserFollow,
    Bookmark, Report, TrendingTopic
)

User = get_user_model()

class CommunitySerializer(serializers.ModelSerializer):
    member_count = serializers.ReadOnlyField()
    post_count = serializers.ReadOnlyField()
    is_member = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = [
            'id', 'name', 'description', 'community_type', 'school',
            'is_public', 'requires_approval', 'member_count', 'post_count',
            'is_member', 'user_role', 'created_at', 'updated_at'
        ]
        read_only_fields = ['school', 'member_count', 'post_count', 'created_at', 'updated_at']
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.memberships.filter(user=request.user, is_approved=True).exists()
        return False
    
    def get_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = obj.memberships.filter(user=request.user, is_approved=True).first()
            return membership.role if membership else None
        return None

class CommunityMembershipSerializer(serializers.ModelSerializer):
    user_display_name = serializers.CharField(source='user.get_display_name', read_only=True)
    community_name = serializers.CharField(source='community.name', read_only=True)
    
    class Meta:
        model = CommunityMembership
        fields = [
            'id', 'community', 'user', 'user_display_name', 'community_name',
            'role', 'is_approved', 'joined_at'
        ]
        read_only_fields = ['joined_at']

class PostSerializer(serializers.ModelSerializer):
    author_display_name = serializers.CharField(source='author.get_display_name', read_only=True)
    community_name = serializers.CharField(source='community.name', read_only=True)
    user_vote = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    comment_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'post_type', 'status', 'community',
            'author_display_name', 'community_name', 'is_anonymous',
            'upvotes', 'downvotes', 'view_count', 'comment_count', 'share_count',
            'poll_question', 'poll_options', 'poll_ends_at', 'is_pinned', 'is_locked',
            'user_vote', 'is_bookmarked', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'author', 'upvotes', 'downvotes', 'view_count', 'comment_count',
            'share_count', 'created_at', 'updated_at'
        ]
    
    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            return vote.vote_type if vote else None
        return None
    
    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarked_by.filter(user=request.user).exists()
        return False
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class CommentSerializer(serializers.ModelSerializer):
    author_display_name = serializers.CharField(source='author.get_display_name', read_only=True)
    user_vote = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'parent_comment', 'content', 'author_display_name',
            'is_anonymous', 'upvotes', 'downvotes', 'is_removed',
            'user_vote', 'reply_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'upvotes', 'downvotes', 'created_at', 'updated_at']
    
    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            return vote.vote_type if vote else None
        return None
    
    def get_reply_count(self, obj):
        return obj.replies.count()
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'post', 'comment', 'vote_type', 'created_at']
        read_only_fields = ['user', 'created_at']

class DirectMessageSerializer(serializers.ModelSerializer):
    sender_display_name = serializers.CharField(source='sender.get_display_name', read_only=True)
    receiver_display_name = serializers.CharField(source='receiver.get_display_name', read_only=True)
    
    class Meta:
        model = DirectMessage
        fields = [
            'id', 'sender', 'receiver', 'sender_display_name', 'receiver_display_name',
            'content', 'is_read', 'read_at', 'is_flagged', 'created_at'
        ]
        read_only_fields = ['sender', 'is_read', 'read_at', 'created_at']

class MessageThreadSerializer(serializers.ModelSerializer):
    participants_info = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MessageThread
        fields = [
            'id', 'participants', 'participants_info', 'last_message',
            'last_message_preview', 'unread_count', 'last_activity', 'created_at'
        ]
    
    def get_participants_info(self, obj):
        return [
            {
                'id': user.id,
                'display_name': user.get_display_name(),
                'role': user.role
            }
            for user in obj.participants.all()
        ]
    
    def get_last_message_preview(self, obj):
        if obj.last_message:
            return obj.last_message.content[:100] + '...' if len(obj.last_message.content) > 100 else obj.last_message.content
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.directmessage_set.filter(receiver=request.user, is_read=False).count()
        return 0

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'post', 'comment', 'community', 'is_read', 'is_sent', 'created_at'
        ]
        read_only_fields = ['created_at']

class UserFollowSerializer(serializers.ModelSerializer):
    follower_display_name = serializers.CharField(source='follower.get_display_name', read_only=True)
    followed_display_name = serializers.CharField(source='followed.get_display_name', read_only=True)
    
    class Meta:
        model = UserFollow
        fields = ['id', 'follower', 'followed', 'follower_display_name', 'followed_display_name', 'created_at']
        read_only_fields = ['created_at']

class BookmarkSerializer(serializers.ModelSerializer):
    post_details = PostSerializer(source='post', read_only=True)
    
    class Meta:
        model = Bookmark
        fields = ['id', 'post', 'post_details', 'created_at']
        read_only_fields = ['user', 'created_at']

class ReportSerializer(serializers.ModelSerializer):
    reporter_display_name = serializers.CharField(source='reporter.get_display_name', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'reporter', 'reporter_display_name', 'post', 'comment', 'message',
            'report_type', 'description', 'is_resolved', 'created_at'
        ]
        read_only_fields = ['reporter', 'created_at']

class TrendingTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendingTopic
        fields = ['id', 'name', 'school', 'post_count', 'score', 'created_at']
        read_only_fields = ['post_count', 'score', 'created_at']