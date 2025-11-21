'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { careerCoachService } from '@/services/careerCoachService';
import { CareerPlan } from '@/types/career';
import AnimatedCard from '@/components/ui/AnimatedCard';
import { 
  SparklesIcon, 
  ChartBarIcon, 
  TrophyIcon, 
  ChatBubbleLeftRightIcon, 
  AcademicCapIcon,
  RocketLaunchIcon,
  BriefcaseIcon,
  LightBulbIcon,
  ArrowTrendingUpIcon,
  BookOpenIcon,
  UserGroupIcon,
  CurrencyDollarIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

export default function CareerCoachPage() {
  const router = useRouter();
  const [plans, setPlans] = useState<CareerPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [activeTab, setActiveTab] = useState<'plans' | 'insights' | 'resources'>('plans');
  const [formData, setFormData] = useState({
    current_role: '',
    target_role: '',
    target_salary: '',
    timeline_months: '12',
  });

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      const data = await careerCoachService.getCareerPlans();
      setPlans(data);
    } catch (error) {
      console.error('Failed to load career plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const plan = await careerCoachService.createCareerPlan({
        current_role: formData.current_role || undefined,
        target_role: formData.target_role,
        target_salary: formData.target_salary ? parseFloat(formData.target_salary) : undefined,
        timeline_months: parseInt(formData.timeline_months),
      });
      router.push(`/career-coach/${plan.id}`);
    } catch (error) {
      console.error('Failed to create plan:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  const careerInsights = [
    { label: 'Career Paths Explored', value: '12+', icon: RocketLaunchIcon, color: 'purple' },
    { label: 'Skills Recommended', value: '24', icon: TrophyIcon, color: 'blue' },
    { label: 'Avg. Salary Growth', value: '+35%', icon: ArrowTrendingUpIcon, color: 'green' },
    { label: 'Success Rate', value: '89%', icon: ChartBarIcon, color: 'orange' },
  ];

  const learningResources = [
    { title: 'Leadership Skills', type: 'Course', duration: '6 weeks', provider: 'LinkedIn Learning', icon: UserGroupIcon },
    { title: 'Advanced React Patterns', type: 'Tutorial', duration: '12 hours', provider: 'Frontend Masters', icon: BookOpenIcon },
    { title: 'System Design Interview', type: 'Course', duration: '8 weeks', provider: 'Educative', icon: LightBulbIcon },
    { title: 'Salary Negotiation', type: 'Workshop', duration: '2 hours', provider: 'Career Coach', icon: CurrencyDollarIcon },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-purple-600 blur-2xl opacity-20 rounded-full"></div>
              <SparklesIcon className="w-16 h-16 text-purple-600 relative" />
            </div>
          </div>
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-600">
            AI Career Coach
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-8">
            Your personal AI advisor for career growth, skill development, and strategic job search planning
          </p>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto mb-8">
            {careerInsights.map((insight, index) => (
              <motion.div
                key={insight.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700"
              >
                <insight.icon className={`w-8 h-8 text-${insight.color}-600 mx-auto mb-2`} />
                <div className={`text-2xl font-bold text-${insight.color}-600 mb-1`}>{insight.value}</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">{insight.label}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-1 shadow-lg inline-flex">
            {[
              { id: 'plans', label: 'Career Plans', icon: BriefcaseIcon },
              { id: 'insights', label: 'AI Insights', icon: LightBulbIcon },
              { id: 'resources', label: 'Learning', icon: BookOpenIcon },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all ${
                  activeTab === tab.id
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'plans' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            {/* Features Grid */}
            {plans.length === 0 && !showCreateForm && (
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                <AnimatedCard className="p-6 text-center hover:scale-105 transition-transform">
                  <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <ChartBarIcon className="w-10 h-10 text-purple-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                    Career Planning
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Get personalized career path recommendations
                  </p>
                </AnimatedCard>

                <AnimatedCard className="p-6 text-center hover:scale-105 transition-transform">
                  <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <TrophyIcon className="w-10 h-10 text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                    Skill Analysis
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Identify skill gaps and get learning resources
                  </p>
                </AnimatedCard>

                <AnimatedCard className="p-6 text-center hover:scale-105 transition-transform">
                  <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <ChatBubbleLeftRightIcon className="w-10 h-10 text-green-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                    AI Coaching
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Chat with AI for personalized advice
                  </p>
                </AnimatedCard>

                <AnimatedCard className="p-6 text-center hover:scale-105 transition-transform">
                  <div className="w-16 h-16 bg-yellow-100 dark:bg-yellow-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <AcademicCapIcon className="w-10 h-10 text-yellow-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                    Salary Insights
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Get market salary data for your target role
                  </p>
                </AnimatedCard>
              </div>
            )}

            {/* Create Plan Form */}
            {showCreateForm ? (
              <AnimatedCard className="max-w-3xl mx-auto p-8 bg-white dark:bg-gray-800 shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <RocketLaunchIcon className="w-8 h-8 text-purple-600" />
                  <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                    Create Your Career Plan
                  </h2>
                </div>
                <form onSubmit={handleCreatePlan} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Current Role (Optional)
                      </label>
                      <input
                        type="text"
                        value={formData.current_role}
                        onChange={(e) => setFormData({ ...formData, current_role: e.target.value })}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                        placeholder="e.g., Software Engineer"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Target Role *
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.target_role}
                        onChange={(e) => setFormData({ ...formData, target_role: e.target.value })}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                        placeholder="e.g., Senior Software Engineer"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Target Salary (Optional)
                      </label>
                      <div className="relative">
                        <CurrencyDollarIcon className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" />
                        <input
                          type="number"
                          value={formData.target_salary}
                          onChange={(e) => setFormData({ ...formData, target_salary: e.target.value })}
                          className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                          placeholder="150000"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Timeline (Months)
                      </label>
                      <div className="relative">
                        <ClockIcon className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" />
                        <input
                          type="number"
                          value={formData.timeline_months}
                          onChange={(e) => setFormData({ ...formData, timeline_months: e.target.value })}
                          className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                          min="1"
                          max="120"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <button
                      type="submit"
                      className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white py-4 rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all font-semibold shadow-lg hover:shadow-xl"
                    >
                      Create Plan with AI
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowCreateForm(false)}
                      className="px-8 py-4 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-semibold"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </AnimatedCard>
            ) : plans.length === 0 ? (
              <div className="text-center py-12">
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="max-w-md mx-auto"
                >
                  <div className="w-24 h-24 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                    <RocketLaunchIcon className="w-12 h-12 text-purple-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                    Start Your Career Journey
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-8">
                    Let AI help you create a personalized career development plan
                  </p>
                  <button
                    onClick={() => setShowCreateForm(true)}
                    className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-10 py-4 rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all font-semibold text-lg shadow-lg hover:shadow-xl"
                  >
                    Create Your First Career Plan
                  </button>
                </motion.div>
              </div>
            ) : (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Your Career Plans
                  </h2>
                  <button
                    onClick={() => setShowCreateForm(true)}
                    className="flex items-center gap-2 bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors font-medium shadow-lg"
                  >
                    <RocketLaunchIcon className="w-5 h-5" />
                    New Plan
                  </button>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  {plans.map((plan, index) => (
                    <motion.div
                      key={plan.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="group p-6 cursor-pointer hover:shadow-2xl transition-all bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-purple-500 dark:hover:border-purple-500"
                      onClick={() => router.push(`/career-coach/${plan.id}`)}
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <BriefcaseIcon className="w-5 h-5 text-purple-600" />
                            <h3 className="text-xl font-semibold text-gray-900 dark:text-white group-hover:text-purple-600 transition-colors">
                              {plan.target_role}
                            </h3>
                          </div>
                          {plan.current_role && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                              <ArrowTrendingUpIcon className="w-4 h-4" />
                              From: {plan.current_role}
                            </p>
                          )}
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          plan.status === 'active'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                        }`}>
                          {plan.status}
                        </span>
                      </div>

                      <div className="space-y-3 mb-4">
                        {plan.target_salary && (
                          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                            <CurrencyDollarIcon className="w-4 h-4" />
                            <span>Target: ${plan.target_salary.toLocaleString()}</span>
                          </div>
                        )}
                        {plan.timeline_months && (
                          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                            <ClockIcon className="w-4 h-4" />
                            <span>Timeline: {plan.timeline_months} months</span>
                          </div>
                        )}
                      </div>

                      <div className="pt-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center">
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Created: {new Date(plan.created_at).toLocaleDateString()}
                        </p>
                        <span className="text-purple-600 text-sm font-medium group-hover:translate-x-1 transition-transform inline-block">
                          View Details →
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* AI Insights Tab */}
        {activeTab === 'insights' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            <AnimatedCard className="p-6 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center">
                  <ChartBarIcon className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="font-bold text-gray-900 dark:text-white">Market Trends</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                AI/ML roles are growing 45% YoY with average salaries increasing by 12%
              </p>
              <button className="text-blue-600 text-sm font-medium hover:underline">
                View Full Report →
              </button>
            </AnimatedCard>

            <AnimatedCard className="p-6 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center">
                  <TrophyIcon className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="font-bold text-gray-900 dark:text-white">Top Skills 2024</h3>
              </div>
              <div className="space-y-2">
                {['React/Next.js', 'TypeScript', 'System Design', 'Cloud (AWS/Azure)'].map((skill) => (
                  <div key={skill} className="flex items-center justify-between text-sm">
                    <span className="text-gray-700 dark:text-gray-300">{skill}</span>
                    <span className="text-green-600 font-medium">High Demand</span>
                  </div>
                ))}
              </div>
            </AnimatedCard>

            <AnimatedCard className="p-6 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center">
                  <LightBulbIcon className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="font-bold text-gray-900 dark:text-white">AI Recommendation</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Based on your profile, consider learning System Design to increase your market value by 25%
              </p>
              <button className="text-purple-600 text-sm font-medium hover:underline">
                Start Learning →
              </button>
            </AnimatedCard>
          </motion.div>
        )}

        {/* Learning Resources Tab */}
        {activeTab === 'resources' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="space-y-4"
          >
            {learningResources.map((resource, index) => (
              <motion.div
                key={resource.title}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <AnimatedCard className="p-6 hover:shadow-xl transition-all">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900/30 dark:to-blue-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                      <resource.icon className="w-8 h-8 text-purple-600" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">{resource.title}</h3>
                        <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 text-xs rounded-full">
                          {resource.type}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                        {resource.provider} • {resource.duration}
                      </p>
                      <div className="flex items-center gap-4">
                        <button className="text-purple-600 text-sm font-medium hover:underline">
                          Start Learning
                        </button>
                        <button className="text-gray-600 dark:text-gray-400 text-sm hover:underline">
                          Save for Later
                        </button>
                      </div>
                    </div>
                  </div>
                </AnimatedCard>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
}
