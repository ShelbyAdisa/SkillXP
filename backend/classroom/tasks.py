from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging

from .models import Assignment, Submission, Classroom, Enrollment, Attendance
from users.models import User

# Set up logger
logger = logging.getLogger(__name__)

def send_assignment_notification(assignment_id):
    # Send notifications for new assignment
    try:
        assignment = Assignment.objects.get(id=assignment_id)
        
        # Only send notifications for published assignments
        if assignment.status != Assignment.AssignmentStatus.PUBLISHED:
            logger.info(f"Assignment {assignment_id} is not published, skipping notifications")
            return
        
        classroom = assignment.classroom
        
        # Get all enrolled active students
        students = classroom.students.filter(
            enrollment__status=Enrollment.EnrollmentStatus.ACTIVE
        )
        
        email_count = 0
        for student in students:
            try:
                subject = f" New Assignment: {assignment.title}"
                message = f"""
                                Hello {student.first_name},

                                A new assignment has been posted in {classroom.name}:

                                Title: {assignment.title}
                                Type: {assignment.get_assignment_type_display()}
                                Due Date: {assignment.due_date.strftime('%B %d, %Y at %I:%M %p')}
                                Points: {assignment.points}
                                XP Reward: {assignment.xp_reward}

                                Description:
                                {assignment.description[:200]}{'...' if len(assignment.description) > 200 else ''}

                                Please log in to SkillXP Nexus to view the complete assignment details and submit your work.

                                Best regards,
                                {classroom.teacher.get_display_name()}
                                {assignment.classroom.school.name}
                """.strip()

                # Only send email if email backend is configured and student has email
                if hasattr(settings, 'EMAIL_BACKEND') and student.email:
                    send_mail(
                        subject,
                        message,
                        getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@skillxp.com'),
                        [student.email],
                        fail_silently=False,
                    )
                    email_count += 1
                    logger.info(f"Sent assignment notification to {student.email}")
                
            except Exception as e:
                logger.error(f"Failed to send email to {student.email}: {str(e)}")
                continue
        
        logger.info(f"Successfully sent {email_count} assignment notifications for assignment {assignment_id}")
        
    except Assignment.DoesNotExist:
        logger.error(f"Assignment {assignment_id} not found")
    except Exception as e:
        logger.error(f"Error sending assignment notifications: {str(e)}")

def send_grade_notification(submission_id):
    # Send notification when assignment is graded
    try:
        submission = Submission.objects.select_related(
            'student', 'assignment', 'assignment__classroom', 'assignment__classroom__teacher'
        ).get(id=submission_id)
        
        student = submission.student
        assignment = submission.assignment
        
        # Only send if submission is graded and has a grade
        if not submission.grade or submission.status != Submission.SubmissionStatus.GRADED:
            logger.info(f"Submission {submission_id} is not graded, skipping notification")
            return
        
        subject = f" Assignment Graded: {assignment.title}"
        message = f"""
                    Hello {student.first_name},

                    Your assignment "{assignment.title}" has been graded.

                    Grade: {submission.grade}/{assignment.points} ({submission.grade_percentage:.1f}%)
                     XP Earned: {submission.xp_earned}
                    {" Late Submission" if submission.is_late else " Submitted on Time"}

                    Feedback:
                    {submission.feedback or 'No additional feedback provided.'}

                    You can view the detailed feedback and your submission in SkillXP Nexus.

                    Best regards,
                    {assignment.classroom.teacher.get_display_name()}
                    {assignment.classroom.school.name}
                 """.strip()

        if hasattr(settings, 'EMAIL_BACKEND') and student.email:
            send_mail(
                subject,
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@skillxp.com'),
                [student.email],
                fail_silently=False,
            )
            logger.info(f"Sent grade notification to {student.email} for submission {submission_id}")
        
    except Submission.DoesNotExist:
        logger.error(f"Submission {submission_id} not found")
    except Exception as e:
        logger.error(f"Error sending grade notification: {str(e)}")

def check_late_submissions():
    # Check for and mark late submissions
    try:
        now = timezone.now()
        assignments = Assignment.objects.filter(
            due_date__lt=now,
            status=Assignment.AssignmentStatus.PUBLISHED
        )
        
        total_updated = 0
        for assignment in assignments:
            late_submissions = Submission.objects.filter(
                assignment=assignment,
                submitted_at__gt=assignment.due_date,
                status=Submission.SubmissionStatus.SUBMITTED
            )
            
            for submission in late_submissions:
                submission.status = Submission.SubmissionStatus.LATE
                submission.save()
                total_updated += 1
        
        logger.info(f"Marked {total_updated} submissions as late")
        return total_updated
        
    except Exception as e:
        logger.error(f"Error checking late submissions: {str(e)}")
        return 0

def update_classroom_analytics(classroom_id):
    # Update analytics for a classroom
    try:
        from .utils import ClassroomAnalytics
        
        classroom = Classroom.objects.get(id=classroom_id)
        stats = ClassroomAnalytics.get_classroom_stats(classroom)
        
        # Update student progress records
        students = classroom.students.all()
        for student in students:
            progress, created = StudentProgress.objects.get_or_create(
                student=student,
                classroom=classroom
            )
            
            # Update progress metrics
            student_stats = ClassroomAnalytics.get_student_progress(student, classroom)
            progress.assignments_completed = student_stats['assignments_completed']
            progress.assignments_total = student_stats['assignments_total']
            progress.average_grade = student_stats['average_grade']
            progress.attendance_rate = student_stats['attendance_rate']
            progress.xp_earned = student_stats['total_xp']
            progress.last_activity = timezone.now()
            progress.save()
        
        logger.info(f"Updated analytics for classroom {classroom_id}")
        return stats
        
    except Classroom.DoesNotExist:
        logger.error(f"Classroom {classroom_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error updating classroom analytics: {str(e)}")
        return None

def send_due_date_reminders():
    # Send reminders for assignments due soon
    try:
        tomorrow = timezone.now() + timedelta(days=1)
        upcoming_assignments = Assignment.objects.filter(
            due_date__range=[timezone.now(), tomorrow],
            status=Assignment.AssignmentStatus.PUBLISHED
        )
        
        total_reminders = 0
        for assignment in upcoming_assignments:
            students = assignment.classroom.students.filter(
                enrollment__status=Enrollment.EnrollmentStatus.ACTIVE
            )
            
            for student in students:
                # Check if student hasn't submitted yet
                if not Submission.objects.filter(
                    assignment=assignment, 
                    student=student, 
                    status__in=[Submission.SubmissionStatus.SUBMITTED, Submission.SubmissionStatus.LATE, Submission.SubmissionStatus.GRADED]
                ).exists():
                    
                    subject = f"Reminder: {assignment.title} Due Soon"
                    message = f"""
                                    Hello {student.first_name},

                                    This is a friendly reminder that your assignment "{assignment.title}" is due soon.

                                    Assignment: {assignment.title}
                                    Due Date: {assignment.due_date.strftime('%B %d, %Y at %I:%M %p')}
                                    Points: {assignment.points}

                                    You haven't submitted this assignment yet. Please make sure to submit it before the due date.

                                    Best regards,
                                    {assignment.classroom.teacher.get_display_name()}
                                    {assignment.classroom.school.name}
                            """.strip()

                    if hasattr(settings, 'EMAIL_BACKEND') and student.email:
                        send_mail(
                            subject,
                            message,
                            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@skillxp.com'),
                            [student.email],
                            fail_silently=False,
                        )
                        total_reminders += 1
        
        logger.info(f"Sent {total_reminders} due date reminders")
        return total_reminders
        
    except Exception as e:
        logger.error(f"Error sending due date reminders: {str(e)}")
        return 0

def update_attendance_records():
    # Update attendance records for today
    try:
        today = timezone.now().date()
        classrooms = Classroom.objects.filter(is_active=True)
        
        total_created = 0
        for classroom in classrooms:
            # Check if attendance already recorded for today
            existing_records = Attendance.objects.filter(
                classroom=classroom,
                date=today
            )
            
            if not existing_records.exists():
                # Create attendance records for all students
                students = classroom.students.filter(
                    enrollment__status=Enrollment.EnrollmentStatus.ACTIVE
                )
                
                for student in students:
                    Attendance.objects.create(
                        classroom=classroom,
                        student=student,
                        date=today,
                        status=Attendance.Status.ABSENT  # Default to absent
                    )
                    total_created += 1
        
        logger.info(f"Created {total_created} attendance records for today")
        return total_created
        
    except Exception as e:
        logger.error(f"Error updating attendance records: {str(e)}")
        return 0

def send_weekly_progress_report():
    # Send weekly progress reports to students
    try:
        one_week_ago = timezone.now() - timedelta(days=7)
        students = User.objects.filter(
            role=User.Role.STUDENT,
            is_active=True
        )
        
        total_reports = 0
        for student in students:
            try:
                # Get student's active classrooms
                classrooms = Classroom.objects.filter(
                    students=student,
                    is_active=True
                )
                
                if not classrooms.exists():
                    continue
                
                progress_data = []
                total_xp_earned = 0
                assignments_completed = 0
                
                for classroom in classrooms:
                    stats = ClassroomAnalytics.get_student_progress(student, classroom)
                    progress_data.append({
                        'classroom': classroom.name,
                        'completion_rate': stats['submission_rate'],
                        'average_grade': stats['average_grade'],
                        'xp_earned': stats['total_xp']
                    })
                    total_xp_earned += stats['total_xp']
                    assignments_completed += stats['assignments_completed']
                
                subject = f"Your Weekly Progress Report - {timezone.now().strftime('%B %d, %Y')}"
                message = f"""
                            Hello {student.first_name},

                            Here's your weekly progress report:

                            Total XP Earned This Week: {total_xp_earned}
                            Assignments Completed: {assignments_completed}

                            Classroom Progress:
                            """ + "\n".join([
                                f"• {data['classroom']}: {data['completion_rate']}% completion, Grade: {data['average_grade']:.1f}%, XP: {data['xp_earned']}"
                                for data in progress_data
                            ]) + f"""

                            Keep up the great work! Log in to SkillXP Nexus to see detailed progress and upcoming assignments.

                            Best regards,
                            The SkillXP Nexus Team
                        """.strip()

                if hasattr(settings, 'EMAIL_BACKEND') and student.email:
                    send_mail(
                        subject,
                        message,
                        getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@skillxp.com'),
                        [student.email],
                        fail_silently=False,
                    )
                    total_reports += 1
                    
            except Exception as e:
                logger.error(f"Error generating progress report for {student.email}: {str(e)}")
                continue
        
        logger.info(f"Sent {total_reports} weekly progress reports")
        return total_reports
        
    except Exception as e:
        logger.error(f"Error sending weekly progress reports: {str(e)}")
        return 0

def cleanup_old_data():
    # Clean up old data
    try:
        # Delete attendance records older than 1 year
        one_year_ago = timezone.now() - timedelta(days=365)
        old_attendance = Attendance.objects.filter(date__lt=one_year_ago)
        attendance_count = old_attendance.count()
        old_attendance.delete()
        
        # Delete old submission drafts (older than 30 days and not submitted)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        old_drafts = Submission.objects.filter(
            status=Submission.SubmissionStatus.DRAFT,
            last_modified__lt=thirty_days_ago
        )
        drafts_count = old_drafts.count()
        old_drafts.delete()
        
        logger.info(f"Cleaned up {attendance_count} old attendance records and {drafts_count} old drafts")
        return {
            'attendance_records': attendance_count,
            'draft_submissions': drafts_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {str(e)}")
        return {'error': str(e)}

# Import here to avoid circular imports
from .models import StudentProgress
from .utils import ClassroomAnalytics