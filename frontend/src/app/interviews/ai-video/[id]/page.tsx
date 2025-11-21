'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MicrophoneIcon,
  VideoCameraIcon,
  XMarkIcon,
  CheckIcon,
  SpeakerWaveIcon,
  ChatBubbleLeftIcon
} from '@heroicons/react/24/outline'
import { EnhancedAIAvatar, SpeechRecognition, InterviewAnalysis } from '@/components/interviews'

export default function AIVideoInterviewPage() {
  const params = useParams()
  const router = useRouter()
  const [interviewState, setInterviewState] = useState<'setup' | 'active' | 'completed'>('setup')
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [isAISpeaking, setIsAISpeaking] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [userResponse, setUserResponse] = useState('')
  const [responses, setResponses] = useState<any[]>([])
  const [cameraEnabled, setCameraEnabled] = useState(false)
  const [micEnabled, setMicEnabled] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)

  const questions = [
    {
      id: 1,
      text: "Hello! I'm Alex, your AI interviewer. Let's start with an easy one - tell me about yourself and your background.",
      duration: 120,
      type: 'introduction'
    },
    {
      id: 2,
      text: "Great! Now, can you describe a challenging project you've worked on and how you overcame the obstacles?",
      duration: 180,
      type: 'behavioral'
    },
    {
      id: 3,
      text: "Interesting! Let's talk about your technical skills. What programming languages are you most comfortable with and why?",
      duration: 120,
      type: 'technical'
    },
    {
      id: 4,
      text: "Excellent! Here's a scenario: You're working on a tight deadline and discover a critical bug. How would you handle it?",
      duration: 150,
      type: 'situational'
    },
    {
      id: 5,
      text: "Perfect! Last question - where do you see yourself in 5 years, and how does this role fit into your career goals?",
      duration: 120,
      type: 'career'
    }
  ]

  useEffect(() => {
    return () => {
      // Cleanup media stream
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  // Handle video stream updates - ensure video plays when stream is available
  useEffect(() => {
    const videoElement = videoRef.current
    const stream = mediaStreamRef.current
    
    if (videoElement && stream && cameraEnabled) {
      console.log('Setting up video stream...', stream.getVideoTracks())
      videoElement.srcObject = stream
      
      // Wait for metadata to load before playing
      videoElement.onloadedmetadata = () => {
        console.log('Video metadata loaded, attempting to play...')
        videoElement.play()
          .then(() => console.log('Video playing successfully'))
          .catch(err => console.error('Video play error:', err))
      }
      
      // Fallback: try to play immediately
      videoElement.play()
        .then(() => console.log('Video started immediately'))
        .catch(err => console.log('Waiting for metadata...', err.message))
    }
  }, [cameraEnabled, interviewState])

  const startInterview = async () => {
    try {
      console.log('Requesting camera and microphone access...')
      
      // Request camera and microphone permissions
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        },
        audio: true
      })
      
      console.log('Media stream obtained:', stream)
      console.log('Video tracks:', stream.getVideoTracks())
      console.log('Audio tracks:', stream.getAudioTracks())
      
      mediaStreamRef.current = stream
      
      // Set states first
      setCameraEnabled(true)
      setMicEnabled(true)
      setInterviewState('active')
      
      // Then set up video after a small delay to ensure DOM is ready
      setTimeout(() => {
        if (videoRef.current) {
          console.log('Setting video srcObject...')
          videoRef.current.srcObject = stream
          
          // Explicitly play the video
          videoRef.current.play()
            .then(() => console.log('Video playing successfully!'))
            .catch(playError => console.error('Error playing video:', playError))
        } else {
          console.error('Video ref is null!')
        }
      }, 100)
      
      // AI starts speaking first question
      setTimeout(() => {
        speakQuestion(questions[0].text)
      }, 1000)
      
    } catch (error) {
      console.error('Error accessing media devices:', error)
      alert('Please allow camera and microphone access to continue with the interview.')
    }
  }

  const speakQuestion = (text: string) => {
    setIsAISpeaking(true)
    
    // Use Web Speech API for text-to-speech with enhanced voice
    const utterance = new SpeechSynthesisUtterance(text)
    
    // Get available voices and select the best one
    const voices = window.speechSynthesis.getVoices()
    
    // Prefer high-quality English voices (Google, Microsoft, or Apple)
    const preferredVoice = voices.find(voice => 
      (voice.name.includes('Google') || 
       voice.name.includes('Microsoft') || 
       voice.name.includes('Samantha') ||
       voice.name.includes('Karen') ||
       voice.name.includes('Daniel')) &&
      voice.lang.startsWith('en')
    ) || voices.find(voice => voice.lang.startsWith('en-US'))
    
    if (preferredVoice) {
      utterance.voice = preferredVoice
      console.log('Using voice:', preferredVoice.name)
    }
    
    // Enhanced voice settings for natural, professional sound
    utterance.rate = 0.95  // Slightly slower for clarity
    utterance.pitch = 1.1  // Slightly higher for friendliness
    utterance.volume = 1.0
    utterance.lang = 'en-US'
    
    utterance.onend = () => {
      setIsAISpeaking(false)
      // Start listening for response after AI finishes speaking
      setTimeout(() => {
        setIsListening(true)
      }, 500)
    }
    
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event)
      setIsAISpeaking(false)
    }
    
    // Cancel any ongoing speech before starting new one
    window.speechSynthesis.cancel()
    window.speechSynthesis.speak(utterance)
  }

  const handleResponseComplete = (transcript: string, analysis: any) => {
    setIsListening(false)
    
    // Save response
    const response = {
      questionId: questions[currentQuestion].id,
      question: questions[currentQuestion].text,
      answer: transcript,
      analysis: analysis,
      timestamp: new Date()
    }
    
    setResponses([...responses, response])
    
    // Move to next question or complete interview
    if (currentQuestion < questions.length - 1) {
      setTimeout(() => {
        setCurrentQuestion(currentQuestion + 1)
        speakQuestion(questions[currentQuestion + 1].text)
      }, 2000)
    } else {
      // Interview complete
      setTimeout(() => {
        setInterviewState('completed')
      }, 2000)
    }
  }

  const toggleCamera = async () => {
    console.log('Toggle camera clicked, current state:', cameraEnabled)
    const newState = !cameraEnabled
    
    if (newState) {
      // Turn camera ON - request new video stream
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
          },
          audio: false // Don't request audio again
        })
        
        const videoTrack = stream.getVideoTracks()[0]
        
        // Replace video track in existing stream
        if (mediaStreamRef.current) {
          const oldVideoTrack = mediaStreamRef.current.getVideoTracks()[0]
          if (oldVideoTrack) {
            mediaStreamRef.current.removeTrack(oldVideoTrack)
            oldVideoTrack.stop()
          }
          mediaStreamRef.current.addTrack(videoTrack)
        }
        
        // Update video element
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStreamRef.current
          await videoRef.current.play()
        }
        
        setCameraEnabled(true)
        console.log('Camera turned ON')
      } catch (error) {
        console.error('Error turning camera on:', error)
      }
    } else {
      // Turn camera OFF - stop video track
      if (mediaStreamRef.current) {
        const videoTrack = mediaStreamRef.current.getVideoTracks()[0]
        if (videoTrack) {
          videoTrack.stop() // This actually turns off the camera hardware
          mediaStreamRef.current.removeTrack(videoTrack)
          console.log('Camera turned OFF and hardware stopped')
        }
      }
      setCameraEnabled(false)
    }
  }

  const toggleMicrophone = () => {
    console.log('Toggle microphone clicked, current state:', micEnabled)
    if (mediaStreamRef.current) {
      const audioTrack = mediaStreamRef.current.getAudioTracks()[0]
      if (audioTrack) {
        const newState = !micEnabled
        audioTrack.enabled = newState
        setMicEnabled(newState)
        console.log('Microphone toggled to:', newState)
      } else {
        console.error('No audio track found')
      }
    } else {
      console.error('No media stream available')
    }
  }

  const endInterview = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop())
    }
    router.push('/dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500 rounded-full filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500 rounded-full filter blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <div className="p-6 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-full flex items-center justify-center">
              <VideoCameraIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-white text-xl font-bold">AI Video Interview</h1>
              <p className="text-white/70 text-sm">
                {interviewState === 'setup' && 'Get ready to start'}
                {interviewState === 'active' && `Question ${currentQuestion + 1} of ${questions.length}`}
                {interviewState === 'completed' && 'Interview Complete'}
              </p>
            </div>
          </div>
          
          <button
            onClick={endInterview}
            className="p-3 bg-red-500/20 hover:bg-red-500/30 backdrop-blur-sm rounded-full transition-colors"
          >
            <XMarkIcon className="w-6 h-6 text-white" />
          </button>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex items-center justify-center p-6">
          <AnimatePresence mode="wait">
            {/* Setup Screen */}
            {interviewState === 'setup' && (
              <motion.div
                key="setup"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="max-w-4xl w-full"
              >
                <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-12 text-center">
                  <div className="w-32 h-32 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mx-auto mb-8 flex items-center justify-center">
                    <VideoCameraIcon className="w-16 h-16 text-white" />
                  </div>
                  
                  <h2 className="text-4xl font-bold text-white mb-4">
                    Ready for Your AI Interview?
                  </h2>
                  
                  <p className="text-xl text-white/80 mb-8 max-w-2xl mx-auto">
                    Meet Alex, your AI interviewer. This will be a natural conversation where Alex will ask you questions and analyze your responses in real-time.
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6">
                      <VideoCameraIcon className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                      <h3 className="text-white font-semibold mb-2">Video Recording</h3>
                      <p className="text-white/70 text-sm">Your camera will be used to record the interview</p>
                    </div>
                    
                    <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6">
                      <MicrophoneIcon className="w-12 h-12 text-purple-400 mx-auto mb-4" />
                      <h3 className="text-white font-semibold mb-2">Voice Recognition</h3>
                      <p className="text-white/70 text-sm">Speak naturally - AI will understand you</p>
                    </div>
                    
                    <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6">
                      <ChatBubbleLeftIcon className="w-12 h-12 text-pink-400 mx-auto mb-4" />
                      <h3 className="text-white font-semibold mb-2">Real-time Analysis</h3>
                      <p className="text-white/70 text-sm">Get instant feedback on your responses</p>
                    </div>
                  </div>

                  <button
                    onClick={startInterview}
                    className="px-12 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xl font-bold rounded-full hover:shadow-2xl hover:scale-105 transition-all duration-200"
                  >
                    Start Interview
                  </button>
                </div>
              </motion.div>
            )}

            {/* Active Interview */}
            {interviewState === 'active' && (
              <motion.div
                key="active"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="max-w-7xl w-full grid grid-cols-1 lg:grid-cols-2 gap-6"
              >
                {/* AI Avatar Side */}
                <div className="space-y-6">
                  <EnhancedAIAvatar
                    isSpeaking={isAISpeaking}
                    isListening={isListening}
                    emotion="friendly"
                  />
                  
                  {/* Question Display */}
                  <motion.div
                    key={currentQuestion}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white/10 backdrop-blur-xl rounded-2xl p-6"
                  >
                    <div className="flex items-start space-x-4">
                      <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                        <ChatBubbleLeftIcon className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="text-white/70 text-sm mb-2">Alex is asking:</p>
                        <p className="text-white text-lg leading-relaxed">
                          {questions[currentQuestion].text}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                </div>

                {/* Candidate Video Side */}
                <div className="space-y-6">
                  {/* Video Feed */}
                  <div className="bg-gray-900 rounded-2xl overflow-hidden aspect-video relative">
                    {!cameraEnabled && interviewState === 'active' && (
                      <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
                        <div className="text-center">
                          <div className="w-20 h-20 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                            <VideoCameraIcon className="w-10 h-10 text-gray-500" />
                            <div className="absolute w-0.5 h-12 bg-red-500 rotate-45"></div>
                          </div>
                          <p className="text-white text-lg font-medium">Camera is off</p>
                          <p className="text-gray-400 text-sm mt-2">Click the camera button to turn it on</p>
                        </div>
                      </div>
                    )}
                    <video
                      ref={videoRef}
                      autoPlay
                      muted
                      playsInline
                      className="w-full h-full"
                      style={{ 
                        display: cameraEnabled ? 'block' : 'none',
                        objectFit: 'contain',
                        backgroundColor: '#1f2937',
                        transform: 'scaleX(-1)'
                      }}
                    />
                    
                    {/* Recording Indicator */}
                    {isListening && (
                      <div className="absolute top-4 right-4 flex items-center space-x-2 bg-red-500 px-4 py-2 rounded-full">
                        <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                        <span className="text-white text-sm font-medium">Recording</span>
                      </div>
                    )}
                    
                    {/* Controls */}
                    <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex items-center space-x-4 z-20">
                      <button
                        onClick={toggleCamera}
                        className={`relative p-4 rounded-full backdrop-blur-md transition-all duration-200 shadow-lg ${
                          cameraEnabled 
                            ? 'bg-gray-700/80 hover:bg-gray-600/80' 
                            : 'bg-red-600 hover:bg-red-700'
                        }`}
                        title={cameraEnabled ? 'Turn off camera' : 'Turn on camera'}
                      >
                        <VideoCameraIcon className="w-6 h-6 text-white" />
                        {!cameraEnabled && (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className="w-0.5 h-8 bg-white rotate-45"></div>
                          </div>
                        )}
                      </button>
                      
                      <button
                        onClick={toggleMicrophone}
                        className={`relative p-4 rounded-full backdrop-blur-md transition-all duration-200 shadow-lg ${
                          micEnabled 
                            ? 'bg-gray-700/80 hover:bg-gray-600/80' 
                            : 'bg-red-600 hover:bg-red-700'
                        }`}
                        title={micEnabled ? 'Mute microphone' : 'Unmute microphone'}
                      >
                        <MicrophoneIcon className="w-6 h-6 text-white" />
                        {!micEnabled && (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className="w-0.5 h-8 bg-white rotate-45"></div>
                          </div>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Speech Recognition Component */}
                  <SpeechRecognition
                    isListening={isListening}
                    onTranscriptComplete={handleResponseComplete}
                    maxDuration={questions[currentQuestion].duration}
                    micEnabled={micEnabled}
                    currentQuestion={questions[currentQuestion].text}
                    questionType={questions[currentQuestion].type}
                  />
                </div>
              </motion.div>
            )}

            {/* Completed Screen */}
            {interviewState === 'completed' && (
              <motion.div
                key="completed"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="max-w-4xl w-full"
              >
                <InterviewAnalysis
                  responses={responses}
                  onClose={endInterview}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Progress Bar */}
        {interviewState === 'active' && (
          <div className="p-6">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white/70 text-sm">Progress</span>
                <span className="text-white/70 text-sm">
                  {Math.round(((currentQuestion + 1) / questions.length) * 100)}%
                </span>
              </div>
              <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
                  initial={{ width: 0 }}
                  animate={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
