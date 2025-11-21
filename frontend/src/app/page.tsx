'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import AnimatedCard from '@/components/ui/AnimatedCard'
import LazyImage from '@/components/ui/LazyImage'
import Footer from '@/components/layout/Footer'
import Logo from '@/components/ui/Logo'
import { 
  UserGroupIcon, 
  StarIcon, 
  ClockIcon, 
  CpuChipIcon,
  ShieldCheckIcon,
  LockClosedIcon,
  KeyIcon,
  CheckBadgeIcon,
  ChartBarIcon,
  BoltIcon,
  UserIcon
} from '@heroicons/react/24/outline'
import { RocketLaunchIcon } from '@heroicons/react/24/solid'

export default function Home() {
  const { isAuthenticated } = useAuth()
  const [activeTab, setActiveTab] = useState<'candidate' | 'company'>('candidate')
  const { scrollYProgress } = useScroll()
  const y = useTransform(scrollYProgress, [0, 1], ['0%', '50%'])

  const candidateFeatures = [
    {
      icon: <StarIcon className="w-8 h-8" />,
      title: 'Smart Job Matching',
      description: 'AI analyzes your skills and preferences to find perfect job matches',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: <CpuChipIcon className="w-8 h-8" />,
      title: 'AI-Powered Assessments',
      description: 'Showcase your abilities through intelligent skill evaluations',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: <ChartBarIcon className="w-8 h-8" />,
      title: 'Career Insights',
      description: 'Get personalized recommendations to advance your career',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: <BoltIcon className="w-8 h-8" />,
      title: 'Fast Applications',
      description: 'Apply to multiple positions with one-click applications',
      color: 'from-orange-500 to-red-500'
    }
  ]

  const companyFeatures = [
    {
      icon: <BoltIcon className="w-8 h-8" />,
      title: 'Instant Screening',
      description: 'AI pre-screens candidates to save 80% of your time',
      color: 'from-indigo-500 to-blue-500'
    },
    {
      icon: <ShieldCheckIcon className="w-8 h-8" />,
      title: 'Bias-Free Hiring',
      description: 'Eliminate unconscious bias with objective AI evaluations',
      color: 'from-teal-500 to-cyan-500'
    },
    {
      icon: <ChartBarIcon className="w-8 h-8" />,
      title: 'Hiring Analytics',
      description: 'Track metrics and optimize your recruitment funnel',
      color: 'from-violet-500 to-purple-500'
    },
    {
      icon: <UserGroupIcon className="w-8 h-8" />,
      title: 'Team Collaboration',
      description: 'Streamline hiring decisions with collaborative tools',
      color: 'from-rose-500 to-pink-500'
    }
  ]

  const stats = [
    { number: '0', label: 'Active Users', icon: <UserGroupIcon className="w-6 h-6" /> },
    { number: '95%', label: 'Match Accuracy', icon: <StarIcon className="w-6 h-6" /> },
    { number: '50%', label: 'Faster Hiring', icon: <ClockIcon className="w-6 h-6" /> },
    { number: '24/7', label: 'AI Support', icon: <CpuChipIcon className="w-6 h-6" /> }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-blue-900/20 dark:to-indigo-900/20 overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 -mt-16 pt-16">
        {/* Background Elements */}
        <motion.div 
          style={{ y }}
          className="absolute inset-0 overflow-hidden"
        >
          <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-blue-400/20 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-400/20 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-cyan-400/10 to-blue-400/10 rounded-full blur-3xl" />
        </motion.div>

        <div className="relative z-10 text-center max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="mb-8"
          >
            <div className="flex items-center justify-center mb-8">
              <Logo size="xl" showText={false} iconColor="text-blue-600 dark:text-white" className="mr-6 w-20 h-20" />
              <h1 className="text-6xl sm:text-7xl md:text-8xl font-bold text-gray-900 dark:text-white">
                HR<span className="text-blue-600 dark:text-cyan-300">.ai</span>
              </h1>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6 leading-tight">
              The Future of
              <br />
              <span className="text-blue-600 dark:text-cyan-300">
                AI-Powered Hiring
              </span>
            </h2>
            <p className="text-lg sm:text-xl md:text-2xl text-gray-700 dark:text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed">
              Connect talent with opportunity through intelligent matching, 
              automated assessments, and data-driven insights.
            </p>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16"
          >
            <Link
              href={isAuthenticated ? "/dashboard" : "/auth/register"}
              className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 min-w-[200px]"
            >
              <span className="relative z-10">
                {isAuthenticated ? "Go to Dashboard" : "Start Free Trial"}
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-blue-700 to-purple-700 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
            </Link>
            <Link
              href="#features"
              className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-gray-700 dark:text-gray-200 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 min-w-[200px]"
            >
              Explore Features
            </Link>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-8 max-w-4xl mx-auto"
          >
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
                className="text-center p-4 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl border border-gray-200/50 dark:border-gray-700/50"
              >
                <div className="text-blue-600 mb-2">{stat.icon}</div>
                <div className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-1">
                  {stat.number}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">
              Built for Everyone
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-12">
              Whether you're looking for your dream job or the perfect candidate, 
              our AI-powered platform has you covered.
            </p>

            {/* Tab Switcher */}
            <div className="inline-flex bg-gray-100 dark:bg-gray-800 rounded-xl p-1 mb-12">
              <button
                onClick={() => setActiveTab('candidate')}
                className={`px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
                  activeTab === 'candidate'
                    ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
              >
                For Candidates
              </button>
              <button
                onClick={() => setActiveTab('company')}
                className={`px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
                  activeTab === 'company'
                    ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
              >
                For Companies
              </button>
            </div>
          </motion.div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {(activeTab === 'candidate' ? candidateFeatures : companyFeatures).map((feature, index) => (
              <AnimatedCard
                key={feature.title}
                delay={index * 0.1}
                className="p-6 h-full"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${feature.color} flex items-center justify-center text-white mb-4`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  {feature.description}
                </p>
              </AnimatedCard>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800/50 dark:to-gray-900/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">
              How It Works
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Get started in minutes with our streamlined process
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                title: 'Create Your Profile',
                description: 'Sign up and let our AI analyze your skills, experience, and preferences',
                icon: <UserIcon className="w-8 h-8" />
              },
              {
                step: '02',
                title: 'Get Matched',
                description: 'Our intelligent algorithm finds the perfect matches based on compatibility',
                icon: <UserGroupIcon className="w-8 h-8" />
              },
              {
                step: '03',
                title: 'Start Your Journey',
                description: 'Connect, interview, and begin your next career adventure',
                icon: <RocketLaunchIcon className="w-8 h-8" />
              }
            ].map((item, index) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="relative mb-8">
                  <div className="w-20 h-20 mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white mb-4">
                    {item.icon}
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center text-sm font-bold text-blue-600 border-2 border-blue-600">
                    {item.step}
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  {item.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  {item.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Trusted by Industry Leaders
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              See what our customers say about transforming their hiring process
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                quote: "HR.ai reduced our time-to-hire by 60% and improved candidate quality significantly.",
                author: "Sarah Chen",
                role: "Head of Talent",
                company: "TechCorp",
                avatar: "SC"
              },
              {
                quote: "The AI matching is incredibly accurate. We've seen a 40% increase in successful placements.",
                author: "Michael Rodriguez",
                role: "Recruiting Director",
                company: "StartupXYZ",
                avatar: "MR"
              },
              {
                quote: "Finally found my dream job through their platform. The matching algorithm is spot-on!",
                author: "Emily Johnson",
                role: "Software Engineer",
                company: "BigTech Inc",
                avatar: "EJ"
              }
            ].map((testimonial, index) => (
              <motion.div
                key={testimonial.author}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow"
              >
                <div className="flex items-start mb-4">
                  <svg className="w-10 h-10 text-blue-500 opacity-50" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
                  </svg>
                </div>
                <p className="text-gray-700 mb-6 text-base leading-relaxed">
                  {testimonial.quote}
                </p>
                <div className="flex items-center pt-4 border-t border-gray-100">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold mr-3">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{testimonial.author}</div>
                    <div className="text-sm text-gray-600">{testimonial.role}</div>
                    <div className="text-sm text-blue-600">{testimonial.company}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust Indicators */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
              Enterprise-Grade Security & Compliance
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Your data is protected with industry-leading security measures
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { icon: <ShieldCheckIcon className="w-8 h-8" />, title: 'SOC 2 Compliant', desc: 'Type II certified' },
              { icon: <LockClosedIcon className="w-8 h-8" />, title: 'GDPR Ready', desc: 'Full compliance' },
              { icon: <KeyIcon className="w-8 h-8" />, title: 'End-to-End Encryption', desc: 'AES-256 encryption' },
              { icon: <CheckBadgeIcon className="w-8 h-8" />, title: '99.9% Uptime', desc: 'SLA guarantee' }
            ].map((item, index) => (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center bg-white rounded-xl p-6 shadow-lg"
              >
                <div className="text-blue-600 mb-3">{item.icon}</div>
                <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-sm text-gray-600">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl p-8 sm:p-12 text-white relative overflow-hidden"
          >
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-32 translate-x-32"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-24 -translate-x-24"></div>
            
            <div className="relative z-10">
              <h2 className="text-3xl sm:text-4xl font-bold mb-6">
                Ready to Transform Your Hiring?
              </h2>
              <p className="text-lg sm:text-xl mb-8 opacity-90">
                Join thousands of companies and candidates who've already discovered 
                the power of AI-driven recruitment.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/auth/register"
                  className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-blue-600 bg-white rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
                >
                  Get Started Free
                  <span className="ml-2">→</span>
                </Link>
                <Link
                  href="/contact"
                  className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white border-2 border-white/30 rounded-xl hover:bg-white/10 transition-all duration-200"
                >
                  Contact Sales
                </Link>
              </div>
              
              <div className="mt-8 flex items-center justify-center gap-6 text-sm opacity-80">
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                  14-day free trial
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                  No credit card required
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                  Cancel anytime
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  )
}