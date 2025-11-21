'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import {
  BriefcaseIcon,
  ChartBarIcon,
  ClockIcon,
  EyeIcon,
  StarIcon,
  TrophyIcon,
  UserIcon,
  DocumentTextIcon,
  GlobeAltIcon,
  SparklesIcon,
  VideoCameraIcon,
  CalendarIcon,
  AcademicCapIcon,
  CheckCircleIcon,
  XCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import DashboardCard from './DashboardCard';
import StatsCard from './StatsCard';
import ChartCard from './ChartCard';
import NotificationCenter from './NotificationCenter';
import ExternalAssessmentCard from './ExternalAssessmentCard';
import CareerInsights from '../advanced/CareerInsights';
import JobMatchIntelligence from '../advanced/JobMatchIntelligence';
import {
  DashboardStats,
  CandidateRecommendation,
  Notification,
  ChartData,
  TimeSeriesData
} from '../../types/dashboard';

interface CandidateDashboardProps {
  candidateId: string;
}

const CandidateDashboard: React.FC<CandidateDashboardProps> = ({ candidateId }) => {
  const router = useRouter();
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({});
  const [recommendations, setRecommendations] = useState<CandidateRecommendation[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [skillsData, setSkillsData] = useState<ChartData>({ labels: [], datasets: [] });
  const [applicationTrends, setApplicationTrends] = useState<ChartData>({ labels: [], datasets: [] });
  const [loading, setLoading] = useState(true);
  const [showProfileDetailsModal, setShowProfileDetailsModal] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, [candidateId]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Try to fetch actual data from API, but fall back to demo data
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('accessToken');
      
      try {
        const response = await fetch(`${API_URL}/api/dashboard/candidate/stats`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setStats(data.stats);
        } else {
          throw new Error('API not available');
        }
      } catch (apiError) {
        // Use demo data
        console.log('Using demo data for dashboard');
        setStats({
          totalApplications: 12,
          matchingJobs: 24,
          profileViews: 156,
          averageScore: 85
        });
      }

      // Demo recommendations
      setRecommendations([
        {
          id: '1',
          jobTitle: 'Senior Frontend Developer',
          companyName: 'TechCorp Inc.',
          matchScore: 95,
          skills: ['React', 'TypeScript', 'Next.js', 'Tailwind CSS'],
          location: 'San Francisco, CA',
          salaryRange: '$120k - $160k',
          postedDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
        },
        {
          id: '2',
          jobTitle: 'Full Stack Engineer',
          companyName: 'StartupXYZ',
          matchScore: 88,
          skills: ['Node.js', 'React', 'PostgreSQL', 'AWS'],
          location: 'Remote',
          salaryRange: '$100k - $140k',
          postedDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000)
        },
        {
          id: '3',
          jobTitle: 'React Developer',
          companyName: 'Digital Solutions Ltd',
          matchScore: 82,
          skills: ['React', 'JavaScript', 'Redux', 'CSS'],
          location: 'New York, NY',
          salaryRange: '$90k - $130k',
          postedDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        }
      ]);

      // Demo notifications
      setNotifications([
        {
          id: '1',
          type: 'application',
          title: 'Application Update',
          message: 'Your application for Senior Frontend Developer at TechCorp has been viewed',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
          read: false
        },
        {
          id: '2',
          type: 'match',
          title: 'New Job Match',
          message: '3 new jobs match your profile',
          timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000),
          read: false
        },
        {
          id: '3',
          type: 'profile',
          title: 'Profile View',
          message: 'Your profile was viewed by StartupXYZ',
          timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
          read: true
        }
      ]);

      // Demo skills data
      setSkillsData({
        labels: ['React', 'TypeScript', 'Node.js', 'CSS', 'Testing'],
        datasets: [{
          label: 'Skill Proficiency',
          data: [95, 88, 82, 90, 75],
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(139, 92, 246, 0.8)',
            'rgba(236, 72, 153, 0.8)'
          ]
        }]
      });

      // Demo application trends
      setApplicationTrends({
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Applications Sent',
          data: [5, 8, 12, 15, 18, 12],
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4
        }]
      });

    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // Even on error, set demo data
      setStats({
        totalApplications: 12,
        matchingJobs: 24,
        profileViews: 156,
        averageScore: 85
      });
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = (notificationId: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
    );
  };

  const handleMarkAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const handleDismissNotification = (notificationId: string) => {
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 80) return 'text-blue-600 bg-blue-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const handleApplyToJob = (jobId: string) => {
    // Navigate to job application page
    router.push(`/jobs/${jobId}/apply`);
  };

  const handleViewAllJobs = () => {
    router.push('/jobs');
  };

  const handleTakeAssessment = () => {
    router.push('/assessments');
  };

  const handleUpdateProfile = () => {
    router.push('/profile/edit');
  };

  const handleBrowseJobs = () => {
    router.push('/jobs/search');
  };

  const handleScheduleInterview = () => {
    router.push('/interviews/schedule');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Welcome back, {user?.firstName || 'there'}!
            </h1>
            <p className="text-gray-600 dark:text-gray-300 mt-1">Here's your job search progress</p>
          </div>
          <NotificationCenter
            notifications={notifications}
            onMarkAsRead={handleMarkAsRead}
            onMarkAllAsRead={handleMarkAllAsRead}
            onDismiss={handleDismissNotification}
          />
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Applications"
            value={stats.totalApplications || 0}
            icon={<BriefcaseIcon className="w-6 h-6" />}
            color="blue"
            change={{ value: 15, type: 'increase', period: 'last month' }}
            loading={loading}
          />
          <StatsCard
            title="Matching Jobs"
            value={stats.matchingJobs || 0}
            icon={<StarIcon className="w-6 h-6" />}
            color="green"
            change={{ value: 8, type: 'increase', period: 'this week' }}
            loading={loading}
          />
          <StatsCard
            title="Profile Views"
            value={stats.profileViews || 0}
            icon={<EyeIcon className="w-6 h-6" />}
            color="purple"
            change={{ value: 12, type: 'increase', period: 'this week' }}
            loading={loading}
          />
          <StatsCard
            title="Average Score"
            value={`${stats.averageScore || 0}%`}
            icon={<TrophyIcon className="w-6 h-6" />}
            color="yellow"
            change={{ value: 5, type: 'increase', period: 'last assessment' }}
            loading={loading}
          />
        </div>

        {/* AI Interview Feature Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 rounded-2xl p-8 text-white shadow-2xl"
        >
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-2xl font-bold">AI Video Interview</h2>
                  <p className="text-white/80">Practice with our AI interviewer</p>
                </div>
              </div>
              <p className="text-white/90 mb-6 max-w-2xl">
                Get instant feedback on your interview skills. Our AI analyzes your responses,
                communication style, and provides personalized recommendations to help you ace your next interview.
              </p>
              <div className="flex items-center space-x-6 text-sm">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>5 Interview Questions</span>
                </div>
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Real-time Analysis</span>
                </div>
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Instant Feedback</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => router.push(`/interviews/ai-video/demo-${Date.now()}`)}
              className="px-8 py-4 bg-white text-purple-600 font-bold rounded-xl hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl hover:scale-105 transform"
            >
              Start AI Interview
            </button>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* Job Recommendations */}
            <DashboardCard
              title="Recommended Jobs"
              actions={
                <button
                  onClick={handleViewAllJobs}
                  className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
                >
                  View All
                </button>
              }
            >
              <div className="space-y-4">
                {recommendations.map((job) => (
                  <motion.div
                    key={job.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white">{job.jobTitle}</h4>
                        <p className="text-gray-600 dark:text-gray-300">{job.companyName}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getMatchScoreColor(job.matchScore)}`}>
                        {job.matchScore}% match
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-2 mb-3">
                      {job.skills.map((skill) => (
                        <span
                          key={skill}
                          className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>

                    <div className="flex justify-between items-center text-sm text-gray-500 dark:text-gray-400">
                      <span>{job.location}</span>
                      <span>{job.salaryRange}</span>
                    </div>

                    <div className="flex justify-between items-center mt-3">
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        Posted {job.postedDate.toLocaleDateString()}
                      </span>
                      <button
                        onClick={() => handleApplyToJob(job.id)}
                        className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      >
                        Apply Now
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </DashboardCard>

            {/* Application Trends */}
            <ChartCard
              title="Application Activity"
              data={applicationTrends}
              type="line"
              height={250}
              description="Your job application activity over the past 6 months"
              loading={loading}
            />

            {/* Profile Strength - Expanded */}
            <DashboardCard title="Profile Strength">
              <div className="grid md:grid-cols-2 gap-6">
                {/* Left Side - Progress */}
                <div>
                  <div className="mb-6">
                    <div className="flex justify-between items-center mb-3">
                      <span className="text-lg font-semibold text-gray-700 dark:text-gray-300">Overall Completion</span>
                      <span className="text-2xl font-bold text-purple-600 dark:text-purple-400">0%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
                      <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 h-4 rounded-full transition-all duration-500 shadow-lg" style={{ width: '0%' }}></div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                      Complete your profile to increase visibility by up to 40%
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                      <div className="flex items-center space-x-3">
                        <CheckCircleIcon className="w-5 h-5 text-green-600" />
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Basic Information</span>
                      </div>
                      <span className="text-xs text-green-600 font-semibold px-2 py-1 bg-green-100 dark:bg-green-900 rounded">Complete</span>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                      <div className="flex items-center space-x-3">
                        <CheckCircleIcon className="w-5 h-5 text-green-600" />
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Work Experience</span>
                      </div>
                      <span className="text-xs text-green-600 font-semibold px-2 py-1 bg-green-100 dark:bg-green-900 rounded">Complete</span>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                      <div className="flex items-center space-x-3">
                        <ClockIcon className="w-5 h-5 text-yellow-600" />
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Skills & Certifications</span>
                      </div>
                      <span className="text-xs text-yellow-600 font-semibold px-2 py-1 bg-yellow-100 dark:bg-yellow-900 rounded">Add more</span>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                      <div className="flex items-center space-x-3">
                        <XCircleIcon className="w-5 h-5 text-gray-400" />
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Video Introduction</span>
                      </div>
                      <span className="text-xs text-gray-500 font-semibold px-2 py-1 bg-gray-200 dark:bg-gray-600 rounded">Missing</span>
                    </div>
                  </div>
                </div>

                {/* Right Side - Recommendations */}
                <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <SparklesIcon className="w-5 h-5 text-purple-600 mr-2" />
                    Quick Wins
                  </h4>
                  <div className="space-y-3">
                    <button
                      onClick={() => router.push('/portfolio')}
                      className="w-full text-left p-3 bg-white dark:bg-gray-800 rounded-lg hover:shadow-md transition-all border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex items-start space-x-3">
                        <VideoCameraIcon className="w-5 h-5 text-blue-600 mt-0.5" />
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">Add Video Introduction</p>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Stand out with a 60-second intro</p>
                          <span className="text-xs text-blue-600 font-medium mt-1 inline-block">+15% visibility</span>
                        </div>
                      </div>
                    </button>

                    <button
                      onClick={handleUpdateProfile}
                      className="w-full text-left p-3 bg-white dark:bg-gray-800 rounded-lg hover:shadow-md transition-all border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex items-start space-x-3">
                        <TrophyIcon className="w-5 h-5 text-yellow-600 mt-0.5" />
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">Add More Skills</p>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Showcase your expertise</p>
                          <span className="text-xs text-yellow-600 font-medium mt-1 inline-block">+10% matches</span>
                        </div>
                      </div>
                    </button>

                    <button
                      onClick={() => router.push('/resume')}
                      className="w-full text-left p-3 bg-white dark:bg-gray-800 rounded-lg hover:shadow-md transition-all border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex items-start space-x-3">
                        <DocumentTextIcon className="w-5 h-5 text-orange-600 mt-0.5" />
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">Optimize Resume</p>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Improve ATS score</p>
                          <span className="text-xs text-orange-600 font-medium mt-1 inline-block">+20% response</span>
                        </div>
                      </div>
                    </button>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex gap-3">
                <button
                  onClick={handleUpdateProfile}
                  className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all font-semibold shadow-lg hover:shadow-xl"
                >
                  Complete Profile Now
                </button>
                <button
                  onClick={() => setShowProfileDetailsModal(true)}
                  className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-all font-semibold"
                >
                  View Details
                </button>
              </div>
            </DashboardCard>

            {/* Profile Details Modal */}
            {showProfileDetailsModal && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={() => setShowProfileDetailsModal(false)}>
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  onClick={(e) => e.stopPropagation()}
                  className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
                >
                  <div className="p-6">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center">
                          <UserIcon className="w-6 h-6 text-purple-600" />
                        </div>
                        <div>
                          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Profile Strength Details</h2>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Complete your profile to stand out</p>
                        </div>
                      </div>
                      <button
                        onClick={() => setShowProfileDetailsModal(false)}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                      >
                        <XMarkIcon className="w-6 h-6 text-gray-500" />
                      </button>
                    </div>

                    {/* Overall Progress */}
                    <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-xl">
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-lg font-semibold text-gray-700 dark:text-gray-300">Overall Completion</span>
                        <span className="text-3xl font-bold text-purple-600 dark:text-purple-400">0%</span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                        <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 h-3 rounded-full transition-all duration-500" style={{ width: '0%' }}></div>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                        You're doing great! Complete the remaining sections to maximize your visibility.
                      </p>
                    </div>

                    {/* Detailed Breakdown */}
                    <div className="space-y-4">
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Section Breakdown</h3>

                      {/* Completed Sections */}
                      <div className="space-y-3">
                        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                          <div className="flex items-start justify-between">
                            <div className="flex items-start gap-3 flex-1">
                              <CheckCircleIcon className="w-6 h-6 text-green-600 mt-0.5" />
                              <div>
                                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Basic Information</h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Name, email, phone, location</p>
                                <div className="flex items-center gap-2">
                                  <div className="w-full bg-green-200 dark:bg-green-900 rounded-full h-2">
                                    <div className="bg-green-600 h-2 rounded-full" style={{ width: '100%' }}></div>
                                  </div>
                                  <span className="text-xs font-medium text-green-600">100%</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                          <div className="flex items-start justify-between">
                            <div className="flex items-start gap-3 flex-1">
                              <CheckCircleIcon className="w-6 h-6 text-green-600 mt-0.5" />
                              <div>
                                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Work Experience</h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">3 positions added</p>
                                <div className="flex items-center gap-2">
                                  <div className="w-full bg-green-200 dark:bg-green-900 rounded-full h-2">
                                    <div className="bg-green-600 h-2 rounded-full" style={{ width: '100%' }}></div>
                                  </div>
                                  <span className="text-xs font-medium text-green-600">100%</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Incomplete Sections */}
                        <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                          <div className="flex items-start justify-between">
                            <div className="flex items-start gap-3 flex-1">
                              <ClockIcon className="w-6 h-6 text-yellow-600 mt-0.5" />
                              <div>
                                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Skills & Certifications</h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Add 3 more skills to reach 100%</p>
                                <div className="flex items-center gap-2">
                                  <div className="w-full bg-yellow-200 dark:bg-yellow-900 rounded-full h-2">
                                    <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '60%' }}></div>
                                  </div>
                                  <span className="text-xs font-medium text-yellow-600">60%</span>
                                </div>
                                <button
                                  onClick={() => {
                                    setShowProfileDetailsModal(false);
                                    router.push('/profile/edit#skills');
                                  }}
                                  className="mt-2 text-sm text-yellow-600 hover:text-yellow-700 font-medium"
                                >
                                  Add Skills →
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                          <div className="flex items-start justify-between">
                            <div className="flex items-start gap-3 flex-1">
                              <XCircleIcon className="w-6 h-6 text-red-600 mt-0.5" />
                              <div>
                                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Video Introduction</h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Stand out with a 60-second video intro</p>
                                <div className="flex items-center gap-2">
                                  <div className="w-full bg-red-200 dark:bg-red-900 rounded-full h-2">
                                    <div className="bg-red-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                                  </div>
                                  <span className="text-xs font-medium text-red-600">0%</span>
                                </div>
                                <button
                                  onClick={() => {
                                    setShowProfileDetailsModal(false);
                                    router.push('/portfolio');
                                  }}
                                  className="mt-2 text-sm text-red-600 hover:text-red-700 font-medium"
                                >
                                  Record Video →
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Benefits */}
                    <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                        <SparklesIcon className="w-5 h-5 text-blue-600" />
                        Why Complete Your Profile?
                      </h3>
                      <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                        <li className="flex items-center gap-2">
                          <CheckCircleIcon className="w-4 h-4 text-blue-600" />
                          <span>40% more profile views from recruiters</span>
                        </li>
                        <li className="flex items-center gap-2">
                          <CheckCircleIcon className="w-4 h-4 text-blue-600" />
                          <span>Better job matching accuracy</span>
                        </li>
                        <li className="flex items-center gap-2">
                          <CheckCircleIcon className="w-4 h-4 text-blue-600" />
                          <span>Higher chance of interview invitations</span>
                        </li>
                        <li className="flex items-center gap-2">
                          <CheckCircleIcon className="w-4 h-4 text-blue-600" />
                          <span>Stand out from other candidates</span>
                        </li>
                      </ul>
                    </div>

                    {/* Action Buttons */}
                    <div className="mt-6 flex gap-3">
                      <button
                        onClick={() => {
                          setShowProfileDetailsModal(false);
                          router.push('/profile/edit');
                        }}
                        className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all font-semibold"
                      >
                        Complete Profile
                      </button>
                      <button
                        onClick={() => setShowProfileDetailsModal(false)}
                        className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-semibold"
                      >
                        Close
                      </button>
                    </div>
                  </div>
                </motion.div>
              </div>
            )}
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            {/* External Assessments Card */}
            <ExternalAssessmentCard />

            {/* Skill Assessment Scores */}
            <ChartCard
              title="Skill Scores"
              data={skillsData}
              type="doughnut"
              height={250}
              description="Your latest assessment scores by skill"
              loading={loading}
            />

            {/* AI-Powered Tools */}
            <DashboardCard title="AI-Powered Tools">
              <div className="space-y-2">
                {/* Career Coach */}
                <button
                  onClick={() => router.push('/career-coach')}
                  className="group w-full flex items-center justify-between p-3 rounded-lg hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                      <SparklesIcon className="w-5 h-5 text-purple-600" />
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-semibold text-gray-900 dark:text-white">Career Coach</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">AI career guidance</div>
                    </div>
                  </div>
                  <svg className="w-4 h-4 text-gray-400 group-hover:text-purple-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>

                {/* Resume Builder */}
                <button
                  onClick={() => router.push('/resume')}
                  className="group w-full flex items-center justify-between p-3 rounded-lg hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center justify-center">
                      <DocumentTextIcon className="w-5 h-5 text-orange-600" />
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-semibold text-gray-900 dark:text-white">Resume Builder</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">ATS-optimized</div>
                    </div>
                  </div>
                  <svg className="w-4 h-4 text-gray-400 group-hover:text-orange-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>

                {/* Smart Scheduling */}
                <button
                  onClick={() => router.push('/scheduling')}
                  className="group w-full flex items-center justify-between p-3 rounded-lg hover:bg-green-50 dark:hover:bg-green-900/20 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                      <CalendarIcon className="w-5 h-5 text-green-600" />
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-semibold text-gray-900 dark:text-white">Smart Scheduling</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">Manage calendar</div>
                    </div>
                  </div>
                  <svg className="w-4 h-4 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>

                {/* Video Portfolio */}
                <button
                  onClick={() => router.push('/portfolio')}
                  className="group w-full flex items-center justify-between p-3 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                      <VideoCameraIcon className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-semibold text-gray-900 dark:text-white">Video Portfolio</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">Showcase projects</div>
                    </div>
                  </div>
                  <svg className="w-4 h-4 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>

                {/* Skill Assessments */}
                <button
                  onClick={handleTakeAssessment}
                  className="group w-full flex items-center justify-between p-3 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex items-center justify-center">
                      <AcademicCapIcon className="w-5 h-5 text-indigo-600" />
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-semibold text-gray-900 dark:text-white">Skill Assessments</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">Test your skills</div>
                    </div>
                  </div>
                  <svg className="w-4 h-4 text-gray-400 group-hover:text-indigo-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>

                {/* Job Matching */}
                <button
                  onClick={handleBrowseJobs}
                  className="group w-full flex items-center justify-between p-3 rounded-lg hover:bg-pink-50 dark:hover:bg-pink-900/20 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-pink-100 dark:bg-pink-900/30 rounded-lg flex items-center justify-center">
                      <BriefcaseIcon className="w-5 h-5 text-pink-600" />
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-semibold text-gray-900 dark:text-white">Job Matching</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">Find perfect roles</div>
                    </div>
                  </div>
                  <svg className="w-4 h-4 text-gray-400 group-hover:text-pink-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </DashboardCard>

            {/* Quick Actions */}
            <DashboardCard title="Quick Actions">
              <div className="space-y-3">
                <button
                  onClick={handleTakeAssessment}
                  className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <AcademicCapIcon className="w-5 h-5 text-blue-600" />
                  <span className="text-gray-900 dark:text-white">Take Assessment</span>
                </button>
                <button
                  onClick={handleUpdateProfile}
                  className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <UserIcon className="w-5 h-5 text-green-600" />
                  <span className="text-gray-900 dark:text-white">Update Profile</span>
                </button>
                <button
                  onClick={handleBrowseJobs}
                  className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <BriefcaseIcon className="w-5 h-5 text-purple-600" />
                  <span className="text-gray-900 dark:text-white">Browse Jobs</span>
                </button>
              </div>
            </DashboardCard>

            {/* Recent Activity */}
            <DashboardCard title="Recent Activity">
              <div className="space-y-3">
                <div className="flex items-center space-x-3 text-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-gray-600 dark:text-gray-300">Completed JavaScript assessment</span>
                  <span className="text-gray-400">2h ago</span>
                </div>
                <div className="flex items-center space-x-3 text-sm">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-gray-600 dark:text-gray-300">Applied to Frontend Developer role</span>
                  <span className="text-gray-400">1d ago</span>
                </div>
                <div className="flex items-center space-x-3 text-sm">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span className="text-gray-600 dark:text-gray-300">Profile viewed by TechCorp</span>
                  <span className="text-gray-400">2d ago</span>
                </div>
                <div className="flex items-center space-x-3 text-sm">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span className="text-gray-600 dark:text-gray-300">Updated work experience</span>
                  <span className="text-gray-400">3d ago</span>
                </div>
              </div>
            </DashboardCard>
          </div>
        </div>

        {/* NEW: Advanced Features Section */}
        <div className="mt-8 space-y-8">
          {/* AI Career Insights */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <CareerInsights />
          </motion.div>

          {/* Job Match Intelligence */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <JobMatchIntelligence />
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default CandidateDashboard;