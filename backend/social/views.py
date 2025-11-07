from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, F, ExpressionWrapper, FloatField
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from .models import (
    Community, CommunityMembership, Post, Comment, Vote,
    DirectMessage, MessageThread, Notification, UserFollow,
    Bookmark, Report, TrendingTopic
)
from .serializers import (
    CommunitySerializer, CommunityMembershipSerializer, PostSerializer,
    CommentSerializer, VoteSerializer, DirectMessageSerializer,
    MessageThreadSerializer, NotificationSerializer, UserFollowSerializer,
    BookmarkSerializer, ReportSerializer, TrendingTopicSerializer
)
from .permissions import (
    IsSchoolMember, CanPostInCommunity, IsCommunityModerator,
    IsOwnerOrModerator, CanMessageUser, CanViewCommunity, CanModerateContent
)

User = get_user_model()

# Community Views
class CommunityListCreateView(generics.ListCreateAPIView):
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Community.objects.filter(school=user.school)
        
        # Filter by type if provided
        community_type = self.request.query_params.get('type')
        if community_type:
            queryset = queryset.filter(community_type=community_type)
        
        # For non-public communities, only show if user is member
        public_communities = queryset.filter(is_public=True)
        user_communities = queryset.filter(memberships__user=user, memberships__is_approved=True)
        
        return (public_communities | user_communities).distinct()
    
    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class CommunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated, CanViewCommunity]
    queryset = Community.objects.all()

class CommunityMembershipView(generics.ListCreateAPIView):
    serializer_class = CommunityMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        community_id = self.kwargs['community_id']
        return CommunityMembership.objects.filter(community_id=community_id)
    
    def perform_create(self, serializer):
        community = Community.objects.get(id=self.kwargs['community_id'])
        
        # Check if already a member
        existing_membership = CommunityMembership.objects.filter(
            community=community,
            user=self.request.user
        ).first()
        
        if existing_membership:
            if not existing_membership.is_approved:
                return Response(
                    {'error': 'Membership request pending approval'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'error': 'Already a member'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Auto-approve if no approval required
        is_approved = not community.requires_approval
        
        serializer.save(
            community=community,
            user=self.request.user,
            is_approved=is_approved
        )
        
        # Update member count
        if is_approved:
            community.member_count = F('member_count') + 1
            community.save()

# Post Views
class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, CanPostInCommunity]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.filter(status=Post.PostStatus.PUBLISHED)
        
        # Filter by community if provided
        community_id = self.request.query_params.get('community')
        if community_id:
            queryset = queryset.filter(community_id=community_id)
        else:
            # School-wide posts (no community)
            queryset = queryset.filter(community__isnull=True)
        
        # Filter by type if provided
        post_type = self.request.query_params.get('type')
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        
        return queryset.select_related('author', 'community').prefetch_related('votes', 'bookmarked_by')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
    queryset = Post.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(
            post_id=post_id, 
            is_removed=False
        ).select_related('author').prefetch_related('votes', 'replies')
    
    def perform_create(self, serializer):
        post = Post.objects.get(id=self.kwargs['post_id'])
        
        # Check if post is locked
        if post.is_locked:
            return Response(
                {'error': 'This post is locked and cannot be commented on'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(post=post, author=self.request.user)
        
        # Update post comment count
        post.comment_count = F('comment_count') + 1
        post.save()

# Vote Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_vote(request, post_id=None, comment_id=None):
    try:
        if post_id:
            obj = Post.objects.get(id=post_id)
        elif comment_id:
            obj = Comment.objects.get(id=comment_id)
        else:
            return Response({'error': 'No object specified'}, status=status.HTTP_400_BAD_REQUEST)
        
        vote_type = request.data.get('vote_type')
        
        if vote_type not in ['UPVOTE', 'DOWNVOTE']:
            return Response({'error': 'Invalid vote type'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for existing vote
        existing_vote = Vote.objects.filter(
            user=request.user,
            post=obj if post_id else None,
            comment=obj if comment_id else None
        ).first()
        
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Remove vote
                existing_vote.delete()
                
                # Update counts
                if vote_type == 'UPVOTE':
                    obj.upvotes = F('upvotes') - 1
                else:
                    obj.downvotes = F('downvotes') - 1
            else:
                # Change vote type
                existing_vote.vote_type = vote_type
                existing_vote.save()
                
                # Update counts
                if vote_type == 'UPVOTE':
                    obj.upvotes = F('upvotes') + 1
                    obj.downvotes = F('downvotes') - 1
                else:
                    obj.upvotes = F('upvotes') - 1
                    obj.downvotes = F('downvotes') + 1
        else:
            # Create new vote
            Vote.objects.create(
                user=request.user,
                post=obj if post_id else None,
                comment=obj if comment_id else None,
                vote_type=vote_type
            )
            
            # Update counts
            if vote_type == 'UPVOTE':
                obj.upvotes = F('upvotes') + 1
            else:
                obj.downvotes = F('downvotes') + 1
        
        obj.save()
        obj.refresh_from_db()
        
        return Response({
            'upvotes': obj.upvotes,
            'downvotes': obj.downvotes,
            'user_vote': vote_type if existing_vote and existing_vote.vote_type == vote_type else None
        })
        
    except (Post.DoesNotExist, Comment.DoesNotExist):
        return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)

# Messaging Views
class DirectMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = DirectMessageSerializer
    permission_classes = [permissions.IsAuthenticated, CanMessageUser]
    
    def get_queryset(self):
        user = self.request.user
        other_user_id = self.request.query_params.get('user_id')
        
        if other_user_id:
            # Get messages between two users
            return DirectMessage.objects.filter(
                (Q(sender=user) & Q(receiver_id=other_user_id)) |
                (Q(sender_id=other_user_id) & Q(receiver=user))
            ).select_related('sender', 'receiver')
        
        # Get all messages for user
        return DirectMessage.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related('sender', 'receiver')
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class MessageThreadListView(generics.ListAPIView):
    serializer_class = MessageThreadSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return MessageThread.objects.filter(participants=user).prefetch_related(
            'participants', 'last_message'
        ).distinct()

# Notification Views
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related(
            'post', 'comment', 'community'
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_read(request):
    notification_ids = request.data.get('notification_ids', [])
    
    if notification_ids == 'all':
        updated = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
    else:
        updated = Notification.objects.filter(
            user=request.user, id__in=notification_ids
        ).update(is_read=True)
    
    return Response({'updated_count': updated})

# User Follow Views
class UserFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        try:
            user_to_follow = User.objects.get(id=user_id)
            
            if user_to_follow == request.user:
                return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user_to_follow.school != request.user.school:
                return Response({'error': 'Cannot follow users from other schools'}, status=status.HTTP_400_BAD_REQUEST)
            
            follow, created = UserFollow.objects.get_or_create(
                follower=request.user,
                followed=user_to_follow
            )
            
            if created:
                return Response({'message': 'Successfully followed user'})
            else:
                follow.delete()
                return Response({'message': 'Successfully unfollowed user'})
                
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# Bookmark Views
class BookmarkListCreateView(generics.ListCreateAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('post')
    
    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        
        # Check if already bookmarked
        existing_bookmark = Bookmark.objects.filter(
            user=self.request.user, post_id=post_id
        ).first()
        
        if existing_bookmark:
            existing_bookmark.delete()
            return Response({'message': 'Bookmark removed'})
        else:
            serializer.save(user=self.request.user)
            return Response({'message': 'Bookmark added'})

# Report Views
class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

# Trending Topics
class TrendingTopicsView(generics.ListAPIView):
    serializer_class = TrendingTopicSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        school = self.request.user.school
        time_threshold = timezone.now() - timedelta(hours=24)
        
        return TrendingTopic.objects.filter(
            school=school,
            created_at__gte=time_threshold
        ).order_by('-score')[:10]

# Feed Views
class PersonalFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Posts from communities user is member of
        community_posts = Post.objects.filter(
            community__memberships__user=user,
            community__memberships__is_approved=True,
            status=Post.PostStatus.PUBLISHED
        )
        
        # School-wide posts
        school_wide_posts = Post.objects.filter(
            community__isnull=True,
            status=Post.PostStatus.PUBLISHED
        )
        
        # Combine and order by recent
        return (community_posts | school_wide_posts).distinct().select_related(
            'author', 'community'
        ).prefetch_related('votes', 'bookmarked_by').order_by('-created_at')

# Search Views
class SearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        search_type = request.query_params.get('type', 'all')
        
        if not query:
            return Response({'error': 'Query parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = {}
        
        if search_type in ['all', 'posts']:
            results['posts'] = PostSerializer(
                Post.objects.filter(
                    Q(title__icontains=query) | Q(content__icontains=query),
                    status=Post.PostStatus.PUBLISHED
                )[:20],
                many=True,
                context={'request': request}
            ).data
        
        if search_type in ['all', 'communities']:
            results['communities'] = CommunitySerializer(
                Community.objects.filter(
                    Q(name__icontains=query) | Q(description__icontains=query),
                    school=request.user.school
                )[:10],
                many=True,
                context={'request': request}
            ).data
        
        if search_type in ['all', 'users']:
            results['users'] = [
                {
                    'id': user.id,
                    'display_name': user.get_display_name(),
                    'role': user.role
                }
                for user in User.objects.filter(
                    Q(first_name__icontains=query) | Q(last_name__icontains=query),
                    school=request.user.school
                )[:10]
            ]
        
        return Response(results)