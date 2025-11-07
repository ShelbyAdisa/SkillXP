from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AIModelConfig, AIRequestLog
from .serializers import AIModelConfigSerializer, AIRequestLogSerializer
from users.permissions import IsSchoolAdmin 

class AIModelConfigViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing AI model configurations. Restricted to Admins.
    """
    queryset = AIModelConfig.objects.all()
    serializer_class = AIModelConfigSerializer
    # Only Admins/School Admins can manage configurations
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin] 

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        config = self.get_object()
        config.is_active = not config.is_active
        config.save()
        return Response({'status': 'Status toggled', 'is_active': config.is_active})

class AIRequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing AI request logs (Read-only). Restricted to Admins.
    """
    queryset = AIRequestLog.objects.all()
    serializer_class = AIRequestLogSerializer
    # Only Admins/School Admins can view logs
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin] 
    
    filter_fields = ['model_config__model_type', 'target_app', 'was_successful']
    search_fields = ['prompt_text', 'error_message']

    def get_queryset(self):
        return AIRequestLog.objects.all()