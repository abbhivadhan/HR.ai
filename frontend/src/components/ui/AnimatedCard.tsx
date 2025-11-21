'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

interface AnimatedCardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  delay?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
}

const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  className,
  hover = true,
  delay = 0,
  direction = 'up'
}) => {
  const directionVariants = {
    up: { y: 20 },
    down: { y: -20 },
    left: { x: 20 },
    right: { x: -20 }
  };

  return (
    <motion.div
      className={clsx(
        'bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden',
        className
      )}
      initial={{ 
        opacity: 0, 
        ...directionVariants[direction]
      }}
      animate={{ 
        opacity: 1, 
        x: 0, 
        y: 0 
      }}
      transition={{ 
        duration: 0.5, 
        delay,
        ease: [0.25, 0.46, 0.45, 0.94]
      }}
      whileHover={hover ? {
        y: -5,
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        transition: { duration: 0.2 }
      } : {}}
    >
      {children}
    </motion.div>
  );
};

export default AnimatedCard;