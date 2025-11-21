'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { 
  CalendarDaysIcon,
  ClockIcon,
  VideoCameraIcon,
  PhoneIcon,
  MapPinIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'

export default function ScheduleInterviewPage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [interview, setInterview] = useState({
    jobTitle: 'Senior Frontend Developer',
    company: 'TechCorp Inc.',
    type: 'video',
    date: '',
    time: '',
    duration: '60',
    timezone: 'PST',
    notes: '',
    interviewers: ['Sarah Johnson - Engineering Manager', 'Mike Chen - Senior Developer']
  })

  const [availability, setAvailability] = useState({
    preferredDays: [] as string[],
    preferredTimes: [] as string[],
    unavailableDates: [] as string[]
  })

  const [submitted, setSubmitted] = useState(false)

  const timeSlots = [
    '9:00 AM', '9:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM',
    '12:00 PM', '12:30 PM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM',
    '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM', '5:00 PM'
  ]

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

  const handleSubmit = async () => {
    // Simulate submission
    await new Promise(resolve => setTimeout(resolve, 1500))
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 text-center max-w-md mx-4"
        >
          <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Interview Scheduled!
          </h2>
          <p className="text-gray-600 mb-6">
            Your interview for {interview.jobTitle} at {interview.company} has been scheduled. 
            You'll receive a confirmation email shortly.
          </p>
          <div className="flex gap-3">
            <button
              onClick={() => router.push('/dashboard')}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go to Dashboard
            </button>
            <button
              onClick={() => router.push('/interviews')}
              className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              View Interviews
            </button>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Schedule Interview
          </h1>
          <p className="text-gray-600">
            Let's find the perfect time for your interview
          </p>
        </motion.div>

        {/* Progress Steps */}
        <div className="flex justify-center mb-8">
          <div className="flex items-center space-x-4">
            {[1, 2, 3].map((stepNumber) => (
              <div key={stepNumber} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step >= stepNumber 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {stepNumber}
                </div>
                {stepNumber < 3 && (
                  <div className={`w-12 h-1 mx-2 ${
                    step > stepNumber ? 'bg-blue-600' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Job Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg p-6 mb-8"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Interview Details
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Position</p>
              <p className="font-medium text-gray-900">{interview.jobTitle}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Company</p>
              <p className="font-medium text-gray-900">{interview.company}</p>
            </div>
            <div className="md:col-span-2">
              <p className="text-sm text-gray-600 mb-2">Interviewers</p>
              <div className="space-y-1">
                {interview.interviewers.map((interviewer, index) => (
                  <p key={index} className="text-gray-900">{interviewer}</p>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Step Content */}
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
        >
          {step === 1 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
                Choose Interview Type
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  {
                    type: 'video',
                    icon: <VideoCameraIcon className="w-8 h-8" />,
                    title: 'Video Call',
                    description: 'Meet via Zoom, Google Meet, or Teams'
                  },
                  {
                    type: 'phone',
                    icon: <PhoneIcon className="w-8 h-8" />,
                    title: 'Phone Call',
                    description: 'Traditional phone interview'
                  },
                  {
                    type: 'in-person',
                    icon: <MapPinIcon className="w-8 h-8" />,
                    title: 'In Person',
                    description: 'Meet at the company office'
                  }
                ].map((option) => (
                  <button
                    key={option.type}
                    onClick={() => setInterview(prev => ({ ...prev, type: option.type }))}
                    className={`p-6 border-2 rounded-xl text-center transition-all ${
                      interview.type === option.type
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className={`mb-3 ${
                      interview.type === option.type ? 'text-blue-600' : 'text-gray-400'
                    }`}>
                      {option.icon}
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-2">{option.title}</h4>
                    <p className="text-sm text-gray-600">{option.description}</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
                Select Your Availability
              </h3>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Preferred Days
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {days.map((day) => (
                      <button
                        key={day}
                        onClick={() => {
                          const newDays = availability.preferredDays.includes(day)
                            ? availability.preferredDays.filter(d => d !== day)
                            : [...availability.preferredDays, day]
                          setAvailability(prev => ({ ...prev, preferredDays: newDays }))
                        }}
                        className={`px-4 py-2 rounded-lg border transition-colors ${
                          availability.preferredDays.includes(day)
                            ? 'bg-blue-100 border-blue-500 text-blue-700'
                            : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        {day}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Preferred Times
                  </label>
                  <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
                    {timeSlots.map((time) => (
                      <button
                        key={time}
                        onClick={() => {
                          const newTimes = availability.preferredTimes.includes(time)
                            ? availability.preferredTimes.filter(t => t !== time)
                            : [...availability.preferredTimes, time]
                          setAvailability(prev => ({ ...prev, preferredTimes: newTimes }))
                        }}
                        className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                          availability.preferredTimes.includes(time)
                            ? 'bg-blue-100 border-blue-500 text-blue-700'
                            : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        {time}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Interview Duration
                  </label>
                  <select
                    value={interview.duration}
                    onChange={(e) => setInterview(prev => ({ ...prev, duration: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="30">30 minutes</option>
                    <option value="45">45 minutes</option>
                    <option value="60">1 hour</option>
                    <option value="90">1.5 hours</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
                Additional Information
              </h3>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Timezone
                  </label>
                  <select
                    value={interview.timezone}
                    onChange={(e) => setInterview(prev => ({ ...prev, timezone: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="PST">Pacific Standard Time (PST)</option>
                    <option value="MST">Mountain Standard Time (MST)</option>
                    <option value="CST">Central Standard Time (CST)</option>
                    <option value="EST">Eastern Standard Time (EST)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Special Notes or Requirements (Optional)
                  </label>
                  <textarea
                    rows={4}
                    value={interview.notes}
                    onChange={(e) => setInterview(prev => ({ ...prev, notes: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Any special accommodations, questions, or notes for the interviewer..."
                  />
                </div>

                {/* Summary */}
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Interview Summary</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Type:</span>
                      <span className="text-gray-900 dark:text-white capitalize">{interview.type} interview</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Duration:</span>
                      <span className="text-gray-900 dark:text-white">{interview.duration} minutes</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Timezone:</span>
                      <span className="text-gray-900 dark:text-white">{interview.timezone}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Preferred Days:</span>
                      <span className="text-gray-900 dark:text-white">
                        {availability.preferredDays.length > 0 
                          ? availability.preferredDays.join(', ')
                          : 'Any day'
                        }
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
            <button
              onClick={() => step > 1 ? setStep(step - 1) : router.back()}
              className="px-6 py-3 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              {step === 1 ? 'Back' : 'Previous'}
            </button>
            
            {step < 3 ? (
              <button
                onClick={() => setStep(step + 1)}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Schedule Interview
              </button>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}