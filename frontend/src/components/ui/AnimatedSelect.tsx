'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

interface Option {
  value: string;
  label: string;
}

interface AnimatedSelectProps {
  label?: string;
  error?: string;
  value: string;
  onChange: (value: string) => void;
  options: Option[];
  placeholder?: string;
  className?: string;
  required?: boolean;
}

const AnimatedSelect: React.FC<AnimatedSelectProps> = ({
  label,
  error,
  value,
  onChange,
  options,
  placeholder = 'Select an option',
  className,
  required
}) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const selectedOption = options.find(opt => opt.value === value);
  const hasValue = !!value;

  const handleSelect = (optionValue: string) => {
    onChange(optionValue);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label} {required && '*'}
        </label>
      )}
      
      <div className="relative">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          onBlur={() => {
            setTimeout(() => setIsOpen(false), 200);
          }}
          className={clsx(
            'w-full px-4 py-3 border-2 rounded-lg transition-all duration-200 bg-white dark:bg-gray-800',
            'focus:outline-none focus:ring-0 text-left relative',
            error 
              ? 'border-red-300 focus:border-red-500 dark:border-red-600 dark:focus:border-red-400' 
              : 'border-gray-300 focus:border-blue-500 dark:border-gray-600 dark:focus:border-blue-400',
            'text-gray-900 dark:text-gray-100',
            !hasValue && 'text-gray-400',
            className
          )}
        >
          <span className={clsx(!hasValue && 'text-gray-400')}>
            {selectedOption ? selectedOption.label : placeholder}
          </span>
          
          <motion.div
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none"
            animate={{ rotate: isOpen ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDownIcon className="w-5 h-5" />
          </motion.div>
        </button>

        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="absolute left-0 right-0 top-full mt-1 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 rounded-lg shadow-xl overflow-hidden"
              style={{ zIndex: 9999 }}
            >
              <div className="max-h-60 overflow-y-auto">
                {options.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => handleSelect(option.value)}
                    className={clsx(
                      'w-full px-4 py-3 text-left transition-colors',
                      'hover:bg-blue-50 dark:hover:bg-gray-700',
                      option.value === value
                        ? 'bg-blue-100 dark:bg-gray-700 text-blue-600 dark:text-blue-400 font-medium'
                        : 'text-gray-900 dark:text-gray-100'
                    )}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
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

export default AnimatedSelect;
