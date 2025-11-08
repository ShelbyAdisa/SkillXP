import React from 'react';

export default function BrandLogo({ className = 'w-8 h-8' }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="12" fill="#1F8FFF" />
      <path d="M12 7l8 3-8 3-8-3 8-3zm0 5v5" stroke="#fff" strokeWidth="0.9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}