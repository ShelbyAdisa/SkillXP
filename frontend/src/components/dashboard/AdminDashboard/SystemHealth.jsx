import React from 'react'
import Card from '../../shared/Card'
import Badge from '../../shared/Badge'

const SystemHealth = ({ metrics = [] }) => {
  const getStatusVariant = (status) => {
    const variants = {
      healthy: 'success',
      warning: 'warning',
      critical: 'danger'
    }
    return variants[status] || 'default'
  }

  return (
    <Card title="System Health" subtitle="Monitor platform performance">
      <div className="space-y-4 mt-4">
        {metrics.map((metric, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${
                metric.status === 'healthy' ? 'bg-green-500' :
                metric.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
              }`} />
              <div>
                <p className="font-medium text-gray-900">{metric.name}</p>
                <p className="text-xs text-gray-600">{metric.description}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-sm font-semibold text-gray-900">{metric.value}</span>
              <Badge variant={getStatusVariant(metric.status)} size="sm">
                {metric.status}
              </Badge>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}

export default SystemHealth

