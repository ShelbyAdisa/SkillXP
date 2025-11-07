from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class AIModelConfig(models.Model):
    """
    Configuration for different AI models used across the platform.
    """
    class ModelType(models.TextChoices):
        NLP = 'NLP', 'Natural Language Processing'
        TOXICITY = 'TOXICITY', 'Toxicity/Safety Filter'
        RECOMMENDATION = 'RECOMMENDATION', 'Recommendation Engine'
        SUMMARIZATION = 'SUMMARIZATION', 'Summarization'
        QNA = 'QNA', 'Question Answering'

    name = models.CharField(max_length=100, unique=True)
    model_type = models.CharField(max_length=20, choices=ModelType.choices)
    provider = models.CharField(max_length=50, default='Google Gemini/OpenAI')
    api_key_env = models.CharField(max_length=50, help_text="Environment variable name for the API Key.")
    temperature = models.FloatField(default=0.7, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    max_tokens = models.IntegerField(default=1024)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_model_configs'
        verbose_name = 'AI Model Configuration'

    def __str__(self):
        return f"{self.name} ({self.model_type})"

class AIRequestLog(models.Model):
    """
    Log of all external AI API calls for auditing, cost tracking, and monitoring performance.
    """
    class TargetApp(models.TextChoices):
        ELIBRARY = 'ELIBRARY', 'eLibrary'
        SOCIAL = 'SOCIAL', 'Social'
        WELLBEING = 'WELLBEING', 'Wellbeing'
        ANALYTICS = 'ANALYTICS', 'Analytics'
        
    model_config = models.ForeignKey(AIModelConfig, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    target_app = models.CharField(max_length=20, choices=TargetApp.choices, default=TargetApp.ELIBRARY)
    
    prompt_text = models.TextField()
    response_text = models.TextField(blank=True, null=True)
    
    # Cost & Performance
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    latency_ms = models.IntegerField(default=0, help_text="Latency in milliseconds.")
    
    # Status
    was_successful = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'ai_request_logs'
        ordering = ['-created_at']
        verbose_name = 'AI Request Log'

    def __str__(self):
        return f"Log for {self.model_config.name if self.model_config else 'Unknown'} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
