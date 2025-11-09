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
      bg-[#0F1A1C] rounded-lg border border-[#223237] 
      ${padding ? 'p-6' : ''} 
      ${hover ? 'hover:border-[#2d3f45] transition-shadow duration-200' : ''}
      ${className}
    `}>
      {(title || action) && (
        <div className="flex justify-between items-start mb-4">
          <div>
            {/* Use dark theme text colors */}
            {title && <h3 className="text-lg font-semibold text-[#D7DADC]">{title}</h3>}
            {subtitle && <p className="text-sm text-[#82959B] mt-1">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  )
}

export default Card