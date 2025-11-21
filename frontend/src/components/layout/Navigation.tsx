'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline'
import { useAuth } from '@/contexts/AuthContext'
import ThemeToggle from '@/components/ui/ThemeToggle'

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const { isAuthenticated, user, logout } = useAuth()
  const pathname = usePathname()

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navItems = [
    { href: '/features', label: 'Features' },
    { href: '/pricing', label: 'Pricing' },
    { href: '/about', label: 'About' },
    { href: '/contact', label: 'Contact' }
  ]

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled 
          ? 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-md shadow-lg' 
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 relative">
              {/* Magnifying glass with AI chip and circuit board */}
              <svg viewBox="0 0 100 100" className="w-full h-full">
                {/* Magnifying glass circle */}
                <circle cx="40" cy="40" r="28" fill="none" stroke="currentColor" strokeWidth="5" className="text-gray-900 dark:text-white"/>
                
                {/* AI chip in center */}
                <rect x="32" y="32" width="16" height="16" rx="2" fill="currentColor" className="text-gray-900 dark:text-white"/>
                <rect x="34" y="34" width="12" height="12" rx="1" fill="currentColor" className="text-blue-600"/>
                
                {/* Circuit board pattern - vertical lines */}
                <line x1="28" y1="40" x2="32" y2="40" stroke="currentColor" strokeWidth="2" className="text-gray-900 dark:text-white"/>
                <line x1="48" y1="40" x2="52" y2="40" stroke="currentColor" strokeWidth="2" className="text-gray-900 dark:text-white"/>
                <line x1="40" y1="28" x2="40" y2="32" stroke="currentColor" strokeWidth="2" className="text-gray-900 dark:text-white"/>
                <line x1="40" y1="48" x2="40" y2="52" stroke="currentColor" strokeWidth="2" className="text-gray-900 dark:text-white"/>
                
                {/* Circuit nodes */}
                <circle cx="28" cy="40" r="2" fill="currentColor" className="text-gray-900 dark:text-white"/>
                <circle cx="52" cy="40" r="2" fill="currentColor" className="text-gray-900 dark:text-white"/>
                <circle cx="40" cy="28" r="2" fill="currentColor" className="text-gray-900 dark:text-white"/>
                <circle cx="40" cy="52" r="2" fill="currentColor" className="text-gray-900 dark:text-white"/>
                
                {/* Diagonal circuit lines */}
                <line x1="25" y1="25" x2="30" y2="30" stroke="currentColor" strokeWidth="1.5" className="text-gray-900 dark:text-white"/>
                <line x1="55" y1="25" x2="50" y2="30" stroke="currentColor" strokeWidth="1.5" className="text-gray-900 dark:text-white"/>
                <line x1="25" y1="55" x2="30" y2="50" stroke="currentColor" strokeWidth="1.5" className="text-gray-900 dark:text-white"/>
                <line x1="55" y1="55" x2="50" y2="50" stroke="currentColor" strokeWidth="1.5" className="text-gray-900 dark:text-white"/>
                
                {/* Magnifying glass handle */}
                <line x1="60" y1="60" x2="78" y2="78" stroke="currentColor" strokeWidth="7" strokeLinecap="round" className="text-gray-900 dark:text-white"/>
              </svg>
            </div>
            <span className="text-2xl font-bold text-gray-900 dark:text-white">
              HR<span className="text-blue-600">.ai</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`relative font-medium transition-colors duration-200 ${
                    isActive
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  {item.label}
                  {isActive && (
                    <motion.div
                      layoutId="activeNav"
                      className="absolute -bottom-1 left-0 right-0 h-0.5 bg-blue-600 dark:bg-blue-400"
                      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                    />
                  )}
                </Link>
              )
            })}
          </div>

          {/* Right Side */}
          <div className="hidden md:flex items-center space-x-4">
            <ThemeToggle />
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <Link
                  href="/dashboard"
                  className={`relative font-medium transition-colors duration-200 ${
                    pathname?.startsWith('/dashboard')
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  Dashboard
                  {pathname?.startsWith('/dashboard') && (
                    <motion.div
                      layoutId="activeNav"
                      className="absolute -bottom-1 left-0 right-0 h-0.5 bg-blue-600 dark:bg-blue-400"
                      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                    />
                  )}
                </Link>
                <button
                  onClick={logout}
                  className="flex items-center space-x-1 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors duration-200 font-medium"
                >
                  <ArrowRightOnRectangleIcon className="w-5 h-5" />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  href="/auth/login"
                  className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors duration-200 font-medium"
                >
                  Login
                </Link>
                <Link
                  href="/auth/register"
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:shadow-lg transform hover:scale-105 transition-all duration-200"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center space-x-2">
            <ThemeToggle />
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white p-2"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {isOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700"
            >
              <div className="px-2 pt-2 pb-3 space-y-1">
                {navItems.map((item) => {
                  const isActive = pathname === item.href
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`block px-3 py-2 rounded-lg transition-colors duration-200 font-medium ${
                        isActive
                          ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                          : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                      }`}
                      onClick={() => setIsOpen(false)}
                    >
                      {item.label}
                    </Link>
                  )
                })}
                {isAuthenticated ? (
                  <>
                    <Link
                      href="/dashboard"
                      className={`block px-3 py-2 rounded-lg transition-colors duration-200 font-medium ${
                        pathname?.startsWith('/dashboard')
                          ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                          : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                      }`}
                      onClick={() => setIsOpen(false)}
                    >
                      Dashboard
                    </Link>
                    <button
                      onClick={() => {
                        logout()
                        setIsOpen(false)
                      }}
                      className="flex items-center space-x-2 w-full text-left px-3 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors duration-200 font-medium"
                    >
                      <ArrowRightOnRectangleIcon className="w-5 h-5" />
                      <span>Logout</span>
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      href="/auth/login"
                      className="block px-3 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors duration-200 font-medium"
                      onClick={() => setIsOpen(false)}
                    >
                      Login
                    </Link>
                    <Link
                      href="/auth/register"
                      className="block mx-3 my-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium text-center"
                      onClick={() => setIsOpen(false)}
                    >
                      Sign Up
                    </Link>
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.nav>
  )
}