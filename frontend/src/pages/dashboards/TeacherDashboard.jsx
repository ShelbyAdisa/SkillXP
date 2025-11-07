import React, { useState } from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../context/AuthContext'
import Card from '../../components/shared/Card'
import Button from '../../components/shared/Button'
// Assuming StatCard is available globally or defined in this file (as per previous fix)
// import StatCard from '../../components/shared/StatCard' 
import { BookOpenText, CheckSquare, UsersRound, ArrowRight, TrendingUp, DollarSign } from 'lucide-react'

// --- SELF-CONTAINED StatCard Component (Ensures correct icon rendering) ---
const StatCard = ({ title, value, icon: Icon, color, linkPath }) => {
    return (
        <Card className="p-5 flex items-center justify-between">
            <div>
                <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
                <h3 className="text-2xl font-bold text-slate-900">{value}</h3>
            </div>
            <div className ={`w-10 h-10 rounded-full flex items-center justify-center ${color}`}>
                {/* Correctly render the icon component using JSX syntax */}
                <Icon className="w-5 h-5 text-white" />
            </div>
        </Card>
    );
};


// --- NEW GRADE MODAL COMPONENT ---
const GradeModal = ({ assignment, onClose }) => (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-90 z-50 overflow-y-auto p-4 sm:p-8">
        <Card className="max-w-4xl mx-auto my-8 p-8">
            <div className="flex justify-between items-start mb-6 border-b pb-4">
                <div>
                    <h2 className="text-3xl font-bold text-slate-900">Grading: {assignment.assignment}</h2>
                    <p className="text-md text-slate-600 mt-1">Student: {assignment.student} &bull; Class: {assignment.class}</p>
                </div>
                <Button variant="outline" color="slate" onClick={onClose}>
                    Close
                </Button>
            </div>

            <div className="space-y-4 mb-8">
                <h3 className="text-xl font-semibold text-slate-800">Submitted Content (Simulated)</h3>
                <textarea
                    readOnly
                    className="w-full border border-slate-300 rounded-lg p-4 h-64 bg-slate-50 text-slate-800 font-mono resize-none"
                    defaultValue={`[Simulated Student Submission for ${assignment.assignment}] 
${assignment.student} submitted this work on ${assignment.due} (Placeholder content since the actual submission isn't linked to this data array).`}
                />
            </div>

            <Card className="p-6 bg-blue-50 border-dashed border-2 border-blue-200">
                <h3 className="text-lg font-semibold text-blue-800 mb-4">Grading & Feedback</h3>
                <div className="flex items-center space-x-4 mb-4">
                    <label className="text-sm font-medium text-slate-700">Score ({assignment.max_score || 100} Points Max):</label>
                    <input
                        type="number"
                        defaultValue={85} // Simulated grade
                        className="w-20 px-2 py-1 border border-slate-300 rounded-lg"
                        min="0"
                        max={assignment.max_score || 100}
                    />
                </div>
                <textarea
                    className="w-full border border-slate-300 rounded-lg p-3 h-24 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter detailed feedback here..."
                    defaultValue="Excellent effort, particularly on the timeline accuracy. Minor points lost for lack of detail in source citation."
                />
                <Button variant="primary" color="success" className="mt-4">
                    Finalize Grade & Send Feedback
                </Button>
            </Card>
        </Card>
    </div>
);
// ---------------------------------

// --- DUMMY DATA ---
const DUMMY_TEACHER_STATS = {
    totalClasses: 3,
    totalStudents: 78,
    pendingGrading: 5,
    recentScoreAvg: 88,
}

const DUMMY_CLASS_OVERVIEW = [
    { id: 1, name: 'Grade 3 Math', code: 'GM301', students: 25, avgScore: 92, lastActivity: 'Yesterday' },
    { id: 2, name: 'Elementary Science', code: 'ES202', students: 28, avgScore: 85, lastActivity: '2 days ago' },
    { id: 3, name: 'Creative Writing', code: 'CW101', students: 25, avgScore: 88, lastActivity: '1 hour ago' },
];

const DUMMY_GRADES = [
    { id: 1, student: 'Alex Johnson', assignment: 'Newton\'s Quiz', class: 'Physics 101', due: '2025-10-15', max_score: 50 },
    { id: 2, student: 'Sarah Lee', assignment: 'Essay Outline', class: 'English Lit', due: '2025-10-17', max_score: 20 },
    { id: 3, student: 'David Kim', assignment: 'Calculus PS1', class: 'AP Calculus', due: '2025-10-16', max_score: 100 },
];
// ------------------

const TeacherDashboard = () => {
    const { user } = useAuth()
    const [activeGradingAssignment, setActiveGradingAssignment] = useState(null);
    
    // Function to simulate navigation (used by View Students and View Class)
    const navigateTo = (path) => {
        console.log(`[NAVIGATION] Navigating to ${path}`)
    }
    
    const handleGradeNow = (assignment) => {
        setActiveGradingAssignment(assignment);
    };

    return (
        <DashboardLayout role={user?.role}>
            
            {/* RENDER GRADE MODAL */}
            {activeGradingAssignment && (
                <GradeModal 
                    assignment={activeGradingAssignment} 
                    onClose={() => setActiveGradingAssignment(null)} 
                />
            )}
            
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-slate-900 mb-1">
                        Welcome, {user?.first_name}
                    </h1>
                    <p className="text-slate-600">Teacher Dashboard: Focus on your students and classes.</p>
                </div>

                {/* Stat Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <StatCard 
                        title="Total Classes"
                        value={DUMMY_TEACHER_STATS.totalClasses}
                        icon={BookOpenText}
                        color="bg-blue-500"
                    />
                    <StatCard 
                        title="Total Students"
                        value={DUMMY_TEACHER_STATS.totalStudents}
                        icon={UsersRound}
                        color="bg-green-500"
                    />
                    <StatCard 
                        title="Pending Grading"
                        value={DUMMY_TEACHER_STATS.pendingGrading}
                        icon={CheckSquare}
                        color="bg-yellow-500"
                        // ACTION: Direct navigation to Assignments queue
                        linkPath="/assignments" 
                    />
                    <StatCard 
                        title="Recent Score Avg"
                        value={`${DUMMY_TEACHER_STATS.recentScoreAvg}%`}
                        icon={TrendingUp}
                        color="bg-purple-500"
                    />
                </div>

                {/* Quick Actions and Class Overview */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    
                    {/* Quick Actions */}
                    <div className="lg:col-span-1 space-y-4">
                        <h2 className="text-xl font-bold text-slate-900 mb-4">Quick Actions</h2>
                        <Card className="p-5">
                            <h3 className="font-semibold text-slate-900 mb-2">Post New Assignment</h3>
                            <p className="text-sm text-slate-600 mb-4">Create and assign new tasks to your classes.</p>
                            
                        </Card>
                         <Card className="p-5">
                            <h3 className="font-semibold text-slate-900 mb-2">Manage Student Access</h3>
                            <p className="text-sm text-slate-600 mb-4">View student details and manage enrollments.</p>
                           
                        </Card>
                    </div>

                    {/* Class Overview */}
                    <div className="lg:col-span-2">
                        <h2 className="text-xl font-bold text-slate-900 mb-4">Class Overview</h2>
                        <Card className="p-0">
                            {DUMMY_CLASS_OVERVIEW.map(cls => (
                                <div key={cls.id} className="p-4 border-b last:border-b-0 border-slate-100 flex justify-between items-center hover:bg-slate-50 transition-colors">
                                    <div>
                                        <h3 className="font-semibold text-slate-900">{cls.name}</h3>
                                        <p className="text-sm text-slate-600">
                                            {cls.students} students &bull; Avg Score: {cls.avgScore}%
                                        </p>
                                    </div>
                                    
                                </div>
                            ))}
                        </Card>
                    </div>
                </div>

                {/* Pending Grading List */}
                <div className="mt-8">
                    <h2 className="text-xl font-bold text-slate-900 mb-4 flex justify-between items-center">
                        Submissions Needing Attention ({DUMMY_GRADES.length})
                        <Button 
                            size="sm" 
                            variant="text" 
                            color="slate"
                            // ACTION: Navigates to full grading queue
                            onClick={() => navigateTo('/assignments')}
                        >
                            View All <ArrowRight className="w-4 h-4 ml-1" />
                        </Button>
                    </h2>
                    <div className="space-y-4">
                        {DUMMY_GRADES.slice(0, 3).map(grade => (
                            <Card key={grade.id} className="p-4 flex justify-between items-center">
                                <div>
                                    <p className="font-medium text-slate-900">{grade.assignment}</p>
                                    <p className="text-sm text-slate-600">
                                        Student: {grade.student} &bull; Class: {grade.class}
                                    </p>
                                </div>
                                <Button 
                                    size="sm" 
                                    variant="primary" 
                                    color="yellow" 
                                    // ACTION: Opens the Grading Modal
                                    onClick={() => handleGradeNow(grade)}
                                >
                                    Grade Now
                                </Button>
                            </Card>
                        ))}
                    </div>
                </div>

            </div>
        </DashboardLayout>
    )
}

export default TeacherDashboard