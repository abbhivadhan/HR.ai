'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useState } from 'react'
import { 
  MagnifyingGlassIcon, 
  MapPinIcon, 
  CurrencyDollarIcon,
  ClockIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline'

export default function JobsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [location, setLocation] = useState('')

  const jobs = [
    {
      id: '1',
      title: 'Senior Frontend Developer',
      company: 'TechCorp Inc.',
      location: 'San Francisco, CA',
      salary: '$120k - $150k',
      type: 'Full-time',
      posted: '2 days ago',
      description: 'We are looking for a skilled Frontend Developer to join our team...',
      skills: ['React', 'TypeScript', 'Node.js', 'GraphQL'],
      matchScore: 95
    },
    {
      id: '2',
      title: 'Full Stack Engineer',
      company: 'StartupXYZ',
      location: 'Remote',
      salary: '$100k - $130k',
      type: 'Full-time',
      posted: '1 week ago',
      description: 'Join our fast-growing startup as a Full Stack Engineer...',
      skills: ['Python', 'React', 'PostgreSQL', 'AWS'],
      matchScore: 88
    },
    {
      id: '3',
      title: 'Software Engineer',
      company: 'BigTech Solutions',
      location: 'New York, NY',
      salary: '$110k - $140k',
      type: 'Full-time',
      posted: '3 days ago',
      description: 'Looking for a passionate Software Engineer to build scalable solutions...',
      skills: ['JavaScript', 'AWS', 'Docker', 'Kubernetes'],
      matchScore: 82
    }
  ]

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100'
    if (score >= 80) return 'text-blue-600 bg-blue-100'
    if (score >= 70) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Find Your Dream Job
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Discover opportunities that match your skills and career goals
          </p>
        </motion.div>

        {/* Search Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg p-6 mb-8"
        >
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Job title, keywords, or company"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex-1 relative">
              <MapPinIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors">
              Search Jobs
            </button>
          </div>
        </motion.div>

        {/* Job Listings */}
        <div className="space-y-6">
          {jobs.map((job, index) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
              className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">
                      {job.title}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getMatchScoreColor(job.matchScore)}`}>
                      {job.matchScore}% match
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-gray-600 mb-3">
                    <div className="flex items-center gap-1">
                      <BuildingOfficeIcon className="w-4 h-4" />
                      <span>{job.company}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MapPinIcon className="w-4 h-4" />
                      <span>{job.location}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <CurrencyDollarIcon className="w-4 h-4" />
                      <span>{job.salary}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <ClockIcon className="w-4 h-4" />
                      <span>{job.posted}</span>
                    </div>
                  </div>
                  <p className="text-gray-700 mb-4">{job.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {job.skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                <span className="text-sm text-gray-500">{job.type}</span>
                <div className="flex gap-3">
                  <button className="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors">
                    Save Job
                  </button>
                  <Link
                    href={`/jobs/${job.id}/apply`}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Apply Now
                  </Link>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Load More */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="text-center mt-12"
        >
          <button className="px-8 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
            Load More Jobs
          </button>
        </motion.div>
      </div>
    </div>
  )
}