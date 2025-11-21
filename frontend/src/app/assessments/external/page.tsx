'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import {
  AcademicCapIcon,
  ClockIcon,
  StarIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  GlobeAltIcon,
  CodeBracketIcon,
  CommandLineIcon,
  BeakerIcon,
  BookOpenIcon
} from '@heroicons/react/24/outline'
import axios from 'axios'
import AnimatedSelect from '@/components/ui/AnimatedSelect'

interface ExternalTest {
  id: string
  name: string
  description: string
  duration: number
  skills: string[]
  difficulty: string
  provider: string
  match_score?: number
}

export default function ExternalAssessmentsPage() {
  const router = useRouter()
  const [tests, setTests] = useState<ExternalTest[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedProvider, setSelectedProvider] = useState<string>('all')
  const [selectedSkill, setSelectedSkill] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')

  const providers = [
    { id: 'all', name: 'All Providers', icon: GlobeAltIcon },
    { id: 'hackerrank', name: 'HackerRank', icon: CodeBracketIcon },
    { id: 'codesignal', name: 'CodeSignal', icon: CommandLineIcon },
    { id: 'testgorilla', name: 'TestGorilla', icon: BeakerIcon },
    { id: 'pluralsight', name: 'Pluralsight', icon: BookOpenIcon }
  ]

  useEffect(() => {
    loadTests()
  }, [selectedProvider, selectedSkill])

  const loadTests = async () => {
    setLoading(true)
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      
      let url = `${API_URL}/api/assessments/external/tests`
      if (selectedProvider !== 'all') {
        url += `?provider=${selectedProvider}`
      }
      if (selectedSkill !== 'all') {
        url += `${selectedProvider !== 'all' ? '&' : '?'}skill=${selectedSkill}`
      }

      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      setTests(response.data)
    } catch (error) {
      console.error('Error loading tests:', error)
      setTests([])
    } finally {
      setLoading(false)
    }
  }

  const handleStartTest = async (test: ExternalTest) => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      
      // For demo purposes, open a mock test URL
      // In production, this would call the real API
      const mockTestUrl = `https://www.${test.provider}.com/test/${test.id}`
      
      // Show success message
      alert(`Opening ${test.name} from ${test.provider}...\n\nIn production, this would redirect to the actual test platform.`)
      
      // Open mock URL in new tab
      window.open(mockTestUrl, '_blank')
      
      // Optionally call backend to track test start
      try {
        await axios.post(
          `${API_URL}/api/assessments/external/start`,
          {
            provider: test.provider,
            test_id: test.id
          },
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        )
      } catch (apiError) {
        console.log('Backend tracking not available, continuing with demo mode')
      }
      
    } catch (error) {
      console.error('Error starting test:', error)
      alert('Test opened in new tab. Check your browser for pop-up blockers.')
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300'
      case 'intermediate': return 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'
      case 'advanced': return 'bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300'
      default: return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
    }
  }

  const getProviderIcon = (provider: string) => {
    const p = providers.find(pr => pr.id === provider)
    return p?.icon || AcademicCapIcon
  }

  const filteredTests = tests.filter(test =>
    test.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    test.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    test.skills.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Professional Skill Assessments
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Take industry-standard tests from leading assessment platforms
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search assessments..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            {/* Provider Filter */}
            <div>
              <AnimatedSelect
                value={selectedProvider}
                onChange={(value) => setSelectedProvider(value)}
                options={providers.map(provider => ({
                  value: provider.id,
                  label: provider.name
                }))}
                placeholder="Select Provider"
              />
            </div>
          </div>
        </div>

        {/* Provider Badges */}
        <div className="flex flex-wrap gap-3 mb-6">
          {providers.map(provider => {
            const Icon = provider.icon
            return (
              <button
                key={provider.id}
                onClick={() => setSelectedProvider(provider.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedProvider === provider.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{provider.name}</span>
              </button>
            )
          })}
        </div>

        {/* Tests Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredTests.map((test, index) => (
              <motion.div
                key={test.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                      {(() => {
                        const Icon = getProviderIcon(test.provider)
                        return <Icon className="w-6 h-6 text-white" />
                      })()}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {test.name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                        {test.provider}
                      </p>
                    </div>
                  </div>
                  {test.match_score && (
                    <div className="flex items-center space-x-1 px-3 py-1 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded-full">
                      <StarIcon className="w-4 h-4" />
                      <span className="text-sm font-bold">{test.match_score}%</span>
                    </div>
                  )}
                </div>

                {/* Description */}
                <p className="text-gray-600 dark:text-gray-300 mb-4 line-clamp-2">
                  {test.description}
                </p>

                {/* Skills */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {test.skills.map((skill) => (
                    <span
                      key={skill}
                      className="px-3 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-sm rounded-full"
                    >
                      {skill}
                    </span>
                  ))}
                </div>

                {/* Meta Info */}
                <div className="flex items-center justify-between mb-4 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-1">
                      <ClockIcon className="w-4 h-4" />
                      <span>{test.duration} min</span>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(test.difficulty)}`}>
                      {test.difficulty.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                {/* Action Button */}
                <button
                  onClick={() => handleStartTest(test)}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  <span>Start Assessment</span>
                  <ArrowRightIcon className="w-5 h-5" />
                </button>
              </motion.div>
            ))}
          </div>
        )}

        {filteredTests.length === 0 && !loading && (
          <div className="text-center py-12">
            <AcademicCapIcon className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No assessments found
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Try adjusting your filters or search term
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
