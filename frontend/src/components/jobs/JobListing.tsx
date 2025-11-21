'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { JobPosting } from '@/types/job'
import { jobService } from '@/services/jobService'
import {
  MapPinIcon,
  CurrencyDollarIcon,
  ClockIcon,
  BuildingOfficeIcon,
  HeartIcon,
  ShareIcon,
  BriefcaseIcon,
  UserGroupIcon,
  CalendarIcon,
  TagIcon,
} from '@heroicons/react/24/outline'
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid'

interface JobListingProps {
  job: JobPosting
  onApply?: (job: JobPosting) => void
  showApplyButton?: boolean
  showSaveButton?: boolean
  compact?: boolean
}

export default function JobListing({
  job,
  onApply,
  showApplyButton = true,
  showSaveButton = true,
  compact = false
}: JobListingProps) {
  const [isSaved, setIsSaved] = useState(false)
  const [isApplying, setIsApplying] = useState(false)

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

  const toggleSaveJob = async () => {
    try {
      if (isSaved) {
        await jobService.unsaveJob(job.id)
        setIsSaved(false)
      } else {
        await jobService.saveJob(job.id)
        setIsSaved(true)
      }
    } catch (error) {
      console.error('Error toggling saved job:', error)
    }
  }

  const handleApply = async () => {
    if (!onApply) return
    
    setIsApplying(true)
    try {
      onApply(job)
    } finally {
      setIsApplying(false)
    }
  }

  const shareJob = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: job.title,
          text: `Check out this job opportunity: ${job.title} at ${job.company?.company_name}`,
          url: window.location.href,
        })
      } catch (error) {
        console.error('Error sharing:', error)
      }
    } else {
      // Fallback to copying URL
      navigator.clipboard.writeText(window.location.href)
    }
  }

  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="card hover:shadow-lg transition-shadow"
      >
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">{job.title}</h3>
            <div className="flex items-center text-gray-600 text-sm mb-2">
              <BuildingOfficeIcon className="h-4 w-4 mr-1" />
              <span>{job.company?.company_name}</span>
              {job.location && (
                <>
                  <span className="mx-2">•</span>
                  <MapPinIcon className="h-4 w-4 mr-1" />
                  <span>{job.location}</span>
                </>
              )}
            </div>
          </div>
          
          {showSaveButton && (
            <button
              onClick={toggleSaveJob}
              className="p-2 hover:bg-gray-100 rounded-full"
              aria-label={isSaved ? "Unsave job" : "Save job"}
            >
              {isSaved ? (
                <HeartSolidIcon className="h-5 w-5 text-red-500" />
              ) : (
                <HeartIcon className="h-5 w-5 text-gray-400" />
              )}
            </button>
          )}
        </div>
        
        <div className="flex flex-wrap gap-2 mb-3">
          <span className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full">
            {job.job_type.replace('_', ' ')}
          </span>
          <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
            {job.remote_type}
          </span>
        </div>
        
        <div className="flex justify-between items-center text-sm text-gray-600">
          <span>{formatSalary(job.salary_min, job.salary_max, job.salary_currency)}</span>
          <span>{getTimeAgo(job.posted_at || job.created_at)}</span>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto"
    >
      {/* Header */}
      <div className="card mb-6">
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between mb-6">
          <div className="flex-1">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{job.title}</h1>
                <div className="flex flex-wrap items-center gap-4 text-gray-600 mb-4">
                  <div className="flex items-center">
                    <BuildingOfficeIcon className="h-5 w-5 mr-2" />
                    <span className="font-medium">{job.company?.company_name}</span>
                  </div>
                  
                  {job.location && (
                    <div className="flex items-center">
                      <MapPinIcon className="h-5 w-5 mr-2" />
                      <span>{job.location}</span>
                    </div>
                  )}
                  
                  <div className="flex items-center">
                    <ClockIcon className="h-5 w-5 mr-2" />
                    <span>Posted {getTimeAgo(job.posted_at || job.created_at)}</span>
                  </div>
                  
                  {job.application_count > 0 && (
                    <div className="flex items-center">
                      <UserGroupIcon className="h-5 w-5 mr-2" />
                      <span>{job.application_count} applicants</span>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="flex items-center space-x-2 ml-4">
                {showSaveButton && (
                  <button
                    onClick={toggleSaveJob}
                    className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                    aria-label={isSaved ? "Unsave job" : "Save job"}
                  >
                    {isSaved ? (
                      <HeartSolidIcon className="h-5 w-5 text-red-500" />
                    ) : (
                      <HeartIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                )}
                
                <button
                  onClick={shareJob}
                  className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  <ShareIcon className="h-5 w-5 text-gray-400" />
                </button>
              </div>
            </div>
            
            {/* Job Tags */}
            <div className="flex flex-wrap gap-2 mb-6">
              <span className="px-3 py-1 bg-primary-100 text-primary-700 text-sm rounded-full font-medium">
                {job.job_type.replace('_', ' ')}
              </span>
              <span className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full font-medium">
                {job.remote_type}
              </span>
              <span className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full font-medium">
                {job.experience_level}
              </span>
              {job.is_urgent && (
                <span className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded-full font-medium">
                  Urgent
                </span>
              )}
              {job.is_featured && (
                <span className="px-3 py-1 bg-yellow-100 text-yellow-700 text-sm rounded-full font-medium">
                  Featured
                </span>
              )}
            </div>
          </div>
          
          {/* Apply Button */}
          {showApplyButton && (
            <div className="lg:ml-6">
              <motion.button
                onClick={handleApply}
                disabled={isApplying}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full lg:w-auto px-8 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isApplying ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Applying...
                  </div>
                ) : (
                  'Apply Now'
                )}
              </motion.button>
            </div>
          )}
        </div>
        
        {/* Key Details */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 border-t border-gray-200">
          <div className="flex items-center">
            <CurrencyDollarIcon className="h-6 w-6 text-gray-400 mr-3" />
            <div>
              <p className="text-sm text-gray-500">Salary</p>
              <p className="font-medium text-gray-900">
                {formatSalary(job.salary_min, job.salary_max, job.salary_currency)}
              </p>
            </div>
          </div>
          
          {job.department && (
            <div className="flex items-center">
              <BriefcaseIcon className="h-6 w-6 text-gray-400 mr-3" />
              <div>
                <p className="text-sm text-gray-500">Department</p>
                <p className="font-medium text-gray-900">{job.department}</p>
              </div>
            </div>
          )}
          
          {job.application_deadline && (
            <div className="flex items-center">
              <CalendarIcon className="h-6 w-6 text-gray-400 mr-3" />
              <div>
                <p className="text-sm text-gray-500">Application Deadline</p>
                <p className="font-medium text-gray-900">
                  {new Date(job.application_deadline).toLocaleDateString()}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Job Description */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Description</h2>
        {job.summary && (
          <div className="mb-6 p-4 bg-primary-50 rounded-lg">
            <p className="text-primary-800 font-medium">{job.summary}</p>
          </div>
        )}
        <div 
          className="prose prose-sm max-w-none text-gray-700"
          dangerouslySetInnerHTML={{ __html: job.description }}
        />
      </div>

      {/* Requirements & Responsibilities */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {job.requirements && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Requirements</h3>
            <div 
              className="prose prose-sm max-w-none text-gray-700"
              dangerouslySetInnerHTML={{ __html: job.requirements }}
            />
          </div>
        )}
        
        {job.responsibilities && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Responsibilities</h3>
            <div 
              className="prose prose-sm max-w-none text-gray-700"
              dangerouslySetInnerHTML={{ __html: job.responsibilities }}
            />
          </div>
        )}
      </div>

      {/* Skills & Qualifications */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {job.required_skills && job.required_skills.length > 0 && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Required Skills</h3>
            <div className="flex flex-wrap gap-2">
              {job.required_skills.map((skill) => (
                <span
                  key={skill.id}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                >
                  {skill.name}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {job.qualifications && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Preferred Qualifications</h3>
            <div 
              className="prose prose-sm max-w-none text-gray-700"
              dangerouslySetInnerHTML={{ __html: job.qualifications }}
            />
          </div>
        )}
      </div>

      {/* Benefits & Perks */}
      {job.benefits && job.benefits.length > 0 && (
        <div className="card mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Benefits & Perks</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {job.benefits.map((benefit, index) => (
              <div key={index} className="flex items-center">
                <div className="w-2 h-2 bg-primary-500 rounded-full mr-3"></div>
                <span className="text-gray-700">{benefit}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Company Info */}
      {job.company && (
        <div className="card mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">About {job.company.company_name}</h3>
          <div className="flex items-start space-x-4">
            {job.company.logo_url && (
              <img
                src={job.company.logo_url}
                alt={job.company.company_name}
                className="w-16 h-16 rounded-lg object-cover"
              />
            )}
            <div className="flex-1">
              {job.company.description && (
                <p className="text-gray-700 mb-3">{job.company.description}</p>
              )}
              <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                <span>Industry: {job.company.industry}</span>
                <span>Size: {job.company.company_size}</span>
                {job.company.website && (
                  <a
                    href={job.company.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700"
                  >
                    Visit Website
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Application Instructions */}
      {job.application_instructions && (
        <div className="card mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Application Instructions</h3>
          <p className="text-gray-700">{job.application_instructions}</p>
        </div>
      )}

      {/* Tags */}
      {job.tags && job.tags.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {job.tags.map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
              >
                <TagIcon className="h-3 w-3 inline mr-1" />
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}