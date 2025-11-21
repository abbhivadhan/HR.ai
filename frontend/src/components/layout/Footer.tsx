'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'

export default function Footer() {
  const footerSections = [
    {
      title: 'Product',
      links: [
        { href: '/features', label: 'Features' },
        { href: '/pricing', label: 'Pricing' },
        { href: '/integrations', label: 'Integrations' },
        { href: '/api', label: 'API' }
      ]
    },
    {
      title: 'Company',
      links: [
        { href: '/about', label: 'About Us' },
        { href: '/careers', label: 'Careers' },
        { href: '/blog', label: 'Blog' },
        { href: '/press', label: 'Press' }
      ]
    },
    {
      title: 'Resources',
      links: [
        { href: '/help', label: 'Help Center' },
        { href: '/docs', label: 'Documentation' },
        { href: '/guides', label: 'Guides' },
        { href: '/webinars', label: 'Webinars' }
      ]
    },
    {
      title: 'Legal',
      links: [
        { href: '/privacy', label: 'Privacy Policy' },
        { href: '/terms', label: 'Terms of Service' },
        { href: '/security', label: 'Security' },
        { href: '/compliance', label: 'Compliance' }
      ]
    }
  ]

  const socialLinks = [
    { 
      href: 'https://instagram.com', 
      label: 'Instagram',
      svg: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
        </svg>
      )
    },
    { 
      href: 'https://x.com', 
      label: 'X (Twitter)',
      svg: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
        </svg>
      )
    },
    { 
      href: 'https://youtube.com', 
      label: 'YouTube',
      svg: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
        </svg>
      )
    },
    { 
      href: 'https://linkedin.com', 
      label: 'LinkedIn',
      svg: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
      )
    }
  ]

  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <Link href="/" className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 relative">
                  {/* Magnifying glass with AI chip */}
                  <svg viewBox="0 0 100 100" className="w-full h-full">
                    {/* Magnifying glass circle */}
                    <circle cx="35" cy="35" r="25" fill="none" stroke="white" strokeWidth="6"/>
                    {/* AI chip in center */}
                    <rect x="28" y="28" width="14" height="14" rx="2" fill="#3B82F6"/>
                    <circle cx="30" cy="30" r="1" fill="white"/>
                    <circle cx="38" cy="30" r="1" fill="white"/>
                    <circle cx="34" cy="38" r="1" fill="white"/>
                    {/* Circuit lines */}
                    <path d="M25 32 L28 32 M40 32 L43 32 M32 25 L32 28 M32 40 L32 43" stroke="white" strokeWidth="1.5"/>
                    {/* Magnifying glass handle */}
                    <line x1="55" y1="55" x2="75" y2="75" stroke="white" strokeWidth="6" strokeLinecap="round"/>
                  </svg>
                </div>
                <span className="text-2xl font-bold">HR<span className="text-blue-400">.ai</span></span>
              </Link>
              <p className="text-gray-400 mb-6 max-w-md">
                AI-powered recruitment platform that transforms how companies find talent 
                and candidates discover opportunities.
              </p>
              <div className="flex space-x-4">
                {socialLinks.map((social) => (
                  <Link
                    key={social.label}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-blue-600 transition-colors duration-200"
                    aria-label={social.label}
                  >
                    {social.svg}
                  </Link>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Footer Links */}
          {footerSections.map((section, index) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <h3 className="text-lg font-semibold mb-4">{section.title}</h3>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-gray-400 hover:text-white transition-colors duration-200"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Newsletter Signup */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-12 pt-8 border-t border-gray-800"
        >
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="mb-4 md:mb-0">
              <h3 className="text-lg font-semibold mb-2">Stay Updated</h3>
              <p className="text-gray-400">
                Get the latest updates on AI hiring trends and platform features.
              </p>
            </div>
            <div className="flex w-full md:w-auto">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 md:w-64 px-4 py-2 bg-gray-800 border border-gray-700 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-r-lg font-medium hover:shadow-lg transition-all duration-200">
                Subscribe
              </button>
            </div>
          </div>
        </motion.div>

        {/* Bottom Bar */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          viewport={{ once: true }}
          className="mt-12 pt-8 border-t border-gray-800"
        >
          <div className="flex flex-col md:flex-row items-center justify-between mb-4">
            <p className="text-gray-400 text-sm mb-4 md:mb-0">
              © 2025 HR.ai. All rights reserved.
            </p>
            <div className="flex items-center space-x-6 text-sm text-gray-400">
              <Link href="/privacy" className="hover:text-white transition-colors duration-200">
                Privacy
              </Link>
              <Link href="/terms" className="hover:text-white transition-colors duration-200">
                Terms
              </Link>
              <Link href="/cookies" className="hover:text-white transition-colors duration-200">
                Cookies
              </Link>
            </div>
          </div>
          
          {/* Watermark */}
          <div className="text-center pt-4 border-t border-gray-800/50">
            <p className="text-gray-500 text-xs">
              Built by{' '}
              <span className="text-blue-400 font-semibold">ABBHIVADHAN</span>
            </p>
          </div>
        </motion.div>
      </div>
    </footer>
  )
}