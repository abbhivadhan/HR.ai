'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState } from 'react'
import { 
  MapPinIcon, 
  CurrencyDollarIcon,
  ClockIcon,
  BuildingOfficeIcon,
  BookmarkIcon,
  ShareIcon
} from '@heroicons/react/24/outline'

export default function JobDetailPage() {
  const params = useParams()
  const jobId = params.id as string
  
  const [job] = useState({
    id: jobId,
    title: 'Senior Frontend Developer',
    company: 'TechCorp Inc.',
    location: 'San Francisco, CA',
    salary: '$120k - $150k',
    type: 'Full-time',
    remote: true,
    posted: '2 days ago',
    description: `We are looking for a skilled Frontend Developer to join our team and help build amazing user experiences. You'll work with cutting-edge technologies and collaborate with a talented team of designers and engineers.

As a Senior Frontend Developer, you'll be responsible for developing and maintaining our web applications, ensuring they are performant, accessible, and user-friendly. You'll also mentor junior developers and contribute to our technical architecture decisions.`,
    requirements: [
      '5+ years of React experience',
      'Strong TypeScript skills',
      'Experience with modern build tools (Webpack, Vite)',
      'Knowledge of testing frameworks (Jest, React Testing Library)',
      'Understanding of responsive design principles',
      'Experience with state management (Redux, Zustand)',
      'Familiarity with CI/CD processes'
    ],
    responsibilities: [
      'Develop and maintain frontend applications using React and TypeScript',
      'Collaborate with designers to implement pixel-perfect UI components',
      'Write clean, maintainable, and well-tested code',
      'Optimize applications for maximum speed and scalability',
      'Mentor junior developers and conduct code reviews',
      'Participate in technical architecture discussions',
      'Stay up-to-date with the latest frontend technologies and best practices'
    ],
    benefits: [
      'Competitive salary and equity package',
      'Comprehensive health, dental, and vision insurance',
      'Flexible work arrangements (remote/hybrid)',
      'Professional development budget',
      'Unlimited PTO policy',
      'Top-tier equipment and home office setup',
      'Team retreats and company events'
    ],
    skills: ['React', 'TypeScript', 'Node.js', 'GraphQL', 'AWS'],
    matchScore: 95,
    logo: 'TC'
  })

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100'
    if (score >= 80) return 'text-blue-600 bg-blue-100'
    if (score >= 70) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8"
        >
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-start gap-4">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-lg">
                {job.logo}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{job.title}</h1>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getMatchScoreColor(job.matchScore)}`}>
                    {job.matchScore}% match
                  </span>
                  {job.remote && (
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                      Remote
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-4 text-gray-600 mb-4">
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
          
          <div className="flex gap-3">
            <Link
              href={`/jobs/${job.id}/apply`}
              className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              Apply Now
            </Link>
            <button className="px-4 py-3 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors flex items-center gap-2">
              <BookmarkIcon className="w-4 h-4" />
              Save Job
            </button>
            <button className="px-4 py-3 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2">
              <ShareIcon className="w-4 h-4" />
              Share
            </button>
          </div>
        </motion.div>

        {/* Job Details */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Description */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
            >
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Job Description</h2>
              <div className="prose prose-gray max-w-none">
                {job.description.split('\n\n').map((paragraph, index) => (
                  <p key={index} className="mb-4 text-gray-700 leading-relaxed">
                    {paragraph}
                  </p>
                ))}
              </div>
            </motion.div>

            {/* Requirements */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
            >
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Requirements</h2>
              <ul className="space-y-3">
                {job.requirements.map((requirement, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    <span className="text-gray-700">{requirement}</span>
                  </li>
                ))}
              </ul>
            </motion.div>

            {/* Responsibilities */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
            >
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Responsibilities</h2>
              <ul className="space-y-3">
                {job.responsibilities.map((responsibility, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    <span className="text-gray-700">{responsibility}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* Job Info */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Job Information</h3>
              <div className="space-y-3">
                <div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Job Type</span>
                  <p className="font-medium text-gray-900 dark:text-white">{job.type}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Location</span>
                  <p className="font-medium text-gray-900 dark:text-white">{job.location}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Salary Range</span>
                  <p className="font-medium text-gray-900 dark:text-white">{job.salary}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Posted</span>
                  <p className="font-medium text-gray-900 dark:text-white">{job.posted}</p>
                </div>
              </div>
            </motion.div>

            {/* Benefits */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Benefits & Perks</h3>
              <ul className="space-y-2">
                {job.benefits.map((benefit, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                    <span className="text-gray-700 text-sm">{benefit}</span>
                  </li>
                ))}
              </ul>
            </motion.div>

            {/* Apply CTA */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white text-center"
            >
              <h3 className="text-lg font-semibold mb-2">Ready to Apply?</h3>
              <p className="text-blue-100 mb-4 text-sm">
                Join our team and help build the future of recruitment
              </p>
              <Link
                href={`/jobs/${job.id}/apply`}
                className="w-full inline-flex items-center justify-center px-6 py-3 bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 font-semibold rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                Apply Now
              </Link>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}