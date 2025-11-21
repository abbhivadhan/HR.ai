'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { CandidateProfile as CandidateProfileType } from '@/types/job'
import { jobService } from '@/services/jobService'
import {
  UserIcon,
  EnvelopeIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  AcademicCapIcon,
  TrophyIcon,
  DocumentTextIcon,
  StarIcon,
  ClockIcon,
  BriefcaseIcon,
} from '@heroicons/react/24/outline'

interface CandidateProfileProps {
  candidateId: string
  showContactInfo?: boolean
  showActions?: boolean
  onContact?: (candidate: CandidateProfileType) => void
  onScheduleInterview?: (candidate: CandidateProfileType) => void
}

export default function CandidateProfile({
  candidateId,
  showContactInfo = false,
  showActions = false,
  onContact,
  onScheduleInterview
}: CandidateProfileProps) {
  const [candidate, setCandidate] = useState<CandidateProfileType | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'experience' | 'education' | 'skills'>('overview')

  useEffect(() => {
    loadCandidate()
  }, [candidateId])

  const loadCandidate = async () => {
    setIsLoading(true)
    try {
      const candidateData = await jobService.getCandidateProfile(candidateId)
      setCandidate(candidateData)
    } catch (error) {
      console.error('Error loading candidate:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getSkillLevelColor = (level?: string) => {
    switch (level?.toLowerCase()) {
      case 'expert':
        return 'bg-green-100 text-green-800'
      case 'advanced':
        return 'bg-blue-100 text-blue-800'
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800'
      case 'beginner':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-primary-100 text-primary-800'
    }
  }

  const formatSalaryExpectation = (salary?: { min: number; max: number; currency: string }) => {
    if (!salary) return 'Not specified'
    if (salary.min && salary.max) {
      return `${salary.currency} ${salary.min.toLocaleString()} - ${salary.max.toLocaleString()}`
    }
    if (salary.min) return `${salary.currency} ${salary.min.toLocaleString()}+`
    return 'Negotiable'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
    })
  }

  const calculateDuration = (startDate: string, endDate?: string) => {
    const start = new Date(startDate)
    const end = endDate ? new Date(endDate) : new Date()
    const months = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth())
    const years = Math.floor(months / 12)
    const remainingMonths = months % 12
    
    if (years === 0) return `${remainingMonths} month${remainingMonths !== 1 ? 's' : ''}`
    if (remainingMonths === 0) return `${years} year${years !== 1 ? 's' : ''}`
    return `${years} year${years !== 1 ? 's' : ''}, ${remainingMonths} month${remainingMonths !== 1 ? 's' : ''}`
  }

  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="flex items-center space-x-4 mb-6">
          <div className="w-20 h-20 bg-gray-200 rounded-full"></div>
          <div className="flex-1">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          </div>
        </div>
        <div className="space-y-4">
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  if (!candidate) {
    return (
      <div className="card text-center py-12">
        <UserIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Candidate not found</h3>
        <p className="text-gray-600">The requested candidate profile could not be loaded.</p>
      </div>
    )
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: UserIcon },
    { id: 'experience', label: 'Experience', icon: BriefcaseIcon },
    { id: 'education', label: 'Education', icon: AcademicCapIcon },
    { id: 'skills', label: 'Skills', icon: StarIcon },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto"
    >
      {/* Header */}
      <div className="card mb-6">
        <div className="flex flex-col md:flex-row items-start md:items-center space-y-4 md:space-y-0 md:space-x-6">
          {/* Profile Picture */}
          <div className="flex-shrink-0">
            {candidate.profile_picture ? (
              <img
                src={candidate.profile_picture}
                alt={`${candidate.first_name} ${candidate.last_name}`}
                className="w-20 h-20 rounded-full object-cover"
              />
            ) : (
              <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
                <UserIcon className="h-10 w-10 text-primary-600" />
              </div>
            )}
          </div>
          
          {/* Basic Info */}
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {candidate.first_name} {candidate.last_name}
            </h1>
            
            <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
              {showContactInfo && (
                <div className="flex items-center">
                  <EnvelopeIcon className="h-4 w-4 mr-1" />
                  <span>{candidate.email}</span>
                </div>
              )}
              
              {candidate.preferred_locations.length > 0 && (
                <div className="flex items-center">
                  <MapPinIcon className="h-4 w-4 mr-1" />
                  <span>{candidate.preferred_locations.join(', ')}</span>
                </div>
              )}
              
              <div className="flex items-center">
                <BriefcaseIcon className="h-4 w-4 mr-1" />
                <span>{candidate.experience_years} years experience</span>
              </div>
              
              {candidate.salary_expectation && (
                <div className="flex items-center">
                  <CurrencyDollarIcon className="h-4 w-4 mr-1" />
                  <span>{formatSalaryExpectation(candidate.salary_expectation)}</span>
                </div>
              )}
              
              {candidate.availability && (
                <div className="flex items-center">
                  <CalendarIcon className="h-4 w-4 mr-1" />
                  <span>Available {formatDate(candidate.availability)}</span>
                </div>
              )}
            </div>
            
            {candidate.bio && (
              <p className="text-gray-700 mb-4">{candidate.bio}</p>
            )}
            
            {/* Quick Skills Preview */}
            <div className="flex flex-wrap gap-2">
              {candidate.skills.slice(0, 5).map((skill) => (
                <span
                  key={skill.id}
                  className={`px-2 py-1 text-xs rounded-full ${getSkillLevelColor(skill.level)}`}
                >
                  {skill.name}
                </span>
              ))}
              {candidate.skills.length > 5 && (
                <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                  +{candidate.skills.length - 5} more
                </span>
              )}
            </div>
          </div>
          
          {/* Actions */}
          {showActions && (
            <div className="flex flex-col space-y-2">
              {candidate.resume_url && (
                <a
                  href={candidate.resume_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  <DocumentTextIcon className="h-4 w-4 mr-2" />
                  View Resume
                </a>
              )}
              
              {onContact && (
                <button
                  onClick={() => onContact(candidate)}
                  className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700"
                >
                  <EnvelopeIcon className="h-4 w-4 mr-2" />
                  Contact
                </button>
              )}
              
              {onScheduleInterview && (
                <button
                  onClick={() => onScheduleInterview(candidate)}
                  className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700"
                >
                  <CalendarIcon className="h-4 w-4 mr-2" />
                  Schedule Interview
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-gray-200 mb-6">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const TabIcon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <TabIcon className="h-4 w-4 mr-2" />
                  {tab.label}
                </button>
              )
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {candidate.bio && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">About</h3>
                  <p className="text-gray-700">{candidate.bio}</p>
                </div>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Key Information</h3>
                  <dl className="space-y-3">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Experience</dt>
                      <dd className="text-sm text-gray-900">{candidate.experience_years} years</dd>
                    </div>
                    {candidate.preferred_locations.length > 0 && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Preferred Locations</dt>
                        <dd className="text-sm text-gray-900">{candidate.preferred_locations.join(', ')}</dd>
                      </div>
                    )}
                    {candidate.salary_expectation && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Salary Expectation</dt>
                        <dd className="text-sm text-gray-900">{formatSalaryExpectation(candidate.salary_expectation)}</dd>
                      </div>
                    )}
                    {candidate.availability && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Availability</dt>
                        <dd className="text-sm text-gray-900">{formatDate(candidate.availability)}</dd>
                      </div>
                    )}
                  </dl>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Top Skills</h3>
                  <div className="space-y-2">
                    {candidate.skills.slice(0, 8).map((skill) => (
                      <div key={skill.id} className="flex justify-between items-center">
                        <span className="text-sm text-gray-900">{skill.name}</span>
                        <span className={`px-2 py-1 text-xs rounded-full ${getSkillLevelColor(skill.level)}`}>
                          {skill.level || 'Proficient'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'experience' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Work Experience</h3>
              <div className="text-center py-8 text-gray-500">
                <BriefcaseIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Work experience details would be displayed here.</p>
                <p className="text-sm">This feature requires additional backend implementation.</p>
              </div>
            </div>
          )}

          {activeTab === 'education' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Education & Certifications</h3>
              
              {candidate.education.length > 0 ? (
                <div className="space-y-6">
                  <div>
                    <h4 className="text-md font-medium text-gray-900 mb-3">Education</h4>
                    <div className="space-y-4">
                      {candidate.education.map((edu) => (
                        <div key={edu.id} className="border-l-4 border-primary-200 pl-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <h5 className="font-medium text-gray-900">{edu.degree} in {edu.field_of_study}</h5>
                              <p className="text-gray-600">{edu.institution}</p>
                              {edu.grade && (
                                <p className="text-sm text-gray-500">Grade: {edu.grade}</p>
                              )}
                            </div>
                            <div className="text-right text-sm text-gray-500">
                              <p>{formatDate(edu.start_date)} - {edu.end_date ? formatDate(edu.end_date) : 'Present'}</p>
                              <p>{calculateDuration(edu.start_date, edu.end_date)}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {candidate.certifications.length > 0 && (
                    <div>
                      <h4 className="text-md font-medium text-gray-900 mb-3">Certifications</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {candidate.certifications.map((cert) => (
                          <div key={cert.id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <h5 className="font-medium text-gray-900">{cert.name}</h5>
                                <p className="text-sm text-gray-600">{cert.issuing_organization}</p>
                                <p className="text-xs text-gray-500 mt-1">
                                  Issued: {formatDate(cert.issue_date)}
                                  {cert.expiration_date && (
                                    <span> • Expires: {formatDate(cert.expiration_date)}</span>
                                  )}
                                </p>
                              </div>
                              <TrophyIcon className="h-5 w-5 text-yellow-500 flex-shrink-0 ml-2" />
                            </div>
                            {cert.credential_url && (
                              <a
                                href={cert.credential_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center mt-2 text-xs text-primary-600 hover:text-primary-700"
                              >
                                View Credential
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <AcademicCapIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>No education information available.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'skills' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Skills & Expertise</h3>
              
              {candidate.skills.length > 0 ? (
                <div className="space-y-6">
                  {/* Group skills by category */}
                  {Array.from(new Set(candidate.skills.map(skill => skill.category))).map(category => (
                    <div key={category}>
                      <h4 className="text-md font-medium text-gray-900 mb-3 capitalize">{category}</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {candidate.skills
                          .filter(skill => skill.category === category)
                          .map((skill) => (
                            <div
                              key={skill.id}
                              className="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
                            >
                              <span className="font-medium text-gray-900">{skill.name}</span>
                              <span className={`px-2 py-1 text-xs rounded-full ${getSkillLevelColor(skill.level)}`}>
                                {skill.level || 'Proficient'}
                              </span>
                            </div>
                          ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <StarIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>No skills information available.</p>
                </div>
              )}
            </div>
          )}
        </motion.div>
      </div>
    </motion.div>
  )
}