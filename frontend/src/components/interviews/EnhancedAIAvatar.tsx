'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { SparklesIcon, MicrophoneIcon } from '@heroicons/react/24/outline'

interface EnhancedAIAvatarProps {
  isSpeaking: boolean
  isListening: boolean
  emotion?: 'friendly' | 'thinking' | 'excited' | 'neutral'
}

export default function EnhancedAIAvatar({
  isSpeaking,
  isListening,
  emotion = 'friendly'
}: EnhancedAIAvatarProps) {
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

  return (
    <div className="relative">
      {/* Main Avatar Container with 3D effect */}
      <motion.div
        animate={{
          scale: isSpeaking ? [1, 1.02, 1] : 1,
          rotateY: isListening ? [0, 5, 0, -5, 0] : 0
        }}
        transition={{
          duration: isSpeaking ? 0.5 : 2,
          repeat: isSpeaking || isListening ? Infinity : 0,
        }}
        className="relative"
        style={{ transformStyle: 'preserve-3d' }}
      >
        {/* Glow Effect */}
        <motion.div
          animate={{
            opacity: isSpeaking ? [0.4, 0.8, 0.4] : 0.3,
            scale: isSpeaking ? [1, 1.2, 1] : 1,
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
          }}
          className="absolute inset-0 bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 opacity-30 blur-3xl rounded-full"
        />

        {/* Avatar Card */}
        <div className="relative bg-gradient-to-br from-gray-800 to-gray-900 rounded-3xl p-8 shadow-2xl border border-gray-700/50 backdrop-blur-xl">
          {/* Professional Avatar */}
          <div className="relative flex items-center justify-center">
            <svg
              width="320"
              height="320"
              viewBox="0 0 320 320"
              className="drop-shadow-2xl"
            >
              <defs>
                {/* Gradients */}
                <linearGradient id="skinGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FFD4A3" />
                  <stop offset="100%" stopColor="#FFAB73" />
                </linearGradient>
                <linearGradient id="hairGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#4A5568" />
                  <stop offset="100%" stopColor="#2D3748" />
                </linearGradient>
                <linearGradient id="suitGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#3B82F6" />
                  <stop offset="50%" stopColor="#2563EB" />
                  <stop offset="100%" stopColor="#1D4ED8" />
                </linearGradient>
                <radialGradient id="eyeShine">
                  <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.9" />
                  <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
                </radialGradient>
                
                {/* Filters for 3D effect */}
                <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                  <feOffset dx="2" dy="4" result="offsetblur"/>
                  <feComponentTransfer>
                    <feFuncA type="linear" slope="0.3"/>
                  </feComponentTransfer>
                  <feMerge>
                    <feMergeNode/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>

              {/* Head */}
              <motion.ellipse
                cx="160"
                cy="140"
                rx="70"
                ry="85"
                fill="url(#skinGradient)"
                filter="url(#shadow)"
                animate={{
                  ry: isSpeaking ? [85, 87, 85] : 85,
                }}
              />

              {/* Hair */}
              <motion.path
                d="M 90 100 Q 90 60, 160 50 Q 230 60, 230 100 Q 230 120, 220 130 L 220 110 Q 215 90, 160 85 Q 105 90, 100 110 L 100 130 Q 90 120, 90 100 Z"
                fill="url(#hairGradient)"
                filter="url(#shadow)"
              />

              {/* Ears */}
              <ellipse cx="90" cy="140" rx="12" ry="18" fill="url(#skinGradient)" opacity="0.9"/>
              <ellipse cx="230" cy="140" rx="12" ry="18" fill="url(#skinGradient)" opacity="0.9"/>

              {/* Neck */}
              <rect x="140" y="210" width="40" height="30" fill="url(#skinGradient)" rx="5"/>

              {/* Suit/Collar */}
              <motion.path
                d="M 120 240 L 140 220 L 160 230 L 180 220 L 200 240 L 200 320 L 120 320 Z"
                fill="url(#suitGradient)"
                filter="url(#shadow)"
              />
              
              {/* Tie */}
              <path
                d="M 160 230 L 155 250 L 160 280 L 165 250 Z"
                fill="#1E40AF"
                opacity="0.8"
              />

              {/* Eyes */}
              <g>
                {/* Left Eye */}
                <motion.ellipse
                  cx="135"
                  cy="135"
                  rx="18"
                  ry={blinkState ? 2 : 22}
                  fill="#FFFFFF"
                  filter="url(#shadow)"
                  animate={{
                    ry: blinkState ? 2 : 22,
                  }}
                  transition={{ duration: 0.1 }}
                />
                <motion.circle
                  cx="135"
                  cy="135"
                  r="10"
                  fill="#2D3748"
                  animate={{
                    cy: isListening ? [135, 133, 135] : 135,
                  }}
                  transition={{
                    duration: 2,
                    repeat: isListening ? Infinity : 0,
                  }}
                />
                <circle cx="138" cy="132" r="4" fill="url(#eyeShine)"/>

                {/* Right Eye */}
                <motion.ellipse
                  cx="185"
                  cy="135"
                  rx="18"
                  ry={blinkState ? 2 : 22}
                  fill="#FFFFFF"
                  filter="url(#shadow)"
                  animate={{
                    ry: blinkState ? 2 : 22,
                  }}
                  transition={{ duration: 0.1 }}
                />
                <motion.circle
                  cx="185"
                  cy="135"
                  r="10"
                  fill="#2D3748"
                  animate={{
                    cy: isListening ? [135, 133, 135] : 135,
                  }}
                  transition={{
                    duration: 2,
                    repeat: isListening ? Infinity : 0,
                  }}
                />
                <circle cx="188" cy="132" r="4" fill="url(#eyeShine)"/>
              </g>

              {/* Eyebrows */}
              <g opacity="0.7">
                <motion.path
                  d="M 115 115 Q 135 110 155 115"
                  stroke="#2D3748"
                  strokeWidth="5"
                  fill="none"
                  strokeLinecap="round"
                  animate={{
                    d: isListening
                      ? "M 115 113 Q 135 108 155 113"
                      : "M 115 115 Q 135 110 155 115",
                  }}
                />
                <motion.path
                  d="M 165 115 Q 185 110 205 115"
                  stroke="#2D3748"
                  strokeWidth="5"
                  fill="none"
                  strokeLinecap="round"
                  animate={{
                    d: isListening
                      ? "M 165 113 Q 185 108 205 113"
                      : "M 165 115 Q 185 110 205 115",
                  }}
                />
              </g>

              {/* Nose */}
              <path
                d="M 160 150 L 155 165 Q 160 168, 165 165 Z"
                fill="#FFAB73"
                opacity="0.6"
              />

              {/* Mouth */}
              <g>
                {isSpeaking ? (
                  <motion.ellipse
                    cx="160"
                    cy="180"
                    rx="20"
                    ry={8 + mouthState * 12}
                    fill="#8B4513"
                    opacity="0.8"
                  />
                ) : (
                  <motion.path
                    d="M 135 180 Q 160 195 185 180"
                    stroke="#8B4513"
                    strokeWidth="4"
                    fill="none"
                    strokeLinecap="round"
                    opacity="0.8"
                  />
                )}
              </g>

              {/* Glasses (Professional touch) */}
              <g opacity="0.3" stroke="#2D3748" strokeWidth="3" fill="none">
                <circle cx="135" cy="135" r="22"/>
                <circle cx="185" cy="135" r="22"/>
                <line x1="157" y1="135" x2="163" y2="135"/>
              </g>
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
                  className="flex items-center space-x-2 bg-blue-500/20 backdrop-blur-sm px-4 py-2 rounded-full border border-blue-400/30"
                >
                  <motion.div
                    animate={{ scale: [1, 1.3, 1] }}
                    transition={{ duration: 0.5, repeat: Infinity }}
                  >
                    <SparklesIcon className="w-4 h-4 text-blue-300" />
                  </motion.div>
                  <span className="text-blue-300 text-sm font-medium">Speaking</span>
                  <div className="flex space-x-1">
                    {[...Array(3)].map((_, i) => (
                      <motion.div
                        key={i}
                        className="w-1 h-3 bg-blue-400 rounded-full"
                        animate={{
                          height: [12, 20, 12],
                        }}
                        transition={{
                          duration: 0.5,
                          repeat: Infinity,
                          delay: i * 0.1,
                        }}
                      />
                    ))}
                  </div>
                </motion.div>
              )}

              {isListening && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="flex items-center space-x-2 bg-purple-500/20 backdrop-blur-sm px-4 py-2 rounded-full border border-purple-400/30"
                >
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  >
                    <MicrophoneIcon className="w-4 h-4 text-purple-300" />
                  </motion.div>
                  <span className="text-purple-300 text-sm font-medium">Listening</span>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Name Tag */}
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-3 rounded-full shadow-lg border border-white/20"
            >
              <div className="flex items-center space-x-2">
                <SparklesIcon className="w-5 h-5 text-white" />
                <span className="text-white font-bold text-lg">Alex - AI Interviewer</span>
              </div>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Floating Particles */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-blue-400 rounded-full"
            style={{
              left: `${20 + i * 15}%`,
              top: `${30 + (i % 3) * 20}%`,
            }}
            animate={{
              y: [-10, 10, -10],
              opacity: [0.3, 0.7, 0.3],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 3 + i * 0.5,
              repeat: Infinity,
              delay: i * 0.3,
            }}
          />
        ))}
      </div>
    </div>
  )
}
