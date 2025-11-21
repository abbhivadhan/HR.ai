'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  SparklesIcon,
  ChartBarIcon,
  UserGroupIcon,
  ClockIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  CpuChipIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline'
import Logo from '@/components/ui/Logo'

export default function FeaturesPage() {
  const features = [
    {
      icon: <SparklesIcon className="w-8 h-8" />,
      title: 'AI-Powered Matching',
      description: 'Our advanced AI algorithms analyze skills, experience, and cultural fit to create perfect matches between candidates and companies.',
      benefits: ['95% match accuracy', 'Reduced time-to-hire', 'Better retention rates'],
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: <CpuChipIcon className="w-8 h-8" />,
      title: 'Smart Assessments',
      description: 'Comprehensive skill evaluations powered by machine learning to accurately assess candidate capabilities.',
      benefits: ['Objective evaluation', 'Skill gap analysis', 'Performance predictions'],
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: <ChartBarIcon className="w-8 h-8" />,
      title: 'Real-time Analytics',
      description: 'Track hiring metrics, monitor performance, and optimize your recruitment process with detailed insights.',
      benefits: ['Performance dashboards', 'Predictive analytics', 'ROI tracking'],
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: <UserGroupIcon className="w-8 h-8" />,
      title: 'Collaborative Hiring',
      description: 'Streamline team collaboration with shared feedback, ratings, and decision-making tools.',
      benefits: ['Team coordination', 'Feedback aggregation', 'Decision tracking'],
      color: 'from-orange-500 to-red-500'
    },
    {
      icon: <ClockIcon className="w-8 h-8" />,
      title: 'Automated Workflows',
      description: 'Reduce manual work with intelligent automation for screening, scheduling, and communication.',
      benefits: ['80% time savings', 'Automated screening', 'Smart scheduling'],
      color: 'from-indigo-500 to-blue-500'
    },
    {
      icon: <ShieldCheckIcon className="w-8 h-8" />,
      title: 'Bias-Free Hiring',
      description: 'Eliminate unconscious bias with objective AI evaluations and structured interview processes.',
      benefits: ['Fair evaluations', 'Diverse hiring', 'Compliance tracking'],
      color: 'from-teal-500 to-cyan-500'
    },
    {
      icon: <GlobeAltIcon className="w-8 h-8" />,
      title: 'Global Talent Pool',
      description: 'Access candidates worldwide with multi-language support and international compliance.',
      benefits: ['Global reach', 'Multi-language', 'Local compliance'],
      color: 'from-violet-500 to-purple-500'
    },
    {
      icon: <LightBulbIcon className="w-8 h-8" />,
      title: 'Predictive Insights',
      description: 'Leverage AI to predict candidate success, retention likelihood, and performance potential.',
      benefits: ['Success prediction', 'Retention analysis', 'Performance forecasting'],
      color: 'from-rose-500 to-pink-500'
    }
  ]

  const integrations = [
    { 
      name: 'LinkedIn', 
      logo: (
        <svg viewBox="0 0 24 24" className="w-8 h-8 fill-current text-blue-600">
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
      )
    },
    { 
      name: 'GitHub', 
      logo: (
        <svg viewBox="0 0 24 24" className="w-8 h-8 fill-current text-gray-800 dark:text-gray-200">
          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
        </svg>
      )
    },
    { 
      name: 'Slack', 
      logo: (
        <svg viewBox="0 0 24 24" className="w-8 h-8 fill-current">
          <path fill="#E01E5A" d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52z"/>
          <path fill="#E01E5A" d="M6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313z"/>
          <path fill="#36C5F0" d="M8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834z"/>
          <path fill="#36C5F0" d="M8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312z"/>
          <path fill="#2EB67D" d="M18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834z"/>
          <path fill="#2EB67D" d="M17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312z"/>
          <path fill="#ECB22E" d="M15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52z"/>
          <path fill="#ECB22E" d="M15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z"/>
        </svg>
      )
    },
    { 
      name: 'Google Workspace', 
      logo: (
        <svg viewBox="0 0 24 24" className="w-8 h-8">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
      )
    },
    { 
      name: 'Microsoft Teams', 
      logo: (
        <svg viewBox="0 0 24 24" className="w-8 h-8">
          <path fill="#5059C9" d="M19.5 0h-15A4.5 4.5 0 0 0 0 4.5v15A4.5 4.5 0 0 0 4.5 24h15a4.5 4.5 0 0 0 4.5-4.5v-15A4.5 4.5 0 0 0 19.5 0z"/>
          <path fill="#7B83EB" d="M19.5 0h-7.5v24h7.5a4.5 4.5 0 0 0 4.5-4.5v-15A4.5 4.5 0 0 0 19.5 0z"/>
          <path fill="#FFF" d="M7.5 6h9v12h-9z"/>
          <path fill="#5059C9" d="M9 8.5h6v7H9z"/>
          <circle fill="#FFF" cx="12" cy="12" r="2"/>
        </svg>
      )
    },
    { 
      name: 'Zoom', 
      logo: (
        <svg viewBox="0 0 24 24" className="w-8 h-8">
          <path fill="#2D8CFF" d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.568 14.432a1.2 1.2 0 0 1-1.2 1.2H7.632a1.2 1.2 0 0 1-1.2-1.2V9.568a1.2 1.2 0 0 1 1.2-1.2h8.736a1.2 1.2 0 0 1 1.2 1.2v4.864z"/>
          <path fill="#FFF" d="M16.368 8.368H7.632a1.2 1.2 0 0 0-1.2 1.2v4.864a1.2 1.2 0 0 0 1.2 1.2h8.736a1.2 1.2 0 0 0 1.2-1.2V9.568a1.2 1.2 0 0 0-1.2-1.2zm-1.2 4.864H8.832V10.768h6.336v2.464z"/>
        </svg>
      )
    },
    { 
      name: 'Salesforce', 
      logo: (
        <svg viewBox="0 0 24 24" className="w-8 h-8">
          <path fill="#00A1E0" d="M12.5 2.4c1.4 0 2.7.6 3.6 1.5.2-.1.5-.1.7-.1 1.8 0 3.3 1.5 3.3 3.3 0 .4-.1.8-.2 1.1 1.1.7 1.8 1.9 1.8 3.3 0 2.2-1.8 4-4 4h-9c-2.2 0-4-1.8-4-4 0-1.9 1.3-3.5 3.1-3.9-.1-.3-.1-.6-.1-.9 0-2.2 1.8-4 4-4 .8 0 1.5.2 2.1.6.5-1.4 1.8-2.4 3.3-2.4z"/>
          <circle fill="#FFF" cx="8.5" cy="11.5" r="1.5"/>
          <circle fill="#FFF" cx="15.5" cy="11.5" r="1.5"/>
          <path fill="#FFF" d="M12 14c-1.1 0-2-.9-2-2h4c0 1.1-.9 2-2 2z"/>
        </svg>
      )
    },
    { 
      name: 'Workday', 
      logo: (
        <svg viewBox="0 0 24 24" className="w-8 h-8">
          <path fill="#F7931E" d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm6 18H6V6h12v12z"/>
          <path fill="#FFF" d="M8 8h8v2H8zm0 3h8v2H8zm0 3h6v2H8z"/>
        </svg>
      )
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 to-purple-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="flex items-center justify-center mb-6">
              <Logo size="xl" showText={false} iconColor="text-white" className="mr-4" />
              <h1 className="text-4xl md:text-6xl font-bold text-white">
                HR<span className="text-cyan-300">.ai</span>
              </h1>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-6 text-white">
              Powerful Features for
              <br />
              <span className="text-cyan-300">Modern Hiring</span>
            </h2>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto opacity-90">
              Discover how HR.ai transforms the way you hire and get hired
            </p>
            <Link
              href="/auth/register"
              className="inline-flex items-center px-8 py-4 bg-white text-blue-600 font-semibold rounded-xl hover:bg-gray-100 transition-colors text-lg"
            >
              Start Free Trial
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Everything You Need to Hire Better
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Our comprehensive suite of features helps you find, evaluate, and hire the best talent
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
              >
                <div className={`w-16 h-16 rounded-xl bg-gradient-to-r ${feature.color} flex items-center justify-center text-white mb-4`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  {feature.description}
                </p>
                <ul className="space-y-1">
                  {feature.benefits.map((benefit) => (
                    <li key={benefit} className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></div>
                      {benefit}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Integrations */}
      <section className="py-20 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Seamless Integrations
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Connect with your favorite tools and platforms
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-6">
            {integrations.map((integration, index) => (
              <motion.div
                key={integration.name}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6 text-center hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
              >
                <div className="w-12 h-12 bg-white dark:bg-gray-800 rounded-lg flex items-center justify-center shadow-sm border border-gray-200 dark:border-gray-600 mb-2">
                  {integration.logo}
                </div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-200">{integration.name}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-white"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Ready to Transform Your Hiring?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Join thousands of companies already using our platform
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/auth/register"
                className="px-8 py-4 bg-white text-blue-600 font-semibold rounded-xl hover:bg-gray-100 transition-colors"
              >
                Start Free Trial
              </Link>
              <Link
                href="/contact"
                className="px-8 py-4 border-2 border-white text-white font-semibold rounded-xl hover:bg-white/10 transition-colors"
              >
                Schedule Demo
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}