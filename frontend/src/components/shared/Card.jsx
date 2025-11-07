import React from 'react'

const Card = ({ 
  children, 
  className = '', 
  title, 
  subtitle,
  action,
  padding = true,
  hover = false 
}) => {
  return (
    <div className={`
      bg-white rounded-lg shadow-sm border border-gray-200 
      ${padding ? 'p-6' : ''} 
      ${hover ? 'hover:shadow-md transition-shadow duration-200' : ''}
      ${className}
    `}>
      {(title || action) && (
        <div className="flex justify-between items-start mb-4">
          <div>
            {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
            {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  )
}

export default Card

