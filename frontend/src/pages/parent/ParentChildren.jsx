import React from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card from '../../components/shared/Card';
// --- FIX: Import Button component ---
import Button from '../../components/shared/Button';
// -----------------------------------
import { useAuth } from '../../context/AuthContext';
import { UsersRound, ArrowRight, UserCheck } from 'lucide-react';

const DUMMY_CHILDREN_LIST = [
    { id: 1, name: 'Lornah Kabuga', grade: 10, classes: 4, lastLogin: '1 hour ago' },
    { id: 2, name: 'Robert Smith', grade: 5, classes: 5, lastLogin: '4 hours ago' },
];

const ParentChildren = () => {
    const { user } = useAuth();
    
    const navigateTo = (path) => {
        console.log(`[NAVIGATION] Navigating to ${path}`);
    };

    return (
        <DashboardLayout role={user?.role}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8 flex items-center space-x-3">
                    <UsersRound className="w-8 h-8 text-blue-600" />
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900 mb-0">Student Enrollment Management</h1>
                        <p className="text-slate-600">Review all enrolled children and verify their current status in the school system.</p>
                    </div>
                </div>

                <div className="space-y-4">
                    {DUMMY_CHILDREN_LIST.map(child => (
                        <Card key={child.id} className="p-5 hover:shadow-lg transition-shadow">
                            <div className="flex justify-between items-center">
                                <div className="flex items-center space-x-4">
                                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
                                        <UserCheck className="w-6 h-6 text-blue-600" />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-semibold text-slate-900">{child.name}</h3>
                                        <p className="text-sm text-slate-600">Grade: {child.grade} &bull; Last Activity: {child.lastLogin}</p>
                                    </div>
                                </div>
                                <Button 
                                    variant="primary" 
                                    color="slate" 
                                    onClick={() => navigateTo(`/parent/progress?child=${child.id}`)}
                                >
                                    View Detailed Progress <ArrowRight className="w-4 h-4 ml-1" />
                                </Button>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>
        </DashboardLayout>
    );
};

export default ParentChildren;