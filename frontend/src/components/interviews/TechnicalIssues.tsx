'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  XMarkIcon,
  ExclamationTriangleIcon,
  WrenchScrewdriverIcon,
  PhoneIcon,
  ChatBubbleLeftRightIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

interface TechnicalIssuesProps {
  onClose: () => void;
  onReconnect: () => void;
  error?: string | null;
}

interface TroubleshootingStep {
  id: string;
  title: string;
  description: string;
  action?: () => void;
  completed?: boolean;
}

export const TechnicalIssues: React.FC<TechnicalIssuesProps> = ({
  onClose,
  onReconnect,
  error
}) => {
  const [selectedIssue, setSelectedIssue] = useState<string>('');
  const [troubleshootingSteps, setTroubleshootingSteps] = useState<TroubleshootingStep[]>([]);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const [contactSupport, setContactSupport] = useState(false);

  const commonIssues = [
    {
      id: 'audio',
      title: 'Audio Problems',
      description: 'Microphone not working or audio quality issues',
      steps: [
        {
          id: 'check-mic-permission',
          title: 'Check microphone permissions',
          description: 'Ensure your browser has permission to access your microphone'
        },
        {
          id: 'test-mic',
          title: 'Test microphone',
          description: 'Speak into your microphone and check if the audio levels are working'
        },
        {
          id: 'check-mic-device',
          title: 'Check microphone device',
          description: 'Make sure the correct microphone is selected in your system settings'
        },
        {
          id: 'restart-browser',
          title: 'Restart browser',
          description: 'Close and reopen your browser, then rejoin the interview'
        }
      ]
    },
    {
      id: 'video',
      title: 'Video Problems',
      description: 'Camera not working or video quality issues',
      steps: [
        {
          id: 'check-camera-permission',
          title: 'Check camera permissions',
          description: 'Ensure your browser has permission to access your camera'
        },
        {
          id: 'test-camera',
          title: 'Test camera',
          description: 'Check if your camera is working in other applications'
        },
        {
          id: 'check-camera-device',
          title: 'Check camera device',
          description: 'Make sure the correct camera is selected and not being used by other apps'
        },
        {
          id: 'update-drivers',
          title: 'Update camera drivers',
          description: 'Ensure your camera drivers are up to date'
        }
      ]
    },
    {
      id: 'connection',
      title: 'Connection Issues',
      description: 'Poor connection quality or frequent disconnections',
      steps: [
        {
          id: 'check-internet',
          title: 'Check internet connection',
          description: 'Ensure you have a stable internet connection with good speed'
        },
        {
          id: 'close-apps',
          title: 'Close other applications',
          description: 'Close unnecessary applications that might be using bandwidth'
        },
        {
          id: 'use-ethernet',
          title: 'Use wired connection',
          description: 'If possible, use an ethernet cable instead of Wi-Fi'
        },
        {
          id: 'restart-router',
          title: 'Restart router',
          description: 'Restart your internet router and modem'
        }
      ]
    },
    {
      id: 'browser',
      title: 'Browser Issues',
      description: 'Browser compatibility or performance problems',
      steps: [
        {
          id: 'update-browser',
          title: 'Update browser',
          description: 'Make sure you are using the latest version of your browser'
        },
        {
          id: 'clear-cache',
          title: 'Clear browser cache',
          description: 'Clear your browser cache and cookies, then refresh the page'
        },
        {
          id: 'disable-extensions',
          title: 'Disable extensions',
          description: 'Temporarily disable browser extensions that might interfere'
        },
        {
          id: 'try-different-browser',
          title: 'Try different browser',
          description: 'Try using Chrome, Firefox, or Safari as an alternative'
        }
      ]
    }
  ];

  const handleIssueSelect = (issueId: string) => {
    setSelectedIssue(issueId);
    const issue = commonIssues.find(i => i.id === issueId);
    if (issue) {
      setTroubleshootingSteps(issue.steps.map(step => ({ ...step, completed: false })));
    }
  };

  const markStepCompleted = (stepId: string) => {
    setTroubleshootingSteps(prev =>
      prev.map(step =>
        step.id === stepId ? { ...step, completed: !step.completed } : step
      )
    );
  };

  const handleReconnect = async () => {
    setIsReconnecting(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate reconnection
      onReconnect();
    } catch (err) {
      console.error('Reconnection failed:', err);
    } finally {
      setIsReconnecting(false);
    }
  };

  const handleContactSupport = () => {
    setContactSupport(true);
    // In a real implementation, this would open a support chat or form
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="bg-red-50 border-b border-red-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Technical Issues</h2>
                <p className="text-sm text-gray-600">
                  {error || 'We\'re here to help resolve any technical problems'}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 rounded-md p-1"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {!selectedIssue ? (
            /* Issue selection */
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  What type of issue are you experiencing?
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {commonIssues.map((issue) => (
                    <button
                      key={issue.id}
                      onClick={() => handleIssueSelect(issue.id)}
                      className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                    >
                      <h4 className="font-medium text-gray-900 mb-1">{issue.title}</h4>
                      <p className="text-sm text-gray-600">{issue.description}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Quick actions */}
              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={handleReconnect}
                    disabled={isReconnecting}
                    className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isReconnecting ? (
                      <ArrowPathIcon className="h-5 w-5 animate-spin" />
                    ) : (
                      <ArrowPathIcon className="h-5 w-5" />
                    )}
                    <span>{isReconnecting ? 'Reconnecting...' : 'Reconnect'}</span>
                  </button>

                  <button
                    onClick={handleContactSupport}
                    className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                  >
                    <ChatBubbleLeftRightIcon className="h-5 w-5" />
                    <span>Contact Support</span>
                  </button>

                  <button
                    onClick={() => window.location.reload()}
                    className="flex items-center space-x-2 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
                  >
                    <ArrowPathIcon className="h-5 w-5" />
                    <span>Refresh Page</span>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            /* Troubleshooting steps */
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">
                  {commonIssues.find(i => i.id === selectedIssue)?.title} Troubleshooting
                </h3>
                <button
                  onClick={() => setSelectedIssue('')}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  ← Back to issues
                </button>
              </div>

              <div className="space-y-4">
                {troubleshootingSteps.map((step, index) => (
                  <div
                    key={step.id}
                    className={`border rounded-lg p-4 ${
                      step.completed ? 'border-green-200 bg-green-50' : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        {step.completed ? (
                          <CheckCircleIcon className="h-5 w-5 text-green-600" />
                        ) : (
                          <div className="w-5 h-5 rounded-full border-2 border-gray-300 flex items-center justify-center">
                            <span className="text-xs text-gray-600">{index + 1}</span>
                          </div>
                        )}
                      </div>
                      <div className="flex-1">
                        <h4 className={`font-medium ${
                          step.completed ? 'text-green-900' : 'text-gray-900'
                        }`}>
                          {step.title}
                        </h4>
                        <p className={`text-sm mt-1 ${
                          step.completed ? 'text-green-700' : 'text-gray-600'
                        }`}>
                          {step.description}
                        </p>
                      </div>
                      <button
                        onClick={() => markStepCompleted(step.id)}
                        className={`px-3 py-1 rounded text-sm font-medium ${
                          step.completed
                            ? 'bg-green-100 text-green-800 hover:bg-green-200'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {step.completed ? 'Completed' : 'Mark Done'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Action buttons */}
              <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                <div className="text-sm text-gray-600">
                  {troubleshootingSteps.filter(s => s.completed).length} of {troubleshootingSteps.length} steps completed
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={handleReconnect}
                    disabled={isReconnecting}
                    className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isReconnecting ? (
                      <ArrowPathIcon className="h-5 w-5 animate-spin" />
                    ) : (
                      <ArrowPathIcon className="h-5 w-5" />
                    )}
                    <span>{isReconnecting ? 'Reconnecting...' : 'Try Again'}</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Contact support section */}
          {contactSupport && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg"
            >
              <div className="flex items-start space-x-3">
                <ChatBubbleLeftRightIcon className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-medium text-blue-900 mb-2">Support Contact Information</h4>
                  <div className="space-y-2 text-sm text-blue-800">
                    <div className="flex items-center space-x-2">
                      <PhoneIcon className="h-4 w-4" />
                      <span>Emergency Support: +1 (555) 123-4567</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <ChatBubbleLeftRightIcon className="h-4 w-4" />
                      <span>Live Chat: Available 24/7 during interview hours</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <ClockIcon className="h-4 w-4" />
                      <span>Response Time: Usually within 2-3 minutes</span>
                    </div>
                  </div>
                  <p className="text-sm text-blue-700 mt-3">
                    Our technical support team will help you resolve the issue and can reschedule 
                    your interview if needed without any penalty.
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};