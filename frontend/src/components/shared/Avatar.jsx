import React from 'react'

const Avatar = ({ 
  src, 
  alt = 'User', 
  size = 'md', 
  status,
  initials 
}) => {
  const sizes = {
    xs: 'h-6 w-6 text-xs',
    sm: 'h-8 w-8 text-sm',
    md: 'h-10 w-10 text-base',
    lg: 'h-12 w-12 text-lg',
    xl: 'h-16 w-16 text-xl',
    '2xl': 'h-24 w-24 text-2xl'
  }
  
  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-gray-400',
    busy: 'bg-red-500',
    away: 'bg-yellow-500'
  }
  
  return (
    <div className="relative inline-block">
      {src ? (
        <img
          src={src}
          alt={alt}
          className={`${sizes[size]} rounded-full object-cover ring-2 ring-white`}
        />
      ) : (
        <div className={`
          ${sizes[size]} rounded-full 
          bg-gradient-to-br from-blue-500 to-purple-500 
          flex items-center justify-center 
          text-white font-semibold
          ring-2 ring-white
        `}>
          {initials || alt.charAt(0).toUpperCase()}
        </div>
      )}
      {status && (
        <span className={`
          absolute bottom-0 right-0 block h-3 w-3 rounded-full 
          ring-2 ring-white ${statusColors[status]}
        `} />
      )}
    </div>
  )
}

export default Avatar

