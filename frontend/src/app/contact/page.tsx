'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import { 
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  ChatBubbleLeftRightIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import AnimatedSelect from '@/components/ui/AnimatedSelect'
import Logo from '@/components/ui/Logo'

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    subject: '',
    message: '',
    type: 'general'
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setIsSubmitting(false)
    setSubmitted(true)
  }

  const contactMethods = [
    {
      icon: <EnvelopeIcon className="w-6 h-6" />,
      title: 'Email Us',
      description: 'Send us an email and we\'ll respond within 24 hours',
      contact: 'abbhivadhan279@gmail.com',
      action: 'mailto:abbhivadhan279@gmail.com'
    },
    {
      icon: <PhoneIcon className="w-6 h-6" />,
      title: 'Call Us',
      description: 'Speak with our team during business hours',
      contact: '+91 8217652927',
      action: 'tel:+918217652927'
    },
    {
      icon: <ChatBubbleLeftRightIcon className="w-6 h-6" />,
      title: 'Live Chat',
      description: 'Chat with our support team in real-time',
      contact: 'Available 24/7',
      action: '#'
    },
    {
      icon: <MapPinIcon className="w-6 h-6" />,
      title: 'Visit Us',
      description: 'Come visit our headquarters',
      contact: 'Dayananda Sagar University, Bangalore, Karnataka, India',
      action: '#'
    }
  ]

  const faqs = [
    {
      question: 'How does the AI matching work?',
      answer: 'Our AI analyzes skills, experience, and cultural preferences to create compatibility scores between candidates and job requirements.'
    },
    {
      question: 'Is there a free trial?',
      answer: 'Yes, we offer a 14-day free trial for all plans. No credit card required to get started.'
    },
    {
      question: 'Can I integrate with my existing ATS?',
      answer: 'Yes, we offer integrations with popular ATS platforms and can create custom integrations for enterprise clients.'
    },
    {
      question: 'How secure is my data?',
      answer: 'We use enterprise-grade security with SOC 2 compliance, end-to-end encryption, and regular security audits.'
    }
  ]

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 text-center max-w-md mx-4"
        >
          <div className="flex justify-center mb-4">
            <div className="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
              <CheckCircleIcon className="w-12 h-12 text-green-600" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Message Sent!
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Thank you for contacting us. We'll get back to you within 24 hours.
          </p>
          <button
            onClick={() => setSubmitted(false)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Send Another Message
          </button>
        </motion.div>
      </div>
    )
  }

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
            <h2 className="text-2xl md:text-3xl font-bold mb-6 text-white">
              Get in Touch
            </h2>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto opacity-90">
              Have questions? We'd love to hear from you. Send us a message and we'll respond as soon as possible.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Contact Methods */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
            {contactMethods.map((method, index) => (
              <motion.a
                key={method.title}
                href={method.action}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-xl transition-shadow group"
              >
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600 mx-auto mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                  {method.icon}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {method.title}
                </h3>
                <p className="text-gray-600 text-sm mb-3">
                  {method.description}
                </p>
                <p className="text-blue-600 font-medium">
                  {method.contact}
                </p>
              </motion.a>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Form */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Form */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl font-bold text-gray-900 mb-6">
                Send us a Message
              </h2>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Your name"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email *
                    </label>
                    <input
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="your@email.com"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company
                  </label>
                  <input
                    type="text"
                    value={formData.company}
                    onChange={(e) => handleInputChange('company', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Your company"
                  />
                </div>
                
                <div>
                  <AnimatedSelect
                    label="Inquiry Type"
                    value={formData.type}
                    onChange={(value) => handleInputChange('type', value)}
                    options={[
                      { value: 'general', label: 'General Inquiry' },
                      { value: 'sales', label: 'Sales' },
                      { value: 'support', label: 'Support' },
                      { value: 'partnership', label: 'Partnership' },
                      { value: 'press', label: 'Press' }
                    ]}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subject *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.subject}
                    onChange={(e) => handleInputChange('subject', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="What's this about?"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message *
                  </label>
                  <textarea
                    required
                    rows={6}
                    value={formData.message}
                    onChange={(e) => handleInputChange('message', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Tell us more about your inquiry..."
                  />
                </div>
                
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isSubmitting ? 'Sending...' : 'Send Message'}
                </button>
              </form>
            </motion.div>

            {/* Info */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="space-y-8"
            >
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  Let's Start a Conversation
                </h3>
                <p className="text-gray-600 mb-6">
                  Whether you're looking to hire top talent or find your dream job, 
                  we're here to help. Our team of experts is ready to answer your questions 
                  and show you how our AI-powered platform can transform your hiring process.
                </p>
              </div>

              <div className="bg-blue-50 rounded-xl p-6">
                <div className="flex items-center mb-4">
                  <ClockIcon className="w-5 h-5 text-blue-600 mr-2" />
                  <h4 className="font-semibold text-gray-900">Response Time</h4>
                </div>
                <p className="text-gray-600 text-sm">
                  We typically respond to all inquiries within 24 hours during business days. 
                  For urgent matters, please call us directly.
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-4">Office Hours</h4>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span>Monday - Friday</span>
                    <span>9:00 AM - 6:00 PM PST</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Saturday</span>
                    <span>10:00 AM - 4:00 PM PST</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Sunday</span>
                    <span>Closed</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-gray-600">
              Quick answers to common questions
            </p>
          </motion.div>

          <div className="space-y-6">
            {faqs.map((faq, index) => (
              <motion.div
                key={faq.question}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl shadow-lg p-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
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
    </div>
  )
}