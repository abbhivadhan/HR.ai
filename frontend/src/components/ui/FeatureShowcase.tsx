'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import AnimatedButton from './AnimatedButton';
import AnimatedCard from './AnimatedCard';
import AnimatedInput from './AnimatedInput';
import ThemeToggle from './ThemeToggle';
import AccessibilityMenu from './AccessibilityMenu';
import LanguageSelector from './LanguageSelector';
import LazyImage from './LazyImage';
import LoadingSpinner from './LoadingSpinner';
import { usePWA } from '@/hooks/usePWA';
import { useTranslation } from '@/hooks/useTranslation';

const FeatureShowcase: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const { isInstallable, installApp, isOnline } = usePWA();
  const { t } = useTranslation('common');

  const handleAsyncAction = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    setLoading(false);
  };

  const features = [
    {
      title: 'Progressive Web App',
      description: 'Install the app for offline access and native-like experience',
      component: isInstallable && (
        <AnimatedButton onClick={installApp} variant="primary">
          Install App
        </AnimatedButton>
      )
    },
    {
      title: 'Dark Mode & Themes',
      description: 'Switch between light, dark, and system themes',
      component: <ThemeToggle />
    },
    {
      title: 'Accessibility Features',
      description: 'WCAG compliant with customizable accessibility options',
      component: <AccessibilityMenu />
    },
    {
      title: 'Internationalization',
      description: 'Multi-language support with automatic locale detection',
      component: <LanguageSelector />
    },
    {
      title: 'Advanced Animations',
      description: 'Smooth micro-interactions and motion design',
      component: (
        <div className="space-y-2">
          <AnimatedButton 
            variant="secondary" 
            loading={loading}
            onClick={handleAsyncAction}
          >
            {loading ? 'Loading...' : 'Animate Me'}
          </AnimatedButton>
          <LoadingSpinner size="md" />
        </div>
      )
    },
    {
      title: 'Smart Input Fields',
      description: 'Enhanced form inputs with floating labels and validation',
      component: (
        <AnimatedInput
          label="Email Address"
          type="email"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Enter your email"
        />
      )
    },
    {
      title: 'Lazy Loading',
      description: 'Optimized image loading with intersection observer',
      component: (
        <LazyImage
          src="https://via.placeholder.com/200x100/3b82f6/ffffff?text=Lazy+Image"
          alt="Lazy loaded image example"
          className="w-full h-20 rounded-lg"
          placeholder="https://via.placeholder.com/200x100/e5e7eb/9ca3af?text=Loading"
        />
      )
    },
    {
      title: 'Performance Monitoring',
      description: 'Real-time performance metrics and Core Web Vitals tracking',
      component: (
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Check the performance monitor in the bottom-right corner
        </div>
      )
    }
  ];

  return (
    <div className="max-w-6xl mx-auto p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-12"
      >
        <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          Advanced UI/UX Features
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
          Experience the enhanced user interface with progressive web app capabilities,
          accessibility features, internationalization, and performance optimizations.
        </p>
        
        {/* Connection Status */}
        <motion.div
          className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full text-sm font-medium mt-4 ${
            isOnline 
              ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300'
              : 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300'
          }`}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`} />
          <span>{isOnline ? 'Online' : 'Offline'}</span>
        </motion.div>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, index) => (
          <AnimatedCard
            key={feature.title}
            delay={index * 0.1}
            className="p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              {feature.title}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
              {feature.description}
            </p>
            <div className="mt-auto">
              {feature.component}
            </div>
          </AnimatedCard>
        ))}
      </div>

      {/* Performance Tips */}
      <motion.div
        className="mt-12 p-6 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
          Performance Optimizations
        </h3>
        <ul className="space-y-2 text-blue-800 dark:text-blue-200 text-sm">
          <li>• Bundle splitting and code optimization</li>
          <li>• Lazy loading for images and components</li>
          <li>• Service worker caching for offline support</li>
          <li>• Virtual scrolling for large lists</li>
          <li>• Memory-efficient caching system</li>
          <li>• Core Web Vitals monitoring</li>
        </ul>
      </motion.div>
    </div>
  );
};

export default FeatureShowcase;