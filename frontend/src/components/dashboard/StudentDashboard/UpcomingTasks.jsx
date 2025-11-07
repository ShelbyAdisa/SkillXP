import React from 'react'
import Card from '../../shared/Card'
import Badge from '../../shared/Badge'

const UpcomingTasks = ({ assignments = [] }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const today = new Date()
    const diffTime = date - today
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Tomorrow'
    if (diffDays < 0) return 'Overdue'
    return `${diffDays} days`
  }

  const getUrgencyVariant = (dueDate) => {
    const diffDays = Math.ceil((new Date(dueDate) - new Date()) / (1000 * 60 * 60 * 24))
    if (diffDays < 0) return 'danger'
    if (diffDays <= 1) return 'warning'
    return 'success'
  }

  return (
    <Card title="Upcoming Assignments" subtitle="Stay on track with your work">
      <div className="space-y-3">
        {assignments.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No upcoming assignments</p>
            <p className="text-sm mt-1">You're all caught up! 🎉</p>
          </div>
        ) : (
          assignments.slice(0, 5).map((assignment) => (
            <div 
              key={assignment.id} 
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
            >
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{assignment.title}</h4>
                <p className="text-sm text-gray-600">{assignment.classroom_name}</p>
              </div>
              <div className="flex items-center space-x-3">
                <Badge variant={getUrgencyVariant(assignment.due_date)}>
                  {formatDate(assignment.due_date)}
                </Badge>
                <span className="text-sm font-medium text-gray-700">
                  {assignment.points} pts
                </span>
              </div>
            </div>
          ))
        )}
      </div>
      {assignments.length > 5 && (
        <button className="mt-4 text-sm text-blue-600 hover:text-blue-700 font-medium">
          View all {assignments.length} assignments →
        </button>
      )}
    </Card>
  )
}

export default UpcomingTasks

