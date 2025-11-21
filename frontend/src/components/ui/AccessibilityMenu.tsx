'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AdjustmentsHorizontalIcon,
  EyeIcon,
  SpeakerWaveIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { useAccessibility } from '@/hooks/useAccessibility';

const AccessibilityMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { preferences, updatePreference } = useAccessibility();

  const fontSizes = [
    { value: 'small', label: 'Small' },
    { value: 'medium', label: 'Medium' },
    { value: 'large', label: 'Large' },
    { value: 'extra-large', label: 'Extra Large' }
  ] as const;

  return (
    <div className="relative">
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        aria-label="Accessibility options"
        aria-expanded={isOpen}
      >
        <AdjustmentsHorizontalIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              className="fixed inset-0 z-40"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
            />

            {/* Menu */}
            <motion.div
              className="absolute right-0 top-full mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50"
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <div className="p-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Accessibility Options
                </h3>

                {/* Reduce Motion */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <EyeIcon className="w-5 h-5 text-gray-500" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      Reduce Motion
                    </span>
                  </div>
                  <motion.button
                    onClick={() => updatePreference('reduceMotion', !preferences.reduceMotion)}
                    className={`
                      relative w-11 h-6 rounded-full transition-colors
                      ${preferences.reduceMotion ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'}
                    `}
                    whileTap={{ scale: 0.95 }}
                    role="switch"
                    aria-checked={preferences.reduceMotion}
                    aria-label="Toggle reduce motion"
                  >
                    <motion.div
                      className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-md"
                      animate={{ x: preferences.reduceMotion ? 20 : 0 }}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  </motion.button>
                </div>

                {/* High Contrast */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <MagnifyingGlassIcon className="w-5 h-5 text-gray-500" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      High Contrast
                    </span>
                  </div>
                  <motion.button
                    onClick={() => updatePreference('highContrast', !preferences.highContrast)}
                    className={`
                      relative w-11 h-6 rounded-full transition-colors
                      ${preferences.highContrast ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'}
                    `}
                    whileTap={{ scale: 0.95 }}
                    role="switch"
                    aria-checked={preferences.highContrast}
                    aria-label="Toggle high contrast"
                  >
                    <motion.div
                      className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-md"
                      animate={{ x: preferences.highContrast ? 20 : 0 }}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  </motion.button>
                </div>

                {/* Font Size */}
                <div className="mb-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <SpeakerWaveIcon className="w-5 h-5 text-gray-500" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      Font Size
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {fontSizes.map(({ value, label }) => (
                      <motion.button
                        key={value}
                        onClick={() => updatePreference('fontSize', value)}
                        className={`
                          px-3 py-2 text-sm rounded-md transition-colors
                          ${preferences.fontSize === value
                            ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 border-2 border-primary-500'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-2 border-transparent hover:bg-gray-200 dark:hover:bg-gray-600'
                          }
                        `}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        aria-pressed={preferences.fontSize === value}
                      >
                        {label}
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Screen Reader Info */}
                {preferences.screenReader && (
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-md">
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      Screen reader detected. Enhanced navigation enabled.
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AccessibilityMenu;