'use client';

import React from 'react';

interface ProgressTrackerProps {
  currentQuestion: number;
  totalQuestions: number;
  timeRemaining: number;
  totalTime: number;
  onTimeWarning?: () => void;
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  currentQuestion,
  totalQuestions,
  timeRemaining,
  totalTime,
  onTimeWarning
}) => {
  const progressPercentage = Math.round((currentQuestion / totalQuestions) * 100);
  const timePercentage = Math.round((timeRemaining / totalTime) * 100);
  
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

  const getTimeColor = () => {
    if (timeRemaining < 300) return 'text-red-600'; // Less than 5 minutes
    if (timeRemaining < 600) return 'text-orange-600'; // Less than 10 minutes
    return 'text-gray-900';
  };

  const getTimeBackgroundColor = () => {
    if (timeRemaining < 300) return 'bg-red-100'; // Less than 5 minutes
    if (timeRemaining < 600) return 'bg-orange-100'; // Less than 10 minutes
    return 'bg-gray-100';
  };

  return (
    <div className="bg-white border-b shadow-sm">
      <div className="max-w-4xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Question Progress */}
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              Question <span className="font-semibold">{currentQuestion}</span> of{' '}
              <span className="font-semibold">{totalQuestions}</span>
            </div>
            
            {/* Progress Bar */}
            <div className="relative">
              <div 
                className="w-32 bg-gray-200 rounded-full h-2" 
                role="progressbar" 
                aria-valuenow={progressPercentage}
                aria-valuemin={0} 
                aria-valuemax={100}
                aria-label={`Assessment progress: ${currentQuestion} of ${totalQuestions} questions completed`}
              >
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
              
              {/* Progress percentage tooltip */}
              <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                {progressPercentage}%
              </div>
            </div>
          </div>

          {/* Time Remaining */}
          <div className="flex items-center space-x-3">
            {/* Time Progress Ring */}
            <div className="relative w-12 h-12">
              <svg className="w-12 h-12 transform -rotate-90" viewBox="0 0 36 36">
                {/* Background circle */}
                <path
                  className="text-gray-200"
                  stroke="currentColor"
                  strokeWidth="3"
                  fill="transparent"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                {/* Progress circle */}
                <path
                  className={timePercentage < 20 ? 'text-red-500' : timePercentage < 40 ? 'text-orange-500' : 'text-blue-500'}
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                  fill="transparent"
                  strokeDasharray={`${timePercentage}, 100`}
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`text-xs font-medium ${getTimeColor()}`}>
                  {Math.round(timePercentage)}%
                </span>
              </div>
            </div>

            {/* Time Display */}
            <div className={`px-3 py-2 rounded-lg ${getTimeBackgroundColor()}`}>
              <div className="text-xs text-gray-600 mb-1">Time Remaining</div>
              <div 
                className={`text-lg font-mono font-semibold ${getTimeColor()}`}
                aria-live="polite"
                aria-label={`Time remaining: ${formatTime(timeRemaining)}`}
              >
                {formatTime(timeRemaining)}
              </div>
            </div>

            {/* Warning indicators */}
            {timeRemaining < 300 && (
              <div className="flex items-center text-red-600 animate-pulse">
                <svg className="w-5 h-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="text-xs font-medium">Low Time</span>
              </div>
            )}
          </div>
        </div>

        {/* Additional Progress Information */}
        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
          <div>
            {currentQuestion > 1 && (
              <span>Average time per question: {formatTime(Math.round((totalTime - timeRemaining) / (currentQuestion - 1)))}</span>
            )}
          </div>
          <div>
            {timeRemaining > 0 && totalQuestions > currentQuestion && (
              <span>
                Estimated time per remaining question: {formatTime(Math.round(timeRemaining / (totalQuestions - currentQuestion + 1)))}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressTracker;