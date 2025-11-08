import React from 'react';

export default function UserAvatar({ className = 'w-10 h-10' }) {
  return (
    <img 
      src="https://api.dicebear.com/7.x/avataaars/svg?seed=User" 
      className={`${className} rounded-full`} 
      alt="User Avatar" 
    />
  );
}