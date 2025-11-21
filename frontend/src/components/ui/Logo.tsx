'use client'

import React from 'react'

interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  showText?: boolean
  className?: string
  textColor?: string
  iconColor?: string
}

const Logo: React.FC<LogoProps> = ({
  size = 'md',
  showText = true,
  className = '',
  textColor = 'text-gray-900 dark:text-white',
  iconColor = 'text-gray-900 dark:text-white'
}) => {
  const sizeClasses = {
    sm: { icon: 'w-6 h-6', text: 'text-lg' },
    md: { icon: 'w-8 h-8', text: 'text-xl' },
    lg: { icon: 'w-12 h-12', text: 'text-2xl' },
    xl: { icon: 'w-16 h-16', text: 'text-3xl' }
  }

  const { icon: iconSize, text: textSize } = sizeClasses[size]

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      <div className={`${iconSize} relative`}>
        <svg viewBox="0 0 100 100" className="w-full h-full">
          {/* Magnifying glass circle */}
          <circle cx="40" cy="40" r="28" fill="none" stroke="currentColor" strokeWidth="5" className={iconColor}/>
          
          {/* AI chip in center */}
          <rect x="32" y="32" width="16" height="16" rx="2" fill="currentColor" className={iconColor}/>
          <rect x="34" y="34" width="12" height="12" rx="1" fill="currentColor" className="text-blue-600"/>
          
          {/* Circuit board pattern - vertical lines */}
          <line x1="28" y1="40" x2="32" y2="40" stroke="currentColor" strokeWidth="2" className={iconColor}/>
          <line x1="48" y1="40" x2="52" y2="40" stroke="currentColor" strokeWidth="2" className={iconColor}/>
          <line x1="40" y1="28" x2="40" y2="32" stroke="currentColor" strokeWidth="2" className={iconColor}/>
          <line x1="40" y1="48" x2="40" y2="52" stroke="currentColor" strokeWidth="2" className={iconColor}/>
          
          {/* Circuit nodes */}
          <circle cx="28" cy="40" r="2" fill="currentColor" className={iconColor}/>
          <circle cx="52" cy="40" r="2" fill="currentColor" className={iconColor}/>
          <circle cx="40" cy="28" r="2" fill="currentColor" className={iconColor}/>
          <circle cx="40" cy="52" r="2" fill="currentColor" className={iconColor}/>
          
          {/* Diagonal circuit lines */}
          <line x1="25" y1="25" x2="30" y2="30" stroke="currentColor" strokeWidth="1.5" className={iconColor}/>
          <line x1="55" y1="25" x2="50" y2="30" stroke="currentColor" strokeWidth="1.5" className={iconColor}/>
          <line x1="25" y1="55" x2="30" y2="50" stroke="currentColor" strokeWidth="1.5" className={iconColor}/>
          <line x1="55" y1="55" x2="50" y2="50" stroke="currentColor" strokeWidth="1.5" className={iconColor}/>
          
          {/* Magnifying glass handle */}
          <line x1="60" y1="60" x2="78" y2="78" stroke="currentColor" strokeWidth="7" strokeLinecap="round" className={iconColor}/>
        </svg>
      </div>
      {showText && (
        <span className={`${textSize} font-bold ${textColor}`}>
          HR<span className="text-blue-600">.ai</span>
        </span>
      )}
    </div>
  )
}

export default Logo