import React from 'react'
import Card from '../../shared/Card'
import Avatar from '../../shared/Avatar'
import Badge from '../../shared/Badge'

const ChildrenCards = ({ children = [] }) => {
  const getPerformanceBadge = (score) => {
    if (score >= 85) return { variant: 'success', label: 'Excellent' }
    if (score >= 70) return { variant: 'primary', label: 'Good' }
    if (score >= 60) return { variant: 'warning', label: 'Fair' }
    return { variant: 'danger', label: 'Needs Support' }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {children.map((child) => {
        const performanceBadge = getPerformanceBadge(child.overall_performance)
        
        return (
          <Card key={child.id} hover className="cursor-pointer">
            <div className="flex flex-col items-center text-center">
              <Avatar
                src={child.avatar}
                alt={child.name}
                initials={child.name.split(' ').map(n => n[0]).join('')}
                size="xl"
              />
              <h3 className="mt-4 text-lg font-semibold text-gray-900">{child.name}</h3>
              <p className="text-sm text-gray-600">{child.grade} • {child.school}</p>
              
              <div className="mt-4 w-full">
                <Badge variant={performanceBadge.variant} size="lg">
                  {performanceBadge.label}
                </Badge>
              </div>

              <div className="mt-6 grid grid-cols-3 gap-4 w-full">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{child.overall_performance}%</p>
                  <p className="text-xs text-gray-600">Performance</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{child.attendance}%</p>
                  <p className="text-xs text-gray-600">Attendance</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">{child.xp_points}</p>
                  <p className="text-xs text-gray-600">XP Points</p>
                </div>
              </div>

              {child.alerts > 0 && (
                <div className="mt-4 w-full p-3 bg-red-50 rounded-lg">
                  <p className="text-sm text-red-800 font-medium">
                    ⚠️ {child.alerts} alert{child.alerts > 1 ? 's' : ''} require attention
                  </p>
                </div>
              )}
            </div>
          </Card>
        )
      })}
    </div>
  )
}

export default ChildrenCards

