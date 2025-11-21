'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MicrophoneIcon,
  StopIcon,
  PlayIcon,
  SpeakerWaveIcon,
  ChatBubbleLeftRightIcon,
  ClockIcon,
  CheckCircleIcon,
  ComputerDesktopIcon,
  UserIcon,
  StarIcon,
  BuildingOfficeIcon,
  WrenchScrewdriverIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';
import {
  Interview,
  InterviewQuestion,
  QuestionCategory
} from '../../types/interview';

interface AIInterviewerProps {
  interview: Interview;
  currentQuestion?: InterviewQuestion;
  questions: InterviewQuestion[];
  currentQuestionIndex: number;
  onQuestionComplete: (response: string) => void;
  isRecording: boolean;
}

export const AIInterviewer: React.FC<AIInterviewerProps> = ({
  interview,
  currentQuestion,
  questions,
  currentQuestionIndex,
  onQuestionComplete,
  isRecording
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [responseTime, setResponseTime] = useState(0);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  
  // Speech recognition refs
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const speechSynthesisRef = useRef<SpeechSynthesisUtterance | null>(null);
  const responseTimerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(0);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => {
        setIsListening(true);
        startTimeRef.current = Date.now();
        
        // Start response timer
        responseTimerRef.current = setInterval(() => {
          setResponseTime(Math.floor((Date.now() - startTimeRef.current) / 1000));
        }, 1000);
      };
      
      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        setTranscript(finalTranscript + interimTranscript);
        setCurrentResponse(finalTranscript);
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
        if (responseTimerRef.current) {
          clearInterval(responseTimerRef.current);
        }
      };
      
      recognitionRef.current = recognition;
    }
    
    return () => {
      if (responseTimerRef.current) {
        clearInterval(responseTimerRef.current);
      }
    };
  }, []);

  // Speak AI question
  const speakQuestion = (text: string) => {
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;
      
      // Try to use a professional voice
      const voices = window.speechSynthesis.getVoices();
      const preferredVoice = voices.find(voice => 
        voice.name.includes('Google') || 
        voice.name.includes('Microsoft') ||
        voice.lang.startsWith('en')
      );
      
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
      
      utterance.onstart = () => setIsAISpeaking(true);
      utterance.onend = () => setIsAISpeaking(false);
      utterance.onerror = () => setIsAISpeaking(false);
      
      speechSynthesisRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    }
  };

  // Start listening for response
  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setCurrentResponse('');
      setTranscript('');
      setResponseTime(0);
      recognitionRef.current.start();
    }
  };

  // Stop listening
  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  // Submit response
  const submitResponse = () => {
    if (currentResponse.trim()) {
      setIsProcessing(true);
      onQuestionComplete(currentResponse.trim());
      setCurrentResponse('');
      setTranscript('');
      setResponseTime(0);
      setIsProcessing(false);
    }
  };

  // Auto-speak question when it changes
  useEffect(() => {
    if (currentQuestion && !isAISpeaking) {
      // Add a small delay to ensure video is ready
      setTimeout(() => {
        speakQuestion(currentQuestion.question_text);
      }, 1000);
    }
  }, [currentQuestion, isAISpeaking]);

  const getCategoryIcon = (category: QuestionCategory) => {
    switch (category) {
      case QuestionCategory.TECHNICAL:
        return <ComputerDesktopIcon className="w-5 h-5" />;
      case QuestionCategory.BEHAVIORAL:
        return <UserIcon className="w-5 h-5" />;
      case QuestionCategory.SITUATIONAL:
        return <StarIcon className="w-5 h-5" />;
      case QuestionCategory.COMPANY_CULTURE:
        return <BuildingOfficeIcon className="w-5 h-5" />;
      case QuestionCategory.PROBLEM_SOLVING:
        return <WrenchScrewdriverIcon className="w-5 h-5" />;
      default:
        return <QuestionMarkCircleIcon className="w-5 h-5" />;
    }
  };

  const getCategoryColor = (category: QuestionCategory) => {
    switch (category) {
      case QuestionCategory.TECHNICAL:
        return 'bg-blue-100 text-blue-800';
      case QuestionCategory.BEHAVIORAL:
        return 'bg-green-100 text-green-800';
      case QuestionCategory.SITUATIONAL:
        return 'bg-purple-100 text-purple-800';
      case QuestionCategory.COMPANY_CULTURE:
        return 'bg-orange-100 text-orange-800';
      case QuestionCategory.PROBLEM_SOLVING:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!currentQuestion) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <div className="text-center text-gray-400">
          <ChatBubbleLeftRightIcon className="h-12 w-12 mx-auto mb-4" />
          <p>Preparing interview questions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-800">
      {/* AI Interviewer Header */}
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold">AI</span>
          </div>
          <div>
            <h3 className="text-white font-medium">AI Interviewer</h3>
            <p className="text-gray-400 text-sm">
              {interview.ai_interviewer_persona || 'Professional Interviewer'}
            </p>
          </div>
          {isAISpeaking && (
            <div className="flex items-center space-x-1">
              <SpeakerWaveIcon className="h-4 w-4 text-blue-400 animate-pulse" />
              <span className="text-blue-400 text-xs">Speaking...</span>
            </div>
          )}
        </div>

        {/* Progress indicator */}
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded-full text-xs ${getCategoryColor(currentQuestion.category)}`}>
              {getCategoryIcon(currentQuestion.category)} {currentQuestion.category}
            </span>
          </div>
        </div>
      </div>

      {/* Current Question */}
      <div className="flex-1 p-6 overflow-y-auto">
        <div className="space-y-6">
          {/* Question text */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                <span className="text-white text-sm font-semibold">Q</span>
              </div>
              <div className="flex-1">
                <p className="text-white leading-relaxed">
                  {currentQuestion.question_text}
                </p>
                {currentQuestion.expected_duration && (
                  <div className="flex items-center space-x-1 mt-2 text-gray-400 text-sm">
                    <ClockIcon className="h-4 w-4" />
                    <span>Expected time: {Math.floor(currentQuestion.expected_duration / 60)} minutes</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Response area */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-white font-medium">Your Response</h4>
              {responseTime > 0 && (
                <div className="flex items-center space-x-1 text-gray-400 text-sm">
                  <ClockIcon className="h-4 w-4" />
                  <span>{Math.floor(responseTime / 60)}:{(responseTime % 60).toString().padStart(2, '0')}</span>
                </div>
              )}
            </div>

            {/* Speech recognition controls */}
            <div className="flex items-center space-x-3">
              {!isListening ? (
                <button
                  onClick={startListening}
                  disabled={isProcessing || isAISpeaking}
                  className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <MicrophoneIcon className="h-5 w-5" />
                  <span>Start Speaking</span>
                </button>
              ) : (
                <button
                  onClick={stopListening}
                  className="flex items-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
                >
                  <StopIcon className="h-5 w-5" />
                  <span>Stop</span>
                </button>
              )}

              {currentResponse && (
                <button
                  onClick={submitResponse}
                  disabled={isProcessing}
                  className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  <CheckCircleIcon className="h-5 w-5" />
                  <span>Submit</span>
                </button>
              )}
            </div>

            {/* Live transcript */}
            <AnimatePresence>
              {(transcript || isListening) && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="bg-gray-700 rounded-lg p-4"
                >
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="text-white text-sm font-semibold">A</span>
                    </div>
                    <div className="flex-1">
                      {isListening && !transcript && (
                        <div className="flex items-center space-x-2 text-gray-400">
                          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                          <span className="text-sm">Listening...</span>
                        </div>
                      )}
                      {transcript && (
                        <p className="text-white">
                          {transcript}
                          {isListening && <span className="animate-pulse">|</span>}
                        </p>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Processing indicator */}
            <AnimatePresence>
              {isProcessing && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center justify-center py-4"
                >
                  <div className="flex items-center space-x-2 text-blue-400">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
                    <span className="text-sm">Processing your response...</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Question context */}
          {currentQuestion.skill_focus.length > 0 && (
            <div className="bg-gray-700 rounded-lg p-4">
              <h5 className="text-white font-medium mb-2">Focus Areas</h5>
              <div className="flex flex-wrap gap-2">
                {currentQuestion.skill_focus.map((skill, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer with tips */}
      <div className="p-4 border-t border-gray-700 bg-gray-750">
        <div className="text-xs text-gray-400 space-y-1">
          <p><strong>Tip:</strong> Speak clearly and take your time to think before responding.</p>
          <p><strong>Remember:</strong> Be specific and provide examples when possible.</p>
        </div>
      </div>
    </div>
  );
};