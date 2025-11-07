import React from 'react'
import Card from '../../shared/Card'
import Badge from '../../shared/Badge'
import Button from '../../shared/Button'

const PendingGrading = ({ submissions = [] }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  return (
    <Card 
      title="Pending Grading" 
      subtitle="Assignments waiting for your review"
      action={
        <Badge variant="warning">{submissions.length} pending</Badge>
      }
    >
      <div className="space-y-3 mt-4">
        {submissions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>All caught up! 🎉</p>
            <p className="text-sm mt-1">No assignments pending grading</p>
          </div>
        ) : (
          submissions.slice(0, 6).map((submission) => (
            <div 
              key={submission.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{submission.assignment_title}</h4>
                <p className="text-sm text-gray-600">
                  {submission.student_name} • {submission.class_name}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Submitted {formatDate(submission.submitted_at)}
                </p>
              </div>
              <Button size="sm" variant="primary">
                Grade
              </Button>
            </div>
          ))
        )}
      </div>
      {submissions.length > 6 && (
        <button className="mt-4 text-sm text-blue-600 hover:text-blue-700 font-medium w-full text-center">
          View all {submissions.length} submissions →
        </button>
      )}
    </Card>
  )
}

export default PendingGrading

