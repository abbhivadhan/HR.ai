'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  CalendarIcon,
  ClockIcon,
  UserIcon,
  BuildingOfficeIcon,
  VideoCameraIcon,
  CheckCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import {
  Interview,
  CreateInterviewRequest,
  InterviewType,
  InterviewStatus
} from '../../types/interview';
import { interviewService } from '../../services/interviewService';

interface InterviewSchedulerProps {
  jobApplicationId: string;
  candidateId: string;
  companyId: string;
  onScheduled: (interview: Interview) => void;
  onCancel: () => void;
}

export const InterviewScheduler: React.FC<InterviewSchedulerProps> = ({
  jobApplicationId,
  candidateId,
  companyId,
  onScheduled,
  onCancel
}) => {
  const [formData, setFormData] = useState<CreateInterviewRequest>({
    job_application_id: jobApplicationId,
    interview_type: InterviewType.AI_SCREENING,
    title: '',
    description: '',
    scheduled_at: '',
    duration_minutes: 30,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    ai_interviewer_persona: 'Professional Interviewer',
    difficulty_level: 'intermediate',
    focus_areas: [],
    max_questions: 10,
    allow_retakes: false,
    recording_enabled: true
  });

  const [availableSlots, setAvailableSlots] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState(1);

  const interviewTypes = [
    {
      type: InterviewType.AI_SCREENING,
      label: 'AI Screening',
      description: 'Initial screening with AI interviewer',
      duration: 30,
      icon: '🤖'
    },
    {
      type: InterviewType.AI_TECHNICAL,
      label: 'AI Technical',
      description: 'Technical skills assessment with AI',
      duration: 45,
      icon: 'TECH'
    },
    {
      type: InterviewType.AI_BEHAVIORAL,
      label: 'AI Behavioral',
      description: 'Behavioral assessment with AI interviewer',
      duration: 30,
      icon: '🧠'
    },
    {
      type: InterviewType.HUMAN_FINAL,
      label: 'Final Interview',
      description: 'Final interview with human interviewer',
      duration: 60,
      icon: 'HR'
    }
  ];

  const difficultyLevels = [
    { value: 'beginner', label: 'Beginner', description: 'Entry-level questions' },
    { value: 'intermediate', label: 'Intermediate', description: 'Standard difficulty' },
    { value: 'advanced', label: 'Advanced', description: 'Challenging questions' },
    { value: 'expert', label: 'Expert', description: 'Highly technical questions' }
  ];

  const commonFocusAreas = [
    'JavaScript', 'Python', 'React', 'Node.js', 'SQL', 'System Design',
    'Problem Solving', 'Communication', 'Leadership', 'Teamwork',
    'Project Management', 'Customer Service', 'Sales', 'Marketing'
  ];

  // Generate available time slots
  useEffect(() => {
    const generateTimeSlots = () => {
      const slots: string[] = [];
      const now = new Date();
      
      // Generate slots for the next 7 days
      for (let day = 1; day <= 7; day++) {
        const date = new Date(now);
        date.setDate(date.getDate() + day);
        
        // Skip weekends for business hours
        if (date.getDay() === 0 || date.getDay() === 6) continue;
        
        // Generate hourly slots from 9 AM to 5 PM
        for (let hour = 9; hour <= 17; hour++) {
          const slotTime = new Date(date);
          slotTime.setHours(hour, 0, 0, 0);
          slots.push(slotTime.toISOString());
        }
      }
      
      setAvailableSlots(slots);
    };

    generateTimeSlots();
  }, []);

  const handleInputChange = (field: keyof CreateInterviewRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleInterviewTypeChange = (type: InterviewType) => {
    const selectedType = interviewTypes.find(t => t.type === type);
    setFormData(prev => ({
      ...prev,
      interview_type: type,
      duration_minutes: selectedType?.duration || 30,
      title: `${selectedType?.label} Interview` || ''
    }));
  };

  const handleFocusAreaToggle = (area: string) => {
    setFormData(prev => ({
      ...prev,
      focus_areas: prev.focus_areas?.includes(area)
        ? prev.focus_areas.filter(a => a !== area)
        : [...(prev.focus_areas || []), area]
    }));
  };

  const handleSchedule = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const interview = await interviewService.createInterview(formData);
      onScheduled(interview);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to schedule interview');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDateTime = (isoString: string): string => {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      timeZoneName: 'short'
    });
  };

  const isFormValid = () => {
    return formData.title && formData.scheduled_at && formData.interview_type;
  };

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-blue-600 text-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <VideoCameraIcon className="h-6 w-6" />
            <div>
              <h2 className="text-xl font-semibold">Schedule Interview</h2>
              <p className="text-blue-100 text-sm">Set up an AI-powered interview session</p>
            </div>
          </div>
          <button
            onClick={onCancel}
            className="text-blue-100 hover:text-white rounded-md p-1"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>
      </div>

      {/* Progress indicator */}
      <div className="bg-gray-50 px-6 py-3">
        <div className="flex items-center space-x-4">
          {[1, 2, 3].map((stepNumber) => (
            <div key={stepNumber} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step >= stepNumber
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-300 text-gray-600'
              }`}>
                {step > stepNumber ? (
                  <CheckCircleIcon className="h-5 w-5" />
                ) : (
                  stepNumber
                )}
              </div>
              {stepNumber < 3 && (
                <div className={`w-12 h-1 mx-2 ${
                  step > stepNumber ? 'bg-blue-600' : 'bg-gray-300'
                }`} />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between mt-2 text-sm text-gray-600">
          <span>Interview Type</span>
          <span>Schedule & Settings</span>
          <span>Review & Confirm</span>
        </div>
      </div>

      <div className="p-6">
        {/* Step 1: Interview Type */}
        {step === 1 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Select Interview Type
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {interviewTypes.map((type) => (
                  <button
                    key={type.type}
                    onClick={() => handleInterviewTypeChange(type.type)}
                    className={`text-left p-4 border-2 rounded-lg transition-colors ${
                      formData.interview_type === type.type
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <span className="text-2xl">{type.icon}</span>
                      <div>
                        <h4 className="font-medium text-gray-900">{type.label}</h4>
                        <p className="text-sm text-gray-600 mt-1">{type.description}</p>
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                          <span className="flex items-center space-x-1">
                            <ClockIcon className="h-3 w-3" />
                            <span>{type.duration} min</span>
                          </span>
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setStep(2)}
                disabled={!formData.interview_type}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next: Schedule & Settings
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 2: Schedule & Settings */}
        {step === 2 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left column */}
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Interview Title
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter interview title"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description (Optional)
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    rows={3}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Additional details about the interview"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Scheduled Time
                  </label>
                  <div className="grid grid-cols-2 gap-3 max-h-48 overflow-y-auto border border-gray-200 rounded-lg p-3">
                    {availableSlots.map((slot) => (
                      <button
                        key={slot}
                        onClick={() => handleInputChange('scheduled_at', slot)}
                        className={`text-left p-2 text-sm rounded border ${
                          formData.scheduled_at === slot
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        {formatDateTime(slot)}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right column */}
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Duration
                  </label>
                  <select
                    value={formData.duration_minutes}
                    onChange={(e) => handleInputChange('duration_minutes', parseInt(e.target.value))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value={15}>15 minutes</option>
                    <option value={30}>30 minutes</option>
                    <option value={45}>45 minutes</option>
                    <option value={60}>60 minutes</option>
                    <option value={90}>90 minutes</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Difficulty Level
                  </label>
                  <select
                    value={formData.difficulty_level}
                    onChange={(e) => handleInputChange('difficulty_level', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {difficultyLevels.map((level) => (
                      <option key={level.value} value={level.value}>
                        {level.label} - {level.description}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Focus Areas
                  </label>
                  <div className="max-h-32 overflow-y-auto border border-gray-200 rounded-lg p-3">
                    <div className="grid grid-cols-2 gap-2">
                      {commonFocusAreas.map((area) => (
                        <label key={area} className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={formData.focus_areas?.includes(area) || false}
                            onChange={() => handleFocusAreaToggle(area)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="text-sm text-gray-700">{area}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Questions
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="50"
                    value={formData.max_questions}
                    onChange={(e) => handleInputChange('max_questions', parseInt(e.target.value))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-between">
              <button
                onClick={() => setStep(1)}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                disabled={!isFormValid()}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next: Review
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 3: Review & Confirm */}
        {step === 3 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Review Interview Details
              </h3>
              
              <div className="bg-gray-50 rounded-lg p-6 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-gray-900">Interview Type</h4>
                    <p className="text-gray-600">
                      {interviewTypes.find(t => t.type === formData.interview_type)?.label}
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Duration</h4>
                    <p className="text-gray-600">{formData.duration_minutes} minutes</p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Scheduled Time</h4>
                    <p className="text-gray-600">
                      {formData.scheduled_at ? formatDateTime(formData.scheduled_at) : 'Not selected'}
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Difficulty</h4>
                    <p className="text-gray-600 capitalize">{formData.difficulty_level}</p>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900">Title</h4>
                  <p className="text-gray-600">{formData.title}</p>
                </div>

                {formData.description && (
                  <div>
                    <h4 className="font-medium text-gray-900">Description</h4>
                    <p className="text-gray-600">{formData.description}</p>
                  </div>
                )}

                {formData.focus_areas && formData.focus_areas.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900">Focus Areas</h4>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {formData.focus_areas.map((area) => (
                        <span
                          key={area}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                        >
                          {area}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-600">{error}</p>
              </div>
            )}

            <div className="flex justify-between">
              <button
                onClick={() => setStep(2)}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400"
              >
                Back
              </button>
              <button
                onClick={handleSchedule}
                disabled={isLoading || !isFormValid()}
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Scheduling...</span>
                  </>
                ) : (
                  <>
                    <CheckCircleIcon className="h-5 w-5" />
                    <span>Schedule Interview</span>
                  </>
                )}
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};