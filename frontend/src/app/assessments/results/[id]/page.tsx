'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { motion } from 'framer-motion'
import {
  CheckCircleIcon,
  XCircleIcon,
  TrophyIcon,
  ClockIcon,
  ChartBarIcon,
  ArrowLeftIcon,
  ShareIcon,
  DocumentArrowDownIcon
} from '@heroicons/react/24/outline'

interface AssessmentResult {
  id: string
  title: string
  score: number
  totalQuestions: number
  correctAnswers: number
  timeSpent: number
  completedAt: Date
  category: string
  difficulty: string
  questions: {
    question: string
    userAnswer: string
    correctAnswer: string
    isCorrect: boolean
    explanation: string
  }[]
}

export default function AssessmentResultsPage() {
  const router = useRouter()
  const params = useParams()
  const { isAuthenticated, isLoading } = useAuth()
  const [result, setResult] = useState<AssessmentResult | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login')
    } else if (isAuthenticated) {
      loadResults()
    }
  }, [isAuthenticated, isLoading, router])

  const loadResults = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${API_URL}/api/assessments/results/${params.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) throw new Error('Failed to fetch results')
      
      const data = await response.json()
      setResult(data.result)
    } catch (error) {
      console.error('Error loading results:', error)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100'
    if (score >= 70) return 'text-blue-600 bg-blue-100'
    if (score >= 50) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}m ${secs}s`
  }

  if (isLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Results not found</h2>
          <button
            onClick={() => router.push('/assessments')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Assessments
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/assessments')}
            className="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-4"
          >
            <ArrowLeftIcon className="w-5 h-5 mr-2" />
            Back to Assessments
          </button>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{result.title}</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Completed on {result.completedAt.toLocaleDateString()} at {result.completedAt.toLocaleTimeString()}
          </p>
        </div>

        {/* Score Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8"
        >
          <div className="text-center mb-8">
            <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full ${getScoreColor(result.score)} mb-4`}>
              <span className="text-5xl font-bold">{result.score}%</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {result.score >= 90 ? 'Excellent!' : result.score >= 70 ? 'Great Job!' : result.score >= 50 ? 'Good Effort!' : 'Keep Practicing!'}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              You scored {result.correctAnswers} out of {result.totalQuestions} questions correctly
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <TrophyIcon className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{result.score}%</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Score</div>
            </div>
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <CheckCircleIcon className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{result.correctAnswers}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Correct</div>
            </div>
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <XCircleIcon className="w-8 h-8 text-red-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{result.totalQuestions - result.correctAnswers}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Incorrect</div>
            </div>
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <ClockIcon className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{formatTime(result.timeSpent)}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Time Spent</div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4 mt-8">
            <button
              onClick={() => router.push('/assessments')}
              className="flex-1 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
            >
              Take Another Assessment
            </button>
            <button className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600">
              <ShareIcon className="w-5 h-5" />
            </button>
            <button className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600">
              <DocumentArrowDownIcon className="w-5 h-5" />
            </button>
          </div>
        </motion.div>

        {/* Question Review */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
            <ChartBarIcon className="w-6 h-6 mr-2" />
            Question Review
          </h3>
          <div className="space-y-6">
            {result.questions.map((q, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`p-6 rounded-lg border-2 ${
                  q.isCorrect
                    ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
                    : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
                }`}
              >
                <div className="flex items-start gap-4">
                  {q.isCorrect ? (
                    <CheckCircleIcon className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
                  ) : (
                    <XCircleIcon className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
                  )}
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
                      Question {index + 1}: {q.question}
                    </h4>
                    <div className="space-y-2">
                      <div>
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Your Answer: </span>
                        <span className={`text-sm ${q.isCorrect ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'}`}>
                          {q.userAnswer}
                        </span>
                      </div>
                      {!q.isCorrect && (
                        <div>
                          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Correct Answer: </span>
                          <span className="text-sm text-green-700 dark:text-green-400">{q.correctAnswer}</span>
                        </div>
                      )}
                      <div className="mt-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Explanation: </span>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{q.explanation}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Next Steps */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-8 text-white"
        >
          <h3 className="text-2xl font-bold mb-4">What's Next?</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <button
              onClick={() => router.push('/assessments')}
              className="p-4 bg-white/10 backdrop-blur-sm rounded-lg hover:bg-white/20 transition-all text-left"
            >
              <TrophyIcon className="w-8 h-8 mb-2" />
              <h4 className="font-semibold mb-1">Take More Tests</h4>
              <p className="text-sm text-white/80">Improve your skills</p>
            </button>
            <button
              onClick={() => router.push('/jobs')}
              className="p-4 bg-white/10 backdrop-blur-sm rounded-lg hover:bg-white/20 transition-all text-left"
            >
              <ChartBarIcon className="w-8 h-8 mb-2" />
              <h4 className="font-semibold mb-1">Find Jobs</h4>
              <p className="text-sm text-white/80">Match your skills</p>
            </button>
            <button
              onClick={() => router.push('/career-coach')}
              className="p-4 bg-white/10 backdrop-blur-sm rounded-lg hover:bg-white/20 transition-all text-left"
            >
              <CheckCircleIcon className="w-8 h-8 mb-2" />
              <h4 className="font-semibold mb-1">Get Coaching</h4>
              <p className="text-sm text-white/80">AI career guidance</p>
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
