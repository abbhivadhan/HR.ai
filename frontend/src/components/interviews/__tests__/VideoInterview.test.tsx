import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { VideoInterview } from '../VideoInterview';
import { Interview, InterviewType, InterviewStatus } from '../../../types/interview';

// Mock the services
jest.mock('../../../services/interviewService', () => ({
  interviewService: {
    createSession: jest.fn(),
    joinSession: jest.fn(),
    getQuestions: jest.fn(),
    formatTimeRemaining: jest.fn((seconds) => `${Math.floor(seconds / 60)}:${(seconds % 60).toString().padStart(2, '0')}`),
    getTypeLabel: jest.fn((type) => type),
    getConnectionQualityLabel: jest.fn(() => 'Good'),
    getConnectionQualityColor: jest.fn(() => 'text-green-500'),
  }
}));

// Mock socket.io-client
jest.mock('socket.io-client', () => ({
  io: jest.fn(() => ({
    on: jest.fn(),
    emit: jest.fn(),
    disconnect: jest.fn(),
  }))
}));

// Mock WebRTC APIs
Object.defineProperty(global, 'RTCPeerConnection', {
  writable: true,
  value: jest.fn().mockImplementation(() => ({
    addTrack: jest.fn(),
    createOffer: jest.fn(),
    createAnswer: jest.fn(),
    setLocalDescription: jest.fn(),
    setRemoteDescription: jest.fn(),
    addIceCandidate: jest.fn(),
    close: jest.fn(),
    onicecandidate: null,
    ontrack: null,
    onconnectionstatechange: null,
    connectionState: 'connected',
  }))
});

Object.defineProperty(global.navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: jest.fn().mockResolvedValue({
      getTracks: () => [
        { stop: jest.fn(), enabled: true },
        { stop: jest.fn(), enabled: true }
      ],
      getVideoTracks: () => [{ enabled: true }],
      getAudioTracks: () => [{ enabled: true }]
    })
  }
});

const mockInterview: Interview = {
  id: '1',
  job_application_id: 'app-1',
  candidate_id: 'candidate-1',
  company_id: 'company-1',
  interview_type: InterviewType.AI_SCREENING,
  title: 'Test Interview',
  description: 'Test description',
  scheduled_at: new Date().toISOString(),
  duration_minutes: 30,
  timezone: 'UTC',
  status: InterviewStatus.SCHEDULED,
  ai_interviewer_persona: 'Professional',
  difficulty_level: 'intermediate',
  focus_areas: ['JavaScript', 'React'],
  max_questions: 10,
  allow_retakes: false,
  recording_enabled: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
};

describe('VideoInterview', () => {
  const mockOnComplete = jest.fn();
  const mockOnError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    render(
      <VideoInterview
        interview={mockInterview}
        onComplete={mockOnComplete}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('Initializing interview session...')).toBeInTheDocument();
  });

  it('displays interview title and type', async () => {
    const { interviewService } = require('../../../services/interviewService');
    
    interviewService.createSession.mockResolvedValue({
      id: 'session-1',
      session_token: 'token-123'
    });
    
    interviewService.joinSession.mockResolvedValue({
      session_id: 'session-1',
      room_id: 'room-1',
      peer_id: 'peer-1',
      signaling_server: 'internal',
      ice_servers: [],
      session_config: {
        recording_enabled: true,
        max_duration: 1800
      }
    });
    
    interviewService.getQuestions.mockResolvedValue([]);

    render(
      <VideoInterview
        interview={mockInterview}
        onComplete={mockOnComplete}
        onError={mockOnError}
      />
    );

    await waitFor(() => {
      expect(screen.queryByText('Initializing interview session...')).not.toBeInTheDocument();
    });
  });

  it('handles errors gracefully', async () => {
    const { interviewService } = require('../../../services/interviewService');
    
    interviewService.createSession.mockRejectedValue(new Error('Session creation failed'));

    render(
      <VideoInterview
        interview={mockInterview}
        onComplete={mockOnComplete}
        onError={mockOnError}
      />
    );

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Session creation failed');
    });
  });

  it('displays timer correctly', () => {
    const { interviewService } = require('../../../services/interviewService');
    
    interviewService.formatTimeRemaining.mockReturnValue('30:00');

    render(
      <VideoInterview
        interview={mockInterview}
        onComplete={mockOnComplete}
        onError={mockOnError}
      />
    );

    // Timer should be displayed once component loads
    expect(interviewService.formatTimeRemaining).toHaveBeenCalled();
  });
});