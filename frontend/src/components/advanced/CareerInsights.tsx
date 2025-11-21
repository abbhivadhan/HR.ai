'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  SparklesIcon,
  TrophyIcon,
  ArrowTrendingUpIcon,
  CurrencyDollarIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  ChartBarIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline';
import { Line, Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface CareerPrediction {
  title: string;
  current: string;
  predicted: string;
  timeframe: string;
  confidence: number;
  icon: React.ReactNode;
}

export default function CareerInsights() {
  // Demo data for career predictions
  const [predictions] = useState<CareerPrediction[]>([
    {
      title: 'Next Role',
      current: 'Senior Developer',
      predicted: 'Tech Lead',
      timeframe: '12-18 months',
      confidence: 0.85,
      icon: <BriefcaseIcon className="w-6 h-6" />
    },
    {
      title: 'Salary Range',
      current: '$120K - $140K',
      predicted: '$150K - $180K',
      timeframe: '18-24 months',
      confidence: 0.78,
      icon: <CurrencyDollarIcon className="w-6 h-6" />
    },
    {
      title: 'Market Demand',
      current: 'High',
      predicted: 'Very High',
      timeframe: '6-12 months',
      confidence: 0.92,
      icon: <ArrowTrendingUpIcon className="w-6 h-6" />
    }
  ]);

  const salaryGrowthData = {
    labels: ['Current', '6 months', '1 year', '18 months', '2 years', '3 years'],
    datasets: [
      {
        label: 'Projected Salary',
        data: [130000, 138000, 150000, 162000, 175000, 195000],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'Market Average',
        data: [130000, 134000, 142000, 148000, 155000, 165000],
        borderColor: 'rgb(156, 163, 175)',
        backgroundColor: 'rgba(156, 163, 175, 0.1)',
        tension: 0.4,
        fill: true,
        borderDash: [5, 5]
      }
    ]
  };

  const skillsRadarData = {
    labels: ['React', 'TypeScript', 'Node.js', 'System Design', 'Leadership', 'Communication'],
    datasets: [
      {
        label: 'Current Level',
        data: [90, 85, 75, 65, 70, 80],
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 2
      },
      {
        label: 'Target for Tech Lead',
        data: [95, 90, 85, 90, 95, 90],
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 2
      }
    ]
  };

  const recommendations = [
    {
      title: 'Learn System Design',
      benefit: 'Critical for Tech Lead roles. Increase your chances by 40%',
      impact: 'High',
      effort: 'Medium',
      timeframe: '3-4 months'
    },
    {
      title: 'Get AWS Certification',
      benefit: 'Highly valued skill. Average salary increase of $15K',
      impact: 'High',
      effort: 'Low',
      timeframe: '1-2 months'
    },
    {
      title: 'Improve Leadership Skills',
      benefit: 'Essential for management track. Opens senior positions',
      impact: 'High',
      effort: 'Medium',
      timeframe: '6 months'
    },
    {
      title: 'Master GraphQL',
      benefit: 'Emerging technology with 60% job growth',
      impact: 'Medium',
      effort: 'Low',
      timeframe: '1 month'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
        <div className="flex items-center space-x-3 mb-2">
          <SparklesIcon className="w-8 h-8" />
          <h2 className="text-2xl font-bold">AI Career Insights</h2>
        </div>
        <p className="text-blue-100">
          Personalized predictions and recommendations for your career growth
        </p>
      </div>

      {/* Career Predictions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {predictions.map((prediction, index) => (
          <motion.div
            key={prediction.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center text-blue-600">
                {prediction.icon}
              </div>
              <span className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-600 rounded-full">
                {(prediction.confidence * 100).toFixed(0)}% confident
              </span>
            </div>

            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
              {prediction.title}
            </h3>

            <div className="space-y-2 mb-4">
              <div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Current</div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {prediction.current}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />
                <div className="flex-1 h-1 bg-gradient-to-r from-blue-500 to-green-500 rounded-full" />
              </div>
              <div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Predicted</div>
                <div className="text-sm font-semibold text-blue-600">
                  {prediction.predicted}
                </div>
              </div>
            </div>

            <div className="text-xs text-gray-600 dark:text-gray-400">
              Timeframe: {prediction.timeframe}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Salary Growth Projection */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center space-x-2 mb-4">
            <CurrencyDollarIcon className="w-6 h-6 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Salary Growth Projection
            </h3>
          </div>
          <div className="h-64">
            <Line
              data={salaryGrowthData}
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
                    ticks: {
                      callback: (value) => `$${(value as number / 1000).toFixed(0)}K`
                    }
                  }
                }
              }}
            />
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-4">
            Based on your skills, experience, and market trends
          </p>
        </div>

        {/* Skills Radar */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center space-x-2 mb-4">
            <ChartBarIcon className="w-6 h-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Skills Assessment
            </h3>
          </div>
          <div className="h-64">
            <Radar
              data={skillsRadarData}
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
                  r: {
                    beginAtZero: true,
                    max: 100
                  }
                }
              }}
            />
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-4">
            Your current skills vs. target for next role
          </p>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="flex items-center space-x-2 mb-6">
          <LightBulbIcon className="w-6 h-6 text-yellow-500" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Personalized Recommendations
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
                <span className={`text-xs px-2 py-1 rounded-full ${
                  rec.impact === 'High' 
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-600'
                    : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600'
                }`}>
                  {rec.impact} Impact
                </span>
              </div>

              <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                {rec.benefit}
              </p>

              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-500 dark:text-gray-400">
                  Effort: {rec.effort}
                </span>
                <span className="text-gray-500 dark:text-gray-400">
                  {rec.timeframe}
                </span>
              </div>

              <button className="mt-3 w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                Start Learning
              </button>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Career Readiness Score */}
      <div className="bg-gradient-to-r from-green-600 to-teal-600 rounded-lg p-6 text-white">
        <h3 className="text-xl font-bold mb-4">Career Readiness Score</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="text-4xl font-bold">87%</div>
            <div className="text-green-100 text-sm">Overall Readiness</div>
          </div>
          <div>
            <div className="text-4xl font-bold">+29%</div>
            <div className="text-green-100 text-sm">Above Market Average</div>
          </div>
          <div>
            <div className="text-4xl font-bold">Top 15%</div>
            <div className="text-green-100 text-sm">In Your Field</div>
          </div>
        </div>
      </div>
    </div>
  );
}
