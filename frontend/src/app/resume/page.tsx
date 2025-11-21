'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { resumeBuilderService } from '@/services/resumeBuilderService';
import { Resume } from '@/types/resume';
import AnimatedCard from '@/components/ui/AnimatedCard';
import { 
  DocumentTextIcon, 
  PlusIcon, 
  ArrowDownTrayIcon, 
  SparklesIcon,
  CheckCircleIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  StarIcon,
  ChartBarIcon,
  ClockIcon,
  DocumentDuplicateIcon
} from '@heroicons/react/24/outline';

export default function ResumePage() {
  const router = useRouter();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  useEffect(() => {
    loadResumes();
  }, []);

  const loadResumes = async () => {
    try {
      const data = await resumeBuilderService.getResumes();
      setResumes(data);
    } catch (error) {
      console.error('Failed to load resumes:', error);
    } finally {
      setLoading(false);
    }
  };

  const getATSScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100 dark:bg-green-900/30';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30';
    return 'text-red-600 bg-red-100 dark:bg-red-900/30';
  };

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen bg-gradient-to-br from-orange-50 via-pink-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-pink-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/30 rounded-xl flex items-center justify-center">
                  <DocumentTextIcon className="w-7 h-7 text-orange-600" />
                </div>
                <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
                  AI Resume Builder
                </h1>
              </div>
              <p className="text-gray-600 dark:text-gray-300 ml-15">
                Create ATS-optimized resumes with AI-powered suggestions
              </p>
            </div>
            <button
              onClick={() => router.push('/resume/builder')}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-600 to-pink-600 text-white rounded-xl hover:from-orange-700 hover:to-pink-700 transition-all shadow-lg hover:shadow-xl font-semibold"
            >
              <PlusIcon className="w-5 h-5" />
              Create Resume
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <AnimatedCard className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border-orange-200 dark:border-orange-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total Resumes</p>
                  <p className="text-2xl font-bold text-orange-600">{resumes.length}</p>
                </div>
                <DocumentTextIcon className="w-8 h-8 text-orange-600 opacity-50" />
              </div>
            </AnimatedCard>

            <AnimatedCard className="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Avg ATS Score</p>
                  <p className="text-2xl font-bold text-green-600">
                    {resumes.length > 0 
                      ? Math.round(resumes.reduce((acc, r) => acc + (r.ats_score || 0), 0) / resumes.length)
                      : 0}
                  </p>
                </div>
                <ChartBarIcon className="w-8 h-8 text-green-600 opacity-50" />
              </div>
            </AnimatedCard>

            <AnimatedCard className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Templates</p>
                  <p className="text-2xl font-bold text-blue-600">12+</p>
                </div>
                <DocumentDuplicateIcon className="w-8 h-8 text-blue-600 opacity-50" />
              </div>
            </AnimatedCard>

            <AnimatedCard className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">AI Powered</p>
                  <p className="text-2xl font-bold text-purple-600">100%</p>
                </div>
                <SparklesIcon className="w-8 h-8 text-purple-600 opacity-50" />
              </div>
            </AnimatedCard>
          </div>
        </motion.div>

        {/* View Toggle */}
        {resumes.length > 0 && (
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Your Resumes</h2>
              <span className="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm">
                {resumes.length} {resumes.length === 1 ? 'resume' : 'resumes'}
              </span>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-1 shadow-md inline-flex">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-4 py-2 rounded-md transition-all ${
                  viewMode === 'grid'
                    ? 'bg-orange-600 text-white'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                Grid
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-md transition-all ${
                  viewMode === 'list'
                    ? 'bg-orange-600 text-white'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                List
              </button>
            </div>
          </div>
        )}

        {/* Resumes Grid/List */}
        {resumes.length > 0 ? (
          <div className={viewMode === 'grid' ? 'grid md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
            {resumes.map((resume, index) => (
              <motion.div
                key={resume.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <AnimatedCard className={`group cursor-pointer hover:shadow-2xl transition-all ${
                  viewMode === 'list' ? 'flex items-center gap-6 p-6' : 'p-6'
                }`}>
                  <div className={viewMode === 'list' ? 'flex items-center gap-6 flex-1' : ''}>
                    {/* Icon/Preview */}
                    <div className={`${viewMode === 'list' ? 'w-16 h-20' : 'w-full h-32'} bg-gradient-to-br from-orange-100 to-pink-100 dark:from-orange-900/30 dark:to-pink-900/30 rounded-lg flex items-center justify-center mb-4 ${viewMode === 'list' ? 'mb-0' : ''}`}>
                      <DocumentTextIcon className={`${viewMode === 'list' ? 'w-8 h-8' : 'w-16 h-16'} text-orange-600`} />
                    </div>

                    {/* Content */}
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1 group-hover:text-orange-600 transition-colors">
                            {resume.title}
                          </h3>
                          <div className="flex items-center gap-2 flex-wrap">
                            {resume.is_primary && (
                              <span className="flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-600 text-xs rounded-full">
                                <StarIcon className="w-3 h-3" />
                                Primary
                              </span>
                            )}
                            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-full">
                              v{resume.version}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* ATS Score */}
                      {resume.ats_score && (
                        <div className="mb-3">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm text-gray-600 dark:text-gray-400">ATS Score</span>
                            <span className={`text-sm font-bold px-2 py-1 rounded ${getATSScoreColor(resume.ats_score)}`}>
                              {resume.ats_score}/100
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full transition-all ${
                                resume.ats_score >= 80 ? 'bg-green-600' : 
                                resume.ats_score >= 60 ? 'bg-yellow-600' : 'bg-red-600'
                              }`}
                              style={{ width: `${resume.ats_score}%` }}
                            />
                          </div>
                        </div>
                      )}

                      {/* Meta Info */}
                      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 mb-4">
                        <div className="flex items-center gap-1">
                          <ClockIcon className="w-3 h-3" />
                          {new Date(resume.updated_at).toLocaleDateString()}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/resume/${resume.id}`);
                          }}
                          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-medium"
                        >
                          <PencilIcon className="w-4 h-4" />
                          Edit
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            // Download logic
                          }}
                          className="flex items-center justify-center gap-2 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
                        >
                          <ArrowDownTrayIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            // Preview logic
                          }}
                          className="flex items-center justify-center gap-2 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
                        >
                          <EyeIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </AnimatedCard>
              </motion.div>
            ))}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-16"
          >
            <div className="max-w-md mx-auto">
              <div className="w-24 h-24 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                <DocumentTextIcon className="w-12 h-12 text-orange-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                Create Your First Resume
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-8">
                Build an ATS-optimized resume with AI-powered suggestions and professional templates
              </p>
              
              {/* Features */}
              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <SparklesIcon className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-900 dark:text-white">AI Suggestions</p>
                </div>
                <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <CheckCircleIcon className="w-6 h-6 text-green-600 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-900 dark:text-white">ATS Optimized</p>
                </div>
                <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <DocumentDuplicateIcon className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-900 dark:text-white">12+ Templates</p>
                </div>
                <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <ArrowDownTrayIcon className="w-6 h-6 text-orange-600 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-900 dark:text-white">Export PDF</p>
                </div>
              </div>

              <button
                onClick={() => router.push('/resume/builder')}
                className="px-10 py-4 bg-gradient-to-r from-orange-600 to-pink-600 text-white rounded-xl hover:from-orange-700 hover:to-pink-700 transition-all font-semibold text-lg shadow-lg hover:shadow-xl"
              >
                Get Started
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
