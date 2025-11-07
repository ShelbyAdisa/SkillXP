import React, { useState } from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../context/AuthContext'
import Card from '../../components/shared/Card'
import Button from '../../components/shared/Button'
import Badge from '../../components/shared/Badge'
import { UsersRound, BarChart2, Bus, Megaphone, ArrowRight, TrendingUp, Truck, BookOpenText } from 'lucide-react' 

// --- SELF-CONTAINED StatCard Component ---
const StatCard = ({ title, value, icon: Icon, color, linkPath }) => {
    return (
        <Card className="p-5 flex items-center justify-between">
            <div>
                <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
                <h3 className="text-2xl font-bold text-slate-900">{value}</h3>
            </div>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${color}`}>
                <Icon className="w-5 h-5 text-white" />
            </div>
        </Card>
    );
};
// ----------------------------------------

// --- DUMMY DATA ---
const ALICE_PROGRESS = [
    { course: 'Grade 3: Advanced Geometry', progress: 95, avgScore: 96, grade: 'A+' },
    { course: 'Creative Writing Workshop', progress: 100, avgScore: 100, grade: 'A+' },
    { course: 'World History: Ancient Civilizations', progress: 60, avgScore: 68, grade: 'C' },
];

const ROBERT_PROGRESS = [
    { course: 'Grade 5: Algebra Foundations', progress: 40, avgScore: 40, grade: 'F' },
    { course: 'Ecology and Habitats', progress: 78, avgScore: 82, grade: 'B' },
    { course: 'Digital Citizenship', progress: 99, avgScore: 99, grade: 'A+' },
];

// Refactored DUMMY_CHILDREN_SUMMARY to hold individual progress data
const DUMMY_CHILDREN_SUMMARY = [
    { id: 1, name: 'Alice Johnson', grade: 3, status: 'On Track', avgScore: 92.5, progressDetails: ALICE_PROGRESS }, 
    { id: 2, name: 'Robert Smith', grade: 5, status: 'Needs Support', avgScore: 80.0, progressDetails: ROBERT_PROGRESS },
];

const DUMMY_ALERTS = [
    { id: 1, type: 'Urgent', message: 'Bus 3 running 15 mins late due to traffic.', time: '10:15 AM' },
    { id: 2, type: 'Info', message: 'Math assignment (Quiz) due tomorrow.', time: 'Yesterday' },
];

const DUMMY_PROGRESS_SUMMARY = {
    totalChildren: DUMMY_CHILDREN_SUMMARY.length,
    avgAssignmentScore: 86.3, 
    recentXP: 750, 
    busDelayCount: 3, 
};
// ------------------

const ParentDashboard = () => {
    const { user } = useAuth()
    const [viewProgressModal, setViewProgressModal] = useState(null); // State for detailed progress modal
    
    // Function to simulate navigation
    const navigateTo = (path) => {
        console.log(`[NAVIGATION] Parent Navigating to ${path}`)
    }
    
    const handleViewProgress = (child) => {
        setViewProgressModal(child);
        console.log(`[ACTION] Viewing detailed progress for: ${child.name}`);
    };
    
    const renderProgressDetailModal = () => {
        if (!viewProgressModal) return null;
        
        const child = viewProgressModal;

        const getProgressColor = (score) => {
            if (score >= 90) return 'bg-green-500';
            if (score >= 70) return 'bg-blue-500';
            return 'bg-red-500';
        };

        return (
            <div className="fixed inset-0 bg-gray-900 bg-opacity-90 z-50 overflow-y-auto p-4 sm:p-8">
                <Card className="max-w-4xl mx-auto my-8 p-8">
                    <div className="flex justify-between items-start mb-6 border-b pb-4">
                        <div>
                            <h2 className="text-3xl font-bold text-slate-900">
                                <BarChart2 className="w-6 h-6 inline mr-2 text-green-600" />
                                Academic Progress: {child.name}
                            </h2>
                            <p className="text-md text-slate-600 mt-1">Grade {child.grade} &bull; Overall Avg: **{child.avgScore}%**</p>
                        </div>
                        <Button variant="outline" color="slate" onClick={() => setViewProgressModal(null)}>
                            Close Report
                        </Button>
                    </div>

                    <div className="space-y-6">
                        {child.progressDetails.map((detail, index) => (
                            <div key={index} className="p-4 bg-slate-50 rounded-lg">
                                <div className="flex justify-between items-center mb-2">
                                    <h3 className="font-semibold text-slate-800 flex items-center">
                                        <BookOpenText className="w-4 h-4 mr-2 text-slate-500" />
                                        {detail.course}
                                    </h3>
                                    <span className="text-lg font-bold text-slate-900">{detail.grade}</span>
                                </div>
                                <div className="flex justify-between items-center text-sm text-slate-600">
                                    <span>Average Score: {detail.avgScore}%</span>
                                    <Badge variant={detail.progress === 100 ? 'success' : (detail.progress < 50 ? 'danger' : 'primary')}>
                                        {detail.progress}% Progress
                                    </Badge>
                                </div>
                                {/* Progress Bar Visualization */}
                                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                    <div
                                        className={`h-full rounded-full transition-all duration-500 ${getProgressColor(detail.avgScore)}`}
                                        style={{ width: `${detail.progress}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
        );
    };

    return (
        <DashboardLayout role={user?.role}>
            {/* Modal for detailed progress view */}
            {viewProgressModal && renderProgressDetailModal()}
            
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-slate-900 mb-1">
                        Welcome, {user?.first_name}
                    </h1>
                    <p className="text-slate-600">Parent Dashboard: Simplified overview of your family's school status.</p>
                </div>

                {/* Stat Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <StatCard 
                        title="Children Enrolled"
                        value={DUMMY_PROGRESS_SUMMARY.totalChildren}
                        icon={UsersRound}
                        color="bg-blue-500"
                    />
                    <StatCard 
                        title="Family Avg Score"
                        value={`${DUMMY_PROGRESS_SUMMARY.avgAssignmentScore}%`}
                        icon={BarChart2}
                        color="bg-green-500"
                    />
                    <StatCard 
                        title="XP Earned (Last 7 Days)"
                        value={DUMMY_PROGRESS_SUMMARY.recentXP}
                        icon={TrendingUp}
                        color="bg-purple-500"
                    />
                    <StatCard 
                        title="Transport Delays (This Month)"
                        value={DUMMY_PROGRESS_SUMMARY.busDelayCount}
                        icon={Truck}
                        color="bg-yellow-500"
                    />
                </div>

                {/* Consolidated Child Status and Alerts */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    
                    {/* Consolidated Child Status */}
                    <div className="lg:col-span-2 space-y-4">
                        <h2 className="text-xl font-bold text-slate-900 mb-4">Current Child Status</h2>
                        <div className="space-y-4">
                            {DUMMY_CHILDREN_SUMMARY.map(child => (
                                <Card 
                                    key={child.id} 
                                    className="p-5 flex justify-between items-center hover:shadow-lg transition-shadow cursor-pointer"
                                    onClick={() => handleViewProgress(child)} // Clicking the card itself
                                >
                                    <div className="flex items-center space-x-4">
                                        <div className="w-12 h-12 bg-slate-200 rounded-full flex items-center justify-center">
                                            <span className="font-bold text-lg text-slate-700">{child.name[0]}</span>
                                        </div>
                                        <div>
                                            <h3 className="font-semibold text-slate-900">{child.name} (Grade {child.grade})</h3>
                                            <p className="text-sm text-slate-600">Current Avg Score: **{child.avgScore}%**</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-3">
                                        <Badge variant={child.status === 'On Track' ? 'success' : 'danger'}>
                                            {child.status}
                                        </Badge>
                                        <Button 
                                            size="sm" 
                                            variant="outline" 
                                            color="blue" 
                                            // Action moved to onClick of the card, but kept here for accessibility
                                            onClick={(e) => { e.stopPropagation(); handleViewProgress(child); }} 
                                        >
                                            View Progress
                                        </Button>
                                    </div>
                                </Card>
                            ))}
                        </div>
                    </div>

                    {/* Alerts (Quick View) */}
                    <div className="lg:col-span-1">
                        <h2 className="text-xl font-bold text-slate-900 mb-4">Urgent Alerts</h2>
                        <Card className="p-0">
                            {DUMMY_ALERTS.map(alert => (
                                <div key={alert.id} className={`p-4 border-l-4 ${alert.type === 'Urgent' ? 'border-red-500 bg-red-50' : 'border-blue-500 bg-blue-50'} border-b last:border-b-0`}>
                                    <p className="text-sm font-medium text-slate-900 flex items-center">
                                        <Megaphone className="w-4 h-4 mr-2" />
                                        {alert.message}
                                    </p>
                                    <p className="text-xs text-slate-600 mt-1 ml-6">{alert.time}</p>
                                </div>
                            ))}
                            <div className="p-4 text-center">
                                <Button size="sm" variant="text" color="slate" onClick={() => navigateTo('/parent/notifications')}>
                                    See All Notifications
                                </Button>
                            </div>
                        </Card>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    )
}

export default ParentDashboard