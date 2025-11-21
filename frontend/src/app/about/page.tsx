'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  UserGroupIcon,
  LightBulbIcon,
  TrophyIcon,
  GlobeAltIcon,
  BuildingOfficeIcon,
  StarIcon
} from '@heroicons/react/24/outline'
import Logo from '@/components/ui/Logo'

export default function AboutPage() {
  const stats = [
    { number: '10,000+', label: 'Active Users', icon: <UserGroupIcon className="w-8 h-8" /> },
    { number: '500+', label: 'Companies', icon: <BuildingOfficeIcon className="w-8 h-8" /> },
    { number: '95%', label: 'Success Rate', icon: <StarIcon className="w-8 h-8" /> },
    { number: '50+', label: 'Countries', icon: <GlobeAltIcon className="w-8 h-8" /> }
  ]

  const team = [
    {
      name: 'Abbhivadhan',
      role: 'Co-Founder',
      image: 'AB',
      linkedin: 'https://www.linkedin.com/in/abbhivadhan-3b838536b'
    },
    {
      name: 'Aarush Shetty',
      role: 'Co-Founder',
      image: 'AS',
      linkedin: 'https://www.linkedin.com/in/aarush-shetty-a71452384?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app'
    },
    {
      name: 'Aditya Raj',
      role: 'Co-Founder',
      image: 'AR',
      linkedin: 'https://www.linkedin.com/in/aditya-raj-030007371/'
    },
    {
      name: 'Advik Gudodagi',
      role: 'Co-Founder',
      image: 'AG',
      linkedin: 'https://www.linkedin.com/in/advik-gudodagi-3b599332b/'
    },
    {
      name: 'Amay Singh',
      role: 'Co-Founder',
      image: 'AM',
      linkedin: 'https://www.linkedin.com/in/amay-vikram-singh-9ab67237b?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app'
    }
  ]

  const values = [
    {
      icon: <UserGroupIcon className="w-8 h-8" />,
      title: 'People First',
      description: 'We believe great hiring starts with understanding people - their skills, aspirations, and potential.',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: <LightBulbIcon className="w-8 h-8" />,
      title: 'Innovation',
      description: 'We continuously push the boundaries of what\'s possible with AI and machine learning.',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: <TrophyIcon className="w-8 h-8" />,
      title: 'Excellence',
      description: 'We strive for excellence in everything we do, from our technology to our customer service.',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: <GlobeAltIcon className="w-8 h-8" />,
      title: 'Global Impact',
      description: 'We\'re building a platform that connects talent worldwide and creates opportunities for everyone.',
      color: 'from-orange-500 to-red-500'
    }
  ]

  const timeline = [
    {
      year: '2025',
      title: 'Company Founded',
      description: 'Started with a vision to revolutionize hiring with AI'
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
              Transforming Hiring with
              <br />
              <span className="text-cyan-300">Artificial Intelligence</span>
            </h2>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto opacity-90">
              We're on a mission to make hiring more efficient, fair, and successful for everyone.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="text-center bg-white rounded-xl p-6 shadow-lg"
              >
                <div className="text-blue-600 mb-2">{stat.icon}</div>
                <div className="text-3xl font-bold text-gray-900 mb-1">{stat.number}</div>
                <div className="text-gray-600">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Mission */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Our Mission
              </h2>
              <p className="text-lg text-gray-600 mb-6">
                We believe that finding the right job or the right candidate shouldn't be left to chance. 
                Traditional hiring processes are often biased, inefficient, and fail to identify the best matches.
              </p>
              <p className="text-lg text-gray-600 mb-6">
                That's why we built an AI-powered platform that analyzes skills, experience, and cultural fit 
                to create perfect matches between candidates and companies. Our technology eliminates bias, 
                reduces time-to-hire, and improves retention rates.
              </p>
              <p className="text-lg text-gray-600">
                We're not just changing how hiring works - we're creating a world where everyone has access 
                to opportunities that match their potential.
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="bg-gradient-to-br from-blue-100 to-purple-100 rounded-2xl p-8"
            >
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <GlobeAltIcon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">
                Vision 2030
              </h3>
              <p className="text-gray-700 text-center">
                To become the world's leading AI-powered hiring platform, 
                connecting 1 million professionals with their dream jobs.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Our Values
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              The principles that guide everything we do
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <motion.div
                key={value.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl shadow-lg p-6 text-center"
              >
                <div className={`w-16 h-16 rounded-xl bg-gradient-to-r ${value.color} flex items-center justify-center text-white mx-auto mb-4`}>
                  {value.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {value.title}
                </h3>
                <p className="text-gray-600">
                  {value.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Our Journey
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From startup to industry leader
            </p>
          </motion.div>

          <div className="relative">
            <div className="absolute left-1/2 transform -translate-x-1/2 w-1 h-full bg-blue-200"></div>
            <div className="space-y-12">
              {timeline.map((item, index) => (
                <motion.div
                  key={item.year}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className={`flex items-center ${index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'}`}
                >
                  <div className={`w-1/2 ${index % 2 === 0 ? 'pr-8 text-right' : 'pl-8'}`}>
                    <div className="bg-white rounded-xl shadow-lg p-6">
                      <div className="text-2xl font-bold text-blue-600 mb-2">{item.year}</div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">{item.title}</h3>
                      <p className="text-gray-600">{item.description}</p>
                    </div>
                  </div>
                  <div className="relative z-10 w-4 h-4 bg-blue-600 rounded-full border-4 border-white shadow-lg"></div>
                  <div className="w-1/2"></div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Meet Our Team
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              The visionary minds behind our AI-powered platform
            </p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {team.map((member, index) => (
              <motion.div
                key={member.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl shadow-lg p-6 text-center"
              >
                <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">
                  {member.image}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">{member.name}</h3>
                <p className="text-blue-600 font-medium mb-3">{member.role}</p>
                {member.linkedin !== '#' && (
                  <Link
                    href={member.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-blue-600 hover:text-blue-800 transition-colors text-sm"
                  >
                    LinkedIn →
                  </Link>
                )}
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
              Join Our Mission
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Ready to experience the future of hiring?
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/auth/register"
                className="px-8 py-4 bg-white text-blue-600 font-semibold rounded-xl hover:bg-gray-100 transition-colors"
              >
                Get Started
              </Link>
              <Link
                href="/contact"
                className="px-8 py-4 border-2 border-white text-white font-semibold rounded-xl hover:bg-white/10 transition-colors"
              >
                Contact Us
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}