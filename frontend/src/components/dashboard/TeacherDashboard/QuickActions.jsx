import React from 'react'
import Card from '../../shared/Card'

const QuickActions = ({ onAction }) => {
  const actions = [
    {
      id: 'create_assignment',
      title: 'Create Assignment',
      description: 'Create a new assignment for your students',
      icon: '✍️',
      color: 'bg-blue-500'
    },
    {
      id: 'upload_resource',
      title: 'Upload Resource',
      description: 'Add learning materials to the library',
      icon: '📚',
      color: 'bg-green-500'
    },
    {
      id: 'take_attendance',
      title: 'Take Attendance',
      description: 'Mark attendance for your classes',
      icon: '✓',
      color: 'bg-purple-500'
    },
    {
      id: 'send_announcement',
      title: 'Send Announcement',
      description: 'Communicate with your students',
      icon: '📢',
      color: 'bg-orange-500'
    },
    {
      id: 'view_analytics',
      title: 'View Analytics',
      description: 'Check detailed performance metrics',
      icon: '📊',
      color: 'bg-indigo-500'
    },
    {
      id: 'grade_submissions',
      title: 'Grade Submissions',
      description: 'Review and grade pending work',
      icon: '📝',
      color: 'bg-pink-500'
    }
  ]

  return (
    <Card title="Quick Actions" subtitle="Common tasks at your fingertips">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={() => onAction && onAction(action.id)}
            className="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 hover:shadow-md transition-all group"
          >
            <div className={`${action.color} w-12 h-12 rounded-full flex items-center justify-center text-2xl mb-2 group-hover:scale-110 transition-transform`}>
              {action.icon}
            </div>
            <h4 className="text-sm font-semibold text-gray-900 text-center">
              {action.title}
            </h4>
            <p className="text-xs text-gray-600 text-center mt-1">
              {action.description}
            </p>
          </button>
        ))}
      </div>
    </Card>
  )
}

export default QuickActions

