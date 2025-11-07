from rest_framework import serializers
from .models import AIModelConfig, AIRequestLog

class AIModelConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModelConfig
        fields = [
            'id', 'name', 'model_type', 'provider', 'temperature', 
            'max_tokens', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
          
            'api_key_env': {'write_only': True, 'required': True}
        }

class AIRequestLogSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model_config.name', read_only=True)
    user_display_name = serializers.CharField(source='user.get_display_name', read_only=True)
    
    class Meta:
        model = AIRequestLog
        fields = [
            'id', 'model_name', 'user_display_name', 'target_app', 'prompt_text', 
            'response_text', 'input_tokens', 'output_tokens', 'cost_usd', 
            'latency_ms', 'was_successful', 'error_message', 'created_at'
        ]
       
        read_only_fields = fields