'use client';

import React from 'react';
import { SunIcon, MoonIcon, ComputerDesktopIcon } from '@heroicons/react/24/outline';
import { useTheme } from '@/contexts/ThemeContext';
import { motion } from 'framer-motion';

const ThemeToggle: React.FC = () => {
  const { theme, setTheme, isDark } = useTheme();

  const themes = [
    { value: 'light', icon: SunIcon, label: 'Light' },
    { value: 'dark', icon: MoonIcon, label: 'Dark' },
    { value: 'system', icon: ComputerDesktopIcon, label: 'System' }
  ] as const;

  return (
    <div className="relative">
      <div className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
        {themes.map(({ value, icon: Icon, label }) => (
          <motion.button
            key={value}
            onClick={() => setTheme(value)}
            className={`
              relative flex items-center justify-center w-8 h-8 rounded-md transition-colors
              ${theme === value 
                ? 'text-white' 
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
              }
            `}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            aria-label={`Switch to ${label} theme`}
          >
            {theme === value && (
              <motion.div
                layoutId="theme-indicator"
                className="absolute inset-0 bg-primary-500 rounded-md"
                initial={false}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              />
            )}
            <Icon className="w-4 h-4 relative z-10" />
          </motion.button>
        ))}
      </div>
    </div>
  );
};

export default ThemeToggle;