'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { motion } from 'framer-motion'
import {
  UserIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  BriefcaseIcon,
  AcademicCapIcon,
  StarIcon,
  DocumentTextIcon,
  VideoCameraIcon,
  CalendarIcon,
  ChatBubbleLeftRightIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline'

interface CandidateDetail {
  id: string
  name: string
  email: string
  phone: string
  location: string
  title: string
  experience: string
  education: string
  skills: string[]
  assessmentScores: { skill: string; score: number }[]
  applications: { jobTitle: string; status: string; date: Date }[]
  resumeUrl?: string
  portfolioUrl?: string
}

export default function CandidateDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { isAuthenticated, isLoading, user } = useAuth()
  const [candidate, setCandidate] = useState<CandidateDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login')
    } else if (isAuthenticated) {
      loadCandidate()
    }
  }, [isAuthenticated, isLoading, router])

  const loadCandidate = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${API_URL}/api/candidates/${params.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) throw new Error('Failed to fetch candidate')
      
      const data = await response.json()
      setCandidate(data.candidate)
    } catch (error) {
      console.error('Error loading candidate:', error)
      setCandidate(null)
    } finally {
      setLoading(false)
    }
  }

  if (isLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!candidate) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Candidate not found</h2>
          <button
            onClick={() => router.push('/dashboard/candidates')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Candidates
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/dashboard/candidates')}
            className="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-4"
          >
            <ArrowLeftIcon className="w-5 h-5 mr-2" />
            Back to Candidates
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Profile */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 sticky top-6"
            >
              {/* Profile Picture */}
              <div className="text-center mb-6">
                <div className="w-32 h-32 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <UserIcon className="w-16 h-16 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{candidate.name}</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">{candidate.title}</p>
                
                {/* Contact Info */}
                <div className="space-y-3 text-left">
                  <div className="flex items-center gap-3 text-sm">
                    <EnvelopeIcon className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700 dark:text-gray-300">{candidate.email}</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <PhoneIcon className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700 dark:text-gray-300">{candidate.phone}</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <MapPinIcon className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700 dark:text-gray-300">{candidate.location}</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3">
                <button className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold flex items-center justify-center gap-2">
                  <ChatBubbleLeftRightIcon className="w-5 h-5" />
                  Message Candidate
                </button>
                <button className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold flex items-center justify-center gap-2">
                  <CalendarIcon className="w-5 h-5" />
                  Schedule Interview
                </button>
                {candidate.resumeUrl && (
                  <button className="w-full py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 font-semibold flex items-center justify-center gap-2">
                    <DocumentTextIcon className="w-5 h-5" />
                    View Resume
                  </button>
                )}
                {candidate.portfolioUrl && (
                  <button className="w-full py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 font-semibold flex items-center justify-center gap-2">
                    <VideoCameraIcon className="w-5 h-5" />
                    View Portfolio
                  </button>
                )}
              </div>
            </motion.div>
          </div>

          {/* Right Column - Details */}
          <div className="lg:col-span-2 space-y-8">
            {/* Experience & Education */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6"
            >
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <BriefcaseIcon className="w-6 h-6" />
                Professional Background
              </h3>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Experience</h4>
                  <p className="text-gray-600 dark:text-gray-400">{candidate.experience}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                    <AcademicCapIcon className="w-5 h-5" />
                    Education
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400">{candidate.education}</p>
                </div>
              </div>
            </motion.div>

            {/* Skills */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6"
            >
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Skills</h3>
              <div className="flex flex-wrap gap-2">
                {candidate.skills.map((skill) => (
                  <span
                    key={skill}
                    className="px-4 py-2 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </motion.div>

            {/* Assessment Scores */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6"
            >
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <StarIcon className="w-6 h-6" />
                Assessment Scores
              </h3>
              <div className="space-y-4">
                {candidate.assessmentScores.map((assessment) => (
                  <div key={assessment.skill}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-gray-900 dark:text-white">{assessment.skill}</span>
                      <span className="text-lg font-bold text-blue-600">{assessment.score}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500"
                        style={{ width: `${assessment.score}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Applications */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6"
            >
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Application History</h3>
              <div className="space-y-4">
                {candidate.applications.map((app, index) => (
                  <div
                    key={index}
                    className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold text-gray-900 dark:text-white">{app.jobTitle}</h4>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        app.status === 'Interview Scheduled'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                          : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                      }`}>
                        {app.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Applied on {app.date.toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}
