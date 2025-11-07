import React from 'react'
import Card from '../../shared/Card'
import Badge from '../../shared/Badge'

const ClassOverview = ({ classes = [] }) => {
  return (
    <Card title="My Classes" subtitle="Quick overview of your classes">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        {classes.length === 0 ? (
          <div className="col-span-2 text-center py-8 text-gray-500">
            <p>No classes assigned yet</p>
          </div>
        ) : (
          classes.map((classItem) => (
            <div 
              key={classItem.id}
              className="p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border border-blue-100 hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{classItem.name}</h3>
                  <p className="text-sm text-gray-600">{classItem.subject}</p>
                </div>
                <Badge variant="primary">{classItem.section}</Badge>
              </div>
              
              <div className="grid grid-cols-3 gap-2 mt-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{classItem.student_count}</p>
                  <p className="text-xs text-gray-600">Students</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{classItem.avg_grade}%</p>
                  <p className="text-xs text-gray-600">Avg Grade</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">{classItem.attendance}%</p>
                  <p className="text-xs text-gray-600">Attendance</p>
                </div>
              </div>

              {classItem.pending_grading > 0 && (
                <div className="mt-3 pt-3 border-t border-blue-200">
                  <p className="text-sm text-orange-600 font-medium">
                    ⚠️ {classItem.pending_grading} assignments need grading
                  </p>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </Card>
  )
}

export default ClassOverview

