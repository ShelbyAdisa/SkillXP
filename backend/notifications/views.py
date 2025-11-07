from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import F

from .models import Notification
from .serializers import NotificationSerializer, BulkMarkReadSerializer
from .permissions import IsNotificationOwner

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for users to view and manage their notifications.
    Read-only for security; modifications handled by custom actions.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotificationOwner]
    
    def get_queryset(self):
        # Users can only see their own notifications
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by read status
        is_read_param = self.request.query_params.get('is_read')
        if is_read_param is not None:
            is_read = is_read_param.lower() in ['true', '1']
            queryset = queryset.filter(is_read=is_read)
        
        return queryset

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Marks a single notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification, context={'request': request}).data)

    @action(detail=False, methods=['post'], url_path='bulk-read')
    def bulk_mark_read(self, request):
        """Marks multiple notifications or all notifications as read."""
        serializer = BulkMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_notifications = Notification.objects.filter(user=request.user, is_read=False)
        updated_count = 0

        if serializer.validated_data['mark_all']:
            # Mark all unread notifications for the user
            updated_count = user_notifications.update(is_read=True)
        
        elif serializer.validated_data.get('notification_ids'):
            # Mark a specific list of notifications as read
            ids_to_mark = serializer.validated_data['notification_ids']
            updated_count = user_notifications.filter(id__in=ids_to_mark).update(is_read=True)
        
        else:
             return Response({"detail": "No notifications specified for bulk update."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'status': 'success', 'updated_count': updated_count})

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """Returns the count of unread notifications for the user."""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})