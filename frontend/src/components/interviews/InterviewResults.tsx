'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  ClockIcon,
  MicrophoneIcon,
  VideoCameraIcon,
  DocumentTextIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  ComputerDesktopIcon,
  UserIcon,
  StarIcon,
  BuildingOfficeIcon,
  WrenchScrewdriverIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';
import {
  Interview,
  InterviewAnalysis,
  InterviewQuestion,
  QuestionCategory
} from '../../types/interview';
import { interviewService } from '../../services/interviewService';

interface InterviewResultsProps {
  interview: Interview;
  analysis?: InterviewAnalysis;
  questions: InterviewQuestion[];
  onClose: () => void;
}

export const InterviewResults: React.FC<InterviewResultsProps> = ({
  interview,
  analysis,
  questions,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'detailed' | 'questions' | 'recommendations'>('overview');
  const [isLoading, setIsLoading] = useState(false);

  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-blue-600';
    if (score >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBackground = (score: number): string => {
    if (score >= 0.8) return 'bg-green-100';
    if (score >= 0.6) return 'bg-blue-100';
    if (score >= 0.4) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getRecommendationIcon = (recommendation?: string) => {
    switch (recommendation?.toLowerCase()) {
      case 'hire':
        return <CheckCircleIcon className="h-6 w-6 text-green-600" />;
      case 'maybe':
        return <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600" />;
      case 'reject':
        return <XCircleIcon className="h-6 w-6 text-red-600" />;
      default:
        return <ChartBarIcon className="h-6 w-6 text-gray-600" />;
    }
  };

  const formatPercentage = (score: number): string => {
    return `${Math.round(score * 100)}%`;
  };

  const formatDuration = (seconds?: number): string => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getCategoryIcon = (category: QuestionCategory) => {
    switch (category) {
      case QuestionCategory.TECHNICAL:
        return <ComputerDesktopIcon className="w-5 h-5" />;
      case QuestionCategory.BEHAVIORAL:
        return <UserIcon className="w-5 h-5" />;
      case QuestionCategory.SITUATIONAL:
        return <StarIcon className="w-5 h-5" />;
      case QuestionCategory.COMPANY_CULTURE:
        return <BuildingOfficeIcon className="w-5 h-5" />;
      case QuestionCategory.PROBLEM_SOLVING:
        return <WrenchScrewdriverIcon className="w-5 h-5" />;
      default:
        return <QuestionMarkCircleIcon className="w-5 h-5" />;
    }
  };

  const handleDownloadReport = async () => {
    setIsLoading(true);
    try {
      // In a real implementation, this would generate and download a PDF report
      console.log('Downloading interview report...');
      // Simulate download
      await new Promise(resolve => setTimeout(resolve, 2000));
    } catch (error) {
      console.error('Failed to download report:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleShareResults = () => {
    // In a real implementation, this would open a share dialog
    console.log('Sharing interview results...');
  };

  if (!analysis) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Processing interview results...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{interview.title}</h1>
              <p className="text-gray-600">
                Interview completed on {new Date(interview.completed_at || '').toLocaleDateString()}
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                {getRecommendationIcon(interview.recommendation)}
                <span className="font-medium text-gray-900">
                  {interview.recommendation || 'Pending'}
                </span>
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={handleDownloadReport}
                  disabled={isLoading}
                  className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {isLoading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <ArrowDownTrayIcon className="h-4 w-4" />
                  )}
                  <span>Download Report</span>
                </button>
                
                <button
                  onClick={handleShareResults}
                  className="flex items-center space-x-2 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
                >
                  <ShareIcon className="h-4 w-4" />
                  <span>Share</span>
                </button>
                
                <button
                  onClick={onClose}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'detailed', label: 'Detailed Analysis' },
              { id: 'questions', label: 'Questions & Responses' },
              { id: 'recommendations', label: 'Recommendations' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Overall Score */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-center">
                <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full ${getScoreBackground(analysis.overall_score)} mb-4`}>
                  <span className={`text-3xl font-bold ${getScoreColor(analysis.overall_score)}`}>
                    {formatPercentage(analysis.overall_score)}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Overall Score</h3>
                <p className="text-gray-600">
                  Based on {analysis.questions_answered} questions answered
                </p>
              </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <MicrophoneIcon className="h-8 w-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Communication</p>
                    <p className={`text-2xl font-semibold ${getScoreColor(analysis.communication_score)}`}>
                      {formatPercentage(analysis.communication_score)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <ChartBarIcon className="h-8 w-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Confidence</p>
                    <p className={`text-2xl font-semibold ${getScoreColor(analysis.confidence_score)}`}>
                      {formatPercentage(analysis.confidence_score)}
                    </p>
                  </div>
                </div>
              </div>

              {analysis.technical_score && (
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center">
                    <DocumentTextIcon className="h-8 w-8 text-purple-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Technical</p>
                      <p className={`text-2xl font-semibold ${getScoreColor(analysis.technical_score)}`}>
                        {formatPercentage(analysis.technical_score)}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <ClockIcon className="h-8 w-8 text-orange-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {formatDuration(analysis.average_response_time)}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Skill Scores */}
            {analysis.skill_scores && Object.keys(analysis.skill_scores).length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Skill Assessment</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(analysis.skill_scores).map(([skill, score]) => (
                    <div key={skill} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="font-medium text-gray-900">{skill}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              score >= 0.8 ? 'bg-green-500' :
                              score >= 0.6 ? 'bg-blue-500' :
                              score >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${score * 100}%` }}
                          />
                        </div>
                        <span className={`text-sm font-medium ${getScoreColor(score)}`}>
                          {formatPercentage(score)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Summary */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Strengths</h3>
                <ul className="space-y-2">
                  {analysis.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <CheckCircleIcon className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Areas for Improvement</h3>
                <ul className="space-y-2">
                  {analysis.areas_for_improvement.map((area, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{area}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        )}

        {/* Detailed Analysis Tab */}
        {activeTab === 'detailed' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Speech Analysis */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Speech Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-semibold text-gray-900">
                    {analysis.speech_pace ? Math.round(analysis.speech_pace) : 'N/A'}
                  </p>
                  <p className="text-sm text-gray-600">Words per minute</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-semibold text-gray-900">{analysis.filler_word_count}</p>
                  <p className="text-sm text-gray-600">Filler words</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-semibold text-gray-900">
                    {analysis.clarity_score ? formatPercentage(analysis.clarity_score) : 'N/A'}
                  </p>
                  <p className="text-sm text-gray-600">Clarity score</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-semibold text-gray-900">
                    {analysis.vocabulary_complexity ? formatPercentage(analysis.vocabulary_complexity) : 'N/A'}
                  </p>
                  <p className="text-sm text-gray-600">Vocabulary complexity</p>
                </div>
              </div>
            </div>

            {/* Video Analysis */}
            {(analysis.engagement_score || analysis.eye_contact_percentage) && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Video Analysis</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {analysis.engagement_score && (
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <p className="text-2xl font-semibold text-gray-900">
                        {formatPercentage(analysis.engagement_score)}
                      </p>
                      <p className="text-sm text-gray-600">Engagement score</p>
                    </div>
                  )}
                  {analysis.eye_contact_percentage && (
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <p className="text-2xl font-semibold text-gray-900">
                        {formatPercentage(analysis.eye_contact_percentage)}
                      </p>
                      <p className="text-sm text-gray-600">Eye contact</p>
                    </div>
                  )}
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-2xl font-semibold text-gray-900">
                      {formatPercentage(analysis.data_quality_score || 0.8)}
                    </p>
                    <p className="text-sm text-gray-600">Data quality</p>
                  </div>
                </div>
              </div>
            )}

            {/* Personality Traits */}
            {analysis.personality_traits && Object.keys(analysis.personality_traits).length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Personality Assessment</h3>
                <div className="space-y-4">
                  {Object.entries(analysis.personality_traits).map(([trait, score]) => (
                    <div key={trait} className="flex items-center justify-between">
                      <span className="font-medium text-gray-900 capitalize">{trait}</span>
                      <div className="flex items-center space-x-3">
                        <div className="w-32 h-3 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500 rounded-full transition-all duration-500"
                            style={{ width: `${score * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-600 w-12">
                          {formatPercentage(score)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Questions Tab */}
        {activeTab === 'questions' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {questions.map((question, index) => (
              <div key={question.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-semibold">{index + 1}</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-lg">{getCategoryIcon(question.category)}</span>
                      <span className="text-sm font-medium text-gray-600 capitalize">
                        {question.category}
                      </span>
                      {question.response_score && (
                        <span className={`text-sm font-medium ${getScoreColor(question.response_score)}`}>
                          {formatPercentage(question.response_score)}
                        </span>
                      )}
                    </div>
                    <h4 className="text-lg font-medium text-gray-900 mb-3">
                      {question.question_text}
                    </h4>
                    {question.candidate_response && (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <h5 className="font-medium text-gray-900 mb-2">Your Response:</h5>
                        <p className="text-gray-700">{question.candidate_response}</p>
                      </div>
                    )}
                    {question.skill_focus.length > 0 && (
                      <div className="mt-3">
                        <div className="flex flex-wrap gap-2">
                          {question.skill_focus.map((skill, skillIndex) => (
                            <span
                              key={skillIndex}
                              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </motion.div>
        )}

        {/* Recommendations Tab */}
        {activeTab === 'recommendations' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Recommendations</h3>
              {analysis.recommendations && (
                <div className="prose max-w-none">
                  <p className="text-gray-700">{analysis.recommendations}</p>
                </div>
              )}
            </div>

            {analysis.red_flags.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-red-900 mb-4">Areas of Concern</h3>
                <ul className="space-y-2">
                  {analysis.red_flags.map((flag, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <XCircleIcon className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                      <span className="text-red-800">{flag}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-4">Analysis Confidence</h3>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <div className="w-full h-4 bg-blue-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-600 rounded-full transition-all duration-500"
                      style={{ width: `${analysis.analysis_confidence * 100}%` }}
                    />
                  </div>
                </div>
                <span className="text-blue-900 font-semibold">
                  {formatPercentage(analysis.analysis_confidence)}
                </span>
              </div>
              <p className="text-blue-800 text-sm mt-2">
                This score reflects the AI's confidence in the analysis based on data quality and response completeness.
              </p>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};