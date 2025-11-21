'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  LightBulbIcon,
  ClockIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface Prediction {
  metric: string;
  current: number;
  predicted: number;
  confidence: number;
  trend: 'up' | 'down' | 'stable';
  insight: string;
}

interface Recommendation {
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'high' | 'medium' | 'low';
  category: string;
}

export default function PredictiveAnalytics() {
  const [predictions, setPredictions] = useState<Prediction[]>([
    {
      metric: 'Time to Hire',
      current: 28,
      predicted: 21,
      confidence: 0.87,
      trend: 'down',
      insight: 'Implementing automated screening will reduce time by 25%'
    },
    {
      metric: 'Cost per Hire',
      current: 4500,
      predicted: 3800,
      confidence: 0.82,
      trend: 'down',
      insight: 'Optimizing job board spend can save $700 per hire'
    },
    {
      metric: 'Candidate Quality',
      current: 72,
      predicted: 85,
      confidence: 0.91,
      trend: 'up',
      insight: 'AI-powered matching will improve quality score by 18%'
    },
    {
      metric: 'Offer Acceptance Rate',
      current: 68,
      predicted: 78,
      confidence: 0.79,
      trend: 'up',
      insight: 'Competitive salary adjustments will boost acceptance'
    }
  ]);

  const [recommendations, setRecommendations] = useState<Recommendation[]>([
    {
      title: 'Implement AI Resume Screening',
      description: 'Automate initial resume screening to reduce time-to-hire by 40%',
      impact: 'high',
      effort: 'medium',
      category: 'Efficiency'
    },
    {
      title: 'Optimize Job Board Strategy',
      description: 'Focus on top 3 performing job boards to reduce cost per hire',
      impact: 'high',
      effort: 'low',
      category: 'Cost'
    },
    {
      title: 'Enhance Candidate Experience',
      description: 'Improve communication touchpoints to boost offer acceptance',
      impact: 'medium',
      effort: 'medium',
      category: 'Quality'
    },
    {
      title: 'Expand Referral Program',
      description: 'Increase employee referral incentives for better quality hires',
      impact: 'high',
      effort: 'low',
      category: 'Quality'
    }
  ]);

  const timeToHireData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
    datasets: [
      {
        label: 'Actual',
        data: [32, 30, 28, 29, 28, 27, 28, 26, 25],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4
      },
      {
        label: 'Predicted',
        data: [null, null, null, null, null, null, null, 25, 23, 21, 20, 19],
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderDash: [5, 5],
        tension: 0.4
      }
    ]
  };

  const costAnalysisData = {
    labels: ['Job Boards', 'Recruiter Time', 'Tools', 'Advertising', 'Other'],
    datasets: [
      {
        data: [1800, 1500, 600, 400, 200],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(139, 92, 246, 0.8)'
        ]
      }
    ]
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'text-green-600 bg-green-100 dark:bg-green-900/30';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30';
      case 'low':
        return 'text-gray-600 bg-gray-100 dark:bg-gray-700';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center space-x-3 mb-2">
          <ChartBarIcon className="w-8 h-8" />
          <h2 className="text-2xl font-bold">Predictive Analytics</h2>
        </div>
        <p className="text-blue-100">
          AI-powered insights to optimize your hiring process
        </p>
      </div>

      {/* Key Predictions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {predictions.map((prediction, index) => (
          <motion.div
            key={prediction.metric}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                {prediction.metric}
              </h3>
              {prediction.trend === 'up' ? (
                <ArrowTrendingUpIcon className="w-5 h-5 text-green-500" />
              ) : prediction.trend === 'down' ? (
                <ArrowTrendingDownIcon className="w-5 h-5 text-red-500" />
              ) : (
                <div className="w-5 h-5" />
              )}
            </div>

            <div className="space-y-2">
              <div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Current</div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {prediction.metric.includes('Cost') ? '$' : ''}
                  {prediction.current}
                  {prediction.metric.includes('Rate') || prediction.metric.includes('Quality') ? '%' : ''}
                  {prediction.metric.includes('Time') ? ' days' : ''}
                </div>
              </div>

              <div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Predicted</div>
                <div className="text-xl font-semibold text-blue-600">
                  {prediction.metric.includes('Cost') ? '$' : ''}
                  {prediction.predicted}
                  {prediction.metric.includes('Rate') || prediction.metric.includes('Quality') ? '%' : ''}
                  {prediction.metric.includes('Time') ? ' days' : ''}
                </div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600 dark:text-gray-400">Confidence</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {(prediction.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${prediction.confidence * 100}%` }}
                  transition={{ delay: index * 0.1 + 0.3, duration: 0.5 }}
                  className="h-full bg-blue-600 rounded-full"
                />
              </div>
            </div>

            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-xs text-gray-700 dark:text-gray-300">
                {prediction.insight}
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Time to Hire Trend */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center space-x-2 mb-4">
            <ClockIcon className="w-6 h-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Time to Hire Trend
            </h3>
          </div>
          <div className="h-64">
            <Line
              data={timeToHireData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: true,
                    position: 'bottom'
                  }
                },
                scales: {
                  y: {
                    beginAtZero: false,
                    title: {
                      display: true,
                      text: 'Days'
                    }
                  }
                }
              }}
            />
          </div>
        </div>

        {/* Cost Breakdown */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center space-x-2 mb-4">
            <CurrencyDollarIcon className="w-6 h-6 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Cost per Hire Breakdown
            </h3>
          </div>
          <div className="h-64">
            <Doughnut
              data={costAnalysisData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: true,
                    position: 'bottom'
                  }
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="flex items-center space-x-2 mb-6">
          <LightBulbIcon className="w-6 h-6 text-yellow-500" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            AI-Powered Recommendations
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations.map((rec, index) => (
            <motion.div
              key={rec.title}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-gray-900 dark:text-white">
                  {rec.title}
                </h4>
                <span className="text-xs px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600">
                  {rec.category}
                </span>
              </div>

              <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                {rec.description}
              </p>

              <div className="flex items-center space-x-4 text-xs">
                <div className="flex items-center space-x-1">
                  <span className="text-gray-500 dark:text-gray-400">Impact:</span>
                  <span className={`px-2 py-1 rounded-full ${getImpactColor(rec.impact)}`}>
                    {rec.impact}
                  </span>
                </div>
                <div className="flex items-center space-x-1">
                  <span className="text-gray-500 dark:text-gray-400">Effort:</span>
                  <span className={`px-2 py-1 rounded-full ${getImpactColor(rec.effort)}`}>
                    {rec.effort}
                  </span>
                </div>
              </div>

              <button className="mt-4 w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                Implement
              </button>
            </motion.div>
          ))}
        </div>
      </div>

      {/* ROI Calculator */}
      <div className="bg-gradient-to-r from-green-600 to-teal-600 rounded-lg p-6 text-white">
        <h3 className="text-xl font-bold mb-4">Projected ROI</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="text-3xl font-bold">$127,000</div>
            <div className="text-green-100 text-sm">Annual Savings</div>
          </div>
          <div>
            <div className="text-3xl font-bold">42%</div>
            <div className="text-green-100 text-sm">Efficiency Gain</div>
          </div>
          <div>
            <div className="text-3xl font-bold">156</div>
            <div className="text-green-100 text-sm">Hours Saved/Month</div>
          </div>
        </div>
      </div>
    </div>
  );
}
