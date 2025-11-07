from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
import logging

from .models import LearningResource, ResourceInteraction, StudyCollection, AIRecommendation, ReadingList
from .utils import AIResourceHelper, ResourceAnalyzer
from users.models import User

logger = logging.getLogger(__name__)

def process_new_resource(resource_id):
    # Process a newly created resource
    try:
        resource = LearningResource.objects.get(id=resource_id)
        
        # Generate AI summary and keywords
        resource.ai_summary = AIResourceHelper.generate_resource_summary(resource)
        resource.ai_keywords = AIResourceHelper.extract_keywords(resource)
        resource.ai_difficulty_score = AIResourceHelper.calculate_difficulty_score(resource)
        
        # Auto-approve for teachers and admins
        if resource.created_by.role in [User.Role.TEACHER, User.Role.ADMIN, User.Role.SCHOOL_ADMIN]:
            resource.is_approved = True
            resource.requires_approval = False
        else:
            # Students need approval
            resource.requires_approval = True
            resource.is_approved = False
        
        resource.save()
        
        logger.info(f"Processed new resource: {resource.title} (ID: {resource_id})")
        
    except LearningResource.DoesNotExist:
        logger.error(f"Resource {resource_id} not found for processing")
    except Exception as e:
        logger.error(f"Error processing resource {resource_id}: {str(e)}")

def generate_daily_recommendations():
    # Generate daily recommendations for all active users
    try:
        active_users = User.objects.filter(
            is_active=True,
            last_login__gte=timezone.now() - timedelta(days=30)
        )
        
        total_recommendations = 0
        for user in active_users:
            try:
                recommendations = AIResourceHelper.generate_recommendations(user, limit=10)
                total_recommendations += recommendations.count()
                logger.info(f"Generated {recommendations.count()} recommendations for user {user.id}")
            except Exception as e:
                logger.error(f"Error generating recommendations for user {user.id}: {str(e)}")
                continue
        
        logger.info(f"Generated total {total_recommendations} daily recommendations")
        return total_recommendations
        
    except Exception as e:
        logger.error(f"Error in daily recommendation generation: {str(e)}")
        return 0

def send_resource_recommendations():
    # Send weekly resource recommendations via email
    try:
        users_with_preferences = User.objects.filter(
            is_active=True,
            profile__email_notifications=True
        )
        
        sent_count = 0
        for user in users_with_preferences:
            try:
                recommendations = AIRecommendation.objects.filter(
                    user=user,
                    expires_at__gte=timezone.now()
                ).select_related('resource').order_by('-confidence_score')[:5]
                
                if not recommendations.exists():
                    continue
                
                subject = "Your Weekly Resource Recommendations"
                
                recommendation_list = "\n".join([
                    f"• {rec.resource.title} (Confidence: {rec.confidence_score:.0%}) - {rec.reason}"
                    for rec in recommendations
                ])
                
                message = f"""
                            Hello {user.first_name},

                            Here are your personalized resource recommendations for this week:

                            {recommendation_list}

                            Log in to SkillXP Nexus to explore these resources and continue your learning journey!

                            Best regards,
                            The SkillXP Nexus Team
                        """.strip()

                if hasattr(settings, 'EMAIL_BACKEND') and user.email:
                    send_mail(
                        subject,
                        message,
                        getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@skillxp.com'),
                        [user.email],
                        fail_silently=False,
                    )
                    sent_count += 1
                    logger.info(f"Sent recommendations to {user.email}")
                    
            except Exception as e:
                logger.error(f"Error sending recommendations to {user.email}: {str(e)}")
                continue
        
        logger.info(f"Sent weekly recommendations to {sent_count} users")
        return sent_count
        
    except Exception as e:
        logger.error(f"Error sending resource recommendations: {str(e)}")
        return 0

def update_resource_analytics():
    # Update analytics for all resources
    try:
        resources = LearningResource.objects.filter(is_published=True, is_approved=True)
        
        updated_count = 0
        for resource in resources:
            try:
                analytics = ResourceAnalyzer.get_resource_analytics(resource)
                
                # Update resource with new analytics data
                resource.view_count = analytics.get('total_views', 0)
                resource.download_count = analytics.get('total_downloads', 0)
                resource.favorite_count = analytics.get('total_favorites', 0)
                
                # Only update rating if we have new data
                if analytics.get('rating_count', 0) > 0:
                    resource.average_rating = analytics.get('average_rating', 0)
                    resource.rating_count = analytics.get('rating_count', 0)
                
                resource.save()
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating analytics for resource {resource.id}: {str(e)}")
                continue
        
        logger.info(f"Updated analytics for {updated_count} resources")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error updating resource analytics: {str(e)}")
        return 0

def cleanup_old_data():
    # Clean up old data and expired recommendations
    try:
        # Delete expired recommendations
        expired_recommendations = AIRecommendation.objects.filter(
            expires_at__lt=timezone.now()
        )
        expired_count = expired_recommendations.count()
        expired_recommendations.delete()
        
        # Delete very old interactions (older than 1 year)
        one_year_ago = timezone.now() - timedelta(days=365)
        old_interactions = ResourceInteraction.objects.filter(created_at__lt=one_year_ago)
        interactions_count = old_interactions.count()
        old_interactions.delete()
        
        # Clean up unused collections (no resources, older than 6 months)
        six_months_ago = timezone.now() - timedelta(days=180)
        unused_collections = StudyCollection.objects.filter(
            resources__isnull=True,
            created_at__lt=six_months_ago
        )
        collections_count = unused_collections.count()
        unused_collections.delete()
        
        # Clean up empty reading lists (older than 3 months)
        three_months_ago = timezone.now() - timedelta(days=90)
        empty_reading_lists = ReadingList.objects.filter(
            resources__isnull=True,
            created_at__lt=three_months_ago
        )
        reading_lists_count = empty_reading_lists.count()
        empty_reading_lists.delete()
        
        logger.info(f"Cleaned up {expired_count} expired recommendations, {interactions_count} old interactions, {collections_count} unused collections, and {reading_lists_count} empty reading lists")
        
        return {
            'expired_recommendations': expired_count,
            'old_interactions': interactions_count,
            'unused_collections': collections_count,
            'empty_reading_lists': reading_lists_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {str(e)}")
        return {}

def generate_trending_report():
    # Generate report of trending resources
    try:
        # Get trending resources (last 7 days)
        one_week_ago = timezone.now() - timedelta(days=7)
        
        trending_resources = LearningResource.objects.filter(
            is_published=True,
            is_approved=True,
            interactions__created_at__gte=one_week_ago
        ).annotate(
            recent_engagement=Count('interactions')
        ).order_by('-recent_engagement', '-view_count')[:10]
        
        # Generate report data
        report_data = {
            'generated_at': timezone.now().isoformat(),
            'time_period': '7 days',
            'trending_resources': []
        }
        
        for resource in trending_resources:
            analytics = ResourceAnalyzer.get_resource_analytics(resource)
            report_data['trending_resources'].append({
                'id': resource.id,
                'title': resource.title,
                'resource_type': resource.resource_type,
                'engagement': analytics.get('engagement_rate', 0),
                'total_views': analytics.get('total_views', 0),
                'average_rating': resource.average_rating,
                'school': resource.school.name
            })
        
        # Store and send report (could be saved to database and sent to admins)
        logger.info(f"Generated trending report with {len(trending_resources)} resources")
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating trending report: {str(e)}")
        return {}

def send_approval_notifications():
    # Send notifications for resources pending approval
    try:
        # Get resources pending approval
        pending_resources = LearningResource.objects.filter(
            requires_approval=True,
            is_approved=False
        ).select_related('created_by', 'school')
        
        if not pending_resources.exists():
            logger.info("No resources pending approval")
            return 0
        
        # Get school admins
        school_admins = User.objects.filter(
            role__in=[User.Role.ADMIN, User.Role.SCHOOL_ADMIN],
            is_active=True
        )
        
        sent_count = 0
        for admin in school_admins:
            try:
                # Get pending resources for this admin's school
                admin_pending = pending_resources.filter(school=admin.school)
                if not admin_pending.exists():
                    continue
                
                subject = "⏳ Resources Pending Approval"
                
                resource_list = "\n".join([
                    f"• {resource.title} by {resource.created_by.get_display_name()} ({resource.get_resource_type_display()})"
                    for resource in admin_pending
                ])
                
                message = f"""
                                Hello {admin.first_name},

                                The following resources are pending your approval:

                                {resource_list}

                                Please log in to SkillXP Nexus to review and approve these resources.

                                Best regards,
                                SkillXP Nexus System
                            """.strip()

                if hasattr(settings, 'EMAIL_BACKEND') and admin.email:
                    send_mail(
                        subject,
                        message,
                        getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@skillxp.com'),
                        [admin.email],
                        fail_silently=False,
                    )
                    sent_count += 1
                    logger.info(f"Sent approval notification to {admin.email}")
                    
            except Exception as e:
                logger.error(f"Error sending approval notification to {admin.email}: {str(e)}")
                continue
        
        logger.info(f"Sent approval notifications for {pending_resources.count()} resources to {sent_count} admins")
        return sent_count
        
    except Exception as e:
        logger.error(f"Error sending approval notifications: {str(e)}")
        return 0

def update_popular_resources():
    # Update and feature popular resources
    try:
        # Get popular resources from the last 30 days
        one_month_ago = timezone.now() - timedelta(days=30)
        
        popular_resources = LearningResource.objects.filter(
            is_published=True,
            is_approved=True,
            interactions__created_at__gte=one_month_ago
        ).annotate(
            recent_engagement=Count('interactions', filter=Q(
                interactions__interaction_type__in=['VIEW', 'DOWNLOAD', 'FAVORITE', 'COMPLETE']
            ))
        ).order_by('-recent_engagement')[:5]
        
        # Unfeature all currently featured resources
        LearningResource.objects.filter(is_featured=True).update(is_featured=False)
        
        # Feature the new popular resources
        featured_count = 0
        for resource in popular_resources:
            if resource.recent_engagement > 10:  
                resource.is_featured = True
                resource.save()
                featured_count += 1
                logger.info(f"Featured resource: {resource.title} (Engagement: {resource.recent_engagement})")
        
        logger.info(f"Updated featured resources: {featured_count} resources featured")
        return featured_count
        
    except Exception as e:
        logger.error(f"Error updating popular resources: {str(e)}")
        return 0