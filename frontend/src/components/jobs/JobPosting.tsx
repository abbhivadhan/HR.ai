'use client'

import React, { useState } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import Select from 'react-select'
import RichTextEditor from '@/components/ui/RichTextEditor'
import { JobPosting as JobPostingType, JobType, RemoteType, JobStatus } from '@/types/job'
import { jobService } from '@/services/jobService'
import {
  BriefcaseIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  TagIcon,
  BuildingOfficeIcon,
} from '@heroicons/react/24/outline'

// Validation schema
const jobPostingSchema = z.object({
  title: z.string().min(1, 'Job title is required').max(100, 'Title too long'),
  summary: z.string().max(200, 'Summary too long').optional(),
  description: z.string().min(50, 'Description must be at least 50 characters'),
  job_type: z.nativeEnum(JobType),
  experience_level: z.string().min(1, 'Experience level is required'),
  department: z.string().optional(),
  location: z.string().optional(),
  remote_type: z.nativeEnum(RemoteType),
  salary_min: z.number().min(0).optional(),
  salary_max: z.number().min(0).optional(),
  salary_currency: z.string().default('USD'),
  benefits: z.array(z.string()).default([]),
  requirements: z.string().optional(),
  responsibilities: z.string().optional(),
  qualifications: z.string().optional(),
  application_deadline: z.string().optional(),
  max_applications: z.number().min(1).optional(),
  application_instructions: z.string().optional(),
  tags: z.array(z.string()).default([]),
  required_skills: z.array(z.string()).default([]),
})

type JobPostingFormData = z.infer<typeof jobPostingSchema>

interface JobPostingProps {
  job?: JobPostingType
  onSuccess?: (job: JobPostingType) => void
  onCancel?: () => void
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

export default function JobPosting({ job, onSuccess, onCancel }: JobPostingProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [currentStep, setCurrentStep] = useState(1)
  const isEditing = !!job

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors },
  } = useForm<JobPostingFormData>({
    resolver: zodResolver(jobPostingSchema),
    defaultValues: job ? {
      title: job.title,
      summary: job.summary || '',
      description: job.description,
      job_type: job.job_type,
      experience_level: job.experience_level,
      department: job.department || '',
      location: job.location || '',
      remote_type: job.remote_type,
      salary_min: job.salary_min,
      salary_max: job.salary_max,
      salary_currency: job.salary_currency,
      benefits: job.benefits,
      requirements: job.requirements || '',
      responsibilities: job.responsibilities || '',
      qualifications: job.qualifications || '',
      application_deadline: job.application_deadline ? 
        new Date(job.application_deadline).toISOString().split('T')[0] : '',
      max_applications: job.max_applications,
      application_instructions: job.application_instructions || '',
      tags: job.tags,
      required_skills: job.required_skills?.map(skill => skill.name) || [],
    } : {
      job_type: JobType.FULL_TIME,
      remote_type: RemoteType.HYBRID,
      salary_currency: 'USD',
      benefits: [],
      tags: [],
      required_skills: [],
    }
  })

  const onSubmit = async (data: JobPostingFormData) => {
    setIsSubmitting(true)
    try {
      // Transform required_skills from string[] to Skill[]
      const jobData = {
        ...data,
        required_skills: data.required_skills?.map(skillName => ({
          id: '', // Will be set by backend
          name: skillName,
          category: 'General',
          level: 'Intermediate'
        }))
      }
      
      let result: JobPostingType
      if (isEditing && job) {
        result = await jobService.updateJob(job.id, jobData)
      } else {
        result = await jobService.createJob(jobData)
      }
      onSuccess?.(result)
    } catch (error) {
      console.error('Error saving job:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const steps = [
    { id: 1, name: 'Basic Info', icon: BriefcaseIcon },
    { id: 2, name: 'Details', icon: BuildingOfficeIcon },
    { id: 3, name: 'Requirements', icon: TagIcon },
    { id: 4, name: 'Application', icon: CalendarIcon },
  ]

  const nextStep = () => setCurrentStep(Math.min(currentStep + 1, 4))
  const prevStep = () => setCurrentStep(Math.max(currentStep - 1, 1))

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto"
    >
      <div className="card">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {isEditing ? 'Edit Job Posting' : 'Create New Job Posting'}
          </h2>
          
          {/* Progress Steps */}
          <div className="flex items-center justify-between mt-6">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div
                  className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                    currentStep >= step.id
                      ? 'bg-primary-600 border-primary-600 text-white'
                      : 'border-gray-300 text-gray-500'
                  }`}
                >
                  <step.icon className="h-5 w-5" />
                </div>
                <span className={`ml-2 text-sm font-medium ${
                  currentStep >= step.id ? 'text-primary-600' : 'text-gray-500'
                }`}>
                  {step.name}
                </span>
                {index < steps.length - 1 && (
                  <div className={`w-16 h-0.5 ml-4 ${
                    currentStep > step.id ? 'bg-primary-600' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Step 1: Basic Info */}
          {currentStep === 1 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                    Job Title *
                  </label>
                  <input
                    {...register('title')}
                    id="title"
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="e.g. Senior Software Engineer"
                  />
                  {errors.title && (
                    <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
                  )}
                </div>

                <div className="md:col-span-2">
                  <label htmlFor="summary" className="block text-sm font-medium text-gray-700 mb-2">
                    Job Summary
                  </label>
                  <textarea
                    {...register('summary')}
                    id="summary"
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Brief summary of the role (optional)"
                  />
                  {errors.summary && (
                    <p className="mt-1 text-sm text-red-600">{errors.summary.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Type *
                  </label>
                  <Controller
                    name="job_type"
                    control={control}
                    render={({ field }) => (
                      <Select
                        {...field}
                        options={jobTypeOptions}
                        value={jobTypeOptions.find(option => option.value === field.value)}
                        onChange={(option) => field.onChange(option?.value)}
                        className="react-select-container"
                        classNamePrefix="react-select"
                      />
                    )}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Experience Level *
                  </label>
                  <Controller
                    name="experience_level"
                    control={control}
                    render={({ field }) => (
                      <Select
                        {...field}
                        options={experienceLevelOptions}
                        value={experienceLevelOptions.find(option => option.value === field.value)}
                        onChange={(option) => field.onChange(option?.value)}
                        className="react-select-container"
                        classNamePrefix="react-select"
                      />
                    )}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Department
                  </label>
                  <input
                    {...register('department')}
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="e.g. Engineering"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Remote Type *
                  </label>
                  <Controller
                    name="remote_type"
                    control={control}
                    render={({ field }) => (
                      <Select
                        {...field}
                        options={remoteTypeOptions}
                        value={remoteTypeOptions.find(option => option.value === field.value)}
                        onChange={(option) => field.onChange(option?.value)}
                        className="react-select-container"
                        classNamePrefix="react-select"
                      />
                    )}
                  />
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 2: Details */}
          {currentStep === 2 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
            >
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description *
                </label>
                <Controller
                  name="description"
                  control={control}
                  render={({ field }) => (
                    <RichTextEditor
                      content={field.value}
                      onChange={field.onChange}
                      placeholder="Describe the role, company culture, and what makes this opportunity exciting..."
                    />
                  )}
                />
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Location
                  </label>
                  <input
                    {...register('location')}
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="e.g. San Francisco, CA"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Salary Currency
                  </label>
                  <select
                    {...register('salary_currency')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="CAD">CAD</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Salary
                  </label>
                  <input
                    {...register('salary_min', { valueAsNumber: true })}
                    type="number"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="50000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Maximum Salary
                  </label>
                  <input
                    {...register('salary_max', { valueAsNumber: true })}
                    type="number"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="80000"
                  />
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 3: Requirements */}
          {currentStep === 3 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
            >
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Requirements
                </label>
                <Controller
                  name="requirements"
                  control={control}
                  render={({ field }) => (
                    <RichTextEditor
                      content={field.value || ''}
                      onChange={field.onChange}
                      placeholder="List the key requirements for this position..."
                    />
                  )}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Responsibilities
                </label>
                <Controller
                  name="responsibilities"
                  control={control}
                  render={({ field }) => (
                    <RichTextEditor
                      content={field.value || ''}
                      onChange={field.onChange}
                      placeholder="Describe the main responsibilities and duties..."
                    />
                  )}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Qualifications
                </label>
                <Controller
                  name="qualifications"
                  control={control}
                  render={({ field }) => (
                    <RichTextEditor
                      content={field.value || ''}
                      onChange={field.onChange}
                      placeholder="List preferred qualifications and nice-to-haves..."
                    />
                  )}
                />
              </div>
            </motion.div>
          )}

          {/* Step 4: Application Settings */}
          {currentStep === 4 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Application Deadline
                  </label>
                  <input
                    {...register('application_deadline')}
                    type="date"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Maximum Applications
                  </label>
                  <input
                    {...register('max_applications', { valueAsNumber: true })}
                    type="number"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Application Instructions
                </label>
                <textarea
                  {...register('application_instructions')}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Any special instructions for applicants..."
                />
              </div>
            </motion.div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between pt-6 border-t border-gray-200">
            <div>
              {currentStep > 1 && (
                <button
                  type="button"
                  onClick={prevStep}
                  className="btn-secondary"
                >
                  Previous
                </button>
              )}
            </div>

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              
              {currentStep < 4 ? (
                <button
                  type="button"
                  onClick={nextStep}
                  className="btn-primary"
                >
                  Next
                </button>
              ) : (
                <motion.button
                  type="submit"
                  disabled={isSubmitting}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="btn-primary disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      {isEditing ? 'Updating...' : 'Creating...'}
                    </div>
                  ) : (
                    isEditing ? 'Update Job' : 'Create Job'
                  )}
                </motion.button>
              )}
            </div>
          </div>
        </form>
      </div>
    </motion.div>
  )
}