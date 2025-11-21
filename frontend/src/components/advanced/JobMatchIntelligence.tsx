'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  SparklesIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowRightIcon,
  FireIcon
} from '@heroicons/react/24/outline';

interface JobMatch {
  id: string;
  title: string;
  company: string;
  location: string;
  salary: string;
  matchScore: number;
  matchReasons: string[];
  missingSkills: string[];
  postedDate: Date;
  applicants: number;
  isHot: boolean;
}

export default function JobMatchIntelligence() {
  // All demo data removed - will be populated from API
  const [matches] = useState<JobMatch[]>([]);

  const getMatchColor = (score: number) => {
    if (score >= 90) return 'from-green-500 to-emerald-500';
    if (score >= 80) return 'from-blue-500 to-cyan-500';
    return 'from-yellow-500 to-orange-500';
  };

  const getMatchBadge = (score: number) => {
    if (score >= 90) return { text: 'Excellent Match', color: 'bg-green-100 dark:bg-green-900/30 text-green-600' };
    if (score >= 80) return { text: 'Good Match', color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600' };
    return { text: 'Fair Match', color: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600' };
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center space-x-3 mb-2">
          <SparklesIcon className="w-8 h-8" />
          <h2 className="text-2xl font-bold">AI Job Match Intelligence</h2>
        </div>
        <p className="text-blue-100">
          Smart job recommendations based on your profile, skills, and preferences
        </p>
      </div>

      {/* Match Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
          <div className="text-3xl font-bold text-blue-600">8</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">New Matches Today</div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
          <div className="text-3xl font-bold text-green-600">95%</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Best Match Score</div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
          <div className="text-3xl font-bold text-purple-600">3</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Hot Opportunities</div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
          <div className="text-3xl font-bold text-orange-600">$155K</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Avg. Salary Match</div>
        </div>
      </div>

      {/* Job Matches */}
      <div className="space-y-4">
        {matches.map((job, index) => {
          const badge = getMatchBadge(job.matchScore);
          
          return (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
            >
              {/* Match Score Bar */}
              <div className={`h-2 bg-gradient-to-r ${getMatchColor(job.matchScore)}`} />

              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                        {job.title}
                      </h3>
                      {job.isHot && (
                        <span className="flex items-center space-x-1 px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-600 rounded-full text-xs font-semibold">
                          <FireIcon className="w-4 h-4" />
                          <span>Hot</span>
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 dark:text-gray-400">{job.company}</p>
                  </div>

                  <div className="text-right">
                    <div className="text-3xl font-bold text-blue-600 mb-1">
                      {job.matchScore}%
                    </div>
                    <span className={`text-xs px-3 py-1 rounded-full ${badge.color}`}>
                      {badge.text}
                    </span>
                  </div>
                </div>

                {/* Job Details */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <MapPinIcon className="w-5 h-5 text-gray-400" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{job.location}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CurrencyDollarIcon className="w-5 h-5 text-gray-400" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{job.salary}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <ClockIcon className="w-5 h-5 text-gray-400" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {Math.floor((Date.now() - job.postedDate.getTime()) / 86400000)}d ago
                    </span>
                  </div>
                </div>

                {/* Match Reasons */}
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                    Why this is a great match:
                  </h4>
                  <div className="space-y-2">
                    {job.matchReasons.map((reason, idx) => (
                      <div key={idx} className="flex items-start space-x-2">
                        <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700 dark:text-gray-300">{reason}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Missing Skills */}
                {job.missingSkills.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                      Skills to develop:
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {job.missingSkills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 text-xs rounded-full"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Competition Indicator */}
                <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      Competition Level:
                    </span>
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        {[1, 2, 3, 4, 5].map((level) => (
                          <div
                            key={level}
                            className={`w-2 h-6 rounded ${
                              level <= Math.ceil(job.applicants / 15)
                                ? 'bg-blue-600'
                                : 'bg-gray-300 dark:bg-gray-600'
                            }`}
                          />
                        ))}
                      </div>
                      <span className="text-sm font-semibold text-gray-900 dark:text-white">
                        {job.applicants} applicants
                      </span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex space-x-3">
                  <button className="flex-1 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold flex items-center justify-center space-x-2">
                    <span>Apply Now</span>
                    <ArrowRightIcon className="w-5 h-5" />
                  </button>
                  <button className="px-6 py-3 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-semibold">
                    Save
                  </button>
                  <button className="px-6 py-3 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-semibold">
                    Details
                  </button>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* AI Insights */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg p-6 text-white">
        <h3 className="text-xl font-bold mb-4">💡 AI Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="text-2xl font-bold mb-1">Best Time to Apply</div>
            <div className="text-purple-100">
              Monday-Wednesday, 9-11 AM for 40% higher response rate
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold mb-1">Your Competitive Edge</div>
            <div className="text-purple-100">
              Your React + Node.js combo puts you in top 10% of candidates
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
