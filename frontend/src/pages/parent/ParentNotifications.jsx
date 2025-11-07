import React from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card from '../../components/shared/Card';
import Badge from '../../components/shared/Badge';
import { useAuth } from '../../context/AuthContext';
import { Megaphone, Clock, AlertTriangle, CheckSquare, MessageSquare } from 'lucide-react';

const DUMMY_FULL_NOTIFICATIONS = [
    { id: 1, type: 'Transport', message: 'Bus 3 running 15 mins late due to traffic on route.', time: '2 hours ago', icon: AlertTriangle },
    { id: 2, type: 'System', message: 'New Parent-Teacher conference slots available.', time: 'Today, 9:00 AM', icon: Megaphone },
    { id: 3, type: 'Academic', message: 'Alice Johnson submitted the Math Assignment.', time: 'Yesterday, 5:30 PM', icon: CheckSquare },
    { id: 4, type: 'Social', message: 'Robert Smith received a recognition badge in class.', time: 'Yesterday, 4:00 PM', icon: MessageSquare },
];

const ParentNotifications = () => {
    const { user } = useAuth();
    
    const getTypeBadge = (type) => {
        if (type === 'Transport') return <Badge variant="danger">{type}</Badge>;
        if (type === 'Academic') return <Badge variant="primary">{type}</Badge>;
        return <Badge variant="slate">{type}</Badge>;
    }

    return (
        <DashboardLayout role={user?.role}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8 flex items-center space-x-3">
                    <Megaphone className="w-8 h-8 text-red-600" />
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900 mb-0">School Alerts & Notifications</h1>
                        <p className="text-slate-600">All real-time communication and system alerts impacting your family.</p>
                    </div>
                </div>

                <div className="space-y-4">
                    {DUMMY_FULL_NOTIFICATIONS.map(notification => {
                        const Icon = notification.icon;
                        return (
                            <Card key={notification.id} className="p-5 flex items-start space-x-4 hover:bg-slate-50 transition-shadow">
                                <Icon className={`w-6 h-6 shrink-0 ${notification.type === 'Transport' ? 'text-red-600' : 'text-blue-600'}`} />
                                <div className="flex-1">
                                    <div className="flex justify-between items-start mb-1">
                                        <p className="font-semibold text-slate-900">{notification.message}</p>
                                        {getTypeBadge(notification.type)}
                                    </div>
                                    <p className="text-sm text-slate-500"><Clock className="w-3 h-3 inline mr-1" /> {notification.time}</p>
                                </div>
                            </Card>
                        );
                    })}
                </div>
            </div>
        </DashboardLayout>
    );
};

export default ParentNotifications;