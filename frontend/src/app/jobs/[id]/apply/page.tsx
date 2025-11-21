'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { 
  DocumentTextIcon,
  PaperClipIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import AnimatedSelect from '@/components/ui/AnimatedSelect'

export default function JobApplicationPage() {
  const params = useParams()
  const router = useRouter()
  const jobId = params.id as string

  const [job] = useState({
    id: jobId,
    title: 'Senior Frontend Developer',
    company: 'TechCorp Inc.',
    location: 'San Francisco, CA',
    salary: '$120k - $150k',
    type: 'Full-time',
    description: 'We are looking for a skilled Frontend Developer to join our team and help build amazing user experiences.',
    requirements: [
      '5+ years of React experience',
      'Strong TypeScript skills',
      'Experience with modern build tools',
      'Knowledge of testing frameworks'
    ]
  })

  const [application, setApplication] = useState({
    coverLetter: '',
    resume: null as File | null,
    portfolio: '',
    availability: '',
    salaryExpectation: '',
    whyInterested: '',
    additionalInfo: ''
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleInputChange = (field: string, value: string) => {
    setApplication(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        setErrors(prev => ({ ...prev, resume: 'File size must be less than 5MB' }))
        return
      }
      if (!['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)) {
        setErrors(prev => ({ ...prev, resume: 'Please upload a PDF or Word document' }))
        return
      }
      setApplication(prev => ({ ...prev, resume: file }))
      setErrors(prev => ({ ...prev, resume: '' }))
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!application.coverLetter.trim()) {
      newErrors.coverLetter = 'Cover letter is required'
    }
    if (!application.resume) {
      newErrors.resume = 'Resume is required'
    }
    if (!application.whyInterested.trim()) {
      newErrors.whyInterested = 'Please tell us why you\'re interested'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setIsSubmitting(false)
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 text-center max-w-md mx-4"
        >
          <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Application Submitted!
          </h2>
          <p className="text-gray-600 mb-6">
            Thank you for applying to {job.title} at {job.company}. 
            We'll review your application and get back to you soon.
          </p>
          <div className="flex gap-3">
            <button
              onClick={() => router.push('/jobs')}
              className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Browse More Jobs
            </button>
            <button
              onClick={() => router.push('/dashboard')}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go to Dashboard
            </button>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Job Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Apply for {job.title}
              </h1>
              <p className="text-gray-600">{job.company} • {job.location}</p>
            </div>
            <div className="text-right">
              <p className="text-lg font-semibold text-green-600">{job.salary}</p>
              <p className="text-sm text-gray-500">{job.type}</p>
            </div>
          </div>
          
          <div className="border-t dark:border-gray-700 pt-4">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">About this role:</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">{job.description}</p>
            
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Requirements:</h3>
            <ul className="space-y-1">
              {job.requirements.map((req, index) => (
                <li key={index} className="flex items-center text-gray-600">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-3"></div>
                  {req}
                </li>
              ))}
            </ul>
          </div>
        </motion.div>

        {/* Application Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <DocumentTextIcon className="w-6 h-6 mr-2" />
            Your Application
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Cover Letter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cover Letter *
              </label>
              <textarea
                rows={6}
                value={application.coverLetter}
                onChange={(e) => handleInputChange('coverLetter', e.target.value)}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.coverLetter ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Tell us about yourself and why you're perfect for this role..."
              />
              {errors.coverLetter && (
                <p className="mt-1 text-sm text-red-600 flex items-center">
                  <ExclamationTriangleIcon className="w-4 h-4 mr-1" />
                  {errors.coverLetter}
                </p>
              )}
            </div>

            {/* Resume Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Resume *
              </label>
              <div className={`border-2 border-dashed rounded-lg p-6 text-center ${
                errors.resume ? 'border-red-300' : 'border-gray-300'
              }`}>
                <PaperClipIcon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <div className="text-sm text-gray-600 mb-2">
                  {application.resume ? (
                    <span className="text-green-600 font-medium">
                      ✓ {application.resume.name}
                    </span>
                  ) : (
                    'Upload your resume (PDF or Word, max 5MB)'
                  )}
                </div>
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                  className="hidden"
                  id="resume-upload"
                />
                <label
                  htmlFor="resume-upload"
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors"
                >
                  Choose File
                </label>
              </div>
              {errors.resume && (
                <p className="mt-1 text-sm text-red-600 flex items-center">
                  <ExclamationTriangleIcon className="w-4 h-4 mr-1" />
                  {errors.resume}
                </p>
              )}
            </div>

            {/* Portfolio */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Portfolio/Website (Optional)
              </label>
              <input
                type="url"
                value={application.portfolio}
                onChange={(e) => handleInputChange('portfolio', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="https://your-portfolio.com"
              />
            </div>

            {/* Why Interested */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Why are you interested in this position? *
              </label>
              <textarea
                rows={4}
                value={application.whyInterested}
                onChange={(e) => handleInputChange('whyInterested', e.target.value)}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.whyInterested ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="What excites you about this opportunity?"
              />
              {errors.whyInterested && (
                <p className="mt-1 text-sm text-red-600 flex items-center">
                  <ExclamationTriangleIcon className="w-4 h-4 mr-1" />
                  {errors.whyInterested}
                </p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Availability */}
              <div className="relative z-10">
                <AnimatedSelect
                  label="Availability"
                  value={application.availability}
                  onChange={(value) => handleInputChange('availability', value)}
                  options={[
                    { value: '', label: 'Select availability' },
                    { value: 'immediately', label: 'Immediately' },
                    { value: '2weeks', label: '2 weeks notice' },
                    { value: '1month', label: '1 month notice' },
                    { value: '2months', label: '2+ months' }
                  ]}
                  placeholder="Select availability"
                />
              </div>

              {/* Salary Expectation */}
              <div className="relative z-0">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Salary Expectation
                </label>
                <input
                  type="text"
                  value={application.salaryExpectation}
                  onChange={(e) => handleInputChange('salaryExpectation', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., $120k - $140k"
                />
              </div>
            </div>

            {/* Additional Info */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Information (Optional)
              </label>
              <textarea
                rows={3}
                value={application.additionalInfo}
                onChange={(e) => handleInputChange('additionalInfo', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Anything else you'd like us to know?"
              />
            </div>

            {/* Submit Button */}
            <div className="flex gap-4 pt-6">
              <button
                type="button"
                onClick={() => router.back()}
                className="flex-1 px-6 py-3 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Application'}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  )
}