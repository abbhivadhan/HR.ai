'use client'

import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth, RegisterData } from '@/contexts/AuthContext'
import { EyeIcon, EyeSlashIcon, CheckIcon } from '@heroicons/react/24/outline'
import GoogleButton from './GoogleButton'

// Validation schemas for each step
const step1Schema = z.object({
  userType: z.enum(['CANDIDATE', 'COMPANY'], {
    required_error: 'Please select your account type',
  }),
})

const step2Schema = z.object({
  firstName: z.string().min(2, 'First name must be at least 2 characters'),
  lastName: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
})

const step3Schema = z.object({
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
  confirmPassword: z.string(),
  agreeToTerms: z.boolean().refine(val => val === true, {
    message: 'You must agree to the terms and conditions',
  }),
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})

type Step1Data = z.infer<typeof step1Schema>
type Step2Data = z.infer<typeof step2Schema>
type Step3Data = z.infer<typeof step3Schema>
type RegisterFormData = Step1Data & Step2Data & Step3Data

interface RegisterFormProps {
  onSuccess?: () => void
  onSwitchToLogin?: () => void
}

const steps = [
  { id: 1, title: 'Account Type', description: 'Choose your account type' },
  { id: 2, title: 'Personal Info', description: 'Tell us about yourself' },
  { id: 3, title: 'Security', description: 'Create a secure password' },
]

export default function RegisterForm({ onSuccess, onSwitchToLogin }: RegisterFormProps) {
  const { register: registerUser, loginWithGoogle, isLoading, error, clearError } = useAuth()
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<Partial<RegisterFormData>>({})
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  // Step 1 form
  const step1Form = useForm<Step1Data>({
    resolver: zodResolver(step1Schema),
    defaultValues: formData,
  })

  // Step 2 form
  const step2Form = useForm<Step2Data>({
    resolver: zodResolver(step2Schema),
    defaultValues: formData,
  })

  // Step 3 form
  const step3Form = useForm<Step3Data>({
    resolver: zodResolver(step3Schema),
    defaultValues: formData,
  })

  const handleStep1Submit = (data: Step1Data) => {
    setFormData(prev => ({ ...prev, ...data }))
    setCurrentStep(2)
  }

  const handleStep2Submit = (data: Step2Data) => {
    setFormData(prev => ({ ...prev, ...data }))
    setCurrentStep(3)
  }

  const handleStep3Submit = async (data: Step3Data) => {
    try {
      clearError()
      const completeData = { ...formData, ...data } as RegisterFormData
      
      const registerData: RegisterData = {
        email: completeData.email,
        password: completeData.password,
        firstName: completeData.firstName,
        lastName: completeData.lastName,
        userType: completeData.userType,
      }

      await registerUser(registerData)
      onSuccess?.()
    } catch (error) {
      // Error is handled by the auth context
    }
  }

  const goToPreviousStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleGoogleSignup = async () => {
    try {
      clearError()
      await loginWithGoogle()
    } catch (error) {
      // Error is handled by the auth context
    }
  }

  const getPasswordStrength = (password: string) => {
    let strength = 0
    if (password.length >= 8) strength++
    if (/[A-Z]/.test(password)) strength++
    if (/[a-z]/.test(password)) strength++
    if (/[0-9]/.test(password)) strength++
    if (/[^A-Za-z0-9]/.test(password)) strength++
    return strength
  }

  const renderProgressBar = () => (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-2">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                currentStep > step.id
                  ? 'bg-green-500 text-white'
                  : currentStep === step.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {currentStep > step.id ? (
                <CheckIcon className="w-4 h-4" />
              ) : (
                step.id
              )}
            </div>
            {index < steps.length - 1 && (
              <div
                className={`w-16 h-1 mx-2 ${
                  currentStep > step.id ? 'bg-green-500' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900">
          {steps[currentStep - 1].title}
        </h3>
        <p className="text-sm text-gray-600">
          {steps[currentStep - 1].description}
        </p>
      </div>
    </div>
  )

  const renderStep1 = () => (
    <form onSubmit={step1Form.handleSubmit(handleStep1Submit)} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-4">
          I want to join as a:
        </label>
        <div className="grid grid-cols-1 gap-4">
          <motion.label
            whileHover={{ scale: 1.02 }}
            className={`relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors ${
              step1Form.watch('userType') === 'CANDIDATE'
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <input
              {...step1Form.register('userType')}
              type="radio"
              value="CANDIDATE"
              className="sr-only"
            />
            <div className="flex-1">
              <div className="flex items-center">
                <div className="text-lg font-medium text-gray-900">Candidate</div>
              </div>
              <div className="text-sm text-gray-600 mt-1">
                Looking for job opportunities and want to showcase my skills
              </div>
            </div>
          </motion.label>

          <motion.label
            whileHover={{ scale: 1.02 }}
            className={`relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors ${
              step1Form.watch('userType') === 'COMPANY'
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <input
              {...step1Form.register('userType')}
              type="radio"
              value="COMPANY"
              className="sr-only"
            />
            <div className="flex-1">
              <div className="flex items-center">
                <div className="text-lg font-medium text-gray-900">Company</div>
              </div>
              <div className="text-sm text-gray-600 mt-1">
                Hiring talent and want to find the best candidates
              </div>
            </div>
          </motion.label>
        </div>
        {step1Form.formState.errors.userType && (
          <p className="mt-2 text-sm text-red-600">
            {step1Form.formState.errors.userType.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        className="w-full btn-primary py-3"
      >
        Continue
      </button>
    </form>
  )

  const renderStep2 = () => (
    <form onSubmit={step2Form.handleSubmit(handleStep2Submit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-1">
            First Name
          </label>
          <input
            {...step2Form.register('firstName')}
            type="text"
            id="firstName"
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors ${
              step2Form.formState.errors.firstName ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="John"
          />
          {step2Form.formState.errors.firstName && (
            <p className="mt-1 text-sm text-red-600">
              {step2Form.formState.errors.firstName.message}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-1">
            Last Name
          </label>
          <input
            {...step2Form.register('lastName')}
            type="text"
            id="lastName"
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors ${
              step2Form.formState.errors.lastName ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Doe"
          />
          {step2Form.formState.errors.lastName && (
            <p className="mt-1 text-sm text-red-600">
              {step2Form.formState.errors.lastName.message}
            </p>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email Address
        </label>
        <input
          {...step2Form.register('email')}
          type="email"
          id="email"
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors ${
            step2Form.formState.errors.email ? 'border-red-300' : 'border-gray-300'
          }`}
          placeholder="john.doe@example.com"
        />
        {step2Form.formState.errors.email && (
          <p className="mt-1 text-sm text-red-600">
            {step2Form.formState.errors.email.message}
          </p>
        )}
      </div>

      <div className="flex space-x-4">
        <button
          type="button"
          onClick={goToPreviousStep}
          className="flex-1 btn-secondary py-3"
        >
          Back
        </button>
        <button
          type="submit"
          className="flex-1 btn-primary py-3"
        >
          Continue
        </button>
      </div>
    </form>
  )

  const renderStep3 = () => {
    const password = step3Form.watch('password') || ''
    const passwordStrength = getPasswordStrength(password)

    return (
      <form onSubmit={step3Form.handleSubmit(handleStep3Submit)} className="space-y-4">
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <div className="relative">
            <input
              {...step3Form.register('password')}
              type={showPassword ? 'text' : 'password'}
              id="password"
              className={`w-full px-3 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors ${
                step3Form.formState.errors.password ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Create a strong password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {showPassword ? (
                <EyeSlashIcon className="h-5 w-5 text-gray-400" />
              ) : (
                <EyeIcon className="h-5 w-5 text-gray-400" />
              )}
            </button>
          </div>
          
          {/* Password Strength Indicator */}
          {password && (
            <div className="mt-2">
              <div className="flex space-x-1">
                {[1, 2, 3, 4, 5].map((level) => (
                  <div
                    key={level}
                    className={`h-1 flex-1 rounded ${
                      passwordStrength >= level
                        ? passwordStrength <= 2
                          ? 'bg-red-500'
                          : passwordStrength <= 3
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                        : 'bg-gray-200'
                    }`}
                  />
                ))}
              </div>
              <p className="text-xs text-gray-600 mt-1">
                Password strength: {
                  passwordStrength <= 2 ? 'Weak' :
                  passwordStrength <= 3 ? 'Medium' : 'Strong'
                }
              </p>
            </div>
          )}
          
          {step3Form.formState.errors.password && (
            <p className="mt-1 text-sm text-red-600">
              {step3Form.formState.errors.password.message}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
            Confirm Password
          </label>
          <div className="relative">
            <input
              {...step3Form.register('confirmPassword')}
              type={showConfirmPassword ? 'text' : 'password'}
              id="confirmPassword"
              className={`w-full px-3 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors ${
                step3Form.formState.errors.confirmPassword ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Confirm your password"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {showConfirmPassword ? (
                <EyeSlashIcon className="h-5 w-5 text-gray-400" />
              ) : (
                <EyeIcon className="h-5 w-5 text-gray-400" />
              )}
            </button>
          </div>
          {step3Form.formState.errors.confirmPassword && (
            <p className="mt-1 text-sm text-red-600">
              {step3Form.formState.errors.confirmPassword.message}
            </p>
          )}
        </div>

        <div className="flex items-start">
          <input
            {...step3Form.register('agreeToTerms')}
            id="agreeToTerms"
            type="checkbox"
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded mt-1"
          />
          <label htmlFor="agreeToTerms" className="ml-2 block text-sm text-gray-700">
            I agree to the{' '}
            <a href="/terms" className="text-primary-600 hover:text-primary-500">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="/privacy" className="text-primary-600 hover:text-primary-500">
              Privacy Policy
            </a>
          </label>
        </div>
        {step3Form.formState.errors.agreeToTerms && (
          <p className="text-sm text-red-600">
            {step3Form.formState.errors.agreeToTerms.message}
          </p>
        )}

        <div className="flex space-x-4">
          <button
            type="button"
            onClick={goToPreviousStep}
            className="flex-1 btn-secondary py-3"
          >
            Back
          </button>
          <button
            type="submit"
            disabled={step3Form.formState.isSubmitting || isLoading}
            className="flex-1 btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {step3Form.formState.isSubmitting || isLoading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Creating Account...
              </div>
            ) : (
              'Create Account'
            )}
          </button>
        </div>
      </form>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="w-full max-w-md mx-auto"
    >
      <div className="card">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Create Account
          </h2>
          <p className="text-gray-600">
            Join our AI-powered recruitment platform
          </p>
        </div>

        {renderProgressBar()}

        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg"
          >
            <p className="text-sm text-red-600">{error}</p>
          </motion.div>
        )}

        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
          >
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}
          </motion.div>
        </AnimatePresence>

        {/* Google Sign Up - Show only on first step */}
        {currentStep === 1 && (
          <>
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or</span>
              </div>
            </div>

            <GoogleButton
              onClick={handleGoogleSignup}
              disabled={isLoading}
              text="Continue with Google"
            />
          </>
        )}

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <button
              onClick={onSwitchToLogin}
              className="text-primary-600 hover:text-primary-500 font-medium"
            >
              Sign in here
            </button>
          </p>
        </div>
      </div>
    </motion.div>
  )
}