'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface DashboardCardProps {
  title: string;
  children: React.ReactNode;
  className?: string;
  loading?: boolean;
  error?: string;
  actions?: React.ReactNode;
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  children,
  className = '',
  loading = false,
  error,
  actions
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`bg-white rounded-lg shadow-md border border-gray-200 ${className}`}
    >
      <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {actions && <div className="flex space-x-2">{actions}</div>}
      </div>
      
      <div className="p-6">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-32 text-red-600">
            <div className="text-center">
              <p className="text-sm">Error loading data</p>
              <p className="text-xs text-gray-500 mt-1">{error}</p>
            </div>
          </div>
        ) : (
          children
        )}
      </div>
    </motion.div>
  );
};

export default DashboardCard;