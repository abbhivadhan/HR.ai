'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useState } from 'react'
import { 
  MagnifyingGlassIcon, 
  MapPinIcon, 
  CurrencyDollarIcon,
  ClockIcon,
  BuildingOfficeIcon,
  FunnelIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline'

export default function JobSearchPage() {
  const [filters, setFilters] = useState({
    search: '',
    location: '',
    jobType: '',
    experience: '',
    salary: '',
    remote: false,
    company: ''
  })

  const [showFilters, setShowFilters] = useState(false)

  const jobs = [
    {
      id: '1',
      title: 'Senior Frontend Developer',
      company: 'TechCorp Inc.',
      location: 'San Francisco, CA',
      salary: '$120k - $150k',
      type: 'Full-time',
      remote: true,
      posted: '2 days ago',
      description: 'We are looking for a skilled Frontend Developer to join our team...',
      skills: ['React', 'TypeScript', 'Node.js', 'GraphQL'],
      matchScore: 95,
      logo: 'TC'
    },
    {
      id: '2',
      title: 'Full Stack Engineer',
      company: 'StartupXYZ',
      location: 'Remote',
      salary: '$100k - $130k',
      type: 'Full-time',
      remote: true,
      posted: '1 week ago',
      description: 'Join our fast-growing startup as a Full Stack Engineer...',
      skills: ['Python', 'React', 'PostgreSQL', 'AWS'],
      matchScore: 88,
      logo: 'SX'
    },
    {
      id: '3',
      title: 'Software Engineer',
      company: 'BigTech Solutions',
      location: 'New York, NY',
      salary: '$110k - $140k',
      type: 'Full-time',
      remote: false,
      posted: '3 days ago',
      description: 'Looking for a passionate Software Engineer to build scalable solutions...',
      skills: ['JavaScript', 'AWS', 'Docker', 'Kubernetes'],
      matchScore: 82,
      logo: 'BT'
    },
    {
      id: '4',
      title: 'DevOps Engineer',
      company: 'CloudFirst',
      location: 'Austin, TX',
      salary: '$130k - $160k',
      type: 'Full-time',
      remote: true,
      posted: '5 days ago',
      description: 'Help us build and maintain our cloud infrastructure...',
      skills: ['AWS', 'Kubernetes', 'Terraform', 'Python'],
      matchScore: 78,
      logo: 'CF'
    },
    {
      id: '5',
      title: 'Product Manager',
      company: 'InnovateCorp',
      location: 'Seattle, WA',
      salary: '$140k - $170k',
      type: 'Full-time',
      remote: true,
      posted: '1 day ago',
      description: 'Lead product strategy and development for our flagship product...',
      skills: ['Product Strategy', 'Analytics', 'Agile', 'Leadership'],
      matchScore: 85,
      logo: 'IC'
    },
    {
      id: '6',
      title: 'UX Designer',
      company: 'DesignStudio',
      location: 'Los Angeles, CA',
      salary: '$90k - $120k',
      type: 'Full-time',
      remote: true,
      posted: '4 days ago',
      description: 'Create beautiful and intuitive user experiences...',
      skills: ['Figma', 'User Research', 'Prototyping', 'Design Systems'],
      matchScore: 72,
      logo: 'DS'
    }
  ]

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100'
    if (score >= 80) return 'text-blue-600 bg-blue-100'
    if (score >= 70) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const handleFilterChange = (key: string, value: string | boolean) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Find Your Perfect Job
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
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Job title, keywords, or company"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex-1 relative">
              <MapPinIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Location"
                value={filters.location}
                onChange={(e) => handleFilterChange('location', e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
              >
                <FunnelIcon className="w-5 h-5" />
                Filters
              </button>
              <button className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors">
                Search
              </button>
            </div>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-6 pt-6 border-t border-gray-200"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Type
                  </label>
                  <select
                    value={filters.jobType}
                    onChange={(e) => handleFilterChange('jobType', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Any</option>
                    <option value="full-time">Full-time</option>
                    <option value="part-time">Part-time</option>
                    <option value="contract">Contract</option>
                    <option value="freelance">Freelance</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Experience Level
                  </label>
                  <select
                    value={filters.experience}
                    onChange={(e) => handleFilterChange('experience', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Any</option>
                    <option value="entry">Entry Level</option>
                    <option value="mid">Mid Level</option>
                    <option value="senior">Senior Level</option>
                    <option value="lead">Lead/Principal</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Salary Range
                  </label>
                  <select
                    value={filters.salary}
                    onChange={(e) => handleFilterChange('salary', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Any</option>
                    <option value="0-50k">$0 - $50k</option>
                    <option value="50k-100k">$50k - $100k</option>
                    <option value="100k-150k">$100k - $150k</option>
                    <option value="150k+">$150k+</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Remote Work
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.remote}
                      onChange={(e) => handleFilterChange('remote', e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Remote OK</span>
                  </label>
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>

        {/* Results Header */}
        <div className="flex justify-between items-center mb-6">
          <p className="text-gray-600">
            Showing {jobs.length} jobs • Sorted by relevance
          </p>
          <div className="flex items-center gap-2">
            <AdjustmentsHorizontalIcon className="w-5 h-5 text-gray-400" />
            <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option>Most Relevant</option>
              <option>Most Recent</option>
              <option>Highest Salary</option>
              <option>Best Match</option>
            </select>
          </div>
        </div>

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
                <div className="flex items-start gap-4 flex-1">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                    {job.logo}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {job.title}
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getMatchScoreColor(job.matchScore)}`}>
                        {job.matchScore}% match
                      </span>
                      {job.remote && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                          Remote
                        </span>
                      )}
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
              </div>
              <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                <span className="text-sm text-gray-500">{job.type}</span>
                <div className="flex gap-3">
                  <button className="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors">
                    Save Job
                  </button>
                  <Link
                    href={`/jobs/${job.id}`}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    View Details
                  </Link>
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
          transition={{ delay: 0.8 }}
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