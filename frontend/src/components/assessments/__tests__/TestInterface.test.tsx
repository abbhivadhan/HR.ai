import React from 'react';
import { render, screen } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import TestInterface from '../TestInterface';
import assessmentService from '../../../services/assessmentService';
import { AssessmentStatus, QuestionType, DifficultyLevel } from '../../../types/assessment';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock assessment service
jest.mock('../../../services/assessmentService', () => ({
  getAssessment: jest.fn(),
  startAssessment: jest.fn(),
  getNextQuestion: jest.fn(),
  submitResponse: jest.fn(),
  completeAssessment: jest.fn(),
  saveDraftResponse: jest.fn(),
  calculateProgress: jest.fn(),
  formatTimeRemaining: jest.fn(),
}));

const mockRouter = {
  push: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
  replace: jest.fn(),
};

const mockAssessment = {
  id: 'test-assessment-id',
  candidate_id: 'test-candidate-id',
  title: 'JavaScript Developer Assessment',
  description: 'Test your JavaScript skills',
  assessment_type: 'technical',
  status: AssessmentStatus.NOT_STARTED,
  duration_minutes: 60,
  total_questions: 5,
  passing_score: 70,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
  questions: [],
};

const mockQuestion = {
  id: 'test-question-id',
  title: 'Array Methods',
  content: 'What is the difference between map() and forEach()?',
  question_type: QuestionType.TEXT_RESPONSE,
  difficulty_level: DifficultyLevel.INTERMEDIATE,
  category: 'javascript',
  max_points: 10,
  ai_generated: false,
  is_active: true,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

describe('TestInterface', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (assessmentService.calculateProgress as jest.Mock).mockReturnValue(20);
    (assessmentService.formatTimeRemaining as jest.Mock).mockReturnValue('59:30');
  });

  describe('Loading State', () => {
    it('should display loading state initially', () => {
      (assessmentService.getAssessment as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      render(<TestInterface assessmentId="test-assessment-id" />);

      expect(screen.getByText('Loading assessment...')).toBeInTheDocument();
    });
  });

  describe('Assessment Display', () => {
    it('should display assessment information when loaded', async () => {
      (assessmentService.getAssessment as jest.Mock).mockResolvedValue(mockAssessment);
      (assessmentService.startAssessment as jest.Mock).mockResolvedValue({
        assessment_id: 'test-assessment-id',
        session_token: 'test-token',
        expires_at: new Date(Date.now() + 3600000).toISOString(),
        first_question: mockQuestion,
      });

      render(<TestInterface assessmentId="test-assessment-id" />);

      // Wait for the assessment to load and display
      await screen.findByText('JavaScript Developer Assessment');
      
      expect(screen.getByText('Question 1 of 5')).toBeInTheDocument();
      expect(screen.getByText('Array Methods')).toBeInTheDocument();
    });
  });

  describe('Accessibility Features', () => {
    it('should have proper ARIA labels and roles', async () => {
      (assessmentService.getAssessment as jest.Mock).mockResolvedValue(mockAssessment);
      (assessmentService.startAssessment as jest.Mock).mockResolvedValue({
        assessment_id: 'test-assessment-id',
        session_token: 'test-token',
        expires_at: new Date(Date.now() + 3600000).toISOString(),
        first_question: mockQuestion,
      });

      render(<TestInterface assessmentId="test-assessment-id" />);

      await screen.findByText('Array Methods');

      expect(screen.getByRole('main', { name: 'Assessment interface' })).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toHaveAttribute('aria-label', expect.stringContaining('Assessment progress'));
      expect(screen.getByRole('region', { name: 'Current question' })).toBeInTheDocument();
    });

    it('should have fullscreen toggle button with proper accessibility', async () => {
      (assessmentService.getAssessment as jest.Mock).mockResolvedValue(mockAssessment);
      (assessmentService.startAssessment as jest.Mock).mockResolvedValue({
        assessment_id: 'test-assessment-id',
        session_token: 'test-token',
        expires_at: new Date(Date.now() + 3600000).toISOString(),
        first_question: mockQuestion,
      });

      render(<TestInterface assessmentId="test-assessment-id" />);

      await screen.findByText('Array Methods');

      const fullscreenButton = screen.getByRole('button', { name: /enter fullscreen/i });
      expect(fullscreenButton).toHaveAttribute('title', 'Enter fullscreen (F11)');
    });
  });

  describe('Error Handling', () => {
    it('should display error when assessment fails to load', async () => {
      (assessmentService.getAssessment as jest.Mock).mockRejectedValue(
        new Error('Assessment not found')
      );

      render(<TestInterface assessmentId="test-assessment-id" />);

      await screen.findByText('Assessment Error');
      
      expect(screen.getByText('Assessment not found')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /back to assessments/i })).toBeInTheDocument();
    });
  });

  describe('Timer Display', () => {
    it('should display timer with proper formatting', async () => {
      (assessmentService.getAssessment as jest.Mock).mockResolvedValue(mockAssessment);
      (assessmentService.startAssessment as jest.Mock).mockResolvedValue({
        assessment_id: 'test-assessment-id',
        session_token: 'test-token',
        expires_at: new Date(Date.now() + 3600000).toISOString(),
        first_question: mockQuestion,
      });

      render(<TestInterface assessmentId="test-assessment-id" />);

      await screen.findByText('Array Methods');

      expect(screen.getByText('59:30')).toBeInTheDocument();
      expect(assessmentService.formatTimeRemaining).toHaveBeenCalled();
    });
  });

  describe('Progress Tracking', () => {
    it('should display progress bar with correct values', async () => {
      (assessmentService.getAssessment as jest.Mock).mockResolvedValue(mockAssessment);
      (assessmentService.startAssessment as jest.Mock).mockResolvedValue({
        assessment_id: 'test-assessment-id',
        session_token: 'test-token',
        expires_at: new Date(Date.now() + 3600000).toISOString(),
        first_question: mockQuestion,
      });

      render(<TestInterface assessmentId="test-assessment-id" />);

      await screen.findByText('Array Methods');

      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', '20');
      expect(progressBar).toHaveAttribute('aria-valuemin', '0');
      expect(progressBar).toHaveAttribute('aria-valuemax', '100');
    });
  });
});