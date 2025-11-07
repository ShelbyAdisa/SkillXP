from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Avg
import threading
import time

from .models import WellbeingPost, SupportTicket, MoodCheck, CrisisAlert, ModerationAction
from django.contrib.auth import get_user_model

User = get_user_model()

def analyze_post_sentiment(post_id):
    # Analyze post sentiment - run in background thread
    def _analyze():
        try:
            time.sleep(2) 
            post = WellbeingPost.objects.get(id=post_id)
            
            # Simple keyword-based analysis for demo purposes
            crisis_keywords = ['suicide', 'self harm', 'kill myself', 'end it all', 'want to die']
            negative_words = ['hate', 'depressed', 'anxious', 'hopeless', 'alone']
            
            content_lower = post.content.lower()
            toxicity_score = 0.0
            
            # Calculate simple toxicity score
            for word in negative_words:
                if word in content_lower:
                    toxicity_score += 0.1
            
            toxicity_score = min(toxicity_score, 1.0)  
            
            # Update post with analysis results
            post.toxicity_score = toxicity_score
            if toxicity_score > 0.7:
                post.is_approved = False
                
                # Create moderation action
                admin_user = User.objects.filter(role=User.Role.ADMIN).first()
                if admin_user:
                    ModerationAction.objects.create(
                        moderator=admin_user,
                        target_user=post.author,
                        action_type=ModerationAction.ActionType.POST_REMOVED,
                        reason="Automated toxicity detection",
                        post=post
                    )
            
            post.save()
            
        except WellbeingPost.DoesNotExist:
            pass
    
    # Run in background thread
    thread = threading.Thread(target=_analyze)
    thread.daemon = True
    thread.start()

def check_crisis_keywords(post_id):
    # Check for crisis keywords - run in background thread
    def _check():
        try:
            post = WellbeingPost.objects.get(id=post_id)
            
            crisis_keywords = ['suicide', 'self harm', 'kill myself', 'end it all', 'want to die']
            content_lower = post.content.lower()
            
            for keyword in crisis_keywords:
                if keyword in content_lower:
                    # Create crisis alert
                    CrisisAlert.objects.create(
                        reported_by=post.author,
                        post=post,
                        description=f"Crisis keyword detected: {keyword}",
                        severity_level=8
                    )
                    break
                    
        except WellbeingPost.DoesNotExist:
            pass
    
    thread = threading.Thread(target=_check)
    thread.daemon = True
    thread.start()

def schedule_wellbeing_checkin(user_id):
    # Schedule wellbeing check-in
    def _schedule():
        try:
            user = User.objects.get(id=user_id)
            
            # Check if user has recent low mood entries
            recent_low_mood = MoodCheck.objects.filter(
                user=user,
                mood_level__lte=2,
                created_at__gte=timezone.now() - timedelta(days=3)
            ).count()
            
            if recent_low_mood >= 2:
                # Create automatic support ticket
                SupportTicket.objects.create(
                    student=user,
                    title="Automated Wellbeing Check-in",
                    description="Our system detected you might be having a tough time. We're here to help!",
                    priority=SupportTicket.PriorityLevel.MEDIUM
                )
                
        except User.DoesNotExist:
            pass
    
    thread = threading.Thread(target=_schedule)
    thread.daemon = True
    thread.start()

def generate_daily_wellbeing_report():
    # Generate daily report for counselors
    yesterday = timezone.now() - timedelta(days=1)
    
    for school in User.objects.values_list('school', flat=True).distinct():
        school_users = User.objects.filter(school=school)
        
        report_data = {
            'new_posts': WellbeingPost.objects.filter(
                author__school=school,
                created_at__gte=yesterday
            ).count(),
            'new_tickets': SupportTicket.objects.filter(
                student__school=school,
                created_at__gte=yesterday
            ).count(),
            'crisis_alerts': CrisisAlert.objects.filter(
                reported_by__school=school,
                created_at__gte=yesterday
            ).count(),
            'avg_mood': MoodCheck.objects.filter(
                user__school=school,
                created_at__gte=yesterday
            ).aggregate(Avg('mood_level'))['mood_level__avg'] or 0,
        }
        
        # Send to school counselors
        counselors = User.objects.filter(
            school=school,
            role=User.Role.TEACHER
        )
        
        for counselor in counselors:
            # Simple email without HTML template
            subject = f'Daily Wellbeing Report - {timezone.now().date()}'
            message = f"""
                        Daily Wellbeing Report for {counselor.get_display_name()}
                        
                        New Posts: {report_data['new_posts']}
                        New Support Tickets: {report_data['new_tickets']}
                        Crisis Alerts: {report_data['crisis_alerts']}
                        Average Mood Score: {report_data['avg_mood']:.1f}/5.0
                        
                        Please check the wellbeing dashboard for details.
                    """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [counselor.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Failed to send email: {e}")

def archive_resolved_tickets():
    # Archive tickets resolved more than 30 days ago
    archive_date = timezone.now() - timedelta(days=30)
    
    resolved_tickets = SupportTicket.objects.filter(
        status=SupportTicket.TicketStatus.RESOLVED,
        resolved_at__lte=archive_date
    )
    
    archive_count = resolved_tickets.count()
    resolved_tickets.update(status=SupportTicket.TicketStatus.CLOSED)
    
    print(f"Archived {archive_count} tickets")
    return archive_count

# Management command for scheduled tasks
def run_scheduled_tasks():
    # Run all scheduled tasks 
    print("Running scheduled wellbeing tasks...")
    
    # Generate daily reports (run in morning)
    generate_daily_wellbeing_report()
    
    # Archive old tickets (run weekly)
    if timezone.now().weekday() == 0: 
        archive_resolved_tickets()
    
    print("Scheduled tasks completed!")