'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChartBarIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { performanceMonitor, analyzeBundleSize, getMemoryUsage } from '@/utils/performance';

const PerformanceMonitor: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [metrics, setMetrics] = useState<any>({});
  const [bundleInfo, setBundleInfo] = useState<any>(null);
  const [memoryInfo, setMemoryInfo] = useState<any>(null);

  useEffect(() => {
    if (isOpen) {
      const updateMetrics = () => {
        const coreWebVitals = performanceMonitor.getCoreWebVitals();
        const bundle = analyzeBundleSize();
        const memory = getMemoryUsage();
        
        setMetrics(coreWebVitals);
        setBundleInfo(bundle);
        setMemoryInfo(memory);
      };

      updateMetrics();
      const interval = setInterval(updateMetrics, 1000);
      
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  const getScoreColor = (value: number, thresholds: { good: number; needs: number }) => {
    if (value <= thresholds.good) return 'text-green-600';
    if (value <= thresholds.needs) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <>
      {/* Toggle Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 z-50 p-3 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        title="Performance Monitor"
      >
        <ChartBarIcon className="w-6 h-6" />
      </motion.button>

      {/* Performance Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="fixed bottom-20 right-4 z-50 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700"
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Performance Monitor
                </h3>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>

              {/* Core Web Vitals */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Core Web Vitals
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">LCP:</span>
                    <span className={`text-sm font-medium ${getScoreColor(metrics.lcp || 0, { good: 2500, needs: 4000 })}`}>
                      {metrics.lcp ? `${Math.round(metrics.lcp)}ms` : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">FID:</span>
                    <span className={`text-sm font-medium ${getScoreColor(metrics.fid || 0, { good: 100, needs: 300 })}`}>
                      {metrics.fid ? `${Math.round(metrics.fid)}ms` : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 dark:text-gray-400">CLS:</span>
                    <span className={`text-sm font-medium ${getScoreColor(metrics.cls || 0, { good: 0.1, needs: 0.25 })}`}>
                      {metrics.cls ? metrics.cls.toFixed(3) : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Bundle Information */}
              {bundleInfo && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Bundle Size
                  </h4>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">JS:</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {bundleInfo.totalJSSize} KB ({bundleInfo.jsFileCount} files)
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">CSS:</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {bundleInfo.totalCSSSize} KB ({bundleInfo.cssFileCount} files)
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Memory Usage */}
              {memoryInfo && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Memory Usage
                  </h4>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Used:</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {memoryInfo.usedJSHeapSize} MB
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Total:</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {memoryInfo.totalJSHeapSize} MB
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Limit:</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {memoryInfo.jsHeapSizeLimit} MB
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex space-x-2">
                <button
                  onClick={() => {
                    const data = performanceMonitor.exportMetrics();
                    const blob = new Blob([data], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'performance-metrics.json';
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="flex-1 px-3 py-2 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                >
                  Export Metrics
                </button>
                <button
                  onClick={() => {
                    performanceMonitor.clear();
                    setMetrics({});
                  }}
                  className="flex-1 px-3 py-2 text-xs bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
                >
                  Clear Data
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default PerformanceMonitor;