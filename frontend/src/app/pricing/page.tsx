'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useState } from 'react'
import { 
  CheckIcon, 
  XMarkIcon,
  RocketLaunchIcon,
  BuildingOfficeIcon,
  StarIcon
} from '@heroicons/react/24/outline'
import Logo from '@/components/ui/Logo'

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly')

  const plans = [
    {
      name: 'Starter',
      description: 'Perfect for small teams and startups',
      price: { monthly: 49, yearly: 39 },
      icon: <RocketLaunchIcon className="w-6 h-6" />,
      features: [
        'Up to 5 job postings',
        'Basic AI matching',
        '50 candidate profiles',
        'Email support',
        'Basic analytics',
        'Standard assessments'
      ],
      limitations: [
        'No advanced analytics',
        'No custom branding',
        'No API access'
      ],
      popular: false,
      color: 'from-gray-500 to-gray-600',
      iconBg: 'from-gray-100 to-gray-200',
      iconColor: 'text-gray-600'
    },
    {
      name: 'Professional',
      description: 'Ideal for growing companies',
      price: { monthly: 149, yearly: 119 },
      icon: <StarIcon className="w-6 h-6" />,
      features: [
        'Unlimited job postings',
        'Advanced AI matching',
        'Unlimited candidate profiles',
        'Priority support',
        'Advanced analytics',
        'Custom assessments',
        'Team collaboration',
        'Interview scheduling',
        'Custom branding'
      ],
      limitations: [
        'No API access',
        'No white-label solution'
      ],
      popular: true,
      color: 'from-blue-500 to-purple-600',
      iconBg: 'from-blue-100 to-purple-100',
      iconColor: 'text-blue-600'
    },
    {
      name: 'Enterprise',
      description: 'For large organizations',
      price: { monthly: 399, yearly: 319 },
      icon: <BuildingOfficeIcon className="w-6 h-6" />,
      features: [
        'Everything in Professional',
        'API access',
        'White-label solution',
        'Dedicated account manager',
        'Custom integrations',
        'Advanced security',
        'SLA guarantee',
        'Custom training',
        'Multi-location support'
      ],
      limitations: [],
      popular: false,
      color: 'from-purple-500 to-pink-600',
      iconBg: 'from-purple-100 to-pink-100',
      iconColor: 'text-purple-600'
    }
  ]

  const faqs = [
    {
      question: 'Can I change my plan at any time?',
      answer: 'Yes, you can upgrade or downgrade your plan at any time. Changes will be reflected in your next billing cycle.'
    },
    {
      question: 'Is there a free trial?',
      answer: 'Yes, we offer a 14-day free trial for all plans. No credit card required to start.'
    },
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards, PayPal, and bank transfers for enterprise customers.'
    },
    {
      question: 'Do you offer refunds?',
      answer: 'Yes, we offer a 30-day money-back guarantee if you\'re not satisfied with our service.'
    },
    {
      question: 'Can I cancel my subscription?',
      answer: 'Yes, you can cancel your subscription at any time. You\'ll continue to have access until the end of your billing period.'
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
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
              Simple, Transparent
              <br />
              <span className="text-cyan-300">Pricing</span>
            </h2>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto opacity-90">
              Choose the perfect plan for your hiring needs. Start free, scale as you grow.
            </p>
            
            {/* Billing Toggle */}
            <div className="inline-flex bg-white/20 dark:bg-gray-800/50 rounded-xl p-1 mb-8">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-6 py-2 rounded-lg font-medium transition-all ${
                  billingCycle === 'monthly'
                    ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-white/80 hover:text-white'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('yearly')}
                className={`px-6 py-2 rounded-lg font-medium transition-all ${
                  billingCycle === 'yearly'
                    ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-white/80 hover:text-white'
                }`}
              >
                Yearly
                <span className="ml-2 px-2 py-1 bg-green-500 text-white text-xs rounded-full">
                  Save 20%
                </span>
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`relative bg-white rounded-2xl shadow-xl overflow-hidden ${
                  plan.popular ? 'ring-2 ring-blue-500 scale-105' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute top-0 left-0 right-0 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-center py-2 text-sm font-medium">
                    Most Popular
                  </div>
                )}
                
                <div className={`p-8 ${plan.popular ? 'pt-12' : ''}`}>
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${plan.iconBg} flex items-center justify-center mb-4 ${plan.iconColor}`}>
                    {plan.icon}
                  </div>
                  
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 mb-6">{plan.description}</p>
                  
                  <div className="mb-6">
                    <div className="flex items-baseline">
                      <span className="text-4xl font-bold text-gray-900">
                        ${plan.price[billingCycle]}
                      </span>
                      <span className="text-gray-500 ml-2">
                        /{billingCycle === 'monthly' ? 'month' : 'year'}
                      </span>
                    </div>
                    {billingCycle === 'yearly' && (
                      <p className="text-sm text-green-600 mt-1">
                        Save ${(plan.price.monthly * 12) - plan.price.yearly} per year
                      </p>
                    )}
                  </div>
                  
                  <Link
                    href="/auth/register"
                    className={`w-full inline-flex items-center justify-center px-6 py-3 rounded-xl font-semibold transition-all mb-6 ${
                      plan.popular
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:shadow-lg'
                        : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                    }`}
                  >
                    Start Free Trial
                  </Link>
                  
                  <div className="space-y-3">
                    <h4 className="font-semibold text-gray-900">What's included:</h4>
                    {plan.features.map((feature) => (
                      <div key={feature} className="flex items-center">
                        <CheckIcon className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </div>
                    ))}
                    
                    {plan.limitations.length > 0 && (
                      <>
                        <h4 className="font-semibold text-gray-900 dark:text-white mt-6">Not included:</h4>
                        {plan.limitations.map((limitation) => (
                          <div key={limitation} className="flex items-center">
                            <XMarkIcon className="w-5 h-5 text-gray-400 mr-3 flex-shrink-0" />
                            <span className="text-gray-500">{limitation}</span>
                          </div>
                        ))}
                      </>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Comparison */}
      <section className="py-20 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Compare Plans
            </h2>
            <p className="text-xl text-gray-600">
              See what's included in each plan
            </p>
          </motion.div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-4 px-6 font-semibold text-gray-900 dark:text-white">Features</th>
                  <th className="text-center py-4 px-6 font-semibold text-gray-900 dark:text-white">Starter</th>
                  <th className="text-center py-4 px-6 font-semibold text-gray-900 dark:text-white">Professional</th>
                  <th className="text-center py-4 px-6 font-semibold text-gray-900 dark:text-white">Enterprise</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {[
                  { feature: 'Job Postings', starter: '5', professional: 'Unlimited', enterprise: 'Unlimited' },
                  { feature: 'Candidate Profiles', starter: '50', professional: 'Unlimited', enterprise: 'Unlimited' },
                  { feature: 'AI Matching', starter: 'Basic', professional: 'Advanced', enterprise: 'Advanced' },
                  { feature: 'Analytics', starter: 'Basic', professional: 'Advanced', enterprise: 'Advanced' },
                  { feature: 'Support', starter: 'Email', professional: 'Priority', enterprise: 'Dedicated' },
                  { feature: 'API Access', starter: '✗', professional: '✗', enterprise: '✓' },
                  { feature: 'White Label', starter: '✗', professional: '✗', enterprise: '✓' }
                ].map((row) => (
                  <tr key={row.feature}>
                    <td className="py-4 px-6 font-medium text-gray-900 dark:text-white">{row.feature}</td>
                    <td className="py-4 px-6 text-center text-gray-700 dark:text-gray-300">{row.starter}</td>
                    <td className="py-4 px-6 text-center text-gray-700 dark:text-gray-300">{row.professional}</td>
                    <td className="py-4 px-6 text-center text-gray-700">{row.enterprise}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Frequently Asked Questions
            </h2>
          </motion.div>

          <div className="space-y-6">
            {faqs.map((faq, index) => (
              <motion.div
                key={faq.question}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg"
              >
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                  {faq.question}
                </h3>
                <p className="text-gray-600">
                  {faq.answer}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-white"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Ready to Get Started?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Start your free trial today. No credit card required.
            </p>
            <Link
              href="/auth/register"
              className="inline-flex items-center px-8 py-4 bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 font-semibold rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-lg"
            >
              Start Free Trial
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  )
}