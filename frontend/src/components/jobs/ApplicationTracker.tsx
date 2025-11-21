'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { JobApplication, ApplicationStatus } from '@/types/job'
import { jobService } from '@/services/jobService'
import {
  ClockIcon,
  EyeIcon,
  CheckCircleIcon,
  XCircleIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  CalendarIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  CurrencyDollarIcon,
} from '@heroicons/react/24/outline'

interface ApplicationTrackerProps {
  candidateId?: string
  jobId?: string
  showJobDetails?: boolean
  showCandidateDetails?: boolean
}

const statusConfig = {
  [ApplicationStatus.PENDING]: {
    color: 'yellow',
    icon: ClockIcon,
    label: 'Pending Review',
    description: 'Your application is waiting to be reviewed'
  },
  [ApplicationStatus.REVIEWING]: {
    color: 'blue',
    icon: EyeIcon,
    label: 'Under Review',
    description: 'Your application is being reviewed by the hiring team'
  },
  [ApplicationStatus.SHORTLISTED]: {
    color: 'purple',
    icon: CheckCircleIcon,
    label: 'Shortlisted',
    description: 'Congratulations! You\'ve been shortlisted for this position'
  },
  [ApplicationStatus.INTERVIEWED]: {
    color: 'indigo',
    icon: ChatBubbleLeftRightIcon,
    label: 'Interviewed',
    description: 'You\'ve completed the interview process'
  },
  [ApplicationStatus.OFFERED]: {
    color: 'green',
    icon: CheckCircleIcon,
    label: 'Offer Extended',
    description: 'Congratulations! You\'ve received a job offer'
  },
  [ApplicationStatus.ACCEPTED]: {
    color: 'green',
    icon: CheckCircleIcon,
    label: 'Offer Accepted',
    description: 'You\'ve accepted the job offer'
  },
  [ApplicationStatus.REJECTED]: {
    color: 'red',
    icon: XCircleIcon,
    label: 'Not Selected',
    description: 'Unfortunately, you weren\'t selected for this position'
  },
  [ApplicationStatus.WITHDRAWN]: {
    color: 'gray',
    icon: XCircleIcon,
    label: 'Withdrawn',
    description: 'Application was withdrawn'
  },
}

export default function ApplicationTracker({
  candidateId,
  jobId,
  showJobDetails = true,
  showCandidateDetails = false
}: ApplicationTrackerProps) {
  const [applications, setApplications] = useState<JobApplication[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedApplication, setSelectedApplication] = useState<JobApplication | null>(null)
  const [filter, setFilter] = useState<ApplicationStatus | 'all'>('all')

  useEffect(() => {
    loadApplications()
  }, [candidateId, jobId])

  const loadApplications = async () => {
    setIsLoading(true)
    try {
      let apps: JobApplication[]
      if (jobId) {
        apps = await jobService.getJobApplications(jobId)
      } else {
        apps = await jobService.getCandidateApplications()
      }
      setApplications(apps)
    } catch (error) {
      console.error('Error loading applications:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const updateApplicationStatus = async (applicationId: string, status: ApplicationStatus, notes?: string) => {
    try {
      const updatedApp = await jobService.updateApplicationStatus(applicationId, status, notes)
      setApplications(prev => 
        prev.map(app => app.id === applicationId ? updatedApp : app)
      )
      if (selectedApplication?.id === applicationId) {
        setSelectedApplication(updatedApp)
      }
    } catch (error) {
      console.error('Error updating application status:', error)
    }
  }

  const filteredApplications = applications.filter(app => 
    filter === 'all' || app.status === filter
  )

  const getStatusColor = (status: ApplicationStatus) => {
    const config = statusConfig[status]
    return {
      bg: `bg-${config.color}-100`,
      text: `text-${config.color}-700`,
      border: `border-${config.color}-200`,
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
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

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-3 bg-gray-200 rounded w-1/4"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Applications List */}
        <div className="flex-1">
          <div className="card mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                {jobId ? 'Job Applications' : 'My Applications'}
              </h2>
              
              {/* Status Filter */}
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as ApplicationStatus | 'all')}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Applications</option>
                {Object.entries(statusConfig).map(([status, config]) => (
                  <option key={status} value={status}>
                    {config.label}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Applications Count */}
            <div className="flex space-x-4 text-sm text-gray-600 mb-6">
              <span>Total: {applications.length}</span>
              <span>Active: {applications.filter(app => 
                ![ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN, ApplicationStatus.ACCEPTED].includes(app.status)
              ).length}</span>
            </div>
          </div>

          {filteredApplications.length === 0 ? (
            <div className="card text-center py-12">
              <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {filter === 'all' ? 'No applications found' : `No ${statusConfig[filter as ApplicationStatus]?.label.toLowerCase()} applications`}
              </h3>
              <p className="text-gray-600">
                {jobId ? 'No one has applied to this job yet.' : 'You haven\'t applied to any jobs yet.'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredApplications.map((application) => {
                const config = statusConfig[application.status]
                const StatusIcon = config.icon
                
                return (
                  <motion.div
                    key={application.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`card hover:shadow-lg transition-shadow cursor-pointer ${
                      selectedApplication?.id === application.id ? 'ring-2 ring-primary-500' : ''
                    }`}
                    onClick={() => setSelectedApplication(application)}
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        {showJobDetails && application.job_posting && (
                          <div className="mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {application.job_posting.title}
                            </h3>
                            <div className="flex items-center text-gray-600 text-sm">
                              <BuildingOfficeIcon className="h-4 w-4 mr-1" />
                              <span>{application.job_posting.company?.company_name}</span>
                              {application.job_posting.location && (
                                <>
                                  <span className="mx-2">•</span>
                                  <MapPinIcon className="h-4 w-4 mr-1" />
                                  <span>{application.job_posting.location}</span>
                                </>
                              )}
                            </div>
                          </div>
                        )}
                        
                        {showCandidateDetails && application.candidate && (
                          <div className="mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {application.candidate.first_name} {application.candidate.last_name}
                            </h3>
                            <p className="text-gray-600 text-sm">{application.candidate.email}</p>
                          </div>
                        )}
                      </div>
                      
                      <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(application.status).bg} ${getStatusColor(application.status).text}`}>
                        <StatusIcon className="h-4 w-4 mr-1" />
                        {config.label}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                      <div>
                        <span className="font-medium">Applied:</span>
                        <br />
                        {formatDate(application.applied_at)}
                      </div>
                      
                      {application.ai_match_score && (
                        <div>
                          <span className="font-medium">AI Match:</span>
                          <br />
                          <span className={`font-semibold ${
                            application.ai_match_score >= 80 ? 'text-green-600' :
                            application.ai_match_score >= 60 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {Math.round(application.ai_match_score)}%
                          </span>
                        </div>
                      )}
                      
                      {application.reviewed_at && (
                        <div>
                          <span className="font-medium">Reviewed:</span>
                          <br />
                          {formatDate(application.reviewed_at)}
                        </div>
                      )}
                      
                      <div>
                        <span className="font-medium">Last Update:</span>
                        <br />
                        {getTimeAgo(application.status_updated_at)}
                      </div>
                    </div>
                    
                    {application.cover_letter && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <p className="text-sm text-gray-700 line-clamp-2">
                          <span className="font-medium">Cover Letter:</span> {application.cover_letter}
                        </p>
                      </div>
                    )}
                  </motion.div>
                )
              })}
            </div>
          )}
        </div>
        
        {/* Application Details Sidebar */}
        <AnimatePresence>
          {selectedApplication && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="lg:w-96"
            >
              <div className="card sticky top-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Application Details
                  </h3>
                  <button
                    onClick={() => setSelectedApplication(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XCircleIcon className="h-5 w-5" />
                  </button>
                </div>
                
                {/* Status Timeline */}
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Status Timeline</h4>
                  <div className="space-y-3">
                    {Object.values(ApplicationStatus).map((status) => {
                      const config = statusConfig[status]
                      const StatusIcon = config.icon
                      const isCurrentStatus = selectedApplication.status === status
                      const isPastStatus = Object.values(ApplicationStatus).indexOf(selectedApplication.status) >= 
                                          Object.values(ApplicationStatus).indexOf(status)
                      
                      return (
                        <div
                          key={status}
                          className={`flex items-center ${
                            isCurrentStatus ? 'text-primary-600' : 
                            isPastStatus ? 'text-green-600' : 'text-gray-400'
                          }`}
                        >
                          <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                            isCurrentStatus ? 'border-primary-600 bg-primary-50' :
                            isPastStatus ? 'border-green-600 bg-green-50' : 'border-gray-300'
                          }`}>
                            <StatusIcon className="h-4 w-4" />
                          </div>
                          <div className="ml-3">
                            <p className="text-sm font-medium">{config.label}</p>
                            {isCurrentStatus && (
                              <p className="text-xs text-gray-600">{config.description}</p>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
                
                {/* Application Info */}
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Application Date</h4>
                    <p className="text-sm text-gray-600">{formatDate(selectedApplication.applied_at)}</p>
                  </div>
                  
                  {selectedApplication.ai_match_score && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">AI Compatibility Score</h4>
                      <div className="flex items-center">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                          <div
                            className={`h-2 rounded-full ${
                              selectedApplication.ai_match_score >= 80 ? 'bg-green-500' :
                              selectedApplication.ai_match_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${selectedApplication.ai_match_score}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">
                          {Math.round(selectedApplication.ai_match_score)}%
                        </span>
                      </div>
                    </div>
                  )}
                  
                  {selectedApplication.resume_url && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Resume</h4>
                      <a
                        href={selectedApplication.resume_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-sm text-primary-600 hover:text-primary-700"
                      >
                        <DocumentTextIcon className="h-4 w-4 mr-1" />
                        View Resume
                      </a>
                    </div>
                  )}
                  
                  {selectedApplication.cover_letter && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Cover Letter</h4>
                      <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                        {selectedApplication.cover_letter}
                      </p>
                    </div>
                  )}
                  
                  {selectedApplication.recruiter_notes && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Recruiter Notes</h4>
                      <p className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
                        {selectedApplication.recruiter_notes}
                      </p>
                    </div>
                  )}
                </div>
                
                {/* Actions for recruiters */}
                {jobId && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Update Status</h4>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => updateApplicationStatus(selectedApplication.id, ApplicationStatus.SHORTLISTED)}
                        className="px-3 py-2 text-xs bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200"
                      >
                        Shortlist
                      </button>
                      <button
                        onClick={() => updateApplicationStatus(selectedApplication.id, ApplicationStatus.INTERVIEWED)}
                        className="px-3 py-2 text-xs bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200"
                      >
                        Interviewed
                      </button>
                      <button
                        onClick={() => updateApplicationStatus(selectedApplication.id, ApplicationStatus.OFFERED)}
                        className="px-3 py-2 text-xs bg-green-100 text-green-700 rounded-lg hover:bg-green-200"
                      >
                        Make Offer
                      </button>
                      <button
                        onClick={() => updateApplicationStatus(selectedApplication.id, ApplicationStatus.REJECTED)}
                        className="px-3 py-2 text-xs bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}