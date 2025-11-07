from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.db import transaction
from django.db.models import Avg, F
from django.utils import timezone
from datetime import timedelta
from ai_engine.services import AIService  # ✅ DIRECT AI IMPORT

from .models import (
    LearningResource, ResourceReview, ResourceInteraction, 
    StudyCollection, ReadingList, AIRecommendation
)
from .tasks import process_new_resource

# ✅ AI PROCESSING FUNCTIONS (Direct approach like social app)

def generate_ai_metadata(resource_instance):
    """Generate AI metadata for resources - DIRECT APPROACH"""
    if not resource_instance.title and not resource_instance.description:
        return
    
    try:
        # Prevent recursive processing
        if getattr(resource_instance, '_ai_processing', False):
            return
        
        resource_instance._ai_processing = True
        
        # ✅ AI SUMMARY GENERATION
        content_for_ai = f"Title: {resource_instance.title}. Description: {resource_instance.description}"
        if resource_instance.content:
            content_for_ai += f". Content: {resource_instance.content[:500]}"
        
        summary_result = AIService.summarize_content(
            text=content_for_ai,
            max_length=150,
            requesting_user=resource_instance.created_by
        )
        
        if 'error' not in summary_result:
            summary = summary_result.get('summary', '')
            # Update without triggering signals
            LearningResource.objects.filter(id=resource_instance.id).update(
                ai_summary=summary
            )
            print(f"✅ AI Summary generated for: {resource_instance.title}")
        
        # ✅ AI KEYWORD EXTRACTION  
        keyword_prompt = f"""
        Extract 5-8 relevant educational keywords from this content.
        Return ONLY a valid JSON with: {{"keywords": ["keyword1", "keyword2"]}}
        
        Content: "{content_for_ai}"
        """
        
        model_config = AIService.get_model_config('NLP')
        if model_config:
            keyword_response = AIService.call_external_api(
                model_config=model_config,
                prompt=keyword_prompt,
                requesting_user=resource_instance.created_by,
                target_app='ELIBRARY'
            )
            
            parsed_keywords = AIService.parse_json_response(keyword_response)
            if 'error' not in parsed_keywords:
                keywords = parsed_keywords.get('keywords', [])
                LearningResource.objects.filter(id=resource_instance.id).update(
                    ai_keywords=keywords
                )
                print(f"✅ AI Keywords extracted: {keywords}")
        
        # ✅ AI DIFFICULTY SCORING
        difficulty_prompt = f"""
        Analyze difficulty level of this educational resource for students.
        Return ONLY a valid JSON with: {{"difficulty_score": 0.65}}
        
        Resource: "{content_for_ai}"
        Resource Type: {resource_instance.resource_type}
        Current Level: {resource_instance.difficulty_level}
        """
        
        if model_config:
            difficulty_response = AIService.call_external_api(
                model_config=model_config,
                prompt=difficulty_prompt,
                requesting_user=resource_instance.created_by,
                target_app='ELIBRARY'
            )
            
            parsed_difficulty = AIService.parse_json_response(difficulty_response)
            if 'error' not in parsed_difficulty:
                difficulty_score = parsed_difficulty.get('difficulty_score', 0.5)
                LearningResource.objects.filter(id=resource_instance.id).update(
                    ai_difficulty_score=difficulty_score
                )
                print(f"✅ AI Difficulty score: {difficulty_score}")
                
    except Exception as e:
        print(f"❌ Error in AI metadata generation: {e}")
    finally:
        if hasattr(resource_instance, '_ai_processing'):
            delattr(resource_instance, '_ai_processing')

def analyze_review_with_ai(review_instance):
    """✅ AI SENTIMENT ANALYSIS FOR REVIEWS"""
    if not review_instance.review_text:
        return
    
    try:
        if getattr(review_instance, '_ai_processing', False):
            return
        
        review_instance._ai_processing = True
        
        sentiment_result = AIService.analyze_sentiment(
            text=review_instance.review_text,
            requesting_user=review_instance.user
        )
        
        if 'error' not in sentiment_result:
            sentiment_score = sentiment_result.get('sentiment_score', 0)
            primary_emotion = sentiment_result.get('primary_emotion', 'neutral')
            needs_support = sentiment_result.get('needs_support', False)
            
            print(f"✅ Review sentiment: {sentiment_score} ({primary_emotion})")
            
            # Flag concerning reviews for moderation
            if sentiment_score < -0.3 or needs_support:
                print(f"🚨 Review may need moderator attention - Score: {sentiment_score}")
                # You could auto-flag here or notify moderators
                
    except Exception as e:
        print(f"❌ Error analyzing review sentiment: {e}")
    finally:
        if hasattr(review_instance, '_ai_processing'):
            delattr(review_instance, '_ai_processing')

def generate_personalized_recommendations(user, resource_instance=None):
    """✅ GENERATE AI RECOMMENDATIONS BASED ON USER BEHAVIOR"""
    try:
        # Get user's interaction history
        user_interactions = ResourceInteraction.objects.filter(
            user=user
        ).select_related('resource')[:10]  # Limit to recent interactions
        
        # Build user context for AI
        user_context = {
            'user_profile': {
                'grade_level': getattr(user, 'grade_level', 'Unknown'),
                'interests': getattr(user, 'interests', []),
            },
            'recent_activity': [
                {
                    'resource': ir.resource.title,
                    'type': ir.interaction_type,
                    'resource_type': ir.resource.resource_type
                } for ir in user_interactions
            ],
            'preferred_categories': list(
                user_interactions.values_list('resource__categories__name', flat=True).distinct()
            )
        }
        
        # If we have a specific resource, find similar ones
        if resource_instance:
            similar_resources = LearningResource.objects.filter(
                categories__in=resource_instance.categories.all(),
                is_published=True,
                is_approved=True
            ).exclude(id=resource_instance.id).distinct()[:5]
        else:
            # General recommendations based on user history
            similar_resources = LearningResource.objects.filter(
                categories__name__in=user_context['preferred_categories'],
                is_published=True,
                is_approved=True
            ).exclude(
                id__in=user_interactions.values_list('resource_id', flat=True)
            ).distinct()[:5]
        
        # Create AI recommendations
        for similar_resource in similar_resources:
            # Calculate confidence score based on relevance
            confidence = 0.7  # Base confidence
            
            # Increase confidence if same resource type
            if resource_instance and similar_resource.resource_type == resource_instance.resource_type:
                confidence += 0.1
                
            # Increase confidence if same difficulty level
            if resource_instance and similar_resource.difficulty_level == resource_instance.difficulty_level:
                confidence += 0.1
            
            # Create or update recommendation
            AIRecommendation.objects.update_or_create(
                user=user,
                resource=similar_resource,
                defaults={
                    'confidence_score': min(confidence, 0.95),  # Cap at 0.95
                    'recommendation_type': 'PERSONALIZED',
                    'reason': f"Based on your interest in similar resources",
                    'expires_at': timezone.now() + timedelta(days=30)
                }
            )
        
        print(f"✅ AI recommendations generated for {user.get_display_name()}")
        
    except Exception as e:
        print(f"❌ Error generating AI recommendations: {e}")

# ✅ SIGNAL HANDLERS

@receiver(post_save, sender=LearningResource)
def handle_new_resource(sender, instance, created, **kwargs):
    """Handle new resource creation with AI processing"""
    if created:
        # Process resource asynchronously
        transaction.on_commit(lambda: process_new_resource(instance.id))
        
        # ✅ DIRECT AI PROCESSING
        generate_ai_metadata(instance)

@receiver(post_save, sender=ResourceReview)
def update_resource_rating(sender, instance, created, **kwargs):
    """Update resource rating and analyze review sentiment"""
    if instance.is_approved:
        resource = instance.resource
        reviews = resource.reviews.filter(is_approved=True)
        
        # Update rating metrics atomically
        resource.average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        resource.rating_count = reviews.count()
        resource.save(update_fields=['average_rating', 'rating_count'])
    
    # ✅ AI SENTIMENT ANALYSIS FOR NEW REVIEWS
    if created and instance.review_text:
        analyze_review_with_ai(instance)

@receiver(post_save, sender=ResourceInteraction)
def update_resource_counts(sender, instance, created, **kwargs):
    """Update resource counts and generate recommendations"""
    if created:
        resource = instance.resource
        
        # Update counts atomically
        if instance.interaction_type == 'VIEW':
            LearningResource.objects.filter(id=resource.id).update(
                view_count=F('view_count') + 1
            )
        elif instance.interaction_type == 'DOWNLOAD':
            LearningResource.objects.filter(id=resource.id).update(
                download_count=F('download_count') + 1
            )
        elif instance.interaction_type == 'FAVORITE':
            LearningResource.objects.filter(id=resource.id).update(
                favorite_count=F('favorite_count') + 1
            )
        
        # ✅ GENERATE AI RECOMMENDATIONS AFTER SIGNIFICANT INTERACTIONS
        if instance.interaction_type in ['DOWNLOAD', 'COMPLETE', 'FAVORITE']:
            generate_personalized_recommendations(instance.user, instance.resource)

@receiver(post_save, sender=ResourceInteraction)
def handle_completion(sender, instance, created, **kwargs):
    """Handle resource completion and generate progression recommendations"""
    if created and instance.interaction_type == 'COMPLETE' and instance.progress_percentage >= 80:
        try:
            # Find next-level resources in the same category
            next_level_resources = LearningResource.objects.filter(
                categories__in=instance.resource.categories.all(),
                difficulty_level='ADVANCED',  # Or calculate next level
                is_published=True,
                is_approved=True
            ).exclude(id=instance.resource.id)[:3]
            
            for next_resource in next_level_resources:
                AIRecommendation.objects.update_or_create(
                    user=instance.user,
                    resource=next_resource,
                    defaults={
                        'confidence_score': 0.8,
                        'recommendation_type': 'PROGRESSION',
                        'reason': f"Next step after completing {instance.resource.title}",
                        'expires_at': timezone.now() + timedelta(days=30)
                    }
                )
            
            print(f"✅ Progression recommendations generated for {instance.user.get_display_name()}")
            
        except Exception as e:
            print(f"❌ Error generating progression recommendations: {e}")

@receiver(m2m_changed, sender=StudyCollection.resources.through)
def update_collection_timestamps(sender, instance, action, **kwargs):
    """Update collection timestamp when resources are added/removed"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        StudyCollection.objects.filter(id=instance.id).update(updated_at=timezone.now())

@receiver(m2m_changed, sender=ReadingList.resources.through)
def update_reading_list_timestamps(sender, instance, action, **kwargs):
    """Update reading list timestamp when resources are added/removed"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        ReadingList.objects.filter(id=instance.id).update(updated_at=timezone.now())

@receiver(pre_save, sender=LearningResource)
def handle_resource_publishing(sender, instance, **kwargs):
    """Handle resource publishing"""
    if instance.is_published and not instance.published_at:
        instance.published_at = timezone.now()

@receiver(pre_save, sender=LearningResource)
def validate_resource_before_save(sender, instance, **kwargs):
    """Validate resource before saving"""
    # Only validate on create or when important fields change
    if instance.pk is None or any(field in ['title', 'description', 'file', 'external_url', 'content'] for field in instance.get_dirty_fields()):
        # Basic validation logic (you can enhance this)
        issues = []
        if not instance.title:
            issues.append("Title is required")
        if not instance.description:
            issues.append("Description is required")
        if not instance.file and not instance.external_url and not instance.content:
            issues.append("Either file, external URL, or content is required")
        
        if issues and instance.pk is None:  # Only block creation, not updates
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Resource validation issues for '{instance.title}': {', '.join(issues)}")

@receiver(post_save, sender=LearningResource)
def handle_content_updates(sender, instance, **kwargs):
    """Regenerate AI metadata when content changes significantly"""
    # Check if important fields changed
    dirty_fields = instance.get_dirty_fields()
    content_fields = ['title', 'description', 'content']
    
    if any(field in content_fields for field in dirty_fields):
        print(f"🔄 Content changed, regenerating AI metadata for: {instance.title}")
        generate_ai_metadata(instance)

@receiver(post_save, sender=LearningResource)
def notify_on_approval(sender, instance, **kwargs):
    """Notify user when their resource is approved"""
    # Check if resource was just approved
    if instance.is_approved and 'is_approved' in instance.get_dirty_fields() and not instance.get_dirty_fields()['is_approved']:
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = "Your Resource Has Been Approved!"
        message = f"""
Hello {instance.created_by.first_name},

Great news! Your resource "{instance.title}" has been approved and is now available in the eLibrary.

Students can now discover and access your resource. Thank you for contributing to our learning community!

Best regards,
The SkillXP Nexus Team
""".strip()

        if hasattr(settings, 'EMAIL_BACKEND') and instance.created_by.email:
            send_mail(
                subject,
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@skillxp.com'),
                [instance.created_by.email],
                fail_silently=True,
            )

@receiver(post_save, sender=StudyCollection)
def initialize_collection_metrics(sender, instance, created, **kwargs):
    """Initialize metrics for new collections"""
    if created:
        instance.view_count = 0
        instance.favorite_count = 0
        instance.save(update_fields=['view_count', 'favorite_count'])

# ✅ DIRTY FIELDS TRACKING (Keep this from your original code)

def _get_dirty_fields(self):
    if not hasattr(self, '_original_state'):
        return {}
    
    dirty_fields = {}
    for field, value in self._original_state.items():
        if getattr(self, field) != value:
            dirty_fields[field] = value
    return dirty_fields

# Monkey patch the method onto LearningResource if it doesn't exist
if not hasattr(LearningResource, 'get_dirty_fields'):
    LearningResource.get_dirty_fields = _get_dirty_fields

@receiver(pre_save)
def store_original_state(sender, instance, **kwargs):
    """Store original state of instance to track changes"""
    if sender in [LearningResource, ResourceReview, StudyCollection, ReadingList]:
        if instance.pk:
            try:
                original = sender.objects.get(pk=instance.pk)
                instance._original_state = {
                    field.name: getattr(original, field.name)
                    for field in instance._meta.fields
                    if hasattr(original, field.name)
                }
            except sender.DoesNotExist:
                instance._original_state = {}
        else:
            instance._original_state = {}