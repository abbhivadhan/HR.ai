'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AnimatedCard from '../ui/AnimatedCard';
import { 
  SparklesIcon,
  VideoCameraIcon,
  DocumentTextIcon,
  CalendarIcon,
  ArrowTrendingUpIcon,
  TrophyIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface CandidateInsight {
  id: string;
  name: string;
  avatar?: string;
  hasCareerPlan: boolean;
  hasVideoPortfolio: boolean;
  hasOptimizedResume: boolean;
  schedulingEnabled: boolean;
  atsScore?: number;
  careerGoal?: string;
  portfolioViews?: number;
}

export function CandidateInsightsCard() {
  const router = useRouter();
  const [insights, setInsights] = useState<CandidateInsight[]>([]);
  const [stats, setStats] = useState({
    withCareerPlans: 0,
    withVideoPortfolios: 0,
    withOptimizedResumes: 0,
    avgATSScore: 0,
  });

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${API_URL}/api/dashboard/candidate-insights`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error('Failed to fetch insights');
      
      const data = await response.json();
      setInsights(data.insights || []);
      setStats(data.stats || {
        withCareerPlans: 0,
        withVideoPortfolios: 0,
        withOptimizedResumes: 0,
        avgATSScore: 0
      });
    } catch (error) {
      console.error('Error loading insights:', error);
      setInsights([]);
    }
  };

  return (
    <AnimatedCard className="p-6">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
            Candidate AI Insights
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Phase 1 feature adoption by candidates
          </p>
        </div>
        <SparklesIcon className="w-6 h-6 text-purple-600" />
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <ChartBarIcon className="w-5 h-5 text-purple-600" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Career Plans</span>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {stats.withCareerPlans}
          </div>
        </div>

        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <VideoCameraIcon className="w-5 h-5 text-blue-600" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Video Portfolios</span>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {stats.withVideoPortfolios}
          </div>
        </div>

        <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <DocumentTextIcon className="w-5 h-5 text-orange-600" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Optimized Resumes</span>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {stats.withOptimizedResumes}
          </div>
        </div>

        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <TrophyIcon className="w-5 h-5 text-green-600" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Avg ATS Score</span>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {stats.avgATSScore}%
          </div>
        </div>
      </div>

      {/* Candidate List */}
      <div className="space-y-3">
        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
          Top Candidates with AI Features
        </h4>
        {insights.map((candidate) => (
          <div
            key={candidate.id}
            className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => router.push(`/dashboard/candidates/${candidate.id}`)}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h5 className="font-semibold text-gray-900 dark:text-white">
                  {candidate.name}
                </h5>
                {candidate.careerGoal && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Goal: {candidate.careerGoal}
                  </p>
                )}
              </div>
              {candidate.atsScore && (
                <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded-full font-medium">
                  ATS: {candidate.atsScore}%
                </span>
              )}
            </div>

            <div className="flex flex-wrap gap-2">
              {candidate.hasCareerPlan && (
                <span className="flex items-center gap-1 px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 text-xs rounded">
                  <ChartBarIcon className="w-3 h-3" />
                  Career Plan
                </span>
              )}
              {candidate.hasVideoPortfolio && (
                <span className="flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded">
                  <VideoCameraIcon className="w-3 h-3" />
                  Video Portfolio
                </span>
              )}
              {candidate.hasOptimizedResume && (
                <span className="flex items-center gap-1 px-2 py-1 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 text-xs rounded">
                  <DocumentTextIcon className="w-3 h-3" />
                  Optimized Resume
                </span>
              )}
              {candidate.schedulingEnabled && (
                <span className="flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded">
                  <CalendarIcon className="w-3 h-3" />
                  Smart Scheduling
                </span>
              )}
            </div>

            {candidate.portfolioViews && (
              <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                Portfolio views: {candidate.portfolioViews}
              </div>
            )}
          </div>
        ))}
      </div>

      <button
        onClick={() => router.push('/dashboard/candidates')}
        className="w-full mt-4 py-2 text-sm text-purple-600 hover:text-purple-700 font-medium"
      >
        View All Candidates →
      </button>
    </AnimatedCard>
  );
}
