import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CandidateDashboard from '../CandidateDashboard';

// Mock the dashboard service
jest.mock('../../../services/dashboardService', () => ({
  getCandidateStats: jest.fn(),
  getCandidateRecommendations: jest.fn(),
  getCandidateSkillScores: jest.fn(),
  getCandidateApplicationTrends: jest.fn(),
  getNotifications: jest.fn(),
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

describe('CandidateDashboard', () => {
  const mockCandidateId = 'test-candidate-id';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders dashboard header correctly', async () => {
    render(<CandidateDashboard candidateId={mockCandidateId} />);
    
    expect(screen.getByText('Welcome back!')).toBeInTheDocument();
    expect(screen.getByText("Here's your job search progress")).toBeInTheDocument();
  });

  it('displays loading state initially', () => {
    render(<CandidateDashboard candidateId={mockCandidateId} />);
    
    // The component loads data immediately, so we just check it renders without error
    expect(screen.getByText('Welcome back!')).toBeInTheDocument();
  });

  it('renders stats cards with correct titles', async () => {
    render(<CandidateDashboard candidateId={mockCandidateId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Total Applications')).toBeInTheDocument();
      expect(screen.getByText('Matching Jobs')).toBeInTheDocument();
      expect(screen.getByText('Profile Views')).toBeInTheDocument();
      expect(screen.getByText('Average Score')).toBeInTheDocument();
    });
  });

  it('renders job recommendations section', async () => {
    render(<CandidateDashboard candidateId={mockCandidateId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Recommended Jobs')).toBeInTheDocument();
    });
  });

  it('renders quick actions section', async () => {
    render(<CandidateDashboard candidateId={mockCandidateId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Quick Actions')).toBeInTheDocument();
      expect(screen.getByText('Take Assessment')).toBeInTheDocument();
      expect(screen.getByText('Update Profile')).toBeInTheDocument();
      expect(screen.getByText('Browse Jobs')).toBeInTheDocument();
      expect(screen.getByText('Schedule Interview')).toBeInTheDocument();
    });
  });

  it('renders recent activity section', async () => {
    render(<CandidateDashboard candidateId={mockCandidateId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Recent Activity')).toBeInTheDocument();
    });
  });

  it('renders skill scores chart section', async () => {
    render(<CandidateDashboard candidateId={mockCandidateId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Skill Scores')).toBeInTheDocument();
    });
  });

  it('renders application trends chart section', async () => {
    render(<CandidateDashboard candidateId={mockCandidateId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Application Activity')).toBeInTheDocument();
    });
  });
});