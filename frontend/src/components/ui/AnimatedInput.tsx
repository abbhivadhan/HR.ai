'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

interface AnimatedInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onAnimationStart' | 'onAnimationEnd'> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}

const AnimatedInput: React.FC<AnimatedInputProps> = ({
  label,
  error,
  icon,
  className,
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [hasValue, setHasValue] = useState(!!props.value || !!props.defaultValue);

  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(true);
    props.onFocus?.(e);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(false);
    props.onBlur?.(e);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setHasValue(!!e.target.value);
    props.onChange?.(e);
  };

  return (
    <div className="relative">
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500">
            {icon}
          </div>
        )}
        
        <motion.input
          {...(props as any)}
          className={clsx(
            'w-full px-4 py-3 border-2 rounded-lg transition-all duration-200 bg-white dark:bg-gray-800',
            'focus:outline-none focus:ring-0',
            icon && 'pl-10',
            error 
              ? 'border-red-300 focus:border-red-500 dark:border-red-600 dark:focus:border-red-400' 
              : 'border-gray-300 focus:border-primary-500 dark:border-gray-600 dark:focus:border-primary-400',
            'text-gray-900 dark:text-gray-100',
            'placeholder-transparent',
            className
          )}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onChange={handleChange}
          whileFocus={{ scale: 1.02 }}
          transition={{ duration: 0.2 }}
        />

        {label && (
          <motion.label
            className={clsx(
              'absolute left-4 transition-all duration-200 pointer-events-none',
              icon && 'left-10',
              isFocused || hasValue
                ? 'top-0 text-xs bg-white dark:bg-gray-800 px-1 -translate-y-1/2'
                : 'top-1/2 text-base -translate-y-1/2',
              error
                ? 'text-red-500 dark:text-red-400'
                : isFocused
                ? 'text-primary-500 dark:text-primary-400'
                : 'text-gray-500 dark:text-gray-400'
            )}
            animate={{
              fontSize: isFocused || hasValue ? '0.75rem' : '1rem',
              y: isFocused || hasValue ? '-50%' : '-50%',
              top: isFocused || hasValue ? '0px' : '50%'
            }}
            transition={{ duration: 0.2 }}
          >
            {label}
          </motion.label>
        )}
      </div>

      {error && (
        <motion.p
          className="mt-1 text-sm text-red-500 dark:text-red-400"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {error}
        </motion.p>
      )}
    </div>
  );
};

export default AnimatedInput;