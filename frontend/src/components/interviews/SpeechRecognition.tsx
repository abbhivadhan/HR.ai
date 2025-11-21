'use client'

import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { MicrophoneIcon, StopIcon } from '@heroicons/react/24/solid'
import { interviewAnalytics } from '@/services/interviewAnalytics'

interface SpeechRecognitionProps {
  isListening: boolean
  onTranscriptComplete: (transcript: string, analysis: any) => void
  maxDuration: number
  micEnabled?: boolean
  currentQuestion?: string
  questionType?: string
}

export default function SpeechRecognition({
  isListening,
  onTranscriptComplete,
  maxDuration,
  micEnabled = true,
  currentQuestion = '',
  questionType = 'general'
}: SpeechRecognitionProps) {
  const [transcript, setTranscript] = useState('')
  const [timeRemaining, setTimeRemaining] = useState(maxDuration)
  const [isRecording, setIsRecording] = useState(false)
  const recognitionRef = useRef<any>(null)
  const timerRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    // Initialize Speech Recognition
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition()
        recognitionRef.current.continuous = true
        recognitionRef.current.interimResults = true
        recognitionRef.current.lang = 'en-US'

        recognitionRef.current.onresult = (event: any) => {
          let interimTranscript = ''
          let finalTranscript = ''

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcriptPiece = event.results[i][0].transcript
            if (event.results[i].isFinal) {
              finalTranscript += transcriptPiece + ' '
            } else {
              interimTranscript += transcriptPiece
            }
          }

          setTranscript(prev => {
            const newTranscript = prev + finalTranscript
            return newTranscript
          })
        }

        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error)
        }
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [])

  useEffect(() => {
    if (isListening && !isRecording && micEnabled) {
      startRecording()
    } else if ((!isListening || !micEnabled) && isRecording) {
      stopRecording()
    }
  }, [isListening, micEnabled])

  // Stop recording when mic is disabled
  useEffect(() => {
    if (!micEnabled && isRecording) {
      console.log('Microphone disabled, pausing recognition')
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop()
        } catch (error) {
          console.error('Error stopping recognition:', error)
        }
      }
    } else if (micEnabled && isListening && !isRecording) {
      console.log('Microphone enabled, resuming recognition')
      startRecording()
    }
  }, [micEnabled])

  const startRecording = () => {
    if (recognitionRef.current) {
      setTranscript('')
      setTimeRemaining(maxDuration)
      setIsRecording(true)
      
      try {
        recognitionRef.current.start()
      } catch (error) {
        console.error('Error starting recognition:', error)
      }

      // Start timer
      timerRef.current = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            stopRecording()
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }
  }

  const stopRecording = () => {
    if (recognitionRef.current && isRecording) {
      try {
        recognitionRef.current.stop()
      } catch (error) {
        console.error('Error stopping recognition:', error)
      }
      
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      
      setIsRecording(false)
      
      // Analyze response
      const analysis = analyzeResponse(transcript)
      onTranscriptComplete(transcript, analysis)
    }
  }

  const analyzeResponse = async (text: string) => {
    // Use real analytics service to analyze the response
    const duration = maxDuration - timeRemaining
    
    if (!text || text.trim().length === 0) {
      return {
        wordCount: 0,
        duration,
        wordsPerMinute: 0,
        overallScore: 0,
        relevanceScore: 0,
        clarityScore: 0,
        completenessScore: 0,
        professionalismScore: 0,
        fillerWordCount: 0,
        keywordsMatched: [],
        strengths: ['No response recorded'],
        improvements: ['Please ensure your microphone is working and speak clearly'],
        detailedFeedback: 'No response was recorded. Please check your microphone settings.'
      }
    }
    
    // Perform real analysis
    const analysis = interviewAnalytics.analyzeResponse(
      currentQuestion,
      text,
      duration,
      questionType
    )
    
    return analysis
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
            !micEnabled ? 'bg-red-600' : isRecording ? 'bg-red-500' : 'bg-gray-500'
          }`}>
            {isRecording ? (
              <MicrophoneIcon className="w-5 h-5 text-white" />
            ) : (
              <StopIcon className="w-5 h-5 text-white" />
            )}
          </div>
          <div>
            <h3 className="text-white font-semibold">Your Response</h3>
            <p className="text-white/70 text-sm">
              {!micEnabled ? 'Microphone muted' : isRecording ? 'Recording...' : 'Waiting to record'}
            </p>
          </div>
        </div>
        
        {!micEnabled && (
          <div className="px-3 py-1 bg-red-500/20 rounded-full">
            <span className="text-red-300 text-xs font-medium">Mic Muted</span>
          </div>
        )}

        {/* Timer */}
        <div className="text-right">
          <div className="text-2xl font-bold text-white">
            {formatTime(timeRemaining)}
          </div>
          <div className="text-white/70 text-sm">remaining</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden mb-4">
        <motion.div
          className={`h-full ${
            timeRemaining < 30 ? 'bg-red-500' : 'bg-green-500'
          }`}
          initial={{ width: '100%' }}
          animate={{ 
            width: `${(timeRemaining / maxDuration) * 100}%` 
          }}
          transition={{ duration: 0.5 }}
        />
      </div>

      {/* Transcript Display */}
      <div className="bg-black/20 rounded-xl p-4 min-h-[150px] max-h-[300px] overflow-y-auto">
        {transcript ? (
          <p className="text-white leading-relaxed">{transcript}</p>
        ) : (
          <p className="text-white/50 italic">
            {isRecording 
              ? 'Start speaking... Your words will appear here.'
              : 'Waiting for AI to finish speaking...'}
          </p>
        )}
      </div>

      {/* Audio Visualizer */}
      {isRecording && (
        <div className="mt-4 flex items-center justify-center space-x-1">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="w-1 bg-blue-400 rounded-full"
              animate={{
                height: [10, Math.random() * 40 + 10, 10],
              }}
              transition={{
                duration: 0.5,
                repeat: Infinity,
                delay: i * 0.05,
              }}
            />
          ))}
        </div>
      )}

      {/* Manual Stop Button */}
      {isRecording && (
        <button
          onClick={stopRecording}
          className="mt-4 w-full py-3 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-xl transition-colors"
        >
          Stop Recording
        </button>
      )}
    </div>
  )
}
