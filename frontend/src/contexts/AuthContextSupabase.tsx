'use client'

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'
import axios from 'axios'
import { supabase, supabaseAuth } from '@/lib/supabase'

// Types
export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  userType: 'CANDIDATE' | 'COMPANY' | 'ADMIN'
  isVerified: boolean
}

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  error: string | null
}

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: User }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'CLEAR_ERROR' }

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>
  loginWithGoogle: () => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => void
  clearError: () => void
}

export interface RegisterData {
  email: string
  password: string
  firstName: string
  lastName: string
  userType: 'CANDIDATE' | 'COMPANY'
}

// Initial state
const initialState: AuthState = {
  user: null,
  isLoading: false,
  isAuthenticated: false,
  error: null,
}

// Reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      }
    case 'AUTH_SUCCESS':
      return {
        ...state,
        isLoading: false,
        isAuthenticated: true,
        user: action.payload,
        error: null,
      }
    case 'AUTH_FAILURE':
      return {
        ...state,
        isLoading: false,
        isAuthenticated: false,
        user: null,
        error: action.payload,
      }
    case 'AUTH_LOGOUT':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        error: null,
      }
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      }
    default:
      return state
  }
}

// Context
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  // Configure axios defaults
  useEffect(() => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }
  }, [])

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      // For now, just set the token without verification
      // In production, you'd verify the token with the server
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      // Try to get user data from localStorage as fallback
      const userData = localStorage.getItem('userData')
      if (userData) {
        try {
          const user = JSON.parse(userData)
          dispatch({ type: 'AUTH_SUCCESS', payload: user })
        } catch (error) {
          // If parsing fails, clear everything
          localStorage.removeItem('accessToken')
          localStorage.removeItem('refreshToken')
          localStorage.removeItem('userData')
        }
      }
    }
  }, [])

  const login = async (email: string, password: string) => {
    try {
      console.log('Login attempt with Supabase:', { email })
      dispatch({ type: 'AUTH_START' })

      // Login with Supabase Auth
      const { data: authData, error: authError } = await supabaseAuth.signIn(email, password)

      if (authError) {
        console.error('Supabase auth error:', authError)
        throw new Error(authError.message)
      }

      if (!authData.user || !authData.session) {
        throw new Error('Login failed - no session returned')
      }

      console.log('Supabase login successful:', authData.user)

      // Get user profile from database
      const { data: profileData, error: profileError } = await supabase
        .from('users')
        .select('*')
        .eq('id', authData.user.id)
        .single()

      if (profileError || !profileData) {
        console.error('Profile fetch error:', profileError)
        throw new Error('Failed to fetch user profile')
      }

      // Create user object for state
      const user: User = {
        id: profileData.id,
        email: profileData.email,
        firstName: profileData.first_name,
        lastName: profileData.last_name,
        userType: profileData.user_type,
        isVerified: profileData.is_verified
      }

      // Store tokens and user data
      localStorage.setItem('accessToken', authData.session.access_token)
      localStorage.setItem('refreshToken', authData.session.refresh_token)
      localStorage.setItem('userData', JSON.stringify(user))

      // Set default authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${authData.session.access_token}`

      dispatch({ type: 'AUTH_SUCCESS', payload: user })
      console.log('Login complete:', user)
    } catch (error: any) {
      console.error('Login error:', error)
      const errorMessage = error.message || 'Login failed'
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage })
      throw new Error(errorMessage)
    }
  }

  const loginWithGoogle = async () => {
    try {
      console.log('Google login attempt')
      dispatch({ type: 'AUTH_START' })

      const { data, error } = await supabaseAuth.signInWithGoogle()

      if (error) {
        console.error('Google auth error:', error)
        throw new Error(error.message)
      }

      // The actual authentication happens in the callback
      // This just redirects to Google
      console.log('Redirecting to Google...')
    } catch (error: any) {
      console.error('Google login error:', error)
      const errorMessage = error.message || 'Google login failed'
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage })
      throw new Error(errorMessage)
    }
  }

  const register = async (userData: RegisterData) => {
    try {
      console.log('Register attempt with Supabase:', { email: userData.email })
      dispatch({ type: 'AUTH_START' })

      // Register with Supabase Auth
      const { data: authData, error: authError } = await supabaseAuth.signUp(
        userData.email,
        userData.password,
        {
          first_name: userData.firstName,
          last_name: userData.lastName,
          user_type: userData.userType
        }
      )

      if (authError) {
        console.error('Supabase auth error:', authError)
        throw new Error(authError.message)
      }

      if (!authData.user) {
        throw new Error('Registration failed - no user returned')
      }

      console.log('Supabase registration successful:', authData.user)

      // Wait a moment for Supabase to process
      await new Promise(resolve => setTimeout(resolve, 500))

      // Create user profile in database
      console.log('Creating profile with data:', {
        id: authData.user.id,
        email: userData.email,
        first_name: userData.firstName,
        last_name: userData.lastName,
        user_type: userData.userType
      })

      const { data: insertData, error: profileError } = await supabase
        .from('users')
        .insert({
          id: authData.user.id,
          email: userData.email,
          first_name: userData.firstName,
          last_name: userData.lastName,
          user_type: userData.userType,
          is_active: true,
          is_verified: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .select()

      if (profileError) {
        console.error('Profile creation error:', profileError)
        console.error('Error details:', JSON.stringify(profileError, null, 2))
        // If it's a table not found error, provide helpful message
        if (profileError.message.includes('relation') || profileError.message.includes('does not exist')) {
          throw new Error('Database not initialized. Please run the Supabase migration first.')
        }
        if (profileError.message.includes('permission') || profileError.message.includes('policy')) {
          throw new Error('Permission denied. Please check Row Level Security policies in Supabase.')
        }
        if (profileError.message.includes('duplicate') || profileError.message.includes('unique')) {
          throw new Error('This email is already registered. Please use a different email or try logging in.')
        }
        throw new Error(`Profile creation failed: ${profileError.message}`)
      }

      console.log('Profile created successfully:', insertData)

      // Create user object for state
      const user: User = {
        id: authData.user.id,
        email: userData.email,
        firstName: userData.firstName,
        lastName: userData.lastName,
        userType: userData.userType,
        isVerified: false
      }

      // Store user data
      localStorage.setItem('userData', JSON.stringify(user))
      if (authData.session) {
        localStorage.setItem('accessToken', authData.session.access_token)
        localStorage.setItem('refreshToken', authData.session.refresh_token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${authData.session.access_token}`
      }

      dispatch({ type: 'AUTH_SUCCESS', payload: user })
      console.log('Registration complete:', user)
    } catch (error: any) {
      console.error('Register error:', error)
      const errorMessage = error.message || 'Registration failed'
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage })
      throw new Error(errorMessage)
    }
  }

  const logout = async () => {
    try {
      await supabaseAuth.signOut()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('userData')
      delete axios.defaults.headers.common['Authorization']
      dispatch({ type: 'AUTH_LOGOUT' })
    }
  }

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  const value: AuthContextType = {
    ...state,
    login,
    loginWithGoogle,
    register,
    logout,
    clearError,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}