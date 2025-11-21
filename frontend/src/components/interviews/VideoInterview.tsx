'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  VideoCameraIcon,
  VideoCameraSlashIcon,
  MicrophoneIcon,
  XMarkIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  CogIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import {
  Interview,
  InterviewSession,
  InterviewQuestion,
  SessionJoinResponse,
  VideoSettings,
  ConnectionQuality,
  SessionStatus,
  SignalingMessage,
  WebSocketMessage
} from '../../types/interview';
import { interviewService } from '../../services/interviewService';
import { AIInterviewer } from './AIInterviewer';
import { VideoControls } from './VideoControls';
import { InterviewProgress } from './InterviewProgress';
import { TechnicalIssues } from './TechnicalIssues';
import { io, Socket } from 'socket.io-client';

interface VideoInterviewProps {
  interview: Interview;
  onComplete: (analysis?: any) => void;
  onError: (error: string) => void;
}

export const VideoInterview: React.FC<VideoInterviewProps> = ({
  interview,
  onComplete,
  onError
}) => {
  // State management
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(interview.duration_minutes * 60);
  const [connectionQuality, setConnectionQuality] = useState<ConnectionQuality>({
    overall: 'good',
    video: 0.8,
    audio: 0.8,
    latency: 50,
    bandwidth: 1000
  });
  const [videoSettings, setVideoSettings] = useState<VideoSettings>({
    camera: true,
    microphone: true,
    speaker: true
  });
  const [showSettings, setShowSettings] = useState(false);
  const [showTechnicalIssues, setShowTechnicalIssues] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Refs
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const socketRef = useRef<Socket | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const sessionInfoRef = useRef<SessionJoinResponse | null>(null);

  // Initialize interview session
  const initializeSession = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // Create session
      const newSession = await interviewService.createSession(interview.id);
      setSession(newSession);

      // Join session
      const sessionInfo = await interviewService.joinSession(newSession.session_token);
      sessionInfoRef.current = sessionInfo;

      // Load questions
      const interviewQuestions = await interviewService.getQuestions(interview.id);
      setQuestions(interviewQuestions);

      // Initialize WebRTC
      await initializeWebRTC(sessionInfo);

      // Connect to WebSocket
      initializeWebSocket(sessionInfo.room_id);

      setIsLoading(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to initialize interview';
      setError(errorMessage);
      onError(errorMessage);
      setIsLoading(false);
    }
  }, [interview.id, onError]);

  // Initialize WebRTC connection
  const initializeWebRTC = useCallback(async (sessionInfo: SessionJoinResponse) => {
    try {
      // Create peer connection
      const peerConnection = new RTCPeerConnection({
        iceServers: sessionInfo.ice_servers
      });

      peerConnectionRef.current = peerConnection;

      // Set up event handlers
      peerConnection.onicecandidate = (event) => {
        if (event.candidate && socketRef.current) {
          socketRef.current.emit('signaling', {
            type: 'ice-candidate',
            candidate: event.candidate.candidate,
            sdpMid: event.candidate.sdpMid,
            sdpMLineIndex: event.candidate.sdpMLineIndex,
            room_id: sessionInfo.room_id,
            peer_id: sessionInfo.peer_id
          });
        }
      };

      peerConnection.ontrack = (event) => {
        if (remoteVideoRef.current && event.streams[0]) {
          remoteVideoRef.current.srcObject = event.streams[0];
        }
      };

      peerConnection.onconnectionstatechange = () => {
        const state = peerConnection.connectionState;
        setIsConnected(state === 'connected');
        
        if (socketRef.current) {
          socketRef.current.emit('signaling', {
            type: 'connection-state',
            state: state,
            room_id: sessionInfo.room_id,
            peer_id: sessionInfo.peer_id
          });
        }
      };

      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({
        video: videoSettings.camera,
        audio: videoSettings.microphone
      });

      localStreamRef.current = stream;
      
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }

      // Add tracks to peer connection
      stream.getTracks().forEach(track => {
        peerConnection.addTrack(track, stream);
      });

    } catch (err) {
      throw new Error('Failed to initialize WebRTC: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  }, [videoSettings]);

  // Initialize WebSocket connection
  const initializeWebSocket = useCallback((roomId: string) => {
    const socket = io(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000', {
      transports: ['websocket']
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      socket.emit('join_room', { room_id: roomId });
    });

    socket.on('signaling', (message: SignalingMessage) => {
      handleSignalingMessage(message);
    });

    socket.on('peer_connection_state', (data: any) => {
      console.log('Peer connection state:', data);
    });

    socket.on('session_ended', (data: any) => {
      handleSessionEnd(data.reason);
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
    });

    socket.on('error', (error: any) => {
      console.error('WebSocket error:', error);
      setError('Connection error occurred');
    });
  }, []);

  // Handle WebRTC signaling messages
  const handleSignalingMessage = useCallback(async (message: SignalingMessage) => {
    const peerConnection = peerConnectionRef.current;
    if (!peerConnection) return;

    try {
      switch (message.type) {
        case 'offer':
          if (message.sdp) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription({
              type: 'offer',
              sdp: message.sdp
            }));
            
            const answer = await peerConnection.createAnswer();
            await peerConnection.setLocalDescription(answer);
            
            if (socketRef.current && sessionInfoRef.current) {
              socketRef.current.emit('signaling', {
                type: 'answer',
                sdp: answer.sdp,
                to_peer: message.from_peer,
                room_id: sessionInfoRef.current.room_id,
                peer_id: sessionInfoRef.current.peer_id
              });
            }
          }
          break;

        case 'answer':
          if (message.sdp) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription({
              type: 'answer',
              sdp: message.sdp
            }));
          }
          break;

        case 'ice-candidate':
          if (message.candidate) {
            await peerConnection.addIceCandidate(new RTCIceCandidate({
              candidate: message.candidate,
              sdpMid: message.sdpMid,
              sdpMLineIndex: message.sdpMLineIndex
            }));
          }
          break;
      }
    } catch (err) {
      console.error('Error handling signaling message:', err);
    }
  }, []);

  // Handle session end
  const handleSessionEnd = useCallback((reason: string) => {
    setIsConnected(false);
    setIsRecording(false);
    
    if (reason === 'completed') {
      onComplete();
    } else {
      setError(`Interview ended: ${reason}`);
    }
  }, [onComplete]);

  // Start interview timer
  const startTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          handleSessionEnd('time_expired');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, [handleSessionEnd]);

  // Toggle video settings
  const toggleCamera = useCallback(async () => {
    if (localStreamRef.current) {
      const videoTrack = localStreamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoSettings.camera;
        setVideoSettings(prev => ({ ...prev, camera: !prev.camera }));
      }
    }
  }, [videoSettings.camera]);

  const toggleMicrophone = useCallback(async () => {
    if (localStreamRef.current) {
      const audioTrack = localStreamRef.current.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !videoSettings.microphone;
        setVideoSettings(prev => ({ ...prev, microphone: !prev.microphone }));
      }
    }
  }, [videoSettings.microphone]);

  const toggleSpeaker = useCallback(() => {
    setVideoSettings(prev => ({ ...prev, speaker: !prev.speaker }));
  }, []);

  // Handle technical issues
  const handleTechnicalIssue = useCallback((issue: string) => {
    setShowTechnicalIssues(true);
    setError(issue);
  }, []);

  // Cleanup
  const cleanup = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
    }

    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
    }

    if (socketRef.current) {
      socketRef.current.disconnect();
    }
  }, []);

  // Effects
  useEffect(() => {
    initializeSession();
    return cleanup;
  }, [initializeSession, cleanup]);

  useEffect(() => {
    if (isConnected && !isRecording) {
      setIsRecording(true);
      startTimer();
    }
  }, [isConnected, isRecording, startTimer]);

  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing interview session...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error && !showTechnicalIssues) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center max-w-md">
          <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Interview Error</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => setShowTechnicalIssues(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Get Help
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-white">{interview.title}</h1>
            <p className="text-gray-400 text-sm">
              {interviewService.getTypeLabel(interview.interview_type)}
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Connection status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-300">
                {isConnected ? 'Connected' : 'Connecting...'}
              </span>
            </div>

            {/* Timer */}
            <div className="flex items-center space-x-2 text-white">
              <ClockIcon className="h-5 w-5" />
              <span className="font-mono">
                {interviewService.formatTimeRemaining(timeRemaining)}
              </span>
            </div>

            {/* Settings */}
            <button
              onClick={() => setShowSettings(true)}
              className="p-2 text-gray-400 hover:text-white rounded-md hover:bg-gray-700"
            >
              <CogIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex">
        {/* Video area */}
        <div className="flex-1 flex flex-col">
          {/* Video streams */}
          <div className="flex-1 relative bg-black">
            {/* Remote video (AI interviewer) */}
            <video
              ref={remoteVideoRef}
              autoPlay
              playsInline
              muted={!videoSettings.speaker}
              className="w-full h-full object-cover"
            />

            {/* Local video (candidate) */}
            <div className="absolute bottom-4 right-4 w-48 h-36 bg-gray-800 rounded-lg overflow-hidden border-2 border-gray-600">
              <video
                ref={localVideoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
              {!videoSettings.camera && (
                <div className="absolute inset-0 bg-gray-800 flex items-center justify-center">
                  <VideoCameraSlashIcon className="h-8 w-8 text-gray-400" />
                </div>
              )}
            </div>

            {/* Connection quality indicator */}
            <div className="absolute top-4 left-4">
              <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                interviewService.getConnectionQualityColor(connectionQuality.video)
              } bg-black bg-opacity-50 text-white`}>
                {interviewService.getConnectionQualityLabel(connectionQuality.video)}
              </div>
            </div>
          </div>

          {/* Video controls */}
          <VideoControls
            videoSettings={videoSettings}
            onToggleCamera={toggleCamera}
            onToggleMicrophone={toggleMicrophone}
            onToggleSpeaker={toggleSpeaker}
            onTechnicalIssue={handleTechnicalIssue}
            connectionQuality={connectionQuality}
          />
        </div>

        {/* AI Interviewer panel */}
        <div className="w-96 bg-gray-800 border-l border-gray-700">
          <AIInterviewer
            interview={interview}
            currentQuestion={currentQuestion}
            questions={questions}
            currentQuestionIndex={currentQuestionIndex}
            onQuestionComplete={(response) => {
              // Handle question response
              if (currentQuestion) {
                interviewService.submitQuestionResponse(currentQuestion.id, {
                  response: response,
                  duration: 120 // TODO: Calculate actual duration
                });
              }
              
              // Move to next question
              if (currentQuestionIndex < questions.length - 1) {
                setCurrentQuestionIndex(prev => prev + 1);
              } else {
                handleSessionEnd('completed');
              }
            }}
            isRecording={isRecording}
          />
        </div>
      </div>

      {/* Progress bar */}
      <InterviewProgress
        currentQuestionIndex={currentQuestionIndex}
        totalQuestions={questions.length}
        timeRemaining={timeRemaining}
        totalDuration={interview.duration_minutes * 60}
      />

      {/* Modals */}
      <AnimatePresence>
        {showTechnicalIssues && (
          <TechnicalIssues
            onClose={() => setShowTechnicalIssues(false)}
            onReconnect={() => {
              setShowTechnicalIssues(false);
              initializeSession();
            }}
            error={error}
          />
        )}
      </AnimatePresence>
    </div>
  );
};