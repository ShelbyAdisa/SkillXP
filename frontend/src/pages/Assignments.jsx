import React, { useEffect, useState, useRef } from 'react'
import DashboardLayout from '../components/layout/DashboardLayout'
import { useAuth } from '../context/AuthContext'
import Card from '../components/shared/Card'
import Button from '../components/shared/Button'
import Badge from '../components/shared/Badge'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import { Calendar, CheckSquare, DollarSign, BookOpen, X, CheckCircle } from 'lucide-react'

// --- DUMMY DATA SETUP ---
const ASSIGNMENT_STORAGE_KEY = 'skillxp_assignments';

const DUMMY_UPCOMING_ASSIGNMENTS_INITIAL = [
  {
    id: 'up1',
    title: "Newton's Laws of Motion Quiz",
    description: 'A short quiz covering the three laws of motion. Focus on conceptual understanding.',
    classroom_name: 'Physics 101: Fall 2024',
    due_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(), 
    max_score: 50,
    status: 'pending',
  },
  {
    id: 'up2',
    title: 'The Great Gatsby: Essay Outline',
    description: 'Submit a detailed outline for your literary analysis essay on The Great Gatsby. Include thesis statement.',
    classroom_name: 'English Literature: AP',
    due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), 
    max_score: 20,
    status: 'pending',
  },
];

const DUMMY_COMPLETED_ASSIGNMENTS_INITIAL = [
  {
    id: 'comp1',
    title: 'Ecology Field Report',
    description: 'Report on observations from the local park field trip. 500 words minimum.',
    classroom_name: 'Biology 201',
    due_date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    submitted_at: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
    max_score: 100,
    status: 'graded',
    score: 92,
    submitted_content: "Ecology Field Report: Local Park Observations\n\n[Simulated student work demonstrating observations and conclusions.]"
  },
];

// Teacher's view of assignments pending grade (separate state to simulate backend query)
const DUMMY_PENDING_GRADE_INITIAL = [
  {
    id: 'pg1',
    assignment_title: 'World War II Timeline Project',
    class_name: 'World History: Fall',
    student_name: 'Alex Johnson',
    due_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    submitted_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    max_score: 75,
    status: 'submitted', 
    submitted_content: "World War II Timeline: Key Events\n\n1. 1939: Germany invades Poland (start of war).\n2. 1941: Pearl Harbor attack (US enters war).\n3. 1944: D-Day invasion (turning point in Europe).\n4. 1945: Atomic bomb dropped on Japan (end of war)."
  },
];

const syncAssignmentsToLocalStorage = (upcoming, completed) => {
    localStorage.setItem(ASSIGNMENT_STORAGE_KEY, JSON.stringify({ upcoming, completed }));
};

const getAssignmentsFromLocalStorage = () => {
    const data = localStorage.getItem(ASSIGNMENT_STORAGE_KEY);
    if (data) {
        return JSON.parse(data);
    }
    return { 
        upcoming: DUMMY_UPCOMING_ASSIGNMENTS_INITIAL, 
        completed: DUMMY_COMPLETED_ASSIGNMENTS_INITIAL 
    };
};
// ----------------------------

// Reusable Notification Modal Component
const NotificationModal = ({ title, message, variant, onClose, onConfirm }) => {
    let colorClass = 'border-slate-500';
    let titleColor = 'text-slate-900';
    if (variant === 'success') {
      colorClass = 'border-green-500';
      titleColor = 'text-green-700';
    } else if (variant === 'danger') {
      colorClass = 'border-red-500';
      titleColor = 'text-red-700';
    }

    return (
      <div className="fixed inset-0 bg-gray-900 bg-opacity-50 z-[60] flex items-start justify-center p-4 sm:p-8">
        <Card className={`max-w-md w-full mt-20 p-6 border-t-4 ${colorClass} shadow-xl transform transition-all`}>
          <div className="flex justify-between items-start">
            <h3 className={`text-xl font-bold ${titleColor}`}>{title}</h3>
            <button onClick={onClose} className="text-slate-500 hover:text-slate-700 text-2xl ml-4">
              &times;
            </button>
          </div>
          <p className="mt-4 text-slate-700">{message}</p>
          <div className="mt-6 flex justify-end">
            <Button size="sm" variant="primary" color="slate" onClick={onConfirm || onClose}>
              Got It
            </Button>
          </div>
        </Card>
      </div>
    );
  };

// Post Assignment Modal
const PostAssignmentModal = ({ user, onPost, onClose }) => { 
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [className, setClassName] = useState('Grade 3 Math');
    const [dueDate, setDueDate] = useState('');
    const [maxScore, setMaxScore] = useState(50);
    const [submitError, setSubmitError] = useState(null);

    const handleSubmit = (e) => {
        e.preventDefault();
        setSubmitError(null);
        if (!title || !dueDate) {
            setSubmitError('Title and Due Date are required.');
            return;
        }

        const newAssignment = {
            id: `new_${Date.now()}`,
            title,
            description,
            classroom_name: className,
            due_date: new Date(dueDate).toISOString(),
            max_score: parseInt(maxScore, 10),
            status: 'pending',
            teacher_name: `${user.first_name} ${user.last_name}`,
            submitted_content: null,
        };

        onPost(newAssignment);
    };

    return (
        <div className="fixed inset-0 bg-gray-900 bg-opacity-90 z-50 overflow-y-auto p-4 sm:p-8">
             <Card className="max-w-3xl mx-auto my-8 p-8">
                 <div className="flex justify-between items-start mb-6 border-b pb-4">
                    <h2 className="text-2xl font-bold text-slate-900">Post New Assignment</h2>
                    <Button variant="outline" color="slate" onClick={onClose}><X className="w-5 h-5" /></Button>
                </div>
                <form onSubmit={handleSubmit} className="space-y-4">
                    {submitError && (
                        <div className="p-3 text-sm font-medium text-red-700 bg-red-100 border border-red-300 rounded-lg">
                            Error: {submitError}
                        </div>
                    )}
                    
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Title</label>
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                            placeholder="e.g., Chapter 4 Review Quiz"
                            required
                        />
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Class/Course</label>
                        <select
                            value={className}
                            onChange={(e) => setClassName(e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                        >
                            <option value="Grade 3 Math">Grade 3 Math</option>
                            <option value="Elementary Science">Elementary Science</option>
                            <option value="Creative Writing">Creative Writing</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg h-24"
                            placeholder="Detailed instructions for students..."
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Due Date</label>
                            <input
                                type="date"
                                value={dueDate}
                                onChange={(e) => setDueDate(e.target.value)}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Max Score</label>
                            <input
                                type="number"
                                value={maxScore}
                                onChange={(e) => setMaxScore(e.target.value)}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                                min="1"
                            />
                        </div>
                    </div>
                    
                    <Button type="submit" variant="primary" color="success" className="w-full mt-6">
                        Post Assignment
                    </Button>
                </form>
            </Card>
        </div>
    );
};

// --- GRADE MODAL COMPONENT ---
const GradeModal = ({ assignment, onGrade, onClose }) => {
    const [score, setScore] = useState(assignment.max_score);
    const [feedback, setFeedback] = useState(`Great work, ${assignment.student_name}!`);
    const [isSaving, setIsSaving] = useState(false);

    const handleFinalize = (e) => {
        e.preventDefault();
        setIsSaving(true);
        const finalScore = parseInt(score, 10);
        
        if (isNaN(finalScore) || finalScore < 0 || finalScore > assignment.max_score) {
            alert(`Score must be between 0 and ${assignment.max_score}.`);
            setIsSaving(false);
            return;
        }

        setTimeout(() => {
            onGrade(assignment.id, finalScore, feedback);
            setIsSaving(false);
        }, 500);
    };

    return (
        <div className="fixed inset-0 bg-gray-900 bg-opacity-90 z-50 overflow-y-auto p-4 sm:p-8">
            <Card className="max-w-4xl mx-auto my-8 p-8">
                <div className="flex justify-between items-start mb-6 border-b pb-4">
                    <div>
                        <h2 className="text-3xl font-bold text-slate-900">Grading: {assignment.assignment_title}</h2>
                        <p className="text-md text-slate-600 mt-1">Student: {assignment.student_name} &bull; Class: {assignment.class_name}</p>
                    </div>
                    <Button variant="outline" color="slate" onClick={onClose}>
                        Close
                    </Button>
                </div>

                <div className="space-y-4 mb-8">
                    <h3 className="text-xl font-semibold text-slate-800">Submitted Content:</h3>
                    <textarea
                        readOnly
                        className="w-full border border-slate-300 rounded-lg p-4 h-64 bg-slate-50 text-slate-800 font-mono resize-none"
                        defaultValue={assignment.submitted_content || "No submitted content found in dummy data."}
                    />
                </div>

                <form onSubmit={handleFinalize} className="p-6 bg-blue-50 border-dashed border-2 border-blue-200">
                    <h3 className="text-lg font-semibold text-blue-800 mb-4">Final Grade & Feedback</h3>
                    <div className="flex items-center space-x-4 mb-4">
                        <label className="text-sm font-medium text-slate-700">Score ({assignment.max_score} Points Max):</label>
                        <input
                            type="number"
                            value={score}
                            onChange={(e) => setScore(e.target.value)}
                            className="w-20 px-2 py-1 border border-slate-300 rounded-lg"
                            min="0"
                            max={assignment.max_score}
                            required
                        />
                    </div>
                    <textarea
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        className="w-full border border-slate-300 rounded-lg p-3 h-24 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter detailed feedback here..."
                        required
                    />
                    <Button type="submit" variant="primary" color="success" className="mt-4" disabled={isSaving}>
                        {isSaving ? 'Saving...' : 'Finalize Grade & Send Feedback'}
                    </Button>
                </form>
            </Card>
        </div>
    );
};
// ---------------------------------


const Assignments = () => {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [upcoming, setUpcoming] = useState([])
  const [pendingGrade, setPendingGrade] = useState([]) // Teacher's grading queue
  const [completed, setCompleted] = useState([])
  const [activeTab, setActiveTab] = useState('upcoming')
  const [activeAssignmentId, setActiveAssignmentId] = useState(null) 
  const [viewingSubmissionId, setViewingSubmissionId] = useState(null)
  const [notificationModal, setNotificationModal] = useState(null)
  const [showPostModal, setShowPostModal] = useState(false); 
  const [activeGradingAssignment, setActiveGradingAssignment] = useState(null); 

  const isTeacher = user?.role === 'TEACHER';
  
  const showModal = (title, message, variant = 'primary') => {
    setNotificationModal({ title, message, variant });
  };
  
  const closeModal = () => {
    setNotificationModal(null);
  };

  // 1. CRITICAL FIX: Use a ref to strictly track if initial data fetch has happened.
  const isDataLoadedRef = useRef(false);

  useEffect(() => {
    if (!user?.role) return;

    const loadDummyData = async () => {
      // Guard against running multiple times due to unexpected re-renders
      if (isDataLoadedRef.current) return; 
      isDataLoadedRef.current = true; // Set flag immediately

      setLoading(true); 
      setError(null);
      
      await new Promise(resolve => setTimeout(resolve, 500)); 

      if (isTeacher) {
        setPendingGrade(DUMMY_PENDING_GRADE_INITIAL)
      } else {
        const localData = getAssignmentsFromLocalStorage();
        setUpcoming(localData.upcoming) 
        setCompleted(localData.completed)
      }
      setLoading(false);
    }
    loadDummyData();
  }, [user?.role]) 

  // 2. Local storage synchronization.
  useEffect(() => {
    if (!isTeacher) {
      // Only sync if data has been fetched once and arrays are ready
      if (isDataLoadedRef.current || upcoming.length > 0 || completed.length > 0) {
        syncAssignmentsToLocalStorage(upcoming, completed);
      }
    }
  }, [upcoming, completed, isTeacher]); 

  // URL query param handler
  useEffect(() => {
    if (typeof window !== 'undefined' && isTeacher && window.location.search.includes('action=new')) {
        setShowPostModal(true);
        window.history.replaceState(null, '', window.location.pathname); 
    }
  }, [isTeacher]);

  // --- TEACHER WORKFLOW ---
  const handlePostAssignment = (newAssignment) => {
    const localData = getAssignmentsFromLocalStorage();
    localData.upcoming.push(newAssignment);
    syncAssignmentsToLocalStorage(localData.upcoming, localData.completed);

    setShowPostModal(false);
    showModal(
        'Assignment Posted! 📢',
        `${newAssignment.title} has been successfully assigned to ${newAssignment.classroom_name}.`,
        'success'
    );
  };

  const handleOpenGradeModal = (assignment) => {
      setActiveGradingAssignment(assignment);
  };

  const handleGradeAssignment = (assignmentId, score, feedback) => {
      const gradedAssignment = pendingGrade.find(a => a.id === assignmentId);
      
      if (!gradedAssignment) {
          showModal('Error', 'Assignment not found in queue.', 'danger');
          setActiveGradingAssignment(null);
          return;
      }
      
      setPendingGrade(prev => prev.filter(a => a.id !== assignmentId));

      const studentLocalData = getAssignmentsFromLocalStorage();
      const studentCompletedAssignment = {
          id: gradedAssignment.id,
          title: gradedAssignment.assignment_title,
          classroom_name: gradedAssignment.class_name,
          due_date: gradedAssignment.due_date,
          submitted_at: gradedAssignment.submitted_at,
          max_score: gradedAssignment.max_score,
          status: 'graded',
          score: score,
          feedback: feedback, 
          submitted_content: gradedAssignment.submitted_content
      };

      const upcomingIndex = studentLocalData.upcoming.findIndex(a => a.id === gradedAssignment.id);
      if (upcomingIndex !== -1) {
          studentLocalData.upcoming.splice(upcomingIndex, 1);
      }
      
      studentLocalData.completed.push(studentCompletedAssignment);
      syncAssignmentsToLocalStorage(studentLocalData.upcoming, studentLocalData.completed);

      setActiveGradingAssignment(null); // Close the modal
      showModal(
          'Grade Finalized! 🎉',
          `${gradedAssignment.assignment_title} for ${gradedAssignment.student_name} scored ${score}/${gradedAssignment.max_score} and feedback has been sent.`,
          'success'
      );
  };
  // -------------------------
  
  // --- STUDENT WORKFLOW ---
  const handleStartAssignment = (assignment) => {
    setActiveAssignmentId(assignment.id);
    setViewingSubmissionId(null);
    showModal(
        'Assignment Started! 🚀',
        `You are now working on: ${assignment.title}. Click "Submit Assignment" to simulate completion.`,
        'success'
    );
  }

  const handleSubmission = (assignment) => {
    const submittedAssignment = {
      ...assignment,
      status: 'submitted',
      submitted_at: new Date().toISOString(),
      submitted_content: `[Simulated submission for ${assignment.title} - Content completed on ${new Date().toLocaleDateString()}. This is now pending grading.]`
    }

    setUpcoming(prev => prev.filter(a => a.id !== assignment.id))
    setCompleted(prev => [submittedAssignment, ...prev])

    setActiveAssignmentId(null)
    setActiveTab('completed')
    
    showModal(
        'Submission Successful! 🎉',
        `${assignment.title} has been moved to your Completed tab, pending teacher review.`,
        'success'
    );
  }

  const handleViewSubmission = (assignment) => {
    setViewingSubmissionId(assignment.id);
    setActiveAssignmentId(null);
  }
  // ---------------------------------------------------------------------------------

  // --- GENERAL UI RENDERERS ---
  const renderAssignmentCard = (assignment, isTeacher = false) => {
    // ... (content remains the same)
      const getStatusBadge = (status, dueDate) => {
        let finalStatus = status;
        
        if (!isTeacher && status === 'pending' && dueDate) {
          const now = new Date();
          const due = new Date(dueDate);
          if (due < now) {
            finalStatus = 'overdue';
          }
        }

        const statusMap = {
          pending: { variant: 'default', text: 'Pending' },
          submitted: { variant: 'slate', text: 'Submitted' },
          graded: { variant: 'success', text: 'Graded' },
          overdue: { variant: 'danger', text: 'Overdue' },
        }
        const config = statusMap[finalStatus] || statusMap.pending
        return <Badge variant={config.variant}>{config.text}</Badge>
      }

      const getDaysUntilDue = (dueDate) => {
        const now = new Date()
        const due = new Date(dueDate)
        const diffTime = due - now
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
        
        if (diffDays < 0) return 'Overdue'
        if (diffDays === 0) return 'Due today'
        if (diffDays === 1) return 'Due tomorrow'
        return `Due in ${diffDays} days`
      }
    return (
    <Card key={assignment.id} className="hover:shadow-md transition-shadow">
      <div className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-slate-900 mb-1">
              {assignment.title || assignment.assignment_title}
            </h3>
            <p className="text-sm text-slate-600">
              <BookOpen className="w-3 h-3 inline mr-1" />
              {assignment.classroom_name || assignment.class_name}
            </p>
            {isTeacher && assignment.student_name && (
              <p className="text-sm text-slate-500 mt-1">
                Student: {assignment.student_name}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2 ml-4">
            {assignment.status && getStatusBadge(assignment.status, assignment.due_date)}
            {assignment.score && assignment.status === 'graded' && (
              <Badge variant="primary">{assignment.score}/{assignment.max_score}</Badge>
            )}
          </div>
        </div>
        {assignment.description && (
          <p className="text-sm text-slate-600 mb-3 line-clamp-2">
            {assignment.description}
          </p>
        )}
        <div className="flex items-center justify-between pt-3 border-t border-slate-100">
          <div className="flex items-center gap-4 text-sm text-slate-500">
            {assignment.due_date && (
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {getDaysUntilDue(assignment.due_date)}
              </span>
            )}
            {assignment.max_score && (
              <span className="flex items-center gap-1">
                <DollarSign className="w-4 h-4" />
                {assignment.max_score} points
              </span>
            )}
            {assignment.submitted_at && (
              <span className="text-xs">
                Submitted {new Date(assignment.submitted_at).toLocaleDateString()}
              </span>
            )}
          </div>
          <div className="flex gap-2">
            {isTeacher ? (
              <Button size="sm" variant="primary" color="slate" onClick={() => handleOpenGradeModal(assignment)}>
                Grade
              </Button>
            ) : (
              <>
                {assignment.status === 'graded' || assignment.status === 'submitted' ? (
                  <Button 
                    size="sm" 
                    variant="outline" 
                    color="slate"
                    onClick={() => handleViewSubmission(assignment)}
                  >
                    {assignment.status === 'graded' ? 'View Feedback' : 'View Submission'}
                  </Button>
                ) : (
                  <Button 
                    size="sm" 
                    variant="primary" 
                    color="slate"
                    onClick={() => handleStartAssignment(assignment)}
                  >
                    Start Assignment
                  </Button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </Card>
  )}
  
  // Renders the full assignment workspace view (modal)
  const renderAssignmentContent = () => {
    const activeAssignment = upcoming.find(a => a.id === activeAssignmentId)

    if (!activeAssignment) return null;

    return (
      <div className="fixed inset-0 bg-gray-900 bg-opacity-90 z-50 overflow-y-auto p-4 sm:p-8">
        <Card className="max-w-4xl mx-auto my-8 p-8">
          <div className="flex justify-between items-start mb-6 border-b pb-4">
            <div>
              <h2 className="text-3xl font-bold text-slate-900">{activeAssignment.title}</h2>
              <p className="text-md text-slate-600 mt-1">Class: {activeAssignment.classroom_name}</p>
            </div>
            <Button variant="outline" color="slate" onClick={() => setActiveAssignmentId(null)}>
              Close
            </Button>
          </div>

          <div className="space-y-4 mb-8">
            <h3 className="text-xl font-semibold text-slate-800">Instructions:</h3>
            <p className="text-slate-700">{activeAssignment.description}</p>
            <p className="text-sm text-slate-500">Due: {new Date(activeAssignment.due_date).toLocaleDateString()}</p>
            <p className="text-sm text-slate-500">Possible Score: {activeAssignment.max_score} points</p>
          </div>

          <Card className="p-6 bg-slate-50 border-dashed border-2 border-slate-200">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Your Submission Area (Simulated)</h3>
            <textarea
              className="w-full border border-slate-300 rounded-lg p-3 h-32 focus:outline-none focus:ring-2 focus:ring-slate-500"
              placeholder="Type your answer, upload your file, or complete the quiz here..."
              defaultValue={`[Simulated Student Work for: ${activeAssignment.title}]`}
            />
            <Button 
              variant="primary" 
              color="success" 
              className="mt-4" 
              onClick={() => handleSubmission(activeAssignment)}
            >
              Submit Assignment
            </Button>
          </Card>
        </Card>
      </div>
    );
  };

  // Renders the submitted assignment content (modal)
  const renderSubmissionContent = () => {
    const submittedAssignment = completed.find(a => a.id === viewingSubmissionId) || upcoming.find(a => a.id === viewingSubmissionId)

    if (!submittedAssignment || !submittedAssignment.submitted_content) return null;

    return (
      <div className="fixed inset-0 bg-gray-900 bg-opacity-90 z-50 overflow-y-auto p-4 sm:p-8">
        <Card className="max-w-4xl mx-auto my-8 p-8">
          <div className="flex justify-between items-start mb-6 border-b pb-4">
            <div>
              <h2 className="text-3xl font-bold text-slate-900">Viewing Submission: {submittedAssignment.title}</h2>
              <p className="text-md text-slate-600 mt-1">Class: {submittedAssignment.classroom_name || submittedAssignment.class_name}</p>
              <p className="text-sm text-slate-500">Submitted on: {new Date(submittedAssignment.submitted_at).toLocaleDateString()}</p>
            </div>
            <Button variant="outline" color="slate" onClick={() => setViewingSubmissionId(null)}>
              Close View
            </Button>
          </div>

          {submittedAssignment.status === 'graded' && (
             <div className="mb-6 p-4 bg-green-50 border border-green-300 rounded-lg">
                <p className="font-semibold text-green-800">Final Score: {submittedAssignment.score}/{submittedAssignment.max_score}</p>
                <p className="text-sm text-green-700 mt-1">Teacher Feedback: Great use of evidence! See comments in the margin (simulated).</p>
             </div>
          )}

          <div className="space-y-4 mb-8">
            <h3 className="text-xl font-semibold text-slate-800">Submitted Work:</h3>
            <textarea
              readOnly
              className="w-full border border-slate-300 rounded-lg p-4 h-64 bg-white text-slate-800 font-mono resize-none focus:outline-none"
              defaultValue={submittedAssignment.submitted_content || 'No content found for this submission.'}
            />
          </div>
        </Card>
      </div>
    );
  };
  
  if (loading) {
    return (
      <DashboardLayout role={user?.role}>
        <div className="flex items-center justify-center min-h-[60vh]">
          <LoadingSpinner text="Loading assignments..." />
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout role={user?.role}>
      {activeAssignmentId && renderAssignmentContent()}
      {viewingSubmissionId && renderSubmissionContent()}
      
      {notificationModal && (
        <NotificationModal 
          title={notificationModal.title}
          message={notificationModal.message}
          variant={notificationModal.variant}
          onClose={closeModal}
        />
      )}

      {isTeacher && activeGradingAssignment && (
          <GradeModal
              assignment={activeGradingAssignment}
              onGrade={handleGradeAssignment}
              onClose={() => setActiveGradingAssignment(null)}
          />
      )}
      
      {isTeacher && showPostModal && (
          <PostAssignmentModal
              user={user}
              onPost={handlePostAssignment}
              onClose={() => setShowPostModal(false)}
          />
      )}
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              {isTeacher ? 'Grading Queue' : 'Assignments'}
            </h1>
            <p className="text-slate-600">
              {isTeacher 
                ? 'Review and grade student submissions' 
                : 'View and manage your assignments'}
            </p>
          </div>
          {isTeacher && (
              <Button 
                  variant="primary" 
                  color="success" 
                  onClick={() => setShowPostModal(true)}
              >
                  <CheckSquare className="w-5 h-5 mr-2" />
                  Post New Assignment
              </Button>
          )}
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
            <p className="font-medium">Error loading data</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Student View - Tabs */}
        {!isTeacher && (
          <div className="mb-6 border-b border-slate-200">
            <div className="flex gap-6">
              <button
                onClick={() => setActiveTab('upcoming')}
                className={`pb-3 px-1 border-b-2 font-medium transition-colors ${
                  activeTab === 'upcoming'
                    ? 'border-slate-900 text-slate-900'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
                }`}
              >
                Upcoming ({upcoming.length})
              </button>
              <button
                onClick={() => setActiveTab('completed')}
                className={`pb-3 px-1 border-b-2 font-medium transition-colors ${
                  activeTab === 'completed'
                    ? 'border-slate-900 text-slate-900'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
                }`}
              >
                Completed ({completed.length})
              </button>
            </div>
          </div>
        )}

        {/* Content */}
        <div>
          {isTeacher ? (
            // Teacher View
            <div>
              {pendingGrade.length === 0 ? (
                <Card>
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <CheckSquare className="w-8 h-8 text-slate-400" />
                    </div>
                    <h3 className="text-lg font-medium text-slate-900 mb-2">All caught up!</h3>
                    <p className="text-slate-600">No submissions pending grading at this time</p>
                  </div>
                </Card>
              ) : (
                <div className="space-y-4">
                  {pendingGrade.map(a => renderAssignmentCard(a, true))}
                </div>
              )}
            </div>
          ) : (
            // Student View
            <div>
              {activeTab === 'upcoming' && (
                <div>
                  {upcoming.length === 0 ? (
                    <Card>
                      <div className="text-center py-12">
                        <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                          <BookOpen className="w-8 h-8 text-slate-400" />
                        </div>
                        <h3 className="text-lg font-medium text-slate-900 mb-2">No upcoming assignments</h3>
                        <p className="text-slate-600">You're all caught up! Check back later for new assignments</p>
                      </div>
                    </Card>
                  ) : (
                    <div className="space-y-4">
                      {upcoming.map(a => renderAssignmentCard(a, false))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'completed' && (
                <div>
                  {completed.length === 0 ? (
                    <Card>
                      <div className="text-center py-12">
                        <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                          <CheckSquare className="w-8 h-8 text-slate-400" />
                        </div>
                        <h3 className="text-lg font-medium text-slate-900 mb-2">No completed assignments yet</h3>
                        <p className="text-slate-600">Completed assignments will appear here</p>
                      </div>
                    </Card>
                  ) : (
                    <div className="space-y-4">
                      {completed.map(a => renderAssignmentCard(a, false))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}

export default Assignments