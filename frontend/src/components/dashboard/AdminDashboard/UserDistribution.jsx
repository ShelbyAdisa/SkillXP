import React from 'react'
import Card from '../../shared/Card'

const UserDistribution = ({ distribution = [] }) => {
  const total = distribution.reduce((sum, item) => sum + item.count, 0)

  const colors = {
    STUDENT: 'bg-blue-500',
    TEACHER: 'bg-green-500',
    PARENT: 'bg-purple-500',
    ADMIN: 'bg-red-500',
    SCHOOL_ADMIN: 'bg-yellow-500'
  }

  return (
    <Card title="User Distribution" subtitle="Platform users by role">
      <div className="space-y-4 mt-4">
        {distribution.map((item) => {
          const percentage = total > 0 ? (item.count / total) * 100 : 0
          
          return (
            <div key={item.role}>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">{item.role}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-bold text-gray-900">{item.count}</span>
                  <span className="text-xs text-gray-500">({percentage.toFixed(1)}%)</span>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className={`${colors[item.role] || 'bg-gray-500'} h-full rounded-full transition-all duration-500`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>
      
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-sm font-semibold text-gray-700">Total Users</span>
          <span className="text-2xl font-bold text-gray-900">{total.toLocaleString()}</span>
        </div>
      </div>
    </Card>
  )
}

export default UserDistribution

