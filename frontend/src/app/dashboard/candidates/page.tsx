'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  StarIcon,
  MapPinIcon,
  BriefcaseIcon,
  AcademicCapIcon,
  EnvelopeIcon,
  PhoneIcon
} from '@heroicons/react/24/outline'

interface Candidate {
  id: string
  name: string
  title: string
  location: string
  experience: string
  skills: string[]
  matchScore: number
  availability: string
  email: string
  phone: string
  education: string
  appliedJobs: number
}

export default function CandidatesPage() {
  const router = useRouter()
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [filterSkill, setFilterSkill] = useState('')
  const [sortBy, setSortBy] = useState<'match' | 'experience' | 'recent'>('match')

  useEffect(() => {
    loadCandidates()
  }, [])

  const loadCandidates = () => {
    setCandidates([
      {
        id: '1',
        name: 'Sarah Johnson',
        title: 'Senior Frontend Developer',
        location: 'San Francisco, CA',
        experience: '7 years',
        skills: ['React', 'TypeScript', 'Node.js', 'GraphQL'],
        matchScore: 95,
        availability: 'Immediate',
        email: 'sarah.j@email.com',
        phone: '+1 (555) 123-4567',
        education: 'BS Computer Science, Stanford',
        appliedJobs: 3
      },
      {
        id: '2',
        name: 'Michael Chen',
        title: 'Full Stack Engineer',
        location: 'New York, NY',
        experience: '5 years',
        skills: ['Python', 'React', 'PostgreSQL', 'AWS'],
        matchScore: 88,
        availability: '2 weeks',
        email: 'michael.c@email.com',
        phone: '+1 (555) 234-5678',
        education: 'MS Software Engineering, MIT',
        appliedJobs: 2
      },
      {
        id: '3',
        name: 'Emily Rodriguez',
        title: 'Backend Developer',
        location: 'Austin, TX',
        experience: '4 years',
        skills: ['Java', 'Spring Boot', 'MongoDB', 'Docker'],
        matchScore: 82,
        availability: '1 month',
        email: 'emily.r@email.com',
        phone: '+1 (555) 345-6789',
        education: 'BS Computer Engineering, UT Austin',
        appliedJobs: 1
      },
      {
        id: '4',
        name: 'David Kim',
        title: 'DevOps Engineer',
        location: 'Seattle, WA',
        experience: '6 years',
        skills: ['Kubernetes', 'AWS', 'Terraform', 'Python'],
        matchScore: 90,
        availability: 'Immediate',
        email: 'david.k@email.com',
        phone: '+1 (555) 456-7890',
        education: 'BS Information Systems, UW',
        appliedJobs: 4
      }
    ])
  }

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/20'
    if (score >= 80) return 'text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/20'
    if (score >= 70) return 'text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-900/20'
    return 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/20'
  }

  const filteredCandidates = candidates
    .filter(c => 
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.skills.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()))
    )
    .sort((a, b) => {
      if (sortBy === 'match') return b.matchScore - a.matchScore
      if (sortBy === 'experience') return parseInt(b.experience) - parseInt(a.experience)
      return 0
    })

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Candidate Pool</h1>
          <p className="text-gray-600 dark:text-gray-300">Browse and connect with talented candidates</p>
        </div>

        {/* Search & Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search candidates by name, title, or skills..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="match">Best Match</option>
                <option value="experience">Most Experience</option>
                <option value="recent">Most Recent</option>
              </select>
              
              <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2 text-gray-700 dark:text-gray-300">
                <FunnelIcon className="w-5 h-5" />
                Filters
              </button>
            </div>
          </div>
        </div>

        {/* Candidates Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredCandidates.map((candidate, index) => (
            <motion.div
              key={candidate.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-xl font-bold">
                    {candidate.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{candidate.name}</h3>
                    <p className="text-gray-600 dark:text-gray-300">{candidate.title}</p>
                  </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-bold ${getMatchScoreColor(candidate.matchScore)}`}>
                  {candidate.matchScore}% Match
                </div>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                  <MapPinIcon className="w-4 h-4 mr-2" />
                  {candidate.location}
                </div>
                <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                  <BriefcaseIcon className="w-4 h-4 mr-2" />
                  {candidate.experience} experience • {candidate.availability}
                </div>
                <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                  <AcademicCapIcon className="w-4 h-4 mr-2" />
                  {candidate.education}
                </div>
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                {candidate.skills.map((skill) => (
                  <span
                    key={skill}
                    className="px-3 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-sm rounded-full"
                  >
                    {skill}
                  </span>
                ))}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex gap-2">
                  <button className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                    <EnvelopeIcon className="w-5 h-5" />
                  </button>
                  <button className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                    <PhoneIcon className="w-5 h-5" />
                  </button>
                  <button className="p-2 text-yellow-600 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 rounded-lg transition-colors">
                    <StarIcon className="w-5 h-5" />
                  </button>
                </div>
                <button
                  onClick={() => router.push(`/dashboard/candidates/${candidate.id}`)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  View Profile
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
