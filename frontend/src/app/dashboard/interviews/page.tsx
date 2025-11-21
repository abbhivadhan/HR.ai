'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  CalendarIcon,
  VideoCameraIcon,
  ClockIcon,
  UserIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlusIcon
} from '@heroicons/react/24/outline'
import { useRouter } from 'next/navigation'

interface Interview {
  id: string
  candidateName: string
  jobTitle: string
  scheduledDate: Date
  duration: number
  status: 'scheduled' | 'completed' | 'cancelled' | 'in-progress'
  type: 'video' | 'phone' | 'in-person'
  meetingLink?: string
  notes?: string
}

export default function InterviewsPage() {
  const router = useRouter()
  const [interviews, setInterviews] = useState<Interview[]>([])
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'completed'>('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadInterviews()
  }, [])

  const loadInterviews = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${API_URL}/api/dashboard/interviews`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) throw new Error('Failed to fetch interviews')
      
      const data = await response.json()
      setInterviews(data.interviews || [])
    } catch (error) {
      console.error('Error loading interviews:', error)
      setInterviews([])
    } finally {
      setLoading(false)
    }
  }

  const startAIInterview = () => {
    // Generate a random interview ID for demo
    const interviewId = `demo-${Date.now()}`
    router.push(`/interviews/ai-video/${interviewId}`)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'
      case 'completed': return 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300'
      case 'cancelled': return 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300'
      case 'in-progress': return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'video': return <VideoCameraIcon className="w-5 h-5" />
      case 'phone': return <ClockIcon className="w-5 h-5" />
      case 'in-person': return <UserIcon className="w-5 h-5" />
      default: return <VideoCameraIcon className="w-5 h-5" />
    }
  }

  const filteredInterviews = interviews.filter(interview => {
    if (filter === 'upcoming') return interview.status === 'scheduled'
    if (filter === 'completed') return interview.status === 'completed'
    return true
  })

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Interviews</h1>
            <p className="text-gray-600 dark:text-gray-300 mt-1">Manage your interview schedule</p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={startAIInterview}
              className="flex items-center space-x-2 px-5 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl"
            >
              <VideoCameraIcon className="w-5 h-5" />
              <span>Try AI Interview</span>
            </button>
            <button
              onClick={() => router.push('/interviews/schedule')}
              className="flex items-center space-x-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <PlusIcon className="w-5 h-5" />
              <span>Schedule Interview</span>
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-3 mb-6">
          {['all', 'upcoming', 'completed'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f as any)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>

        {/* Interviews List */}
        <div className="space-y-4">
          {filteredInterviews.map((interview, index) => (
            <motion.div
              key={interview.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 flex-1">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                    {interview.candidateName.split(' ').map(n => n[0]).join('')}
                  </div>
                  
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {interview.candidateName}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300">{interview.jobTitle}</p>
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
                      <span className="flex items-center gap-1">
                        <CalendarIcon className="w-4 h-4" />
                        {interview.scheduledDate.toLocaleDateString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <ClockIcon className="w-4 h-4" />
                        {interview.scheduledDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      <span className="flex items-center gap-1">
                        {getTypeIcon(interview.type)}
                        {interview.duration} min
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(interview.status)}`}>
                    {interview.status}
                  </span>

                  <div className="flex gap-2">
                    {interview.status === 'scheduled' && interview.meetingLink && (
                      <button
                        onClick={() => window.open(interview.meetingLink, '_blank')}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                      >
                        Join Meeting
                      </button>
                    )}
                    <button
                      onClick={() => router.push(`/interviews/${interview.id}`)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {filteredInterviews.length === 0 && (
          <div className="text-center py-12">
            <CalendarIcon className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No interviews found</h3>
            <p className="text-gray-600 dark:text-gray-400">Schedule your first interview to get started</p>
          </div>
        )}
      </div>
    </div>
  )
}
