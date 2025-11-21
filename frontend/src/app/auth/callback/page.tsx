'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { User } from '@/contexts/AuthContext'

export default function AuthCallback() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(true)

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get the session from the URL hash
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()

        if (sessionError) {
          console.error('Session error:', sessionError)
          setError(sessionError.message)
          setIsProcessing(false)
          return
        }

        if (!session) {
          console.error('No session found')
          setError('Authentication failed - no session')
          setIsProcessing(false)
          return
        }

        console.log('Session retrieved:', session.user)

        // Check if user profile exists
        const { data: existingProfile, error: profileCheckError } = await supabase
          .from('users')
          .select('*')
          .eq('id', session.user.id)
          .single()

        if (profileCheckError && profileCheckError.code !== 'PGRST116') {
          // PGRST116 is "not found" error, which is expected for new users
          console.error('Profile check error:', profileCheckError)
          throw new Error('Failed to check user profile')
        }

        // If profile doesn't exist, create it
        if (!existingProfile) {
          console.log('Creating new user profile for Google user')
          
          // Extract name from user metadata
          const fullName = session.user.user_metadata?.full_name || ''
          const [firstName = '', ...lastNameParts] = fullName.split(' ')
          const lastName = lastNameParts.join(' ') || ''

          const { error: insertError } = await supabase
            .from('users')
            .insert({
              id: session.user.id,
              email: session.user.email!,
              first_name: firstName || 'User',
              last_name: lastName || '',
              user_type: 'CANDIDATE', // Default to candidate, can be changed later
              is_active: true,
              is_verified: true, // Google accounts are pre-verified
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            })

          if (insertError) {
            console.error('Profile creation error:', insertError)
            throw new Error(`Failed to create user profile: ${insertError.message}`)
          }

          console.log('Profile created successfully')
        }

        // Get the complete user profile
        const { data: profileData, error: profileError } = await supabase
          .from('users')
          .select('*')
          .eq('id', session.user.id)
          .single()

        if (profileError || !profileData) {
          console.error('Failed to fetch profile:', profileError)
          throw new Error('Failed to fetch user profile')
        }

        // Create user object for local storage
        const user: User = {
          id: profileData.id,
          email: profileData.email,
          firstName: profileData.first_name,
          lastName: profileData.last_name,
          userType: profileData.user_type,
          isVerified: profileData.is_verified
        }

        // Store tokens and user data
        localStorage.setItem('accessToken', session.access_token)
        localStorage.setItem('refreshToken', session.refresh_token)
        localStorage.setItem('userData', JSON.stringify(user))

        console.log('Authentication complete, redirecting to dashboard...')
        
        // Redirect to dashboard
        router.push('/dashboard')
      } catch (error: any) {
        console.error('Callback error:', error)
        setError(error.message || 'Authentication failed')
        setIsProcessing(false)
      }
    }

    handleCallback()
  }, [router])

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
              <svg
                className="h-6 w-6 text-red-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Authentication Failed
            </h3>
            <p className="text-sm text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => router.push('/auth/login')}
              className="btn-primary px-6 py-2"
            >
              Back to Login
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-primary-100 mb-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {isProcessing ? 'Completing Authentication...' : 'Redirecting...'}
          </h3>
          <p className="text-sm text-gray-600">
            Please wait while we set up your account
          </p>
        </div>
      </div>
    </div>
  )
}
