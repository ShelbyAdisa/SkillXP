import React from 'react'
import Card from '../../shared/Card'

const ProgressSummary = ({ childName, progressData = [] }) => {
  return (
    <Card title={`${childName}'s Progress`} subtitle="Recent academic performance">
      <div className="space-y-4 mt-4">
        {progressData.map((subject, index) => (
          <div key={index}>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">{subject.name}</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-bold text-gray-900">{subject.grade}%</span>
                {subject.trend && (
                  <span className={`text-xs ${subject.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                    {subject.trend === 'up' ? '↑' : '↓'} {Math.abs(subject.change)}%
                  </span>
                )}
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  subject.grade >= 85
                    ? 'bg-green-500'
                    : subject.grade >= 70
                    ? 'bg-blue-500'
                    : subject.grade >= 60
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${subject.grade}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}

export default ProgressSummary

