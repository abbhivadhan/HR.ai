'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Assessment, 
  Question, 
  QuestionType, 
  AssessmentStatus,
  NextQuestionResponse,
  SubmitResponseRequest 
} from '../../types/assessment';
import assessmentService from '../../services/assessmentService';
import SkillAssessment from './SkillAssessment';
import AccessibilityHelper from './AccessibilityHelper';
import ProgressTracker from './ProgressTracker';

interface TestInterfaceProps {
  assessmentId: string;
}

interface QuestionComponentProps {
  question: Question;
  onSubmit: (response: SubmitResponseRequest['response']) => void;
  timeRemaining: number;
}

const MultipleChoiceQuestion: React.FC<QuestionComponentProps> = ({ 
  question, 
  onSubmit, 
  timeRemaining 
}) => {
  const [selectedOption, setSelectedOption] = useState<string>('');

  const handleSubmit = () => {
    if (selectedOption) {
      onSubmit({ selected_options: [selectedOption] });
    }
  };

  return (
    <div className="space-y-6">
      <div className="prose max-w-none">
        <h3 className="text-xl font-semibold text-gray-900">{question.title}</h3>
        <div className="mt-4 text-gray-700 whitespace-pre-wrap">
          {question.content}
        </div>
      </div>

      <div className="space-y-3">
        {question.options && Object.entries(question.options).map(([key, value]) => (
          <label
            key={key}
            className={`flex items-center p-4 border rounded-lg cursor-pointer transition-colors ${
              selectedOption === key
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <input
              type="radio"
              name="answer"
              value={key}
              checked={selectedOption === key}
              onChange={(e) => setSelectedOption(e.target.value)}
              className="mr-3 text-blue-600"
            />
            <span className="font-medium text-gray-900 mr-2">{key}.</span>
            <span className="text-gray-700">{value}</span>
          </label>
        ))}
      </div>

      <button
        onClick={handleSubmit}
        disabled={!selectedOption}
        className="w-full py-3 px-6 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        Submit Answer
      </button>
    </div>
  );
};

const CodingQuestion: React.FC<QuestionComponentProps> = ({ 
  question, 
  onSubmit, 
  timeRemaining 
}) => {
  const [code, setCode] = useState(question.code_template || '');

  const handleSubmit = () => {
    onSubmit({ code_solution: code });
  };

  return (
    <div className="space-y-6">
      <div className="prose max-w-none">
        <h3 className="text-xl font-semibold text-gray-900">{question.title}</h3>
        <div className="mt-4 text-gray-700 whitespace-pre-wrap">
          {question.content}
        </div>
      </div>

      {question.test_cases && question.test_cases.length > 0 && (
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-2">Test Cases:</h4>
          <div className="space-y-2">
            {question.test_cases.map((testCase, index) => (
              <div key={index} className="text-sm font-mono">
                <span className="text-gray-600">Input:</span> {testCase.input} →{' '}
                <span className="text-gray-600">Expected:</span> {testCase.expected}
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Your Solution:
        </label>
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="w-full h-64 p-4 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Write your code here..."
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={!code.trim()}
        className="w-full py-3 px-6 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        Submit Solution
      </button>
    </div>
  );
};

const TextResponseQuestion: React.FC<QuestionComponentProps> = ({ 
  question, 
  onSubmit, 
  timeRemaining 
}) => {
  const [response, setResponse] = useState('');

  const handleSubmit = () => {
    if (response.trim()) {
      onSubmit({ response_text: response });
    }
  };

  return (
    <div className="space-y-6">
      <div className="prose max-w-none">
        <h3 className="text-xl font-semibold text-gray-900">{question.title}</h3>
        <div className="mt-4 text-gray-700 whitespace-pre-wrap">
          {question.content}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Your Response:
        </label>
        <textarea
          value={response}
          onChange={(e) => setResponse(e.target.value)}
          className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Type your answer here..."
        />
        <div className="mt-2 text-sm text-gray-500">
          {response.length} characters
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={!response.trim()}
        className="w-full py-3 px-6 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        Submit Response
      </button>
    </div>
  );
};

const TestInterface: React.FC<TestInterfaceProps> = ({ assessmentId }) => {
  const router = useRouter();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoSaveStatus, setAutoSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showTimeWarning, setShowTimeWarning] = useState(false);
  const [showAccessibilityHelper, setShowAccessibilityHelper] = useState(false);
  const [focusedElement, setFocusedElement] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<NodeJS.Timeout>();
  const questionRef = useRef<HTMLDivElement>(null);

  // Enhanced timer effect with multiple warnings
  useEffect(() => {
    if (timeRemaining > 0) {
      timerRef.current = setInterval(() => {
        setTimeRemaining(prev => {
          const newTime = prev - 1;
          
          // Show warning when 5 minutes remaining
          if (newTime === 300 && !showTimeWarning) {
            setShowTimeWarning(true);
            // Announce to screen readers
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'assertive');
            announcement.setAttribute('aria-atomic', 'true');
            announcement.className = 'sr-only';
            announcement.textContent = '5 minutes remaining in assessment';
            document.body.appendChild(announcement);
            setTimeout(() => document.body.removeChild(announcement), 1000);
          }
          
          // Additional warnings for better UX
          if (newTime === 60) {
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'assertive');
            announcement.className = 'sr-only';
            announcement.textContent = '1 minute remaining in assessment';
            document.body.appendChild(announcement);
            setTimeout(() => document.body.removeChild(announcement), 1000);
          }
          
          if (newTime <= 0) {
            handleTimeUp();
            return 0;
          }
          return newTime;
        });
      }, 1000);

      return () => {
        if (timerRef.current) {
          clearInterval(timerRef.current);
        }
      };
    }
  }, [timeRemaining, showTimeWarning]);

  const handleTimeUp = useCallback(async () => {
    try {
      await assessmentService.completeAssessment(assessmentId);
      router.push(`/assessments/${assessmentId}/results`);
    } catch (error) {
      console.error('Error completing assessment on timeout:', error);
    }
  }, [assessmentId, router]);

  // Load assessment and start session
  useEffect(() => {
    const initializeAssessment = async () => {
      try {
        setLoading(true);
        
        // Get assessment details
        const assessmentData = await assessmentService.getAssessment(assessmentId);
        setAssessment(assessmentData);

        if (assessmentData.status === AssessmentStatus.NOT_STARTED) {
          // Start the assessment
          const startResponse = await assessmentService.startAssessment(assessmentId);
          setCurrentQuestion(startResponse.first_question);
          setTimeRemaining(Math.floor((new Date(startResponse.expires_at).getTime() - Date.now()) / 1000));
        } else if (assessmentData.status === AssessmentStatus.IN_PROGRESS) {
          // Resume assessment - get current question
          const nextResponse = await assessmentService.getNextQuestion(assessmentId, currentIndex);
          setCurrentQuestion(nextResponse.question || null);
          setTimeRemaining(nextResponse.time_remaining_seconds);
        } else if (assessmentData.status === AssessmentStatus.COMPLETED) {
          // Redirect to results
          router.push(`/assessments/${assessmentId}/results`);
          return;
        } else {
          setError('Assessment is not available');
          return;
        }
      } catch (error) {
        console.error('Error initializing assessment:', error);
        setError(error instanceof Error ? error.message : 'Failed to load assessment');
      } finally {
        setLoading(false);
      }
    };

    initializeAssessment();
  }, [assessmentId, router]);

  // Auto-save functionality
  const handleAutoSave = useCallback(async (responseData: SubmitResponseRequest['response']) => {
    if (!currentQuestion) return;

    try {
      setAutoSaveStatus('saving');
      
      // Save draft response (you'd need to implement this endpoint)
      await assessmentService.saveDraftResponse(assessmentId, {
        question_id: currentQuestion.id,
        response: responseData
      });
      
      setAutoSaveStatus('saved');
      
      // Reset status after 2 seconds
      setTimeout(() => setAutoSaveStatus('idle'), 2000);
    } catch (error) {
      console.error('Auto-save failed:', error);
      setAutoSaveStatus('error');
      setTimeout(() => setAutoSaveStatus('idle'), 3000);
    }
  }, [assessmentId, currentQuestion]);

  const handleSubmitResponse = async (responseData: SubmitResponseRequest['response']) => {
    if (!currentQuestion || !assessment) return;

    try {
      setSubmitting(true);
      
      // Submit the response
      await assessmentService.submitResponse(assessmentId, {
        question_id: currentQuestion.id,
        response: responseData
      });

      // Get next question
      const nextResponse = await assessmentService.getNextQuestion(assessmentId, currentIndex);
      
      if (nextResponse.question) {
        setCurrentQuestion(nextResponse.question);
        setCurrentIndex(nextResponse.question_index);
        setTimeRemaining(nextResponse.time_remaining_seconds);
        setAutoSaveStatus('idle'); // Reset auto-save status for new question
        
        // Focus management for accessibility
        setTimeout(() => {
          questionRef.current?.focus();
          // Announce new question to screen readers
          const announcement = document.createElement('div');
          announcement.setAttribute('aria-live', 'polite');
          announcement.className = 'sr-only';
          announcement.textContent = `Question ${nextResponse.question_index + 1}: ${nextResponse.question?.title}`;
          document.body.appendChild(announcement);
          setTimeout(() => document.body.removeChild(announcement), 1000);
        }, 100);
      } else {
        // Assessment completed
        const results = await assessmentService.completeAssessment(assessmentId);
        router.push(`/assessments/${assessmentId}/results`);
      }
    } catch (error) {
      console.error('Error submitting response:', error);
      setError(error instanceof Error ? error.message : 'Failed to submit response');
    } finally {
      setSubmitting(false);
    }
  };

  // Fullscreen functionality
  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen().then(() => {
        setIsFullscreen(true);
      }).catch(err => {
        console.error('Error attempting to enable fullscreen:', err);
      });
    } else {
      document.exitFullscreen().then(() => {
        setIsFullscreen(false);
      });
    }
  }, []);

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Enhanced keyboard shortcuts and accessibility
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Fullscreen toggle
      if (e.key === 'F11') {
        e.preventDefault();
        toggleFullscreen();
      }
      
      // Accessibility shortcuts
      if (e.altKey) {
        switch (e.key) {
          case 't':
            // Alt+T: Focus on timer
            e.preventDefault();
            const timerElement = document.querySelector('[aria-label*="Time remaining"]') as HTMLElement;
            timerElement?.focus();
            break;
          case 'p':
            // Alt+P: Announce progress
            e.preventDefault();
            const progressText = `Question ${currentIndex + 1} of ${assessment?.total_questions}`;
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'polite');
            announcement.className = 'sr-only';
            announcement.textContent = progressText;
            document.body.appendChild(announcement);
            setTimeout(() => document.body.removeChild(announcement), 1000);
            break;
          case 'h':
            // Alt+H: Show accessibility helper
            e.preventDefault();
            setShowAccessibilityHelper(true);
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [toggleFullscreen, currentIndex, assessment?.total_questions]);

  const renderQuestion = () => {
    if (!currentQuestion) return null;

    const props = {
      question: currentQuestion,
      onSubmit: handleSubmitResponse,
      timeRemaining,
      onAutoSave: handleAutoSave,
      autoSaveInterval: 30000 // 30 seconds
    };

    // Use SkillAssessment for interactive challenges, fallback to original components
    if (currentQuestion.question_type === QuestionType.CODING || 
        currentQuestion.category === 'interactive') {
      return <SkillAssessment {...props} />;
    }

    switch (currentQuestion.question_type) {
      case QuestionType.MULTIPLE_CHOICE:
        return <MultipleChoiceQuestion {...props} />;
      case QuestionType.TEXT_RESPONSE:
        return <TextResponseQuestion {...props} />;
      default:
        return <TextResponseQuestion {...props} />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading assessment...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Assessment Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.push('/assessments')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Assessments
          </button>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className={`min-h-screen bg-gray-50 ${isFullscreen ? 'bg-white' : ''}`}
      role="main"
      aria-label="Assessment interface"
    >
      {/* Time Warning Modal */}
      {showTimeWarning && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          role="dialog"
          aria-modal="true"
          aria-labelledby="time-warning-title"
        >
          <div className="bg-white rounded-lg p-6 max-w-md mx-4">
            <div className="flex items-center mb-4">
              <div className="text-orange-500 text-2xl mr-3">⏰</div>
              <h2 id="time-warning-title" className="text-lg font-semibold text-gray-900">
                Time Warning
              </h2>
            </div>
            <p className="text-gray-600 mb-4">
              You have 5 minutes remaining to complete this assessment.
            </p>
            <button
              onClick={() => setShowTimeWarning(false)}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              autoFocus
            >
              Continue Assessment
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                {assessment?.title}
              </h1>
              <p className="text-sm text-gray-600">
                Question {currentIndex + 1} of {assessment?.total_questions}
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Auto-save status */}
              {autoSaveStatus !== 'idle' && (
                <div className="flex items-center text-sm">
                  {autoSaveStatus === 'saving' && (
                    <span className="text-blue-600 flex items-center">
                      <svg className="animate-spin -ml-1 mr-1 h-3 w-3 text-blue-600" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Saving...
                    </span>
                  )}
                  {autoSaveStatus === 'saved' && (
                    <span className="text-green-600">✓ Saved</span>
                  )}
                  {autoSaveStatus === 'error' && (
                    <span className="text-red-600">⚠ Save failed</span>
                  )}
                </div>
              )}

              {/* Enhanced Progress bar with tooltip */}
              <div className="relative group">
                <div className="w-32 bg-gray-200 rounded-full h-2" role="progressbar" 
                     aria-valuenow={assessmentService.calculateProgress(currentIndex + 1, assessment?.total_questions || 1)}
                     aria-valuemin={0} aria-valuemax={100}
                     aria-label={`Assessment progress: ${currentIndex + 1} of ${assessment?.total_questions} questions completed`}>
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${assessmentService.calculateProgress(currentIndex + 1, assessment?.total_questions || 1)}%`
                    }}
                  ></div>
                </div>
                {/* Progress tooltip */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                  {assessmentService.calculateProgress(currentIndex + 1, assessment?.total_questions || 1)}% Complete
                </div>
              </div>
              
              {/* Timer */}
              <div 
                className={`text-lg font-mono ${timeRemaining < 300 ? 'text-red-600' : 'text-gray-900'}`}
                aria-live="polite"
                aria-label={`Time remaining: ${assessmentService.formatTimeRemaining(timeRemaining)}`}
              >
                {assessmentService.formatTimeRemaining(timeRemaining)}
              </div>

              {/* Accessibility Helper */}
              <button
                onClick={() => setShowAccessibilityHelper(true)}
                className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
                aria-label="Open accessibility settings and help"
                title="Accessibility settings and keyboard shortcuts (Alt+H)"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>

              {/* Fullscreen toggle */}
              <button
                onClick={toggleFullscreen}
                className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
                aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
                title={isFullscreen ? 'Exit fullscreen (F11)' : 'Enter fullscreen (F11)'}
              >
                {isFullscreen ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Question content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          {submitting ? (
            <div className="text-center py-8" role="status" aria-live="polite">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Submitting response...</p>
            </div>
          ) : (
            <div 
              ref={questionRef}
              role="region" 
              aria-label="Current question"
              tabIndex={-1}
              className="focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-lg"
            >
              {renderQuestion()}
            </div>
          )}
        </div>
      </main>

      {/* Skip to content link for screen readers */}
      <a 
        href="#main-content" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded-lg z-50"
      >
        Skip to main content
      </a>

      {/* Accessibility Helper */}
      <AccessibilityHelper
        isVisible={showAccessibilityHelper}
        onClose={() => setShowAccessibilityHelper(false)}
      />
    </div>
  );
};

export default TestInterface;