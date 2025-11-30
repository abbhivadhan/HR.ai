'use client'

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'
import axios from 'axios'

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

// API base URL - using simple server
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
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      const userData = localStorage.getItem('userData')
      if (userData) {
        try {
          const user = JSON.parse(userData)
          dispatch({ type: 'AUTH_SUCCESS', payload: user })
        } catch (error) {
          localStorage.removeItem('accessToken')
          localStorage.removeItem('refreshToken')
          localStorage.removeItem('userData')
        }
      }
    }
  }, [])

  const login = async (email: string, password: string) => {
    try {
      console.log('Login attempt with simple server:', { email })
      dispatch({ type: 'AUTH_START' })

      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        email,
        password,
      })

      const { access_token, refresh_token, user } = response.data

      // Store tokens and user data
      localStorage.setItem('accessToken', access_token)
      localStorage.setItem('refreshToken', refresh_token)
      localStorage.setItem('userData', JSON.stringify(user))

      // Set default authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      dispatch({ type: 'AUTH_SUCCESS', payload: user })
      console.log('Login complete:', user)
    } catch (error: any) {
      console.error('Login error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed'
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage })
      throw new Error(errorMessage)
    }
  }

  const loginWithGoogle = async () => {
    try {
      console.log('Google login not implemented for simple server')
      dispatch({ type: 'AUTH_START' })
      
      // For now, just show an error
      throw new Error('Google login is not available in simple server mode')
    } catch (error: any) {
      console.error('Google login error:', error)
      const errorMessage = error.message || 'Google login failed'
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage })
      throw new Error(errorMessage)
    }
  }

  const register = async (userData: RegisterData) => {
    try {
      console.log('Register attempt with simple server:', { email: userData.email })
      dispatch({ type: 'AUTH_START' })

      const response = await axios.post(`${API_BASE_URL}/api/auth/register`, userData)

      const { user } = response.data

      // Store user data
      localStorage.setItem('userData', JSON.stringify(user))

      dispatch({ type: 'AUTH_SUCCESS', payload: user })
      console.log('Registration complete:', user)
      
      // Auto-login after registration
      await login(userData.email, userData.password)
    } catch (error: any) {
      console.error('Register error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Registration failed'
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage })
      throw new Error(errorMessage)
    }
  }

  const logout = () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userData')
    delete axios.defaults.headers.common['Authorization']
    dispatch({ type: 'AUTH_LOGOUT' })
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
