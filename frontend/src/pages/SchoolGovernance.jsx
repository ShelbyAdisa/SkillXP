import React, { useState } from 'react';
import DashboardLayout from '../components/layout/DashboardLayout';
import { useAuth } from '../context/AuthContext';
import Card from '../components/shared/Card';
import Button from '../components/shared/Button';
import Badge from '../components/shared/Badge';
import { Vote, DollarSign, TrendingUp, PieChart, CheckCircle, XCircle } from 'lucide-react';

// Dummy data for voting matters
const DUMMY_VOTING_MATTERS = [
  {
    id: 1,
    title: 'School Uniform Policy Update',
    description: 'Should we update the school uniform to include more comfortable options?',
    options: ['Yes', 'No'],
    votes: { Yes: 45, No: 23 },
    totalVotes: 68,
    status: 'active',
    endDate: '2024-12-15'
  },
  {
    id: 2,
    title: 'Extended School Day',
    description: 'Propose extending school hours by 30 minutes for additional activities.',
    options: ['Approve', 'Reject'],
    votes: { Approve: 32, Reject: 41 },
    totalVotes: 73,
    status: 'active',
    endDate: '2024-12-20'
  },
  {
    id: 3,
    title: 'New Cafeteria Menu',
    description: 'Introduce healthier lunch options with local ingredients.',
    options: ['Yes', 'No'],
    votes: { Yes: 67, No: 12 },
    totalVotes: 79,
    status: 'closed',
    endDate: '2024-11-30'
  }
];

// Dummy data for school finances
const DUMMY_FINANCES = {
  totalBudget: 2500000,
  totalExpenses: 1850000,
  remainingBudget: 650000,
  categories: [
    { name: 'Staff Salaries', amount: 1200000, percentage: 48 },
    { name: 'Facilities & Maintenance', amount: 350000, percentage: 14 },
    { name: 'Educational Materials', amount: 150000, percentage: 6 },
    { name: 'Transportation', amount: 80000, percentage: 3.2 },
    { name: 'Technology & IT', amount: 120000, percentage: 4.8 },
    { name: 'Student Activities', amount: 50000, percentage: 2 },
    { name: 'Other', amount: 350000, percentage: 14 }
  ],
  recentTransactions: [
    { id: 1, description: 'Monthly Staff Salaries', amount: -100000, date: '2024-11-01', category: 'Staff Salaries' },
    { id: 2, description: 'New Computers Purchase', amount: -25000, date: '2024-11-05', category: 'Technology & IT' },
    { id: 3, description: 'Bus Maintenance', amount: -5000, date: '2024-11-10', category: 'Transportation' },
    { id: 4, description: 'Fundraising Event Income', amount: 15000, date: '2024-11-15', category: 'Student Activities' }
  ]
};

const SchoolGovernance = () => {
  const { user } = useAuth();
  const [selectedVotes, setSelectedVotes] = useState({});

  const handleVote = (matterId, option) => {
    setSelectedVotes(prev => ({
      ...prev,
      [matterId]: option
    }));
    // In a real app, this would submit to backend
    console.log(`Voted ${option} for matter ${matterId}`);
  };

  const getVotePercentage = (votes, option) => {
    const total = Object.values(votes).reduce((sum, count) => sum + count, 0);
    return total > 0 ? Math.round((votes[option] / total) * 100) : 0;
  };

  return (
    <DashboardLayout role={user?.role}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-1">
            School Governance
          </h1>
          <p className="text-slate-600">
            Participate in school decisions and monitor financial transparency.
          </p>
        </div>

        {/* Voting Section */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
            <Vote className="w-6 h-6 mr-2 text-blue-600" />
            School Matters Voting
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {DUMMY_VOTING_MATTERS.map(matter => (
              <Card key={matter.id} className="p-6">
                <div className="mb-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold text-slate-900">{matter.title}</h3>
                    <Badge variant={matter.status === 'active' ? 'primary' : 'secondary'}>
                      {matter.status}
                    </Badge>
                  </div>
                  <p className="text-slate-600 text-sm mb-4">{matter.description}</p>
                  <p className="text-xs text-slate-500">Ends: {matter.endDate} | Total Votes: {matter.totalVotes}</p>
                </div>

                {matter.status === 'active' ? (
                  <div className="space-y-3">
                    {matter.options.map(option => (
                      <Button
                        key={option}
                        variant={selectedVotes[matter.id] === option ? 'primary' : 'outline'}
                        size="sm"
                        className="w-full justify-start"
                        onClick={() => handleVote(matter.id, option)}
                        disabled={selectedVotes[matter.id]}
                      >
                        {selectedVotes[matter.id] === option && <CheckCircle className="w-4 h-4 mr-2" />}
                        {option}
                      </Button>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-2">
                    {matter.options.map(option => (
                      <div key={option} className="flex justify-between items-center">
                        <span className="text-sm">{option}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-24 bg-slate-200 rounded-full h-2">
                            <div
                              className="bg-blue-500 h-2 rounded-full"
                              style={{ width: `${getVotePercentage(matter.votes, option)}%` }}
                            />
                          </div>
                          <span className="text-xs text-slate-600 w-8 text-right">
                            {getVotePercentage(matter.votes, option)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            ))}
          </div>
        </div>

        {/* Finances Section */}
        <div>
          <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
            <DollarSign className="w-6 h-6 mr-2 text-green-600" />
            School Finances
          </h2>

          {/* Financial Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500">Total Budget</p>
                  <h3 className="text-2xl font-bold text-slate-900">
                    ${(DUMMY_FINANCES.totalBudget / 1000).toFixed(0)}K
                  </h3>
                </div>
                <DollarSign className="w-8 h-8 text-green-500" />
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500">Total Expenses</p>
                  <h3 className="text-2xl font-bold text-slate-900">
                    ${(DUMMY_FINANCES.totalExpenses / 1000).toFixed(0)}K
                  </h3>
                </div>
                <TrendingUp className="w-8 h-8 text-red-500" />
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500">Remaining Budget</p>
                  <h3 className="text-2xl font-bold text-slate-900">
                    ${(DUMMY_FINANCES.remainingBudget / 1000).toFixed(0)}K
                  </h3>
                </div>
                <PieChart className="w-8 h-8 text-blue-500" />
              </div>
            </Card>
          </div>

          {/* Budget Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card title="Budget Allocation" className="p-6">
              <div className="space-y-4">
                {DUMMY_FINANCES.categories.map(category => (
                  <div key={category.name} className="flex justify-between items-center">
                    <div className="flex-1">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-medium">{category.name}</span>
                        <span>${(category.amount / 1000).toFixed(0)}K ({category.percentage}%)</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${category.percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card title="Recent Transactions" className="p-6">
              <div className="space-y-3">
                {DUMMY_FINANCES.recentTransactions.map(transaction => (
                  <div key={transaction.id} className="flex justify-between items-center py-2 border-b border-slate-100 last:border-b-0">
                    <div>
                      <p className="text-sm font-medium text-slate-900">{transaction.description}</p>
                      <p className="text-xs text-slate-500">{transaction.date} • {transaction.category}</p>
                    </div>
                    <span className={`text-sm font-semibold ${transaction.amount > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {transaction.amount > 0 ? '+' : ''}${(Math.abs(transaction.amount) / 1000).toFixed(1)}K
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default SchoolGovernance;
