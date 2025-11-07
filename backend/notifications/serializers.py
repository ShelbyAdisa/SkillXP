from rest_framework import serializers
from .models import Notification
from django.contrib.contenttypes.models import ContentType

class NotificationSerializer(serializers.ModelSerializer):
    target_object_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'message', 'is_read', 'created_at',
            'content_type', 'object_id', 'target_object_url'
        ]
        read_only_fields = ['user', 'notification_type', 'message', 'content_type', 'object_id', 'created_at']

    def get_target_object_url(self, obj):
        if obj.content_object:
            # Simple URL construction based on known object types
            obj_type = obj.content_object.__class__.__name__.lower()
            
            if obj_type in ['assignment', 'learningresource', 'supportticket']:
                return f"/{obj_type}/{obj.object_id}"
            if obj_type == 'post': # Social Post
                return f"/social/post/{obj.object_id}"
            
        return None

class BulkMarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        required=False,
        min_length=1
    )
    mark_all = serializers.BooleanField(default=False)