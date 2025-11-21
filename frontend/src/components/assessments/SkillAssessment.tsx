'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Question, QuestionType, DifficultyLevel, SubmitResponseRequest } from '../../types/assessment';

interface SkillAssessmentProps {
  question: Question;
  onSubmit: (response: SubmitResponseRequest['response']) => void;
  timeRemaining: number;
  onAutoSave?: (response: SubmitResponseRequest['response']) => void;
  autoSaveInterval?: number; // in milliseconds
}

interface CodingChallengeProps extends SkillAssessmentProps {
  onRunTests?: (code: string) => Promise<{ passed: boolean; results: any[] }>;
}

const CodingChallenge: React.FC<CodingChallengeProps> = ({
  question,
  onSubmit,
  timeRemaining,
  onAutoSave,
  autoSaveInterval = 30000,
  onRunTests
}) => {
  const [code, setCode] = useState(question.code_template || '');
  const [testResults, setTestResults] = useState<{ passed: boolean; results: any[] } | null>(null);
  const [isRunningTests, setIsRunningTests] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout>();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-save functionality
  useEffect(() => {
    if (hasUnsavedChanges && onAutoSave) {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
      
      autoSaveTimeoutRef.current = setTimeout(async () => {
        try {
          await onAutoSave({ code_solution: code });
          setHasUnsavedChanges(false);
          setSaveError(null);
          setLastSavedAt(new Date());
        } catch (error) {
          setSaveError('Failed to auto-save. Please save manually.');
          console.error('Auto-save failed:', error);
        }
      }, autoSaveInterval);
    }

    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, [code, hasUnsavedChanges, onAutoSave, autoSaveInterval]);

  const handleCodeChange = (newCode: string) => {
    setCode(newCode);
    setHasUnsavedChanges(true);
    setTestResults(null);
  };

  const handleRunTests = async () => {
    if (!onRunTests) return;
    
    setIsRunningTests(true);
    try {
      const results = await onRunTests(code);
      setTestResults(results);
      
      // Announce test results to screen readers
      const announcement = document.createElement('div');
      announcement.setAttribute('aria-live', 'polite');
      announcement.className = 'sr-only';
      announcement.textContent = results.passed 
        ? 'All tests passed successfully' 
        : `${results.results.filter(r => !r.passed).length} tests failed`;
      document.body.appendChild(announcement);
      setTimeout(() => document.body.removeChild(announcement), 1000);
    } catch (error) {
      console.error('Error running tests:', error);
      setTestResults({
        passed: false,
        results: [{ passed: false, error: 'Failed to run tests. Please try again.' }]
      });
    } finally {
      setIsRunningTests(false);
    }
  };

  const handleSubmit = () => {
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
    onSubmit({ code_solution: code });
  };

  // Enhanced keyboard shortcuts with accessibility
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 's':
            e.preventDefault();
            if (onAutoSave) {
              onAutoSave({ code_solution: code });
              setHasUnsavedChanges(false);
              // Announce save to screen readers
              const announcement = document.createElement('div');
              announcement.setAttribute('aria-live', 'polite');
              announcement.className = 'sr-only';
              announcement.textContent = 'Code saved successfully';
              document.body.appendChild(announcement);
              setTimeout(() => document.body.removeChild(announcement), 1000);
            }
            break;
          case 'Enter':
            if (e.shiftKey) {
              e.preventDefault();
              handleRunTests();
            }
            break;
          case '/':
            // Ctrl+/ for help
            e.preventDefault();
            const helpText = 'Keyboard shortcuts:\nCtrl+S: Save code\nCtrl+Shift+Enter: Run tests\nCtrl+/: Show help';
            alert(helpText);
            break;
        }
      }
      
      // Accessibility: Escape to focus on submit button
      if (e.key === 'Escape' && textareaRef.current === document.activeElement) {
        const submitButton = document.querySelector('button[type="submit"], button:contains("Submit")') as HTMLElement;
        submitButton?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [code, onAutoSave]);

  return (
    <div className="space-y-6">
      {/* Question Header */}
      <div className="prose max-w-none">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-900 m-0">{question.title}</h3>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              question.difficulty_level === DifficultyLevel.BEGINNER ? 'bg-green-100 text-green-800' :
              question.difficulty_level === DifficultyLevel.INTERMEDIATE ? 'bg-yellow-100 text-yellow-800' :
              question.difficulty_level === DifficultyLevel.ADVANCED ? 'bg-orange-100 text-orange-800' :
              'bg-red-100 text-red-800'
            }`}>
              {question.difficulty_level}
            </span>
            <span className="text-sm text-gray-500">{question.max_points} points</span>
          </div>
        </div>
        <div className="text-gray-700 whitespace-pre-wrap">
          {question.content}
        </div>
      </div>

      {/* Test Cases */}
      {question.test_cases && question.test_cases.length > 0 && (
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-3">Test Cases:</h4>
          <div className="space-y-3">
            {question.test_cases.map((testCase, index) => (
              <div key={index} className="bg-white p-3 rounded border">
                <div className="text-sm font-mono space-y-1">
                  <div>
                    <span className="text-gray-600 font-medium">Input:</span>{' '}
                    <span className="text-blue-600">{testCase.input}</span>
                  </div>
                  <div>
                    <span className="text-gray-600 font-medium">Expected Output:</span>{' '}
                    <span className="text-green-600">{testCase.expected}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Code Editor */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="block text-sm font-medium text-gray-700">
            Your Solution:
          </label>
          <div className="flex items-center space-x-2 text-xs text-gray-500">
            {hasUnsavedChanges && (
              <span className="text-orange-600">● Unsaved changes</span>
            )}
            {saveError && (
              <span className="text-red-600">⚠ {saveError}</span>
            )}
            {lastSavedAt && !hasUnsavedChanges && !saveError && (
              <span className="text-green-600">✓ Saved at {lastSavedAt.toLocaleTimeString()}</span>
            )}
            <span>Ctrl+S to save • Ctrl+Shift+Enter to run tests • Ctrl+/ for help</span>
          </div>
        </div>
        
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={code}
            onChange={(e) => handleCodeChange(e.target.value)}
            className="w-full h-80 p-4 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            placeholder="Write your code here..."
            spellCheck={false}
            aria-label="Code editor"
            aria-describedby="code-editor-help"
          />
          <div id="code-editor-help" className="sr-only">
            Code editor for writing your solution. Use Ctrl+S to save and Ctrl+Shift+Enter to run tests.
          </div>
        </div>
      </div>

      {/* Test Results */}
      {testResults && (
        <div className={`p-4 rounded-lg border ${
          testResults.passed 
            ? 'bg-green-50 border-green-200' 
            : 'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-center mb-2">
            <span className={`text-lg mr-2 ${
              testResults.passed ? 'text-green-600' : 'text-red-600'
            }`}>
              {testResults.passed ? '✅' : '❌'}
            </span>
            <h4 className={`font-medium ${
              testResults.passed ? 'text-green-800' : 'text-red-800'
            }`}>
              {testResults.passed ? 'All Tests Passed!' : 'Some Tests Failed'}
            </h4>
          </div>
          {testResults.results.length > 0 && (
            <div className="space-y-2">
              {testResults.results.map((result, index) => (
                <div key={index} className="text-sm font-mono">
                  <span className={result.passed ? 'text-green-600' : 'text-red-600'}>
                    Test {index + 1}: {result.passed ? 'PASS' : 'FAIL'}
                  </span>
                  {!result.passed && result.error && (
                    <div className="text-red-600 ml-4">{result.error}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between">
        <div className="flex space-x-3">
          {onRunTests && (
            <button
              onClick={handleRunTests}
              disabled={!code.trim() || isRunningTests}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {isRunningTests ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Running Tests...
                </span>
              ) : (
                'Run Tests'
              )}
            </button>
          )}
        </div>
        
        <button
          onClick={handleSubmit}
          disabled={!code.trim()}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          Submit Solution
        </button>
      </div>
    </div>
  );
};

const InteractiveChallenge: React.FC<SkillAssessmentProps> = ({
  question,
  onSubmit,
  timeRemaining,
  onAutoSave,
  autoSaveInterval = 30000
}) => {
  const [responses, setResponses] = useState<Record<string, any>>({});
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout>();

  // Auto-save functionality
  useEffect(() => {
    if (hasUnsavedChanges && onAutoSave) {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
      
      autoSaveTimeoutRef.current = setTimeout(() => {
        onAutoSave(responses);
        setHasUnsavedChanges(false);
      }, autoSaveInterval);
    }

    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, [responses, hasUnsavedChanges, onAutoSave, autoSaveInterval]);

  const handleResponseChange = (key: string, value: any) => {
    setResponses(prev => ({ ...prev, [key]: value }));
    setHasUnsavedChanges(true);
  };

  const handleSubmit = () => {
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
    onSubmit(responses);
  };

  const renderInteractiveElement = () => {
    switch (question.question_type) {
      case QuestionType.MULTIPLE_CHOICE:
        return (
          <div className="space-y-3">
            {question.options && Object.entries(question.options).map(([key, value]) => (
              <label
                key={key}
                className={`flex items-center p-4 border rounded-lg cursor-pointer transition-colors ${
                  responses.selected_options?.includes(key)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name="answer"
                  value={key}
                  checked={responses.selected_options?.includes(key) || false}
                  onChange={(e) => handleResponseChange('selected_options', [e.target.value])}
                  className="mr-3 text-blue-600"
                  aria-describedby={`option-${key}-description`}
                />
                <span className="font-medium text-gray-900 mr-2">{key}.</span>
                <span className="text-gray-700" id={`option-${key}-description`}>{value}</span>
              </label>
            ))}
          </div>
        );

      case QuestionType.TEXT_RESPONSE:
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Response:
            </label>
            <textarea
              value={responses.response_text || ''}
              onChange={(e) => handleResponseChange('response_text', e.target.value)}
              className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Type your answer here..."
              aria-label="Text response input"
            />
            <div className="mt-2 text-sm text-gray-500">
              {(responses.response_text || '').length} characters
            </div>
          </div>
        );

      default:
        return (
          <div className="text-center py-8 text-gray-500">
            Interactive element for {question.question_type} not implemented yet.
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Question Header */}
      <div className="prose max-w-none">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-900 m-0">{question.title}</h3>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              question.difficulty_level === DifficultyLevel.BEGINNER ? 'bg-green-100 text-green-800' :
              question.difficulty_level === DifficultyLevel.INTERMEDIATE ? 'bg-yellow-100 text-yellow-800' :
              question.difficulty_level === DifficultyLevel.ADVANCED ? 'bg-orange-100 text-orange-800' :
              'bg-red-100 text-red-800'
            }`}>
              {question.difficulty_level}
            </span>
            <span className="text-sm text-gray-500">{question.max_points} points</span>
            {hasUnsavedChanges && (
              <span className="text-xs text-orange-600">● Unsaved</span>
            )}
          </div>
        </div>
        <div className="text-gray-700 whitespace-pre-wrap">
          {question.content}
        </div>
      </div>

      {/* Interactive Element */}
      {renderInteractiveElement()}

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={Object.keys(responses).length === 0}
        className="w-full py-3 px-6 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        Submit Answer
      </button>
    </div>
  );
};

const SkillAssessment: React.FC<SkillAssessmentProps> = (props) => {
  const { question } = props;

  // Render appropriate component based on question type
  if (question.question_type === QuestionType.CODING) {
    return <CodingChallenge {...props} />;
  }

  return <InteractiveChallenge {...props} />;
};

export default SkillAssessment;