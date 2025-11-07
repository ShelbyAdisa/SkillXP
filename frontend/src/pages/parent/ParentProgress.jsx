import React from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card from '../../components/shared/Card';
import Badge from '../../components/shared/Badge';
import { useAuth } from '../../context/AuthContext';
import { BarChart2, TrendingUp, BookOpenText, Target } from 'lucide-react'; // Added Target

const DUMMY_PROGRESS_DETAILS = [
    { course: 'Grade 3: Advanced Geometry', avgScore: 95, currentGrade: 'A', trend: 'up' },
    { course: 'World History: Ancient Civilizations', avgScore: 68, currentGrade: 'C', trend: 'down' },
    { course: 'Creative Writing Workshop', avgScore: 88, currentGrade: 'B+', trend: 'stable' },
    { course: 'Digital Literacy', avgScore: 100, currentGrade: 'A+', trend: 'up' },
];

const ParentProgress = () => {
    const { user } = useAuth();
    const childName = "Alice Johnson"; 

    const getStatusVariant = (score) => {
        if (score >= 85) return 'success';
        if (score >= 70) return 'primary';
        return 'danger';
    }
    
    const getTrendIcon = (trend) => {
        if (trend === 'up') return <TrendingUp className="w-4 h-4 text-green-600" />;
        if (trend === 'down') return <TrendingUp className="w-4 h-4 text-red-600 rotate-180" />;
        return null;
    }

    return (
        <DashboardLayout role={user?.role}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8 flex items-center space-x-3">
                    <BarChart2 className="w-8 h-8 text-green-600" />
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900 mb-0">Academic Performance Tracking</h1>
                        <p className="text-slate-600">Detailed subject performance, average scores, and grade trends for **{childName}**.</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <Card className="p-5 flex items-center space-x-4">
                        <Target className="w-8 h-8 text-purple-500" />
                        <div>
                            <p className="text-sm text-slate-500">Subject Count</p>
                            <h3 className="text-2xl font-bold text-slate-900">{DUMMY_PROGRESS_DETAILS.length}</h3>
                        </div>
                    </Card>
                    <Card className="p-5 flex items-center space-x-4">
                        <BarChart2 className="w-8 h-8 text-blue-500" />
                        <div>
                            <p className="text-sm text-slate-500">Overall GPA (Simulated)</p>
                            <h3 className="text-2xl font-bold text-slate-900">3.7</h3>
                        </div>
                    </Card>
                </div>

                <Card className="p-0">
                    <h2 className="text-xl font-bold text-slate-900 p-6 border-b border-slate-200">Course Breakdown</h2>
                    <table className="min-w-full divide-y divide-slate-200">
                        <thead>
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Course</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Avg Score</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Trend</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Current Grade</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-slate-100">
                            {DUMMY_PROGRESS_DETAILS.map((detail, index) => (
                                <tr key={index} className="hover:bg-slate-50">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900 flex items-center">
                                        <BookOpenText className="w-4 h-4 mr-2 text-slate-500" />
                                        {detail.course}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{detail.avgScore}%</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm flex items-center space-x-1">
                                        {getTrendIcon(detail.trend)}
                                        <Badge variant={getStatusVariant(detail.avgScore)}>{detail.trend.toUpperCase()}</Badge>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600 font-bold">{detail.currentGrade}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </Card>
            </div>
        </DashboardLayout>
    );
};

export default ParentProgress;