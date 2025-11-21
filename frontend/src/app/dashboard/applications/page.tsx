'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  FunnelIcon,
  MagnifyingGlassIcon,
  UserGroupIcon,
  CheckCircleIcon,
  XMarkIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

export default function ApplicationsPage() {
  const [filter, setFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  const applications = [
    {
      id: '1',
      candidateName: 'Sarah Johnson',
      jobTitle: 'Senior Frontend Developer',
      status: 'shortlisted',
      matchScore: 92,
      appliedDate: '2024-01-20',
      email: 'sarah.j@email.com',
      experience: '7 years'
    },
    {
      id: '2',
      candidateName: 'Michael Chen',
      jobTitle: 'Backend Engineer',
      status: 'reviewing',
      matchScore: 88,
      appliedDate: '2024-01-19',
      email: 'michael.c@email.com',
      experience: '5 years'
    },
    {
      id: '3',
      candidateName: 'Emily Rodriguez',
      jobTitle: 'Senior Frontend Developer',
      status: 'interviewed',
      matchScore: 95,
      appliedDate: '2024-01-18',
      email: 'emily.r@email.com',
      experience: '8 years'
    },
    {
      id: '4',
      candidateName: 'David Kim',
      jobTitle: 'DevOps Engineer',
      status: 'pending',
      matchScore: 85,
      appliedDate: '2024-01-17',
      email: 'david.k@email.com',
      experience: '6 years'
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'shortlisted': return 'bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300'
      case 'interviewed': return 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/20 dark:text-indigo-300'
      case 'reviewing': return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300'
      case 'pending': return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 dark:text-green-400'
    if (score >= 80) return 'text-blue-600 dark:text-blue-400'
    if (score >= 70) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Applications</h1>
          <p className="text-gray-600 dark:text-gray-300">Review and manage candidate applications</p>
        </div>

        {/* Filters & Search */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search candidates..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              {['all', 'pending', 'reviewing', 'shortlisted', 'interviewed'].map((status) => (
                <button
                  key={status}
                  onClick={() => setFilter(status)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    filter === status
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Applications List */}
        <div className="space-y-4">
          {applications.map((application, index) => (
            <motion.div
              key={application.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 flex-1">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                    {application.candidateName.split(' ').map(n => n[0]).join('')}
                  </div>
                  
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {application.candidateName}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300">{application.jobTitle}</p>
                    <div className="flex items-center gap-4 mt-1 text-sm text-gray-500 dark:text-gray-400">
                      <span>{application.email}</span>
                      <span>•</span>
                      <span>{application.experience}</span>
                      <span>•</span>
                      <span>Applied {application.appliedDate}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className={`text-2xl font-bold ${getMatchScoreColor(application.matchScore)}`}>
                      {application.matchScore}%
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">Match Score</div>
                  </div>

                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(application.status)}`}>
                    {application.status}
                  </span>

                  <div className="flex gap-2">
                    <button className="p-2 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors">
                      <CheckCircleIcon className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors">
                      <XMarkIcon className="w-5 h-5" />
                    </button>
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      Review
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
