import React from 'react'
import Card from '../../shared/Card'
import Avatar from '../../shared/Avatar'
import Badge from '../../shared/Badge'

const StudentPerformance = ({ students = [] }) => {
  const getPerformanceBadge = (score) => {
    if (score >= 90) return { variant: 'success', label: 'Excellent' }
    if (score >= 75) return { variant: 'primary', label: 'Good' }
    if (score >= 60) return { variant: 'warning', label: 'Fair' }
    return { variant: 'danger', label: 'Needs Help' }
  }

  return (
    <Card title="Student Performance" subtitle="Top and struggling students">
      <div className="space-y-4 mt-4">
        {/* Top Performers */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3">🌟 Top Performers</h4>
          <div className="space-y-2">
            {students
              .filter(s => s.performance_score >= 85)
              .slice(0, 3)
              .map((student) => (
                <div key={student.id} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Avatar
                      src={student.avatar}
                      alt={student.name}
                      initials={student.name.charAt(0)}
                      size="sm"
                    />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{student.name}</p>
                      <p className="text-xs text-gray-500">{student.class_name}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-bold text-gray-900">{student.performance_score}%</span>
                    <Badge variant={getPerformanceBadge(student.performance_score).variant}>
                      {getPerformanceBadge(student.performance_score).label}
                    </Badge>
                  </div>
                </div>
              ))}
          </div>
        </div>

        {/* Needs Attention */}
        <div className="pt-4 border-t border-gray-200">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">⚠️ Needs Attention</h4>
          <div className="space-y-2">
            {students
              .filter(s => s.performance_score < 60)
              .slice(0, 3)
              .map((student) => (
                <div key={student.id} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Avatar
                      src={student.avatar}
                      alt={student.name}
                      initials={student.name.charAt(0)}
                      size="sm"
                    />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{student.name}</p>
                      <p className="text-xs text-gray-500">{student.class_name}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-bold text-gray-900">{student.performance_score}%</span>
                    <Badge variant="danger">
                      Action Needed
                    </Badge>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </Card>
  )
}

export default StudentPerformance

