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
  oauthProvider?: string
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
        password
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
      console.log('Google login - opening popup')
      dispatch({ type: 'AUTH_START' })

      // For simple server, we'll use a mock Google OAuth flow
      // In production, this would redirect to Google
      
      // Open Google OAuth in popup
      const width = 500
      const height = 600
      const left = window.screenX + (window.outerWidth - width) / 2
      const top = window.screenY + (window.outerHeight - height) / 2
      
      const popup = window.open(
        'about:blank',
        'Google Sign In',
        `width=${width},height=${height},left=${left},top=${top}`
      )

      if (!popup) {
        throw new Error('Popup blocked. Please allow popups for this site.')
      }

      // For testing, simulate Google OAuth response
      // In production, this would come from Google
      popup.document.write(`
        <html>
          <head>
            <title>Google Sign In</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: #f5f5f5;
              }
              .container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
              }
              h2 { color: #333; margin-bottom: 20px; }
              input {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
              }
              button {
                background: #4285f4;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                margin-top: 10px;
              }
              button:hover { background: #357ae8; }
              .note {
                font-size: 12px;
                color: #666;
                margin-top: 20px;
              }
            </style>
          </head>
          <body>
            <div class="container">
              <h2>🔐 Mock Google Sign In</h2>
              <p>For testing purposes</p>
              <input type="email" id="email" placeholder="Email" value="test@gmail.com" />
              <input type="text" id="firstName" placeholder="First Name" value="Test" />
              <input type="text" id="lastName" placeholder="Last Name" value="User" />
              <button onclick="signIn()">Sign In with Google</button>
              <p class="note">This is a mock OAuth flow for testing.<br/>In production, this would be Google's actual OAuth page.</p>
            </div>
            <script>
              function signIn() {
                const email = document.getElementById('email').value;
                const firstName = document.getElementById('firstName').value;
                const lastName = document.getElementById('lastName').value;
                
                if (!email || !firstName || !lastName) {
                  alert('Please fill in all fields');
                  return;
                }
                
                window.opener.postMessage({
                  type: 'GOOGLE_AUTH_SUCCESS',
                  data: {
                    email: email,
                    firstName: firstName,
                    lastName: lastName,
                    googleId: 'google_' + Date.now()
                  }
                }, '*');
                
                window.close();
              }
            </script>
          </body>
        </html>
      `)

      // Listen for message from popup
      const handleMessage = async (event: MessageEvent) => {
        if (event.data.type === 'GOOGLE_AUTH_SUCCESS') {
          window.removeEventListener('message', handleMessage)
          
          try {
            const { email, firstName, lastName, googleId } = event.data.data

            // Send to backend
            const response = await axios.post(`${API_BASE_URL}/api/auth/google`, {
              email,
              firstName,
              lastName,
              googleId,
              userType: 'CANDIDATE'
            })

            const { access_token, refresh_token, user } = response.data

            // Store tokens and user data
            localStorage.setItem('accessToken', access_token)
            localStorage.setItem('refreshToken', refresh_token)
            localStorage.setItem('userData', JSON.stringify(user))

            // Set default authorization header
            axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

            dispatch({ type: 'AUTH_SUCCESS', payload: user })
            console.log('Google login complete:', user)
          } catch (error: any) {
            console.error('Google auth error:', error)
            const errorMessage = error.response?.data?.detail || error.message || 'Google login failed'
            dispatch({ type: 'AUTH_FAILURE', payload: errorMessage })
          }
        }
      }

      window.addEventListener('message', handleMessage)

      // Clean up if popup is closed without completing auth
      const checkPopup = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkPopup)
          window.removeEventListener('message', handleMessage)
          if (state.isLoading) {
            dispatch({ type: 'AUTH_FAILURE', payload: 'Authentication cancelled' })
          }
        }
      }, 500)

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
