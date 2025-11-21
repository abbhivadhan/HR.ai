'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Select from 'react-select'
import { 
  JobPosting, 
  JobSearchFilters, 
  JobType, 
  RemoteType,
  JobSearchResponse 
} from '@/types/job'
import { jobService } from '@/services/jobService'
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  BriefcaseIcon,
  CurrencyDollarIcon,
  AdjustmentsHorizontalIcon,
  XMarkIcon,
  HeartIcon,
  ClockIcon,
  BuildingOfficeIcon,
} from '@heroicons/react/24/outline'
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid'

interface JobSearchProps {
  onJobSelect?: (job: JobPosting) => void
  initialFilters?: Partial<JobSearchFilters>
  showSaveButton?: boolean
}

const jobTypeOptions = [
  { value: JobType.FULL_TIME, label: 'Full Time' },
  { value: JobType.PART_TIME, label: 'Part Time' },
  { value: JobType.CONTRACT, label: 'Contract' },
  { value: JobType.TEMPORARY, label: 'Temporary' },
  { value: JobType.INTERNSHIP, label: 'Internship' },
  { value: JobType.FREELANCE, label: 'Freelance' },
]

const remoteTypeOptions = [
  { value: RemoteType.ONSITE, label: 'On-site' },
  { value: RemoteType.REMOTE, label: 'Remote' },
  { value: RemoteType.HYBRID, label: 'Hybrid' },
]

const experienceLevelOptions = [
  { value: 'entry', label: 'Entry Level' },
  { value: 'junior', label: 'Junior' },
  { value: 'mid', label: 'Mid Level' },
  { value: 'senior', label: 'Senior' },
  { value: 'lead', label: 'Lead' },
  { value: 'executive', label: 'Executive' },
]

const sortOptions = [
  { value: 'relevance', label: 'Most Relevant' },
  { value: 'date', label: 'Most Recent' },
  { value: 'salary', label: 'Highest Salary' },
  { value: 'company', label: 'Company A-Z' },
]

export default function JobSearch({ 
  onJobSelect, 
  initialFilters = {},
  showSaveButton = true 
}: JobSearchProps) {
  const [filters, setFilters] = useState<JobSearchFilters>({
    query: '',
    location: '',
    remote_type: [],
    job_type: [],
    experience_level: [],
    salary_min: undefined,
    salary_max: undefined,
    skills: [],
    posted_within: undefined,
    sort_by: 'relevance',
    sort_order: 'desc',
    ...initialFilters
  })
  
  const [searchResults, setSearchResults] = useState<JobSearchResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set())
  const [currentPage, setCurrentPage] = useState(1)

  const searchJobs = useCallback(async (page = 1) => {
    setIsLoading(true)
    try {
      const results = await jobService.searchJobs(filters, page, 20)
      setSearchResults(results)
      setCurrentPage(page)
    } catch (error) {
      console.error('Error searching jobs:', error)
    } finally {
      setIsLoading(false)
    }
  }, [filters])

  useEffect(() => {
    searchJobs(1)
  }, [searchJobs])

  const handleFilterChange = (key: keyof JobSearchFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const clearFilters = () => {
    setFilters({
      query: '',
      location: '',
      remote_type: [],
      job_type: [],
      experience_level: [],
      salary_min: undefined,
      salary_max: undefined,
      skills: [],
      posted_within: undefined,
      sort_by: 'relevance',
      sort_order: 'desc',
    })
  }

  const toggleSaveJob = async (jobId: string) => {
    try {
      if (savedJobs.has(jobId)) {
        await jobService.unsaveJob(jobId)
        setSavedJobs(prev => {
          const newSet = new Set(prev)
          newSet.delete(jobId)
          return newSet
        })
      } else {
        await jobService.saveJob(jobId)
        setSavedJobs(prev => new Set(prev).add(jobId))
      }
    } catch (error) {
      console.error('Error toggling saved job:', error)
    }
  }

  const formatSalary = (min?: number, max?: number, currency = 'USD') => {
    if (!min && !max) return 'Salary not specified'
    if (min && max) return `${currency} ${min.toLocaleString()} - ${max.toLocaleString()}`
    if (min) return `${currency} ${min.toLocaleString()}+`
    if (max) return `Up to ${currency} ${max.toLocaleString()}`
  }

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 24) return `${diffInHours}h ago`
    const diffInDays = Math.floor(diffInHours / 24)
    if (diffInDays < 7) return `${diffInDays}d ago`
    const diffInWeeks = Math.floor(diffInDays / 7)
    return `${diffInWeeks}w ago`
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Search Header */}
      <div className="card mb-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Main Search */}
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search jobs, companies, or keywords..."
              value={filters.query || ''}
              onChange={(e) => handleFilterChange('query', e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          
          {/* Location Search */}
          <div className="lg:w-64 relative">
            <MapPinIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Location"
              value={filters.location || ''}
              onChange={(e) => handleFilterChange('location', e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          
          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <AdjustmentsHorizontalIcon className="h-5 w-5 mr-2" />
            Filters
          </button>
          
          {/* Search Button */}
          <motion.button
            onClick={() => searchJobs(1)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="btn-primary px-8"
          >
            Search
          </motion.button>
        </div>
        
        {/* Advanced Filters */}
        <AnimatePresence>
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
                  <Select
                    isMulti
                    options={jobTypeOptions}
                    value={jobTypeOptions.filter(option => 
                      filters.job_type?.includes(option.value)
                    )}
                    onChange={(selected) => 
                      handleFilterChange('job_type', selected.map(s => s.value))
                    }
                    className="react-select-container"
                    classNamePrefix="react-select"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Remote Type
                  </label>
                  <Select
                    isMulti
                    options={remoteTypeOptions}
                    value={remoteTypeOptions.filter(option => 
                      filters.remote_type?.includes(option.value)
                    )}
                    onChange={(selected) => 
                      handleFilterChange('remote_type', selected.map(s => s.value))
                    }
                    className="react-select-container"
                    classNamePrefix="react-select"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Experience Level
                  </label>
                  <Select
                    isMulti
                    options={experienceLevelOptions}
                    value={experienceLevelOptions.filter(option => 
                      filters.experience_level?.includes(option.value)
                    )}
                    onChange={(selected) => 
                      handleFilterChange('experience_level', selected.map(s => s.value))
                    }
                    className="react-select-container"
                    classNamePrefix="react-select"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sort By
                  </label>
                  <Select
                    options={sortOptions}
                    value={sortOptions.find(option => option.value === filters.sort_by)}
                    onChange={(selected) => 
                      handleFilterChange('sort_by', selected?.value)
                    }
                    className="react-select-container"
                    classNamePrefix="react-select"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Min Salary
                  </label>
                  <input
                    type="number"
                    placeholder="50000"
                    value={filters.salary_min || ''}
                    onChange={(e) => 
                      handleFilterChange('salary_min', e.target.value ? Number(e.target.value) : undefined)
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Salary
                  </label>
                  <input
                    type="number"
                    placeholder="100000"
                    value={filters.salary_max || ''}
                    onChange={(e) => 
                      handleFilterChange('salary_max', e.target.value ? Number(e.target.value) : undefined)
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Posted Within
                  </label>
                  <select
                    value={filters.posted_within || ''}
                    onChange={(e) => 
                      handleFilterChange('posted_within', e.target.value ? Number(e.target.value) : undefined)
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Any time</option>
                    <option value="1">Last 24 hours</option>
                    <option value="7">Last week</option>
                    <option value="30">Last month</option>
                  </select>
                </div>
                
                <div className="flex items-end">
                  <button
                    onClick={clearFilters}
                    className="w-full px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Clear Filters
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Results */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Job List */}
        <div className="lg:col-span-2">
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="card animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="space-y-2">
                    <div className="h-3 bg-gray-200 rounded"></div>
                    <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : searchResults?.jobs.length ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <p className="text-gray-600">
                  {searchResults.total} jobs found
                </p>
              </div>
              
              {searchResults.jobs.map((job) => (
                <motion.div
                  key={job.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="card hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => onJobSelect?.(job)}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {job.title}
                      </h3>
                      <div className="flex items-center text-gray-600 mb-2">
                        <BuildingOfficeIcon className="h-4 w-4 mr-1" />
                        <span className="text-sm">{job.company?.company_name}</span>
                        {job.location && (
                          <>
                            <span className="mx-2">•</span>
                            <MapPinIcon className="h-4 w-4 mr-1" />
                            <span className="text-sm">{job.location}</span>
                          </>
                        )}
                      </div>
                    </div>
                    
                    {showSaveButton && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          toggleSaveJob(job.id)
                        }}
                        className="p-2 hover:bg-gray-100 rounded-full"
                      >
                        {savedJobs.has(job.id) ? (
                          <HeartSolidIcon className="h-5 w-5 text-red-500" />
                        ) : (
                          <HeartIcon className="h-5 w-5 text-gray-400" />
                        )}
                      </button>
                    )}
                  </div>
                  
                  <p className="text-gray-700 mb-3 line-clamp-2">
                    {job.summary || job.description.replace(/<[^>]*>/g, '').substring(0, 150) + '...'}
                  </p>
                  
                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full">
                      {job.job_type.replace('_', ' ')}
                    </span>
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                      {job.remote_type}
                    </span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                      {job.experience_level}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center text-sm text-gray-600">
                    <div className="flex items-center">
                      <CurrencyDollarIcon className="h-4 w-4 mr-1" />
                      <span>{formatSalary(job.salary_min, job.salary_max, job.salary_currency)}</span>
                    </div>
                    <div className="flex items-center">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      <span>{getTimeAgo(job.posted_at || job.created_at)}</span>
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {/* Pagination */}
              {searchResults.total_pages > 1 && (
                <div className="flex justify-center mt-8">
                  <div className="flex space-x-2">
                    {currentPage > 1 && (
                      <button
                        onClick={() => searchJobs(currentPage - 1)}
                        className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                      >
                        Previous
                      </button>
                    )}
                    
                    {[...Array(Math.min(5, searchResults.total_pages))].map((_, i) => {
                      const page = i + 1
                      return (
                        <button
                          key={page}
                          onClick={() => searchJobs(page)}
                          className={`px-3 py-2 border rounded-lg ${
                            currentPage === page
                              ? 'bg-primary-600 text-white border-primary-600'
                              : 'border-gray-300 hover:bg-gray-50'
                          }`}
                        >
                          {page}
                        </button>
                      )
                    })}
                    
                    {currentPage < searchResults.total_pages && (
                      <button
                        onClick={() => searchJobs(currentPage + 1)}
                        className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                      >
                        Next
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="card text-center py-12">
              <BriefcaseIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
              <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
            </div>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Filters */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Filters</h3>
            <div className="space-y-3">
              <button
                onClick={() => handleFilterChange('posted_within', 1)}
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50"
              >
                Posted today
              </button>
              <button
                onClick={() => handleFilterChange('remote_type', [RemoteType.REMOTE])}
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50"
              >
                Remote only
              </button>
              <button
                onClick={() => handleFilterChange('job_type', [JobType.FULL_TIME])}
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50"
              >
                Full-time only
              </button>
            </div>
          </div>
          
          {/* Search Tips */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Search Tips</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Use specific keywords for better results</li>
              <li>• Try different job titles or synonyms</li>
              <li>• Filter by location for local opportunities</li>
              <li>• Set salary range to match your expectations</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}