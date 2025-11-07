from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
import logging
import json

logger = logging.getLogger(__name__)

class AIResourceHelper:
    # AI-powered resource management and recommendations
    
    @staticmethod
    def generate_resource_summary(resource):
        # Generate AI summary for a resource
        try:
            # This would integrate with your AI service (OpenAI, Gemini, etc.)
            # For now, return a basic summary
            content = resource.content or resource.description
            if len(content) > 200:
                return content[:197] + "..."
            return content
        except Exception as e:
            logger.error(f"Error generating resource summary: {str(e)}")
            return resource.description[:200] + "..." if len(resource.description) > 200 else resource.description
    
    @staticmethod
    def extract_keywords(resource):
        # Extract keywords from resource content
        try:
            # Basic keyword extraction
            text = f"{resource.title} {resource.description} {resource.content or ''}"
            words = text.lower().split()
            # Remove common words and get unique words
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            keywords = [word for word in set(words) if word not in common_words and len(word) > 3]
            return keywords[:10]  # Return top 10 keywords
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    @staticmethod
    def calculate_difficulty_score(resource):
        # Calculate difficulty score based on content analysis
        try:
            # Simple heuristic-based scoring
            score = 0.5  
            
            # Adjust based on difficulty level
            if resource.difficulty_level == 'BEGINNER':
                score = 0.3
            elif resource.difficulty_level == 'ADVANCED':
                score = 0.8
            
            # Adjust based on content length
            if resource.content and len(resource.content) > 1000:
                score += 0.1
            if resource.pages and resource.pages > 50:
                score += 0.1
            
            return min(1.0, max(0.0, score))
        except Exception as e:
            logger.error(f"Error calculating difficulty score: {str(e)}")
            return 0.5
    
    @staticmethod
    def get_similar_resources(resource, user, limit=10):
        # Find similar resources based on content and metadata
        from .models import LearningResource
        
        try:
            # Get resources with same categories
            similar = LearningResource.objects.filter(
                school=user.school,
                is_published=True,
                is_approved=True,
                categories__in=resource.categories.all()
            ).exclude(id=resource.id).distinct()
            
            # Filter by similar difficulty
            if resource.ai_difficulty_score:
                difficulty_range = 0.2
                similar = similar.filter(
                    ai_difficulty_score__range=(
                        resource.ai_difficulty_score - difficulty_range,
                        resource.ai_difficulty_score + difficulty_range
                    )
                )
            
            # Order by relevance (category match, then rating)
            similar = similar.annotate(
                category_match=Count('categories'),
                weighted_score=Avg('average_rating') + Count('categories') * 0.1
            ).order_by('-weighted_score', '-average_rating')[:limit]
            
            return similar
        except Exception as e:
            logger.error(f"Error finding similar resources: {str(e)}")
            return LearningResource.objects.none()
    
    @staticmethod
    def generate_recommendations(user, limit=20):
        # Generate personalized resource recommendations
        from .models import LearningResource, AIRecommendation, ResourceInteraction
        
        try:
            # Get user's interaction history
            user_interactions = ResourceInteraction.objects.filter(user=user)
            viewed_resources = user_interactions.filter(interaction_type='VIEW').values_list('resource_id', flat=True)
            favorited_resources = user_interactions.filter(interaction_type='FAVORITE').values_list('resource_id', flat=True)
            
            # Get resources from favorite categories
            favorite_categories = LearningResource.objects.filter(
                id__in=favorited_resources
            ).values_list('categories', flat=True)
            
            # Generate recommendations
            recommendations = LearningResource.objects.filter(
                school=user.school,
                is_published=True,
                is_approved=True
            ).exclude(id__in=viewed_resources)
            
            if favorite_categories:
                recommendations = recommendations.filter(categories__in=favorite_categories)
            
            # Calculate confidence scores based on various factors
            recommended_resources = []
            for resource in recommendations[:limit]:
                confidence = 0.5
                
                # Boost confidence for same categories as favorites
                if favorite_categories:
                    category_match = resource.categories.filter(id__in=favorite_categories).count()
                    confidence += category_match * 0.1
                
                # Boost confidence for high-rated resources
                if resource.average_rating > 4.0:
                    confidence += 0.2
                elif resource.average_rating > 3.0:
                    confidence += 0.1
                
                # Adjust based on difficulty (prefer similar to viewed resources)
                viewed_difficulty = LearningResource.objects.filter(
                    id__in=viewed_resources
                ).aggregate(avg_difficulty=Avg('ai_difficulty_score'))['avg_difficulty'] or 0.5
                
                if resource.ai_difficulty_score:
                    difficulty_diff = abs(resource.ai_difficulty_score - viewed_difficulty)
                    confidence += (1 - difficulty_diff) * 0.2
                
                confidence = min(1.0, max(0.1, confidence))
                
                recommended_resources.append({
                    'resource': resource,
                    'confidence_score': confidence,
                    'reason': f"Based on your interests and learning pattern"
                })
            
            # Sort by confidence and create AIRecommendation objects
            recommended_resources.sort(key=lambda x: x['confidence_score'], reverse=True)
            
            for rec_data in recommended_resources[:10]:
                AIRecommendation.objects.update_or_create(
                    user=user,
                    resource=rec_data['resource'],
                    defaults={
                        'confidence_score': rec_data['confidence_score'],
                        'reason': rec_data['reason'],
                        'recommendation_type': 'PERSONALIZED',
                        'expires_at': timezone.now() + timedelta(days=7)
                    }
                )
            
            return AIRecommendation.objects.filter(user=user).order_by('-confidence_score')[:limit]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return AIRecommendation.objects.none()

class SearchHelper:
    # Advanced search functionality for resources
    
    @staticmethod
    def search_resources(user, query=None, resource_type=None, category_id=None, 
                       difficulty=None, tags=None, sort_by='relevance', limit=20):
        # Advanced search with multiple filters
        from .models import LearningResource
        
        try:
            queryset = LearningResource.objects.filter(
                school=user.school,
                is_published=True,
                is_approved=True
            )
            
            # Text search
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(content__icontains=query) |
                    Q(author__icontains=query) |
                    Q(tags__icontains=query)
                )
            
            # Resource type filter
            if resource_type:
                queryset = queryset.filter(resource_type=resource_type)
            
            # Category filter
            if category_id:
                queryset = queryset.filter(categories__id=category_id)
            
            # Difficulty filter
            if difficulty:
                queryset = queryset.filter(difficulty_level=difficulty)
            
            # Tags filter
            if tags:
                for tag in tags:
                    queryset = queryset.filter(tags__icontains=tag)
            
            # Apply sorting
            if sort_by == 'relevance' and query:
                # Basic relevance scoring for text search
                queryset = queryset.annotate(
                    relevance=Count('title', filter=Q(title__icontains=query)) * 3 +
                             Count('description', filter=Q(description__icontains=query)) * 2 +
                             Count('content', filter=Q(content__icontains=query)) * 1
                ).order_by('-relevance', '-created_at')
            elif sort_by == 'popular':
                queryset = queryset.order_by('-view_count', '-average_rating')
            elif sort_by == 'rating':
                queryset = queryset.order_by('-average_rating', '-view_count')
            elif sort_by == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort_by == 'oldest':
                queryset = queryset.order_by('created_at')
            else:
                queryset = queryset.order_by('-created_at')
            
            return queryset.distinct()[:limit]
            
        except Exception as e:
            logger.error(f"Error in resource search: {str(e)}")
            return LearningResource.objects.none()
    
    @staticmethod
    def build_search_filters(user):
        # Build available search filters for the current user
        from .models import ResourceCategory, LearningResource
        
        try:
            categories = ResourceCategory.objects.filter(
                school=user.school,
                is_active=True
            ).values('id', 'name')
            
            resource_types = LearningResource.objects.filter(
                school=user.school,
                is_published=True,
                is_approved=True
            ).values_list('resource_type', flat=True).distinct()
            
            difficulty_levels = LearningResource.objects.filter(
                school=user.school,
                is_published=True,
                is_approved=True
            ).values_list('difficulty_level', flat=True).distinct()
            
            # Get popular tags
            all_tags = []
            resources_with_tags = LearningResource.objects.filter(
                school=user.school,
                is_published=True,
                is_approved=True
            ).exclude(tags=[]).values_list('tags', flat=True)
            
            for tags_list in resources_with_tags:
                if tags_list:  
                    all_tags.extend(tags_list)
            
            popular_tags = list(set(all_tags))[:20]  
            
            return {
                'categories': list(categories),
                'resource_types': list(resource_types),
                'difficulty_levels': list(difficulty_levels),
                'popular_tags': popular_tags
            }
            
        except Exception as e:
            logger.error(f"Error building search filters: {str(e)}")
            return {}

class ResourceAnalyzer:
    # Analyze resource usage and engagement
    
    @staticmethod
    def get_resource_analytics(resource):
        # Get detailed analytics for a resource
        from .models import ResourceInteraction
        
        try:
            interactions = ResourceInteraction.objects.filter(resource=resource)
            
            # Basic counts
            total_views = interactions.filter(interaction_type='VIEW').count()
            total_downloads = interactions.filter(interaction_type='DOWNLOAD').count()
            total_favorites = interactions.filter(interaction_type='FAVORITE').count()
            total_completions = interactions.filter(interaction_type='COMPLETE').count()
            
            # Engagement rate 
            engagement_rate = 0
            if total_views > 0:
                engagement_rate = (total_downloads + total_favorites + total_completions) / total_views * 100
            
            # Average completion time (for completable resources)
            completion_times = []
            completion_interactions = interactions.filter(interaction_type='COMPLETE')
            for interaction in completion_interactions:
                if interaction.duration_seconds > 0:
                    completion_times.append(interaction.duration_seconds)
            
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
            
            # User demographics (simplified)
            user_roles = interactions.values('user__role').annotate(count=Count('user__role'))
            
            return {
                'total_views': total_views,
                'total_downloads': total_downloads,
                'total_favorites': total_favorites,
                'total_completions': total_completions,
                'engagement_rate': round(engagement_rate, 2),
                'average_completion_time': round(avg_completion_time, 2),
                'user_demographics': list(user_roles),
                'average_rating': resource.average_rating,
                'rating_count': resource.rating_count
            }
            
        except Exception as e:
            logger.error(f"Error getting resource analytics: {str(e)}")
            return {}
    
    @staticmethod
    def get_popular_resources(school, days=30, limit=10):
        # Get most popular resources in a time period
        from .models import LearningResource, ResourceInteraction
        
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            popular_resources = LearningResource.objects.filter(
                school=school,
                is_published=True,
                is_approved=True,
                interactions__created_at__gte=start_date
            ).annotate(
                recent_views=Count('interactions', filter=Q(interactions__interaction_type='VIEW')),
                recent_downloads=Count('interactions', filter=Q(interactions__interaction_type='DOWNLOAD')),
                engagement_score=Count('interactions', filter=Q(
                    interactions__interaction_type__in=['DOWNLOAD', 'FAVORITE', 'COMPLETE']
                ))
            ).order_by('-engagement_score', '-recent_views')[:limit]
            
            return popular_resources
            
        except Exception as e:
            logger.error(f"Error getting popular resources: {str(e)}")
            return LearningResource.objects.none()

class ContentProcessor:
    # Process and validate resource content
    
    @staticmethod
    def validate_resource_content(resource):
        # Validate resource content for quality and appropriateness
        issues = []
        
        # Check title
        if not resource.title or len(resource.title.strip()) < 5:
            issues.append("Title is too short")
        
        # Check description
        if not resource.description or len(resource.description.strip()) < 20:
            issues.append("Description is too short")
        
        # Check content availability
        if not resource.file and not resource.external_url and not resource.content:
            issues.append("No content provided (file, URL, or text content required)")
        
        # Check file type if file is provided
        if resource.file and resource.file.name:
            allowed_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
                                 '.mp4', '.avi', '.mov', '.mp3', '.wav', '.jpg', '.jpeg', '.png', '.gif']
            file_extension = '.' + resource.file.name.lower().split('.')[-1]
            if file_extension not in allowed_extensions:
                issues.append(f"File type {file_extension} is not allowed")
        
        return issues
    
    @staticmethod
    def generate_preview_content(resource, max_length=150):
        # Generate preview content for resource cards
        if resource.content:
            # Use actual content for preview
            preview = resource.content[:max_length]
            if len(resource.content) > max_length:
                preview += "..."
            return preview
        elif resource.description:
            # Use description for preview
            preview = resource.description[:max_length]
            if len(resource.description) > max_length:
                preview += "..."
            return preview
        else:
            return f"{resource.get_resource_type_display()} resource"
    
    @staticmethod
    def extract_metadata(resource):
        # Extract metadata from resource content
        metadata = {}
        
        # Basic metadata
        metadata['word_count'] = len(resource.content.split()) if resource.content else 0
        metadata['has_file'] = bool(resource.file)
        metadata['has_external_content'] = bool(resource.external_url)
        metadata['has_embedded_content'] = bool(resource.embed_code)
        
        # Estimate reading time (assuming 200 words per minute)
        if metadata['word_count'] > 0:
            metadata['estimated_reading_minutes'] = max(1, metadata['word_count'] // 200)
        else:
            metadata['estimated_reading_minutes'] = None
        
        return metadata