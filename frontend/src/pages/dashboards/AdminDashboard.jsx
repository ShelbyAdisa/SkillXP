import React from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card from '../../components/shared/Card';
import Button from '../../components/shared/Button';
// Assuming StatCard is available globally or defined locally
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
// ------------------------------------------------------------------------

import { useAuth } from '../../context/AuthContext';
import { Users, GraduationCap, BarChart3, Clock, ArrowRight, UserPlus, Scale } from 'lucide-react';

// --- DUMMY DATA ---
const DUMMY_ADMIN_STATS = {
    totalUsers: 1500,
    activeSchools: 12,
    activeTeachers: 75,
    systemUptime: '99.9%',
};

const DUMMY_RECENT_ACTIVITY = [
    { id: 1, type: 'User', action: 'New teacher account created: Ms. Davies', date: '2025-10-10', path: '/admin/users' },
    { id: 2, type: 'System', action: 'Content sync job successfully completed', date: '2025-10-09', path: '/admin/content' },
    { id: 3, type: 'School', action: 'Hilltop High School enrollment updated (+50 students)', date: '2025-10-08', path: '/admin/schools' },
];

const DUMMY_QUICK_ACTIONS = [
    { name: 'Manage Users', icon: Users, path: '/admin/users', description: 'Add, edit, or disable user accounts across the platform.' },
    { name: 'Review Reports', icon: Scale, path: '/transparency', description: 'Access system and compliance reports.' },
    { name: 'Content Library', icon: GraduationCap, path: '/admin/content', description: 'Oversee and audit learning materials.' },
];
// ------------------

const AdminDashboard = () => {
    const { user } = useAuth();
    
    // Function to simulate navigation
    const navigateTo = (path) => {
        console.log(`[NAVIGATION] Admin Navigating to ${path}`);
    };

    return (
        <DashboardLayout role={user?.role}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-slate-900 mb-1">
                        System Administrator Dashboard
                    </h1>
                    <p className="text-slate-600">Central control and monitoring panel for SkillXP Nexus platform operations.</p>
                </div>

                {/* Stat Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <StatCard 
                        title="Total Users"
                        value={DUMMY_ADMIN_STATS.totalUsers.toLocaleString()}
                        icon={Users}
                        color="bg-blue-600"
                    />
                    <StatCard 
                        title="Active Schools"
                        value={DUMMY_ADMIN_STATS.activeSchools}
                        icon={GraduationCap}
                        color="bg-green-600"
                    />
                    <StatCard 
                        title="Active Teachers"
                        value={DUMMY_ADMIN_STATS.activeTeachers}
                        icon={UserPlus}
                        color="bg-yellow-600"
                    />
                    <StatCard 
                        title="System Uptime"
                        value={DUMMY_ADMIN_STATS.systemUptime}
                        icon={Clock}
                        color="bg-purple-600"
                    />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    
                    {/* Quick Actions Panel */}
                    <div className="lg:col-span-1 space-y-4">
                        <h2 className="text-xl font-bold text-slate-900 mb-4">Quick Actions</h2>
                        {DUMMY_QUICK_ACTIONS.map(action => {
                            const Icon = action.icon;
                            return (
                                <Card key={action.path} className="p-5 hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigateTo(action.path)}>
                                    <div className="flex items-center space-x-3">
                                        <Icon className="w-6 h-6 text-slate-700" />
                                        <div>
                                            <h3 className="font-semibold text-slate-900">{action.name}</h3>
                                            <p className="text-sm text-slate-600">{action.description}</p>
                                        </div>
                                    </div>
                                </Card>
                            );
                        })}
                    </div>

                    {/* Recent Activity Log */}
                    <div className="lg:col-span-2">
                        <h2 className="text-xl font-bold text-slate-900 mb-4 flex justify-between items-center">
                            Recent System Activity
                            <Button 
                                size="sm" 
                                variant="text" 
                                color="slate"
                                onClick={() => navigateTo('/analytics')}
                            >
                                View Analytics <BarChart3 className="w-4 h-4 ml-1" />
                            </Button>
                        </h2>
                        <Card className="p-0">
                            {DUMMY_RECENT_ACTIVITY.map(activity => (
                                <div key={activity.id} className="p-4 border-b last:border-b-0 border-slate-100 flex justify-between items-center hover:bg-slate-50 transition-colors">
                                    <div>
                                        <p className={`font-medium ${activity.type === 'User' ? 'text-blue-700' : 'text-slate-800'}`}>{activity.action}</p>
                                        <p className="text-xs text-slate-500 mt-0.5">Category: {activity.type} &bull; Date: {activity.date}</p>
                                    </div>
                                    <Button size="sm" variant="outline" color="slate" onClick={() => navigateTo(activity.path)}>
                                        Details
                                    </Button>
                                </div>
                            ))}
                        </Card>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default AdminDashboard;