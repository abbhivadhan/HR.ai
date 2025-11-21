'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ClockIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

interface InterviewProgressProps {
  currentQuestionIndex: number;
  totalQuestions: number;
  timeRemaining: number;
  totalDuration: number;
}

export const InterviewProgress: React.FC<InterviewProgressProps> = ({
  currentQuestionIndex,
  totalQuestions,
  timeRemaining,
  totalDuration
}) => {
  const questionProgress = totalQuestions > 0 ? ((currentQuestionIndex + 1) / totalQuestions) * 100 : 0;
  const timeProgress = totalDuration > 0 ? ((totalDuration - timeRemaining) / totalDuration) * 100 : 0;

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    } else {
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
  };

  const getTimeColor = (remaining: number, total: number): string => {
    const percentage = (remaining / total) * 100;
    if (percentage > 50) return 'text-green-400';
    if (percentage > 25) return 'text-yellow-400';
    if (percentage > 10) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <div className="bg-gray-800 border-t border-gray-700 px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Question progress */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <CheckCircleIcon className="h-5 w-5 text-blue-400" />
            <span className="text-white text-sm font-medium">
              Question {currentQuestionIndex + 1} of {totalQuestions}
            </span>
          </div>
          
          {/* Question progress bar */}
          <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-blue-500 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${questionProgress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
          
          <span className="text-gray-400 text-sm">
            {Math.round(questionProgress)}%
          </span>
        </div>

        {/* Time remaining */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <ClockIcon className="h-5 w-5 text-gray-400" />
            <span className="text-gray-400 text-sm">Time remaining:</span>
            <span className={`text-sm font-mono font-medium ${getTimeColor(timeRemaining, totalDuration)}`}>
              {formatTime(timeRemaining)}
            </span>
          </div>
          
          {/* Time progress bar */}
          <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              className={`h-full rounded-full ${
                timeProgress > 75 ? 'bg-red-500' :
                timeProgress > 50 ? 'bg-orange-500' :
                timeProgress > 25 ? 'bg-yellow-500' :
                'bg-green-500'
              }`}
              initial={{ width: 0 }}
              animate={{ width: `${timeProgress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
          
          <span className="text-gray-400 text-sm">
            {Math.round(timeProgress)}%
          </span>
        </div>
      </div>

      {/* Question indicators */}
      {totalQuestions > 0 && (
        <div className="mt-3 flex items-center justify-center space-x-2">
          {Array.from({ length: totalQuestions }, (_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full transition-colors ${
                index < currentQuestionIndex
                  ? 'bg-green-500'
                  : index === currentQuestionIndex
                  ? 'bg-blue-500'
                  : 'bg-gray-600'
              }`}
              title={`Question ${index + 1}`}
            />
          ))}
        </div>
      )}

      {/* Warning indicators */}
      {timeRemaining <= 300 && timeRemaining > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-2 flex items-center justify-center"
        >
          <div className="bg-red-900 border border-red-700 rounded-lg px-3 py-1">
            <span className="text-red-300 text-sm font-medium">
              ⚠️ Less than 5 minutes remaining
            </span>
          </div>
        </motion.div>
      )}

      {timeRemaining <= 60 && timeRemaining > 0 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mt-2 flex items-center justify-center"
        >
          <div className="bg-red-800 border border-red-600 rounded-lg px-4 py-2 animate-pulse">
            <span className="text-red-200 text-sm font-bold">
              ALERT: Final minute - prepare to wrap up!
            </span>
          </div>
        </motion.div>
      )}
    </div>
  );
};