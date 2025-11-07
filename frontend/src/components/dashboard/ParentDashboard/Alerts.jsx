import React from 'react'
import Card from '../../shared/Card'
import Badge from '../../shared/Badge'

const Alerts = ({ alerts = [] }) => {
  const getAlertVariant = (type) => {
    const variants = {
      urgent: 'danger',
      warning: 'warning',
      info: 'info',
      success: 'success'
    }
    return variants[type] || 'default'
  }

  const getAlertIcon = (type) => {
    const icons = {
      urgent: '🚨',
      warning: '⚠️',
      info: 'ℹ️',
      success: '✅'
    }
    return icons[type] || '📌'
  }

  return (
    <Card 
      title="Important Alerts" 
      subtitle="Stay informed about your children"
      action={alerts.length > 0 && <Badge variant="danger">{alerts.length}</Badge>}
    >
      <div className="space-y-3 mt-4">
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No alerts at the moment</p>
            <p className="text-sm mt-1">All is well! 😊</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div 
              key={alert.id}
              className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <span className="text-2xl">{getAlertIcon(alert.type)}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{alert.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                    <div className="flex items-center mt-2 space-x-2">
                      <Badge variant={getAlertVariant(alert.type)} size="sm">
                        {alert.category}
                      </Badge>
                      <span className="text-xs text-gray-500">{alert.child_name}</span>
                      <span className="text-xs text-gray-400">• {alert.date}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  )
}

export default Alerts

