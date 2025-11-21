'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useState } from 'react'
import { 
  ClockIcon, 
  StarIcon, 
  PlayIcon,
  CheckCircleIcon,
  TrophyIcon
} from '@heroicons/react/24/outline'

export default function AssessmentsPage() {
  const [selectedCategory, setSelectedCategory] = useState('all')

  const assessments = [
    {
      id: 'external',
      title: 'Professional Assessments',
      description: 'Take industry-standard tests from HackerRank, CodeSignal, TestGorilla & Pluralsight',
      duration: 0,
      questions: 0,
      difficulty: 'All Levels',
      category: 'external',
      completed: false,
      score: null,
      icon: 'GA',
      isExternal: true
    },
    {
      id: '1',
      title: 'JavaScript Fundamentals',
      description: 'Test your knowledge of JavaScript basics, ES6+, and modern features',
      duration: 30,
      questions: 25,
      difficulty: 'Intermediate',
      category: 'programming',
      completed: true,
      score: 92,
      icon: 'JS'
    },
    {
      id: '2',
      title: 'React Development',
      description: 'Assess your React skills including hooks, state management, and best practices',
      duration: 45,
      questions: 30,
      difficulty: 'Advanced',
      category: 'programming',
      completed: false,
      score: null,
      icon: 'RC'
    },
    {
      id: '3',
      title: 'System Design',
      description: 'Evaluate your ability to design scalable systems and architectures',
      duration: 60,
      questions: 15,
      difficulty: 'Expert',
      category: 'design',
      completed: false,
      score: null,
      icon: 'SD'
    },
    {
      id: '4',
      title: 'Problem Solving',
      description: 'Test your analytical thinking and problem-solving capabilities',
      duration: 40,
      questions: 20,
      difficulty: 'Intermediate',
      category: 'cognitive',
      completed: true,
      score: 87,
      icon: 'PS'
    },
    {
      id: '5',
      title: 'Communication Skills',
      description: 'Assess your written and verbal communication abilities',
      duration: 25,
      questions: 18,
      difficulty: 'Beginner',
      category: 'soft-skills',
      completed: false,
      score: null,
      icon: 'CS'
    }
  ]

  const categories = [
    { id: 'all', label: 'All Assessments' },
    { id: 'programming', label: 'Programming' },
    { id: 'design', label: 'System Design' },
    { id: 'cognitive', label: 'Cognitive' },
    { id: 'soft-skills', label: 'Soft Skills' }
  ]

  const filteredAssessments = selectedCategory === 'all' 
    ? assessments 
    : assessments.filter(assessment => assessment.category === selectedCategory)

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner': return 'text-green-600 bg-green-100'
      case 'Intermediate': return 'text-yellow-600 bg-yellow-100'
      case 'Advanced': return 'text-orange-600 bg-orange-100'
      case 'Expert': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 80) return 'text-blue-600'
    if (score >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Skill Assessments
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Showcase your abilities and get matched with the right opportunities
          </p>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          <div className="bg-white rounded-xl p-6 text-center shadow-lg">
            <TrophyIcon className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">2</div>
            <div className="text-gray-600">Completed</div>
          </div>
          <div className="bg-white rounded-xl p-6 text-center shadow-lg">
            <StarIcon className="w-8 h-8 text-blue-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">89.5%</div>
            <div className="text-gray-600">Average Score</div>
          </div>
          <div className="bg-white rounded-xl p-6 text-center shadow-lg">
            <ClockIcon className="w-8 h-8 text-green-500 mx-auto mb-2" />
            <div className="text-2xl font-bold text-gray-900">3</div>
            <div className="text-gray-600">Available</div>
          </div>
        </motion.div>

        {/* Category Filter */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex flex-wrap gap-2 mb-8 justify-center"
        >
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedCategory === category.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {category.label}
            </button>
          ))}
        </motion.div>

        {/* Assessment Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAssessments.map((assessment, index) => (
            <motion.div
              key={assessment.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
              className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                {assessment.icon}
              </div>
                {assessment.completed && (
                  <CheckCircleIcon className="w-6 h-6 text-green-500" />
                )}
              </div>
              
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {assessment.title}
              </h3>
              
              <p className="text-gray-600 mb-4 text-sm">
                {assessment.description}
              </p>
              
              <div className="flex items-center gap-4 mb-4 text-sm text-gray-500">
                <div className="flex items-center gap-1">
                  <ClockIcon className="w-4 h-4" />
                  <span>{assessment.duration} min</span>
                </div>
                <div>
                  {assessment.questions} questions
                </div>
              </div>
              
              <div className="flex items-center justify-between mb-4">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(assessment.difficulty)}`}>
                  {assessment.difficulty}
                </span>
                {assessment.completed && assessment.score && (
                  <span className={`font-semibold ${getScoreColor(assessment.score)}`}>
                    Score: {assessment.score}%
                  </span>
                )}
              </div>
              
              <div className="flex gap-2">
                {assessment.completed ? (
                  <>
                    <Link
                      href={`/assessments/${assessment.id}/results`}
                      className="flex-1 px-4 py-2 text-center text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                    >
                      View Results
                    </Link>
                    <button className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
                      Retake
                    </button>
                  </>
                ) : (
                  <Link
                    href={`/assessments/${assessment.id}/start`}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <PlayIcon className="w-4 h-4" />
                    Start Assessment
                  </Link>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="text-center mt-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 text-white"
        >
          <h2 className="text-2xl font-bold mb-4">
            Complete More Assessments
          </h2>
          <p className="text-lg mb-6 opacity-90">
            The more assessments you complete, the better we can match you with relevant opportunities
          </p>
          <button className="px-8 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-gray-100 transition-colors">
            Browse All Assessments
          </button>
        </motion.div>
      </div>
    </div>
  )
}