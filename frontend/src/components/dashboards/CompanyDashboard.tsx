'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import {
  BriefcaseIcon,
  UserGroupIcon,
  ChartBarIcon,
  ClockIcon,
  EyeIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlusIcon,
  UsersIcon,
  FunnelIcon,
  DocumentDuplicateIcon,
  BellAlertIcon
} from '@heroicons/react/24/outline';
import DashboardCard from './DashboardCard';
import StatsCard from './StatsCard';
import ChartCard from './ChartCard';
import NotificationCenter from './NotificationCenter';
import { CandidateInsightsCard } from './CandidateInsightsCard';
import PredictiveAnalytics from '../advanced/PredictiveAnalytics';
import CollaborativeHiring from '../advanced/CollaborativeHiring';
import { 
  CompanyAnalytics, 
  Notification, 
  ChartData 
} from '../../types/dashboard';

interface CompanyDashboardProps {
  companyId: string;
}

interface JobPosting {
  id: string;
  title: string;
  status: 'active' | 'paused' | 'filled' | 'expired';
  applications: number;
  views: number;
  postedDate: Date;
  location: string;
}

interface CandidateApplication {
  id: string;
  candidateName: string;
  jobTitle: string;
  status: 'pending' | 'reviewing' | 'shortlisted' | 'interviewed' | 'offered' | 'rejected';
  matchScore: number;
  appliedDate: Date;
  avatar?: string;
}

const CompanyDashboard: React.FC<CompanyDashboardProps> = ({ companyId }) => {
  const router = useRouter();
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState<CompanyAnalytics | null>(null);
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([]);
  const [recentApplications, setRecentApplications] = useState<CandidateApplication[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [hiringFunnelData, setHiringFunnelData] = useState<ChartData>({ labels: [], datasets: [] });
  const [applicationTrendsData, setApplicationTrendsData] = useState<ChartData>({ labels: [], datasets: [] });
  const [skillsInDemandData, setSkillsInDemandData] = useState<ChartData>({ labels: [], datasets: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, [companyId]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('accessToken');
      
      // Try to fetch real data, fall back to demo data
      try {
        const analyticsResponse = await fetch(`${API_URL}/api/dashboard/company/analytics`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (analyticsResponse.ok) {
          const data = await analyticsResponse.json();
          setAnalytics(data.analytics);
        } else {
          throw new Error('API not available');
        }
      } catch (apiError) {
        // Use demo data
        console.log('Using demo data for company dashboard');
        setAnalytics({
          totalJobs: 8,
          activeJobs: 5,
          totalApplications: 156,
          newApplications: 23,
          shortlistedCandidates: 18,
          interviewsScheduled: 12,
          offersExtended: 4,
          hiredCandidates: 2,
          averageTimeToHire: 21,
          applicationResponseRate: 68
        });
      }

      // Demo job postings
      setJobPostings([
        {
          id: '1',
          title: 'Senior Frontend Developer',
          status: 'active',
          applications: 45,
          views: 234,
          postedDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
          location: 'San Francisco, CA'
        },
        {
          id: '2',
          title: 'Full Stack Engineer',
          status: 'active',
          applications: 38,
          views: 189,
          postedDate: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),
          location: 'Remote'
        },
        {
          id: '3',
          title: 'Product Manager',
          status: 'active',
          applications: 52,
          views: 312,
          postedDate: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000),
          location: 'New York, NY'
        },
        {
          id: '4',
          title: 'UX Designer',
          status: 'filled',
          applications: 28,
          views: 156,
          postedDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
          location: 'Austin, TX'
        },
        {
          id: '5',
          title: 'DevOps Engineer',
          status: 'paused',
          applications: 21,
          views: 98,
          postedDate: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
          location: 'Seattle, WA'
        }
      ]);

      // Demo recent applications
      setRecentApplications([
        {
          id: '1',
          candidateName: 'Sarah Johnson',
          jobTitle: 'Senior Frontend Developer',
          status: 'shortlisted',
          matchScore: 95,
          appliedDate: new Date(Date.now() - 2 * 60 * 60 * 1000)
        },
        {
          id: '2',
          candidateName: 'Michael Chen',
          jobTitle: 'Full Stack Engineer',
          status: 'reviewing',
          matchScore: 88,
          appliedDate: new Date(Date.now() - 5 * 60 * 60 * 1000)
        },
        {
          id: '3',
          candidateName: 'Emily Rodriguez',
          jobTitle: 'Product Manager',
          status: 'interviewed',
          matchScore: 92,
          appliedDate: new Date(Date.now() - 24 * 60 * 60 * 1000)
        },
        {
          id: '4',
          candidateName: 'David Kim',
          jobTitle: 'Senior Frontend Developer',
          status: 'pending',
          matchScore: 85,
          appliedDate: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
        },
        {
          id: '5',
          candidateName: 'Jessica Taylor',
          jobTitle: 'UX Designer',
          status: 'offered',
          matchScore: 94,
          appliedDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        }
      ]);

      // Demo notifications
      setNotifications([
        {
          id: '1',
          type: 'application',
          title: 'New Application',
          message: 'Sarah Johnson applied for Senior Frontend Developer',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
          read: false
        },
        {
          id: '2',
          type: 'interview',
          title: 'Interview Scheduled',
          message: 'Interview with Emily Rodriguez scheduled for tomorrow',
          timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000),
          read: false
        },
        {
          id: '3',
          type: 'offer',
          title: 'Offer Accepted',
          message: 'Jessica Taylor accepted your offer',
          timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
          read: true
        }
      ]);

      // Demo hiring funnel data
      setHiringFunnelData({
        labels: ['Applied', 'Screening', 'Interview', 'Offer', 'Hired'],
        datasets: [{
          label: 'Candidates',
          data: [156, 45, 18, 8, 2],
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
      setApplicationTrendsData({
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Applications Received',
          data: [45, 52, 48, 65, 58, 72],
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4
        }]
      });

      // Demo skills in demand
      setSkillsInDemandData({
        labels: ['React', 'Node.js', 'Python', 'AWS', 'TypeScript'],
        datasets: [{
          label: 'Job Postings',
          data: [8, 6, 5, 7, 9],
          backgroundColor: 'rgba(59, 130, 246, 0.8)'
        }]
      });

    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // Set demo data even on error
      setAnalytics({
        totalJobs: 8,
        activeJobs: 5,
        totalApplications: 156,
        newApplications: 23,
        shortlistedCandidates: 18,
        interviewsScheduled: 12,
        offersExtended: 4,
        hiredCandidates: 2,
        averageTimeToHire: 21,
        applicationResponseRate: 68
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-700 dark:text-green-400 bg-green-100 dark:bg-green-500/20 border border-green-200 dark:border-green-500/30';
      case 'filled':
        return 'text-blue-700 dark:text-blue-400 bg-blue-100 dark:bg-blue-500/20 border border-blue-200 dark:border-blue-500/30';
      case 'paused':
        return 'text-yellow-700 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-500/20 border border-yellow-200 dark:border-yellow-500/30';
      case 'expired':
        return 'text-red-700 dark:text-red-400 bg-red-100 dark:bg-red-500/20 border border-red-200 dark:border-red-500/30';
      case 'shortlisted':
        return 'text-purple-700 dark:text-purple-400 bg-purple-100 dark:bg-purple-500/20 border border-purple-200 dark:border-purple-500/30';
      case 'interviewed':
        return 'text-indigo-700 dark:text-indigo-400 bg-indigo-100 dark:bg-indigo-500/20 border border-indigo-200 dark:border-indigo-500/30';
      case 'reviewing':
        return 'text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-500/20 border border-amber-200 dark:border-amber-500/30';
      default:
        return 'text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-gray-500/20 border border-gray-200 dark:border-gray-500/30';
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 dark:text-green-400';
    if (score >= 80) return 'text-blue-600 dark:text-blue-400';
    if (score >= 70) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#1a1f2e] p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Welcome back, {user?.firstName || 'there'}!
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your hiring pipeline and track performance</p>
          </div>
          <div className="flex items-center space-x-3">
            <NotificationCenter
              notifications={notifications}
              onMarkAsRead={handleMarkAsRead}
              onMarkAllAsRead={handleMarkAllAsRead}
              onDismiss={handleDismissNotification}
            />
            <button 
              onClick={() => router.push('/dashboard/jobs/new')}
              className="flex items-center space-x-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-500 dark:to-blue-600 text-white rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-200"
            >
              <PlusIcon className="w-5 h-5" />
              <span className="font-medium">Post Job</span>
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Active Jobs"
            value={analytics?.jobPostings.active || 0}
            icon={<BriefcaseIcon className="w-6 h-6" />}
            color="blue"
            change={{ value: 12, type: 'increase', period: 'this month' }}
            loading={loading}
          />
          <StatsCard
            title="Total Applications"
            value={analytics?.applications.total || 0}
            icon={<UserGroupIcon className="w-6 h-6" />}
            color="green"
            change={{ value: 8, type: 'increase', period: 'this week' }}
            loading={loading}
          />
          <StatsCard
            title="Avg. Time to Hire"
            value={`${analytics?.performance.averageTimeToHire || 0} days`}
            icon={<ClockIcon className="w-6 h-6" />}
            color="yellow"
            change={{ value: 15, type: 'decrease', period: 'last quarter' }}
            loading={loading}
          />
          <StatsCard
            title="Candidates Hired"
            value={analytics?.applications.hired || 0}
            icon={<CheckCircleIcon className="w-6 h-6" />}
            color="purple"
            change={{ value: 25, type: 'increase', period: 'this quarter' }}
            loading={loading}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* Job Postings */}
            <DashboardCard
              title="Active Job Postings"
              actions={
                <button 
                  onClick={() => router.push('/dashboard/jobs')}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Manage All
                </button>
              }
            >
              <div className="space-y-4">
                {jobPostings.map((job) => (
                  <motion.div
                    key={job.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white dark:bg-[#252d3d] border border-gray-200 dark:border-[#3a4556] rounded-xl p-5 hover:shadow-lg hover:border-blue-400 dark:hover:border-blue-500 transition-all duration-200"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 dark:text-white text-lg mb-1">{job.title}</h4>
                        <p className="text-gray-600 dark:text-gray-400 text-sm flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                          {job.location}
                        </p>
                      </div>
                      <span className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wide ${getStatusColor(job.status)}`}>
                        {job.status}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4 mb-4 p-3 bg-gray-50 dark:bg-[#1e2533] rounded-lg">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{job.applications}</div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Applications</div>
                      </div>
                      <div className="text-center border-x border-gray-200 dark:border-[#3a4556]">
                        <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">{job.views}</div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Views</div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm font-semibold text-gray-900 dark:text-white">{job.postedDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Posted</div>
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center pt-3 border-t border-gray-200 dark:border-[#3a4556]">
                      <div className="flex space-x-3">
                        <button 
                          onClick={() => router.push(`/dashboard/jobs/${job.id}/applications`)}
                          className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                        >
                          View Applications
                        </button>
                        <button 
                          onClick={() => router.push(`/dashboard/jobs/${job.id}/edit`)}
                          className="text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
                        >
                          Edit
                        </button>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="text-sm font-semibold text-green-600 dark:text-green-400">
                          {((job.applications / job.views) * 100).toFixed(1)}%
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-500">conversion</div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </DashboardCard>

            {/* Application Trends */}
            <ChartCard
              title="Application Trends"
              data={applicationTrendsData}
              type="line"
              height={250}
              description="Monthly application volume over the past 6 months"
              loading={loading}
            />

            {/* Recent Applications */}
            <DashboardCard
              title="Recent Applications"
              actions={
                <button 
                  onClick={() => router.push('/dashboard/applications')}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  View All
                </button>
              }
            >
              <div className="space-y-4">
                {recentApplications.map((application) => (
                  <motion.div
                    key={application.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex items-center justify-between p-4 bg-white dark:bg-[#252d3d] border border-gray-200 dark:border-[#3a4556] rounded-xl hover:shadow-md hover:border-blue-400 dark:hover:border-blue-500 transition-all duration-200"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-md">
                        <span className="text-sm font-bold text-white">
                          {application.candidateName.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white">{application.candidateName}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{application.jobTitle}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className={`text-sm font-bold ${getMatchScoreColor(application.matchScore)}`}>
                          {application.matchScore}% match
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-500">
                          {application.appliedDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </div>
                      </div>
                      <span className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wide ${getStatusColor(application.status)}`}>
                        {application.status}
                      </span>
                      <button 
                        onClick={() => router.push(`/dashboard/candidates/${application.id}`)}
                        className="px-4 py-2 bg-blue-600 dark:bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors"
                      >
                        Review
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </DashboardCard>

            {/* Quick Actions - Expanded Grid */}
            <DashboardCard title="Quick Actions">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button 
                  onClick={() => router.push('/dashboard/jobs/new')}
                  className="flex flex-col items-center justify-center p-6 text-center bg-blue-50 dark:bg-blue-500/20 hover:bg-blue-100 dark:hover:bg-blue-500/30 rounded-xl transition-all duration-200 border border-blue-200 dark:border-blue-500/40 hover:scale-105 hover:shadow-lg"
                >
                  <div className="w-16 h-16 bg-blue-600 dark:bg-blue-500 rounded-2xl flex items-center justify-center shadow-lg mb-4">
                    <PlusIcon className="w-8 h-8 text-white" />
                  </div>
                  <span className="text-gray-900 dark:text-white font-bold text-lg mb-1">Post New Job</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400">Create job posting</span>
                </button>

                <button 
                  onClick={() => router.push('/dashboard/candidates')}
                  className="flex flex-col items-center justify-center p-6 text-center bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 hover:from-indigo-100 hover:to-purple-100 dark:hover:from-indigo-900/30 dark:hover:to-purple-900/30 rounded-xl transition-all duration-200 border border-indigo-200 dark:border-indigo-800 hover:scale-105 hover:shadow-lg"
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-lg mb-4">
                    <FunnelIcon className="w-8 h-8 text-white" />
                  </div>
                  <span className="text-gray-900 dark:text-white font-bold text-lg mb-1">Candidate Pipeline</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400">Manage hiring stages</span>
                </button>

                <button 
                  onClick={() => router.push('/dashboard/settings')}
                  className="flex flex-col items-center justify-center p-6 text-center bg-gradient-to-br from-cyan-50 to-blue-50 dark:from-cyan-900/20 dark:to-blue-900/20 hover:from-cyan-100 hover:to-blue-100 dark:hover:from-cyan-900/30 dark:hover:to-blue-900/30 rounded-xl transition-all duration-200 border border-cyan-200 dark:border-cyan-800 hover:scale-105 hover:shadow-lg"
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-2xl flex items-center justify-center shadow-lg mb-4">
                    <UsersIcon className="w-8 h-8 text-white" />
                  </div>
                  <span className="text-gray-900 dark:text-white font-bold text-lg mb-1">Team Management</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400">Manage hiring team</span>
                </button>

                <button 
                  onClick={() => router.push('/dashboard/messages')}
                  className="flex flex-col items-center justify-center p-6 text-center bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 hover:from-orange-100 hover:to-red-100 dark:hover:from-orange-900/30 dark:hover:to-red-900/30 rounded-xl transition-all duration-200 border border-orange-200 dark:border-orange-800 hover:scale-105 hover:shadow-lg"
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl flex items-center justify-center shadow-lg mb-4">
                    <BellAlertIcon className="w-8 h-8 text-white" />
                  </div>
                  <span className="text-gray-900 dark:text-white font-bold text-lg mb-1">Bulk Actions</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400">Send bulk messages</span>
                </button>

                <button 
                  onClick={() => router.push('/dashboard/applications')}
                  className="flex flex-col items-center justify-center p-6 text-center bg-green-50 dark:bg-green-500/20 hover:bg-green-100 dark:hover:bg-green-500/30 rounded-xl transition-all duration-200 border border-green-200 dark:border-green-500/40 hover:scale-105 hover:shadow-lg"
                >
                  <div className="w-16 h-16 bg-green-600 dark:bg-green-500 rounded-2xl flex items-center justify-center shadow-lg mb-4">
                    <UserGroupIcon className="w-8 h-8 text-white" />
                  </div>
                  <span className="text-gray-900 dark:text-white font-bold text-lg mb-1">Review Applications</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400">View candidates</span>
                </button>

                <button 
                  onClick={() => router.push('/dashboard/analytics')}
                  className="flex flex-col items-center justify-center p-6 text-center bg-purple-50 dark:bg-purple-500/20 hover:bg-purple-100 dark:hover:bg-purple-500/30 rounded-xl transition-all duration-200 border border-purple-200 dark:border-purple-500/40 hover:scale-105 hover:shadow-lg"
                >
                  <div className="w-16 h-16 bg-purple-600 dark:bg-purple-500 rounded-2xl flex items-center justify-center shadow-lg mb-4">
                    <ChartBarIcon className="w-8 h-8 text-white" />
                  </div>
                  <span className="text-gray-900 dark:text-white font-bold text-lg mb-1">View Analytics</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400">Track metrics</span>
                </button>

                <button 
                  onClick={() => router.push('/dashboard/interviews')}
                  className="flex flex-col items-center justify-center p-6 text-center bg-amber-50 dark:bg-amber-500/20 hover:bg-amber-100 dark:hover:bg-amber-500/30 rounded-xl transition-all duration-200 border border-amber-200 dark:border-amber-500/40 hover:scale-105 hover:shadow-lg"
                >
                  <div className="w-16 h-16 bg-amber-600 dark:bg-amber-500 rounded-2xl flex items-center justify-center shadow-lg mb-4">
                    <ClockIcon className="w-8 h-8 text-white" />
                  </div>
                  <span className="text-gray-900 dark:text-white font-bold text-lg mb-1">Schedule Interviews</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400">Book time slots</span>
                </button>
              </div>
            </DashboardCard>
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            {/* Phase 1: Candidate AI Insights */}
            <CandidateInsightsCard />

            {/* Hiring Funnel */}
            <ChartCard
              title="Hiring Funnel"
              data={hiringFunnelData}
              type="bar"
              height={300}
              description="Current hiring pipeline breakdown"
              loading={loading}
            />

            {/* Skills in Demand */}
            <ChartCard
              title="Top Skills in Demand"
              data={skillsInDemandData}
              type="doughnut"
              height={250}
              description="Most requested skills in your job postings"
              loading={loading}
            />

            {/* Performance Metrics */}
            <DashboardCard title="Performance Metrics">
              <div className="space-y-3">
                <div className="flex justify-between items-center p-4 bg-blue-50 dark:bg-blue-500/20 rounded-lg border border-blue-200 dark:border-blue-500/40">
                  <span className="text-gray-700 dark:text-white font-medium">Application Rate</span>
                  <span className="font-bold text-blue-600 dark:text-blue-300 text-lg">{analytics?.performance.applicationRate}%</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-green-50 dark:bg-green-500/20 rounded-lg border border-green-200 dark:border-green-500/40">
                  <span className="text-gray-700 dark:text-white font-medium">Interview to Hire</span>
                  <span className="font-bold text-green-600 dark:text-green-300 text-lg">{analytics?.performance.interviewToHireRatio}</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-purple-50 dark:bg-purple-500/20 rounded-lg border border-purple-200 dark:border-purple-500/40">
                  <span className="text-gray-700 dark:text-white font-medium">Avg. Candidate Score</span>
                  <span className="font-bold text-purple-600 dark:text-purple-300 text-lg">{analytics?.candidates.averageScore}%</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-amber-50 dark:bg-amber-500/20 rounded-lg border border-amber-200 dark:border-amber-500/40">
                  <span className="text-gray-700 dark:text-white font-medium">Profile Views</span>
                  <span className="font-bold text-amber-600 dark:text-amber-300 text-lg">{analytics?.candidates.totalViewed}</span>
                </div>
              </div>
            </DashboardCard>
          </div>
        </div>

        {/* NEW: Advanced Features Section */}
        <div className="mt-8 space-y-8">
          {/* Predictive Analytics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <PredictiveAnalytics />
          </motion.div>

          {/* Collaborative Hiring */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <CollaborativeHiring />
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default CompanyDashboard;