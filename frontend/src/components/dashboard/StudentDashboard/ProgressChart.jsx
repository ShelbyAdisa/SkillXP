import React from 'react'
import Card from '../../shared/Card'

const ProgressChart = ({ progressData = [] }) => {
  // Simple bar chart visualization
  const maxXP = Math.max(...progressData.map(d => d.xp), 100)

  return (
    <Card title="XP Progress" subtitle="Your learning journey this week">
      <div className="space-y-3 mt-4">
        {progressData.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No progress data yet</p>
            <p className="text-sm mt-1">Start completing tasks to track your progress!</p>
          </div>
        ) : (
          progressData.map((day, index) => (
            <div key={index} className="flex items-center space-x-3">
              <span className="text-sm font-medium text-gray-600 w-12">
                {day.label}
              </span>
              <div className="flex-1 bg-slate-200 rounded-full h-8 overflow-hidden">
                <div
                  className="bg-slate-700 h-full rounded-full flex items-center justify-end pr-3 transition-all duration-500"
                  style={{ width: `${(day.xp / maxXP) * 100}%` }}
                >
                  {day.xp > 0 && (
                    <span className="text-xs font-semibold text-white">
                      {day.xp} XP
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      
      {progressData.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-200 flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-600">Weekly Total</p>
            <p className="text-2xl font-bold text-gray-900">
              {progressData.reduce((sum, day) => sum + day.xp, 0)} XP
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Daily Average</p>
            <p className="text-2xl font-bold text-gray-900">
              {Math.round(progressData.reduce((sum, day) => sum + day.xp, 0) / progressData.length)} XP
            </p>
          </div>
        </div>
      )}
    </Card>
  )
}

export default ProgressChart

