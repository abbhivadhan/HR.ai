'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { motion } from 'framer-motion'
import {
  BriefcaseIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  ClockIcon,
  StarIcon,
  BookmarkIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline'
import { StarIcon as StarIconSolid, BookmarkIcon as BookmarkIconSolid } from '@heroicons/react/24/solid'

interface JobRecommendation {
  id: string
  title: string
  company: string
  location: string
  salary: string
  matchScore: number
  postedDate: Date
  type: string
  skills: string[]
  description: string
  saved: boolean
}

export default function JobRecommendationsPage() {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuth()
  const [jobs, setJobs] = useState<JobRecommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'high' | 'medium'>('all')

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login')
    } else if (isAuthenticated) {
      loadRecommendations()
    }
  }, [isAuthenticated, isLoading, router])

  const loadRecommendations = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${API_URL}/api/jobs/recommendations`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) throw new Error('Failed to fetch recommendations')
      
      const data = await response.json()
      setJobs(data.jobs || [])
    } catch (error) {
      console.error('Error loading recommendations:', error)
      setJobs([])
    } finally {
      setLoading(false)
    }
  }

  const toggleSave = (jobId: string) => {
    setJobs(prev => prev.map(job => 
      job.id === jobId ? { ...job, saved: !job.saved } : job
    ))
  }

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100'
    if (score >= 80) return 'text-blue-600 bg-blue-100'
    if (score >= 70) return 'text-yellow-600 bg-yellow-100'
    return 'text-gray-600 bg-gray-100'
  }

  const filteredJobs = jobs.filter(job => {
    if (filter === 'high') return job.matchScore >= 90
    if (filter === 'medium') return job.matchScore >= 80 && job.matchScore < 90
    return true
  })

  if (isLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Job Recommendations</h1>
          <p className="text-gray-600 dark:text-gray-400">
            We found {jobs.length} jobs that match your profile
          </p>
        </div>

        {/* Filters */}
        <div className="mb-8 flex gap-4">
          <button
            onClick={() => setFilter('all')}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            All Matches
          </button>
          <button
            onClick={() => setFilter('high')}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              filter === 'high'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            High Match (90%+)
          </button>
          <button
            onClick={() => setFilter('medium')}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              filter === 'medium'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            Good Match (80-89%)
          </button>
        </div>

        {/* Job List */}
        <div className="space-y-6">
          {filteredJobs.map((job, index) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">{job.title}</h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getMatchScoreColor(job.matchScore)}`}>
                      {job.matchScore}% match
                    </span>
                  </div>
                  <p className="text-lg text-gray-700 dark:text-gray-300 mb-3">{job.company}</p>
                  
                  <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400 mb-4">
                    <div className="flex items-center gap-1">
                      <MapPinIcon className="w-4 h-4" />
                      {job.location}
                    </div>
                    <div className="flex items-center gap-1">
                      <CurrencyDollarIcon className="w-4 h-4" />
                      {job.salary}
                    </div>
                    <div className="flex items-center gap-1">
                      <BriefcaseIcon className="w-4 h-4" />
                      {job.type}
                    </div>
                    <div className="flex items-center gap-1">
                      <ClockIcon className="w-4 h-4" />
                      Posted {Math.floor((Date.now() - job.postedDate.getTime()) / (1000 * 60 * 60 * 24))} days ago
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {job.skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>

                  <p className="text-gray-600 dark:text-gray-400">{job.description}</p>
                </div>

                <button
                  onClick={() => toggleSave(job.id)}
                  className="ml-4 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  {job.saved ? (
                    <BookmarkIconSolid className="w-6 h-6 text-blue-600" />
                  ) : (
                    <BookmarkIcon className="w-6 h-6 text-gray-400" />
                  )}
                </button>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => router.push(`/jobs/${job.id}`)}
                  className="flex-1 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold flex items-center justify-center gap-2"
                >
                  View Details
                  <ArrowRightIcon className="w-5 h-5" />
                </button>
                <button
                  onClick={() => router.push(`/jobs/${job.id}/apply`)}
                  className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold"
                >
                  Apply Now
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        {filteredJobs.length === 0 && (
          <div className="text-center py-12">
            <BriefcaseIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No jobs found</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">Try adjusting your filters</p>
            <button
              onClick={() => setFilter('all')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Show All Jobs
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
