from xml.dom.minidom import Comment
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import timedelta
import random
import string

from classroom.models import Attendance, ClassPost, Submission

class ClassroomAnalytics:
    @staticmethod
    def get_classroom_stats(classroom):
        # Get comprehensive statistics for a classroom
        total_students = classroom.student_count()
        total_assignments = classroom.assignments.filter(status='PUBLISHED').count()
        
        # Assignment completion
        submissions = Submission.objects.filter(
            assignment__classroom=classroom,
            status__in=['SUBMITTED', 'LATE', 'GRADED']
        )
        
        total_possible_submissions = total_students * total_assignments
        completion_rate = (submissions.count() / total_possible_submissions * 100) if total_possible_submissions > 0 else 0
        
        # Grade statistics
        graded_submissions = submissions.filter(grade__isnull=False)
        average_grade = graded_submissions.aggregate(avg=Avg('grade'))['avg'] or 0
        
        # Attendance (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        attendance = Attendance.objects.filter(
            classroom=classroom,
            date__gte=thirty_days_ago
        )
        attendance_rate = (attendance.filter(status='PRESENT').count() / attendance.count() * 100) if attendance.count() > 0 else 0
        
        # Engagement metrics
        posts_count = ClassPost.objects.filter(classroom=classroom).count()
        comments_count = Comment.objects.filter(post__classroom=classroom).count()
        
        return {
            'total_students': total_students,
            'total_assignments': total_assignments,
            'completion_rate': round(completion_rate, 2),
            'average_grade': float(average_grade),
            'attendance_rate': round(attendance_rate, 2),
            'engagement_score': posts_count + comments_count,
            'total_xp_awarded': sum(sub.xp_earned for sub in graded_submissions),
            'active_students': classroom.students.filter(last_login__gte=timezone.now()-timedelta(days=7)).count()
        }
    
    @staticmethod
    def get_student_progress(student, classroom):
        # Get progress analytics for a specific student
        submissions = Submission.objects.filter(
            student=student,
            assignment__classroom=classroom
        )
        
        graded_submissions = submissions.filter(grade__isnull=False)
        completed_assignments = submissions.filter(status__in=['SUBMITTED', 'LATE', 'GRADED'])
        total_assignments = classroom.assignments.filter(status='PUBLISHED').count()
        
        avg_grade = graded_submissions.aggregate(avg=Avg('grade'))['avg'] or 0
        submission_rate = (completed_assignments.count() / total_assignments * 100) if total_assignments > 0 else 0
        
        return {
            'assignments_completed': completed_assignments.count(),
            'assignments_total': total_assignments,
            'average_grade': float(avg_grade),
            'total_xp': sum(sub.xp_earned for sub in graded_submissions),
            'submission_rate': round(submission_rate, 2),
            'attendance_rate': ClassroomAnalytics.get_student_attendance_rate(student, classroom)
        }
    
    @staticmethod
    def get_student_attendance_rate(student, classroom):
        # Calculate student attendance rate
        thirty_days_ago = timezone.now() - timedelta(days=30)
        attendance = Attendance.objects.filter(
            classroom=classroom,
            student=student,
            date__gte=thirty_days_ago
        )
        present_count = attendance.filter(status='PRESENT').count()
        total_count = attendance.count()
        
        return round((present_count / total_count * 100) if total_count > 0 else 0, 2)

class GradeCalculator:
    @staticmethod
    def calculate_letter_grade(percentage):
        # Convert percentage to letter grade
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    @staticmethod
    def calculate_xp_reward(assignment, grade_percentage, is_late=False):
        # Calculate XP reward based on grade and timeliness
        base_xp = assignment.xp_reward
        
        # Grade-based multiplier
        if grade_percentage >= 90:
            multiplier = 1.0
        elif grade_percentage >= 80:
            multiplier = 0.8
        elif grade_percentage >= 70:
            multiplier = 0.6
        elif grade_percentage >= 60:
            multiplier = 0.4
        else:
            multiplier = 0.2
        
        # Late submission penalty
        if is_late:
            multiplier *= 0.5
        
        xp_earned = int(base_xp * multiplier)
        
        # Add bonus XP if applicable
        xp_earned += assignment.bonus_xp
        
        return max(0, xp_earned)
    
    @staticmethod
    def calculate_grade_percentage(points_earned, points_possible):
        # Calculate grade percentage
        if points_possible == 0:
            return 0
        return (points_earned / points_possible) * 100

class NotificationHelper:
    @staticmethod
    def create_assignment_notification(assignment):
        # Create notification for new assignment
        from .tasks import send_assignment_notification
        send_assignment_notification(assignment.id)
    
    @staticmethod
    def create_grade_notification(submission):
        # Create notification for graded assignment
        from .tasks import send_grade_notification
        send_grade_notification(submission.id)
    
    @staticmethod
    def create_classroom_invite_notification(classroom, student):
        # Send classroom invitation notification
        pass

class CodeGenerator:
    @staticmethod
    def generate_class_code(length=6):
        # Generate a unique class code
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choices(characters, k=length))
    
    @staticmethod
    def generate_assignment_code():
        # Generate assignment reference code
        return f"ASMT{random.randint(1000, 9999)}"

class DateHelper:
    @staticmethod
    def is_weekend(date):
        # Check if date is weekend
        return date.weekday() >= 5
    
    @staticmethod
    def get_upcoming_due_dates(student, days=7):
        # Get assignments due in the next specified days
        from .models import Assignment
        end_date = timezone.now() + timedelta(days=days)
        return Assignment.objects.filter(
            classroom__students=student,
            due_date__range=[timezone.now(), end_date],
            status='PUBLISHED'
        ).order_by('due_date')