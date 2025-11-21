'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  UserGroupIcon,
  BriefcaseIcon,
  EyeIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import ChartCard from '@/components/dashboards/ChartCard'
import StatsCard from '@/components/dashboards/StatsCard'
import { ChartData } from '@/types/dashboard'

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d')
  const [loading, setLoading] = useState(true)
  const [applicationTrends, setApplicationTrends] = useState<ChartData>({ labels: [], datasets: [] })
  const [skillsAnalysis, setSkillsAnalysis] = useState<ChartData>({ labels: [], datasets: [] })
  const [conversionFunnel, setConversionFunnel] = useState<ChartData>({ labels: [], datasets: [] })
  const [timeToHire, setTimeToHire] = useState<ChartData>({ labels: [], datasets: [] })

  useEffect(() => {
    loadAnalytics()
  }, [timeRange])

  const loadAnalytics = async () => {
    try {
      setLoading(true)
      
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${API_URL}/api/dashboard/analytics?timeRange=${timeRange}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) throw new Error('Failed to fetch analytics')
      
      const data = await response.json()
      setApplicationTrends(data.applicationTrends || { labels: [], datasets: [] })
      setSkillsAnalysis(data.skillsAnalysis || { labels: [], datasets: [] })
      setConversionFunnel(data.conversionFunnel || { labels: [], datasets: [] })
      setTimeToHire(data.timeToHire || { labels: [], datasets: [] })
    } catch (error) {
      console.error('Error loading analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Analytics</h1>
            <p className="text-gray-600 dark:text-gray-300 mt-1">Track your hiring performance</p>
          </div>
          
          <div className="flex gap-2">
            {(['7d', '30d', '90d', '1y'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  timeRange === range
                    ? 'bg-blue-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : range === '90d' ? '90 Days' : '1 Year'}
              </button>
            ))}
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Applications"
            value={234}
            icon={<UserGroupIcon className="w-6 h-6" />}
            color="blue"
            change={{ value: 12, type: 'increase', period: 'vs last period' }}
            loading={loading}
          />
          <StatsCard
            title="Active Jobs"
            value={15}
            icon={<BriefcaseIcon className="w-6 h-6" />}
            color="green"
            change={{ value: 3, type: 'increase', period: 'vs last period' }}
            loading={loading}
          />
          <StatsCard
            title="Profile Views"
            value={1250}
            icon={<EyeIcon className="w-6 h-6" />}
            color="purple"
            change={{ value: 8, type: 'increase', period: 'vs last period' }}
            loading={loading}
          />
          <StatsCard
            title="Avg. Time to Hire"
            value="16 days"
            icon={<ClockIcon className="w-6 h-6" />}
            color="yellow"
            change={{ value: 20, type: 'decrease', period: 'vs last period' }}
            loading={loading}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <ChartCard
            title="Application & Interview Trends"
            data={applicationTrends}
            type="line"
            height={300}
            description="Track application volume and interview activity"
            loading={loading}
          />

          <ChartCard
            title="Conversion Funnel"
            data={conversionFunnel}
            type="bar"
            height={300}
            description="Candidate progression through hiring stages"
            loading={loading}
          />

          <ChartCard
            title="Skills in Demand"
            data={skillsAnalysis}
            type="doughnut"
            height={300}
            description="Most requested skills across job postings"
            loading={loading}
          />

          <ChartCard
            title="Time to Hire Trend"
            data={timeToHire}
            type="line"
            height={300}
            description="Average days from application to hire"
            loading={loading}
          />
        </div>

        {/* Detailed Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top Performing Jobs</h3>
            <div className="space-y-3">
              {[
                { title: 'Senior Frontend Developer', applications: 45, conversion: 12.5 },
                { title: 'Backend Engineer', applications: 38, conversion: 10.2 },
                { title: 'DevOps Engineer', applications: 32, conversion: 9.8 }
              ].map((job, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{job.title}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{job.applications} applications</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-green-600 dark:text-green-400">{job.conversion}%</p>
                    <p className="text-xs text-gray-500">conversion</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Source Performance</h3>
            <div className="space-y-3">
              {[
                { source: 'Direct Apply', count: 89, percentage: 38 },
                { source: 'LinkedIn', count: 67, percentage: 29 },
                { source: 'Indeed', count: 45, percentage: 19 },
                { source: 'Referral', count: 33, percentage: 14 }
              ].map((source, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-700 dark:text-gray-300">{source.source}</span>
                    <span className="font-medium text-gray-900 dark:text-white">{source.count} ({source.percentage}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${source.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Key Insights</h3>
            <div className="space-y-4">
              <div className="flex items-start space-x-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <ArrowTrendingUpIcon className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">Application rate increased</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">12% more applications this month</p>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <ArrowTrendingUpIcon className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">Faster hiring process</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">20% reduction in time to hire</p>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <ArrowTrendingDownIcon className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">Lower conversion on mobile</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">Consider optimizing mobile experience</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
