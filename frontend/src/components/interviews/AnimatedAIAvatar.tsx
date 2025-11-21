'use client'

import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  SpeakerWaveIcon,
  EyeIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

interface AnimatedAIAvatarProps {
  isSpeaking: boolean
  isListening: boolean
  emotion?: 'friendly' | 'thinking' | 'excited' | 'neutral'
}

export default function AnimatedAIAvatar({
  isSpeaking,
  isListening,
  emotion = 'friendly'
}: AnimatedAIAvatarProps) {
  const [blinkState, setBlinkState] = useState(false)
  const [mouthState, setMouthState] = useState(0)

  // Blinking animation
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      setBlinkState(true)
      setTimeout(() => setBlinkState(false), 150)
    }, 3000 + Math.random() * 2000)

    return () => clearInterval(blinkInterval)
  }, [])

  // Mouth animation when speaking
  useEffect(() => {
    if (isSpeaking) {
      const mouthInterval = setInterval(() => {
        setMouthState(Math.random())
      }, 100)
      return () => clearInterval(mouthInterval)
    } else {
      setMouthState(0)
    }
  }, [isSpeaking])

  const getEmotionColors = () => {
    switch (emotion) {
      case 'friendly':
        return 'from-blue-400 to-purple-500'
      case 'thinking':
        return 'from-purple-400 to-pink-500'
      case 'excited':
        return 'from-pink-400 to-orange-500'
      default:
        return 'from-gray-400 to-gray-600'
    }
  }

  return (
    <div className="relative">
      {/* Main Avatar Container */}
      <motion.div
        animate={{
          scale: isSpeaking ? [1, 1.02, 1] : 1,
        }}
        transition={{
          duration: 0.5,
          repeat: isSpeaking ? Infinity : 0,
        }}
        className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 relative overflow-hidden"
      >
        {/* Glow Effect */}
        <motion.div
          animate={{
            opacity: isSpeaking ? [0.3, 0.6, 0.3] : 0.3,
            scale: isSpeaking ? [1, 1.1, 1] : 1,
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
          }}
          className={`absolute inset-0 bg-gradient-to-br ${getEmotionColors()} opacity-30 blur-3xl`}
        />

        {/* Avatar SVG */}
        <div className="relative z-10 flex items-center justify-center">
          <svg
            width="300"
            height="300"
            viewBox="0 0 300 300"
            className="drop-shadow-2xl"
          >
            {/* Head */}
            <motion.circle
              cx="150"
              cy="150"
              r="100"
              fill="url(#avatarGradient)"
              animate={{
                r: isSpeaking ? [100, 102, 100] : 100,
              }}
              transition={{
                duration: 0.3,
                repeat: isSpeaking ? Infinity : 0,
              }}
            />

            {/* Gradient Definition */}
            <defs>
              <linearGradient id="avatarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#60A5FA" />
                <stop offset="100%" stopColor="#A78BFA" />
              </linearGradient>
              <linearGradient id="eyeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#FFFFFF" />
                <stop offset="100%" stopColor="#E0E7FF" />
              </linearGradient>
            </defs>

            {/* Eyes */}
            <g>
              {/* Left Eye */}
              <motion.ellipse
                cx="125"
                cy="140"
                rx="15"
                ry={blinkState ? 2 : 20}
                fill="url(#eyeGradient)"
                animate={{
                  ry: blinkState ? 2 : 20,
                }}
                transition={{ duration: 0.1 }}
              />
              <motion.circle
                cx="125"
                cy="140"
                r="8"
                fill="#1E293B"
                animate={{
                  cy: isListening ? [140, 138, 140] : 140,
                }}
                transition={{
                  duration: 2,
                  repeat: isListening ? Infinity : 0,
                }}
              />
              <circle cx="128" cy="137" r="3" fill="#FFFFFF" opacity="0.8" />

              {/* Right Eye */}
              <motion.ellipse
                cx="175"
                cy="140"
                rx="15"
                ry={blinkState ? 2 : 20}
                fill="url(#eyeGradient)"
                animate={{
                  ry: blinkState ? 2 : 20,
                }}
                transition={{ duration: 0.1 }}
              />
              <motion.circle
                cx="175"
                cy="140"
                r="8"
                fill="#1E293B"
                animate={{
                  cy: isListening ? [140, 138, 140] : 140,
                }}
                transition={{
                  duration: 2,
                  repeat: isListening ? Infinity : 0,
                }}
              />
              <circle cx="178" cy="137" r="3" fill="#FFFFFF" opacity="0.8" />
            </g>

            {/* Mouth */}
            <g>
              {isSpeaking ? (
                // Animated mouth when speaking
                <motion.ellipse
                  cx="150"
                  cy="180"
                  rx="25"
                  ry={10 + mouthState * 15}
                  fill="#1E293B"
                  opacity="0.8"
                />
              ) : (
                // Smile when not speaking
                <path
                  d="M 125 180 Q 150 195 175 180"
                  stroke="#1E293B"
                  strokeWidth="4"
                  fill="none"
                  strokeLinecap="round"
                  opacity="0.8"
                />
              )}
            </g>

            {/* Eyebrows */}
            <g opacity="0.6">
              <motion.path
                d="M 110 120 Q 125 115 140 120"
                stroke="#1E293B"
                strokeWidth="4"
                fill="none"
                strokeLinecap="round"
                animate={{
                  d: isListening
                    ? "M 110 118 Q 125 113 140 118"
                    : "M 110 120 Q 125 115 140 120",
                }}
              />
              <motion.path
                d="M 160 120 Q 175 115 190 120"
                stroke="#1E293B"
                strokeWidth="4"
                fill="none"
                strokeLinecap="round"
                animate={{
                  d: isListening
                    ? "M 160 118 Q 175 113 190 118"
                    : "M 160 120 Q 175 115 190 120",
                }}
              />
            </g>

            {/* Decorative Elements */}
            <motion.circle
              cx="80"
              cy="100"
              r="5"
              fill="#FFFFFF"
              opacity="0.4"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.4, 0.6, 0.4],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: 0,
              }}
            />
            <motion.circle
              cx="220"
              cy="120"
              r="4"
              fill="#FFFFFF"
              opacity="0.4"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.4, 0.6, 0.4],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: 0.5,
              }}
            />
            <motion.circle
              cx="100"
              cy="200"
              r="6"
              fill="#FFFFFF"
              opacity="0.4"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.4, 0.6, 0.4],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: 1,
              }}
            />
          </svg>
        </div>

        {/* Status Indicators */}
        <div className="absolute top-4 right-4 flex flex-col space-y-2">
          <AnimatePresence>
            {isSpeaking && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center space-x-2 bg-blue-500/20 backdrop-blur-sm px-3 py-2 rounded-full"
              >
                <SpeakerWaveIcon className="w-4 h-4 text-blue-300" />
                <span className="text-blue-300 text-sm font-medium">Speaking</span>
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.5, repeat: Infinity }}
                  className="w-2 h-2 bg-blue-400 rounded-full"
                />
              </motion.div>
            )}

            {isListening && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center space-x-2 bg-purple-500/20 backdrop-blur-sm px-3 py-2 rounded-full"
              >
                <EyeIcon className="w-4 h-4 text-purple-300" />
                <span className="text-purple-300 text-sm font-medium">Listening</span>
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.5, repeat: Infinity }}
                  className="w-2 h-2 bg-purple-400 rounded-full"
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Name Tag */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
          <div className="bg-white/20 backdrop-blur-sm px-6 py-3 rounded-full">
            <div className="flex items-center space-x-2">
              <SparklesIcon className="w-5 h-5 text-white" />
              <span className="text-white font-semibold">Alex - AI Interviewer</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Sound Waves Effect */}
      {isSpeaking && (
        <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 flex items-center space-x-1">
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              className="w-1 bg-blue-400 rounded-full"
              animate={{
                height: [10, 30, 10],
              }}
              transition={{
                duration: 0.5,
                repeat: Infinity,
                delay: i * 0.1,
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
