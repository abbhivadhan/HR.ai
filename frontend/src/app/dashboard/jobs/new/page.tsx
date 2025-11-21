'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  BriefcaseIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  ClockIcon,
  UserGroupIcon,
  AcademicCapIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import AnimatedSelect from '@/components/ui/AnimatedSelect'

export default function PostJobPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [jobData, setJobData] = useState({
    // Basic Info
    title: '',
    department: '',
    location: '',
    locationType: 'onsite',
    
    // Job Details
    employmentType: 'full-time',
    experienceLevel: 'mid',
    salaryMin: '',
    salaryMax: '',
    currency: 'USD',
    
    // Description
    description: '',
    responsibilities: [''],
    requirements: [''],
    niceToHave: [''],
    
    // Benefits & Perks
    benefits: [],
    
    // Skills
    requiredSkills: [],
    preferredSkills: [],
    
    // Application Settings
    applicationDeadline: '',
    numberOfPositions: '1',
    urgency: 'normal'
  })

  const steps = [
    { id: 1, name: 'Basic Info', icon: BriefcaseIcon },
    { id: 2, name: 'Job Details', icon: ClockIcon },
    { id: 3, name: 'Description', icon: AcademicCapIcon },
    { id: 4, name: 'Requirements', icon: UserGroupIcon },
    { id: 5, name: 'Review', icon: CheckIcon }
  ]

  const benefitOptions = [
    'Health Insurance',
    'Dental Insurance',
    'Vision Insurance',
    '401(k) Matching',
    'Flexible Hours',
    'Remote Work',
    'Unlimited PTO',
    'Paid Parental Leave',
    'Professional Development',
    'Gym Membership',
    'Stock Options',
    'Commuter Benefits'
  ]

  const handleInputChange = (field: string, value: any) => {
    setJobData(prev => ({ ...prev, [field]: value }))
  }

  const handleArrayChange = (field: string, index: number, value: string) => {
    setJobData(prev => ({
      ...prev,
      [field]: prev[field as keyof typeof prev].map((item: string, i: number) => 
        i === index ? value : item
      )
    }))
  }

  const addArrayItem = (field: string) => {
    setJobData(prev => ({
      ...prev,
      [field]: [...prev[field as keyof typeof prev] as string[], '']
    }))
  }

  const removeArrayItem = (field: string, index: number) => {
    setJobData(prev => ({
      ...prev,
      [field]: (prev[field as keyof typeof prev] as string[]).filter((_, i) => i !== index)
    }))
  }

  const toggleBenefit = (benefit: string) => {
    setJobData(prev => ({
      ...prev,
      benefits: prev.benefits.includes(benefit)
        ? prev.benefits.filter(b => b !== benefit)
        : [...prev.benefits, benefit]
    }))
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // In production, save to backend
    console.log('Job Posted:', jobData)
    
    setIsSubmitting(false)
    router.push('/dashboard')
  }

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Job Title *
        </label>
        <input
          type="text"
          value={jobData.title}
          onChange={(e) => handleInputChange('title', e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          placeholder="e.g., Senior Frontend Developer"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Department
          </label>
          <input
            type="text"
            value={jobData.department}
            onChange={(e) => handleInputChange('department', e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            placeholder="e.g., Engineering"
          />
        </div>

        <div>
          <AnimatedSelect
            label="Location Type"
            value={jobData.locationType}
            onChange={(value) => handleInputChange('locationType', value)}
            options={[
              { value: 'onsite', label: 'On-site' },
              { value: 'remote', label: 'Remote' },
              { value: 'hybrid', label: 'Hybrid' }
            ]}
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Location *
        </label>
        <input
          type="text"
          value={jobData.location}
          onChange={(e) => handleInputChange('location', e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          placeholder="e.g., San Francisco, CA or Remote"
        />
      </div>
    </div>
  )

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <AnimatedSelect
          label="Employment Type"
          value={jobData.employmentType}
          onChange={(value) => handleInputChange('employmentType', value)}
          options={[
            { value: 'full-time', label: 'Full-time' },
            { value: 'part-time', label: 'Part-time' },
            { value: 'contract', label: 'Contract' },
            { value: 'internship', label: 'Internship' }
          ]}
        />

        <AnimatedSelect
          label="Experience Level"
          value={jobData.experienceLevel}
          onChange={(value) => handleInputChange('experienceLevel', value)}
          options={[
            { value: 'entry', label: 'Entry Level' },
            { value: 'mid', label: 'Mid Level' },
            { value: 'senior', label: 'Senior Level' },
            { value: 'lead', label: 'Lead/Principal' }
          ]}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Salary Range
        </label>
        <div className="grid grid-cols-3 gap-4">
          <input
            type="number"
            value={jobData.salaryMin}
            onChange={(e) => handleInputChange('salaryMin', e.target.value)}
            className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            placeholder="Min"
          />
          <input
            type="number"
            value={jobData.salaryMax}
            onChange={(e) => handleInputChange('salaryMax', e.target.value)}
            className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            placeholder="Max"
          />
          <AnimatedSelect
            label=""
            value={jobData.currency}
            onChange={(value) => handleInputChange('currency', value)}
            options={[
              { value: 'USD', label: 'USD' },
              { value: 'EUR', label: 'EUR' },
              { value: 'GBP', label: 'GBP' },
              { value: 'INR', label: 'INR' }
            ]}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Number of Positions
          </label>
          <input
            type="number"
            min="1"
            value={jobData.numberOfPositions}
            onChange={(e) => handleInputChange('numberOfPositions', e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Application Deadline
          </label>
          <input
            type="date"
            value={jobData.applicationDeadline}
            onChange={(e) => handleInputChange('applicationDeadline', e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
      </div>
    </div>
  )

  const renderStep3 = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Job Description *
        </label>
        <textarea
          rows={6}
          value={jobData.description}
          onChange={(e) => handleInputChange('description', e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          placeholder="Describe the role, team, and what makes this opportunity exciting..."
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Key Responsibilities
        </label>
        {jobData.responsibilities.map((resp, index) => (
          <div key={index} className="flex gap-2 mb-2">
            <input
              type="text"
              value={resp}
              onChange={(e) => handleArrayChange('responsibilities', index, e.target.value)}
              className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              placeholder="e.g., Design and implement new features"
            />
            {jobData.responsibilities.length > 1 && (
              <button
                onClick={() => removeArrayItem('responsibilities', index)}
                className="px-3 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            )}
          </div>
        ))}
        <button
          onClick={() => addArrayItem('responsibilities')}
          className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
        >
          + Add Responsibility
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Benefits & Perks
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {benefitOptions.map((benefit) => (
            <button
              key={benefit}
              onClick={() => toggleBenefit(benefit)}
              className={`px-4 py-2 rounded-lg border-2 transition-colors text-sm ${
                jobData.benefits.includes(benefit)
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                  : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 text-gray-700 dark:text-gray-300'
              }`}
            >
              {benefit}
            </button>
          ))}
        </div>
      </div>
    </div>
  )

  const renderStep4 = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Required Qualifications
        </label>
        {jobData.requirements.map((req, index) => (
          <div key={index} className="flex gap-2 mb-2">
            <input
              type="text"
              value={req}
              onChange={(e) => handleArrayChange('requirements', index, e.target.value)}
              className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              placeholder="e.g., 5+ years of React experience"
            />
            {jobData.requirements.length > 1 && (
              <button
                onClick={() => removeArrayItem('requirements', index)}
                className="px-3 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            )}
          </div>
        ))}
        <button
          onClick={() => addArrayItem('requirements')}
          className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
        >
          + Add Requirement
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Nice to Have
        </label>
        {jobData.niceToHave.map((item, index) => (
          <div key={index} className="flex gap-2 mb-2">
            <input
              type="text"
              value={item}
              onChange={(e) => handleArrayChange('niceToHave', index, e.target.value)}
              className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              placeholder="e.g., Experience with TypeScript"
            />
            {jobData.niceToHave.length > 1 && (
              <button
                onClick={() => removeArrayItem('niceToHave', index)}
                className="px-3 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            )}
          </div>
        ))}
        <button
          onClick={() => addArrayItem('niceToHave')}
          className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
        >
          + Add Nice to Have
        </button>
      </div>
    </div>
  )

  const renderStep5 = () => (
    <div className="space-y-6">
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Job Preview</h3>
        
        <div className="space-y-4">
          <div>
            <h4 className="text-2xl font-bold text-gray-900 dark:text-white">{jobData.title || 'Job Title'}</h4>
            <p className="text-gray-600 dark:text-gray-300">{jobData.department} • {jobData.location} • {jobData.locationType}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            <span className="px-3 py-1 bg-white dark:bg-gray-800 rounded-full text-sm text-gray-700 dark:text-gray-300">
              {jobData.employmentType}
            </span>
            <span className="px-3 py-1 bg-white dark:bg-gray-800 rounded-full text-sm text-gray-700 dark:text-gray-300">
              {jobData.experienceLevel}
            </span>
            {jobData.salaryMin && jobData.salaryMax && (
              <span className="px-3 py-1 bg-white dark:bg-gray-800 rounded-full text-sm text-gray-700 dark:text-gray-300">
                {jobData.currency} {jobData.salaryMin} - {jobData.salaryMax}
              </span>
            )}
          </div>

          {jobData.description && (
            <div>
              <h5 className="font-semibold text-gray-900 dark:text-white mb-2">Description</h5>
              <p className="text-gray-600 dark:text-gray-300">{jobData.description}</p>
            </div>
          )}

          {jobData.responsibilities.filter(r => r).length > 0 && (
            <div>
              <h5 className="font-semibold text-gray-900 dark:text-white mb-2">Responsibilities</h5>
              <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-300">
                {jobData.responsibilities.filter(r => r).map((resp, i) => (
                  <li key={i}>{resp}</li>
                ))}
              </ul>
            </div>
          )}

          {jobData.requirements.filter(r => r).length > 0 && (
            <div>
              <h5 className="font-semibold text-gray-900 dark:text-white mb-2">Requirements</h5>
              <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-300">
                {jobData.requirements.filter(r => r).map((req, i) => (
                  <li key={i}>{req}</li>
                ))}
              </ul>
            </div>
          )}

          {jobData.benefits.length > 0 && (
            <div>
              <h5 className="font-semibold text-gray-900 dark:text-white mb-2">Benefits</h5>
              <div className="flex flex-wrap gap-2">
                {jobData.benefits.map((benefit, i) => (
                  <span key={i} className="px-3 py-1 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded-full text-sm">
                    {benefit}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Post a New Job</h1>
          <p className="text-gray-600 dark:text-gray-300">Fill in the details to create your job posting</p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      currentStep >= step.id
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                    }`}
                  >
                    <step.icon className="w-5 h-5" />
                  </div>
                  <span className="text-xs mt-2 text-gray-600 dark:text-gray-400">{step.name}</span>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`h-1 flex-1 mx-2 ${
                      currentStep > step.id ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Form */}
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 mb-8"
        >
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
          {currentStep === 4 && renderStep4()}
          {currentStep === 5 && renderStep5()}
        </motion.div>

        {/* Navigation Buttons */}
        <div className="flex justify-between">
          <button
            onClick={() => currentStep > 1 ? setCurrentStep(currentStep - 1) : router.back()}
            className="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            {currentStep === 1 ? 'Cancel' : 'Previous'}
          </button>

          {currentStep < 5 ? (
            <button
              onClick={() => setCurrentStep(currentStep + 1)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Next Step
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting ? 'Publishing...' : 'Publish Job'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
