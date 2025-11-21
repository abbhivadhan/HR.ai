'use client'

import { motion } from 'framer-motion'
import {
  CheckCircleIcon,
  ChartBarIcon,
  ClockIcon,
  ChatBubbleLeftRightIcon,
  SparklesIcon,
  ArrowDownTrayIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

interface InterviewAnalysisProps {
  responses: any[]
  onClose: () => void
}

export default function InterviewAnalysis({
  responses,
  onClose
}: InterviewAnalysisProps) {
  // Calculate overall metrics
  const totalWords = responses.reduce((sum, r) => sum + (r.analysis?.wordCount || 0), 0)
  const avgWordsPerMinute = Math.round(
    responses.reduce((sum, r) => sum + (r.analysis?.wordsPerMinute || 0), 0) / responses.length
  )
  const totalDuration = responses.reduce((sum, r) => sum + (r.analysis?.duration || 0), 0)
  const overallScore = 85 // Placeholder - will be calculated by backend AI

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    return 'Needs Improvement'
  }

  return (
    <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 max-w-4xl w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
            <CheckCircleIcon className="w-10 h-10 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-white">Interview Complete!</h2>
            <p className="text-white/70">Here's your performance analysis</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-3 bg-white/10 hover:bg-white/20 rounded-full transition-colors"
        >
          <XMarkIcon className="w-6 h-6 text-white" />
        </button>
      </div>

      {/* Overall Score */}
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-2xl p-8 mb-6 text-center"
      >
        <div className="flex items-center justify-center mb-4">
          <SparklesIcon className="w-8 h-8 text-yellow-400" />
        </div>
        <div className={`text-6xl font-bold mb-2 ${getScoreColor(overallScore)}`}>
          {overallScore}%
        </div>
        <div className="text-2xl text-white font-semibold mb-2">
          {getScoreLabel(overallScore)}
        </div>
        <p className="text-white/70">
          You performed well across all questions. Keep up the great work!
        </p>
      </motion.div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6">
          <div className="flex items-center space-x-3 mb-3">
            <ChatBubbleLeftRightIcon className="w-6 h-6 text-blue-400" />
            <h3 className="text-white font-semibold">Total Words</h3>
          </div>
          <div className="text-3xl font-bold text-white">{totalWords}</div>
          <p className="text-white/70 text-sm mt-1">words spoken</p>
        </div>

        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6">
          <div className="flex items-center space-x-3 mb-3">
            <ChartBarIcon className="w-6 h-6 text-purple-400" />
            <h3 className="text-white font-semibold">Speaking Rate</h3>
          </div>
          <div className="text-3xl font-bold text-white">{avgWordsPerMinute}</div>
          <p className="text-white/70 text-sm mt-1">words per minute</p>
        </div>

        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6">
          <div className="flex items-center space-x-3 mb-3">
            <ClockIcon className="w-6 h-6 text-pink-400" />
            <h3 className="text-white font-semibold">Duration</h3>
          </div>
          <div className="text-3xl font-bold text-white">
            {Math.floor(totalDuration / 60)}m {totalDuration % 60}s
          </div>
          <p className="text-white/70 text-sm mt-1">total time</p>
        </div>
      </div>

      {/* Question-by-Question Analysis */}
      <div className="mb-6">
        <h3 className="text-xl font-bold text-white mb-4">Question Analysis</h3>
        <div className="space-y-4">
          {responses.map((response, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/5 backdrop-blur-sm rounded-xl p-6"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-white/70 text-sm">Question {index + 1}</span>
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full">
                      {response.analysis?.wordCount || 0} words
                    </span>
                  </div>
                  <p className="text-white/90 text-sm leading-relaxed">
                    {response.question}
                  </p>
                </div>
                <div className="text-right ml-4">
                  <div className={`text-2xl font-bold ${getScoreColor(82)}`}>
                    82%
                  </div>
                  <div className="text-white/70 text-xs">score</div>
                </div>
              </div>

              {/* Response Preview */}
              <div className="bg-black/20 rounded-lg p-4 mt-3">
                <p className="text-white/70 text-sm line-clamp-3">
                  {response.answer || 'No response recorded'}
                </p>
              </div>

              {/* Metrics */}
              <div className="flex items-center space-x-6 mt-3 text-sm">
                <div className="flex items-center space-x-2">
                  <ClockIcon className="w-4 h-4 text-white/50" />
                  <span className="text-white/70">
                    {response.analysis?.duration || 0}s
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <ChartBarIcon className="w-4 h-4 text-white/50" />
                  <span className="text-white/70">
                    {response.analysis?.wordsPerMinute || 0} wpm
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Strengths & Areas for Improvement */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-green-500/10 backdrop-blur-sm rounded-xl p-6">
          <h3 className="text-lg font-bold text-green-400 mb-4">Strengths</h3>
          <ul className="space-y-2">
            <li className="flex items-start space-x-2">
              <CheckCircleIcon className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span className="text-white/90 text-sm">
                Clear and articulate communication
              </span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircleIcon className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span className="text-white/90 text-sm">
                Good pacing and speaking rate
              </span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircleIcon className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span className="text-white/90 text-sm">
                Comprehensive answers with examples
              </span>
            </li>
          </ul>
        </div>

        <div className="bg-yellow-500/10 backdrop-blur-sm rounded-xl p-6">
          <h3 className="text-lg font-bold text-yellow-400 mb-4">Areas to Improve</h3>
          <ul className="space-y-2">
            <li className="flex items-start space-x-2">
              <SparklesIcon className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
              <span className="text-white/90 text-sm">
                Add more specific technical details
              </span>
            </li>
            <li className="flex items-start space-x-2">
              <SparklesIcon className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
              <span className="text-white/90 text-sm">
                Structure answers with clear frameworks
              </span>
            </li>
            <li className="flex items-start space-x-2">
              <SparklesIcon className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
              <span className="text-white/90 text-sm">
                Practice concise conclusions
              </span>
            </li>
          </ul>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center space-x-4">
        <button
          onClick={onClose}
          className="flex-1 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold rounded-xl hover:shadow-2xl hover:scale-105 transition-all"
        >
          Return to Dashboard
        </button>
        <button
          className="px-6 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl transition-colors flex items-center space-x-2"
        >
          <ArrowDownTrayIcon className="w-5 h-5" />
          <span>Download Report</span>
        </button>
      </div>

      {/* Next Steps */}
      <div className="mt-6 bg-blue-500/10 backdrop-blur-sm rounded-xl p-6">
        <h3 className="text-white font-semibold mb-2">What's Next?</h3>
        <p className="text-white/70 text-sm">
          Your interview results have been saved to your profile. Recruiters can now view your performance. 
          Keep practicing to improve your score!
        </p>
      </div>
    </div>
  )
}
