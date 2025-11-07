from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.db import transaction
from ai_engine.services import AIService
from .models import Classroom, Assignment, Submission, Enrollment, StudentProgress, ClassPost, Comment
from .tasks import send_assignment_notification, send_grade_notification, update_classroom_analytics

@receiver(post_save, sender=Enrollment)
def create_student_progress(sender, instance, created, **kwargs):
    # Create student progress record when enrolled
    if created and instance.status == 'ACTIVE':
        StudentProgress.objects.get_or_create(
            student=instance.student,
            classroom=instance.classroom
        )

@receiver(post_save, sender=Submission)
def handle_submission_xp(sender, instance, created, **kwargs):
    # Award XP when submission is graded
    if instance.grade and not instance.is_xp_awarded:
        from .utils import GradeCalculator
        
        percentage = instance.grade_percentage
        xp_earned = GradeCalculator.calculate_xp_reward(
            instance.assignment, 
            percentage, 
            instance.is_late
        )
        
        instance.xp_earned = xp_earned
        instance.is_xp_awarded = True
        instance.save()
        
        # Update student's total XP
        instance.student.xp_points += xp_earned
        instance.student.save()
        
        # Send grade notification
        send_grade_notification(instance.id)

@receiver(post_save, sender=Assignment)
def publish_assignment(sender, instance, created, **kwargs):
    # Send notifications when assignment is published
    if instance.status == 'PUBLISHED' and not created:
        send_assignment_notification(instance.id)

@receiver(m2m_changed, sender=Classroom.students.through)
def update_classroom_stats(sender, instance, action, **kwargs):
    # Update classroom statistics when students change
    if action in ['post_add', 'post_remove']:
        # Trigger analytics update
        update_classroom_analytics(instance.id)

@receiver(post_save, sender=Classroom)
def generate_class_code(sender, instance, created, **kwargs):
    # Generate class code if not provided
    if created and not instance.code:
        instance.code = instance.generate_class_code()
        instance.save()


@receiver(post_save, sender=Enrollment)
def create_student_progress(sender, instance, created, **kwargs):
    """Create student progress record when enrolled"""
    if created and instance.status == 'ACTIVE':
        StudentProgress.objects.get_or_create(
            student=instance.student,
            classroom=instance.classroom
        )

@receiver(post_save, sender=Assignment)
def analyze_assignment_quality(sender, instance, created, **kwargs):
    """AI analysis when new assignment is created"""
    if created and instance.description and instance.status == 'PUBLISHED':
        try:
            # Prevent recursive signal triggering
            if hasattr(instance, '_ai_processing'):
                return
            
            instance._ai_processing = True
            
            # Call AI engine for assignment quality analysis
            quality_result = AIService.analyze_assignment_quality(
                assignment_title=instance.title,
                assignment_description=instance.description,
                rubric=instance.rubric or "Standard educational rubric",
                requesting_user=instance.created_by
            )
            
            if 'error' not in quality_result:
                # Update assignment with AI insights (without triggering save signal)
                Assignment.objects.filter(id=instance.id).update(
                    ai_clarity_score=quality_result.get('clarity_score', 0),
                    ai_difficulty_level=quality_result.get('difficulty_level', 'medium'),
                    ai_suggestions=quality_result.get('suggested_improvements', [])
                )
                print(f"✅ Assignment analyzed: {instance.title} - Clarity: {quality_result.get('clarity_score', 0)}")
                
        except Exception as e:
            print(f"❌ Error analyzing assignment: {e}")
        finally:
            # Clean up flag
            if hasattr(instance, '_ai_processing'):
                delattr(instance, '_ai_processing')

@receiver(post_save, sender=Submission)
def handle_submission_ai_feedback(sender, instance, created, **kwargs):
    """AI feedback when submission is created or updated"""
    if instance.content and instance.status == 'SUBMITTED':
        try:
            # Prevent recursive signal triggering
            if hasattr(instance, '_ai_processing'):
                return
            
            instance._ai_processing = True
            
            # 1. AI Feedback Generation
            feedback_result = AIService.provide_submission_feedback(
                submission_content=instance.content,
                assignment_rubric=instance.assignment.rubric or {},
                requesting_user=instance.assignment.created_by
            )
            
            # 2. Plagiarism Risk Analysis
            plagiarism_result = AIService.detect_plagiarism_risk(
                submission_content=instance.content,
                assignment_context=f"{instance.assignment.title} - {instance.assignment.description}",
                requesting_user=instance.assignment.created_by
            )
            
            # Update submission with AI insights
            update_data = {}
            
            if 'error' not in feedback_result:
                update_data['ai_feedback'] = feedback_result.get('overall_feedback', '')
                print(f"✅ AI feedback generated for submission #{instance.id}")
            
            if 'error' not in plagiarism_result:
                update_data['similarity_score'] = plagiarism_result.get('originality_score', 1.0)
                print(f"✅ Plagiarism analysis completed for submission #{instance.id}")
            
            if update_data:
                Submission.objects.filter(id=instance.id).update(**update_data)
                
        except Exception as e:
            print(f"❌ Error processing submission with AI: {e}")
        finally:
            # Clean up flag
            if hasattr(instance, '_ai_processing'):
                delattr(instance, '_ai_processing')

@receiver(post_save, sender=Submission)
def handle_submission_xp(sender, instance, created, **kwargs):
    """Award XP when submission is graded"""
    if instance.grade and not instance.is_xp_awarded:
        from .utils import GradeCalculator
        
        percentage = instance.grade_percentage
        xp_earned = GradeCalculator.calculate_xp_reward(
            instance.assignment, 
            percentage, 
            instance.is_late
        )
        
        instance.xp_earned = xp_earned
        instance.is_xp_awarded = True
        instance.save()
        
        # Update student's total XP
        instance.student.xp_points += xp_earned
        instance.student.save()
        
        # Send grade notification
        send_grade_notification(instance.id)

@receiver(post_save, sender=Assignment)
def publish_assignment(sender, instance, created, **kwargs):
    """Send notifications when assignment is published"""
    if instance.status == 'PUBLISHED' and not created:
        send_assignment_notification(instance.id)

@receiver(post_save, sender=ClassPost)
def analyze_class_post_toxicity(sender, instance, created, **kwargs):
    """AI toxicity analysis for class posts"""
    if created and instance.content:
        try:
            # Use existing toxicity analysis from social app
            toxicity_result = AIService.analyze_toxicity(
                instance.content, 
                instance.author
            )
            
            if 'error' not in toxicity_result:
                toxicity_score = toxicity_result.get('toxicity_score', 0)
                
                # Update post with toxicity score
                ClassPost.objects.filter(id=instance.id).update(
                    toxicity_score=toxicity_score
                )
                
                # Auto-moderate high toxicity posts
                if toxicity_score > 0.7:
                    ClassPost.objects.filter(id=instance.id).update(is_approved=False)
                    print(f"🚨 High toxicity class post flagged: Post #{instance.id}")
                    
        except Exception as e:
            print(f"❌ Error analyzing class post toxicity: {e}")

@receiver(post_save, sender=Comment)
def analyze_class_comment_toxicity(sender, instance, created, **kwargs):
    """AI toxicity analysis for class comments"""
    if created and instance.content:
        try:
            toxicity_result = AIService.analyze_toxicity(
                instance.content, 
                instance.author
            )
            
            if 'error' not in toxicity_result:
                toxicity_score = toxicity_result.get('toxicity_score', 0)
                
                # Update comment with toxicity score
                Comment.objects.filter(id=instance.id).update(
                    toxicity_score=toxicity_score
                )
                
                # Auto-remove high toxicity comments
                if toxicity_score > 0.8:
                    Comment.objects.filter(id=instance.id).update(is_approved=False)
                    print(f"🚨 High toxicity comment removed: Comment #{instance.id}")
                    
        except Exception as e:
            print(f"❌ Error analyzing class comment toxicity: {e}")

@receiver(m2m_changed, sender=Classroom.students.through)
def update_classroom_stats(sender, instance, action, **kwargs):
    """Update classroom statistics when students change"""
    if action in ['post_add', 'post_remove']:
        # Trigger analytics update
        update_classroom_analytics(instance.id)

@receiver(post_save, sender=Classroom)
def generate_class_code(sender, instance, created, **kwargs):
    """Generate class code if not provided"""
    if created and not instance.code:
        instance.code = instance.generate_class_code()
        instance.save()