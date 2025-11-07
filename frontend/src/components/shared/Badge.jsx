import React from 'react'

const Badge = ({ 
  children, 
  variant = 'default', 
  size = 'md',
  rounded = false 
}) => {
  const variants = {
    default: 'bg-slate-100 text-slate-800',
    primary: 'bg-slate-200 text-slate-900',
    success: 'bg-slate-200 text-slate-900',
    warning: 'bg-slate-200 text-slate-900',
    danger: 'bg-slate-200 text-slate-900',
    info: 'bg-slate-200 text-slate-900',
    purple: 'bg-slate-200 text-slate-900'
  }
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  }
  
  return (
    <span className={`
      inline-flex items-center font-medium
      ${variants[variant]} 
      ${sizes[size]}
      ${rounded ? 'rounded-full' : 'rounded'}
    `}>
      {children}
    </span>
  )
}

export default Badge

