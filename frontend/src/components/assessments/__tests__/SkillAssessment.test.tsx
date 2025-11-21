import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SkillAssessment from '../SkillAssessment';
import { QuestionType, DifficultyLevel } from '../../../types/assessment';

const mockTextQuestion = {
  id: 'text-question-id',
  title: 'Explain JavaScript Closures',
  content: 'What are closures in JavaScript and how do they work?',
  question_type: QuestionType.TEXT_RESPONSE,
  difficulty_level: DifficultyLevel.INTERMEDIATE,
  category: 'javascript',
  max_points: 15,
  ai_generated: false,
  is_active: true,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

const mockCodingQuestion = {
  id: 'coding-question-id',
  title: 'Implement Fibonacci',
  content: 'Write a function that returns the nth Fibonacci number.',
  question_type: QuestionType.CODING,
  difficulty_level: DifficultyLevel.ADVANCED,
  category: 'algorithms',
  max_points: 25,
  code_template: 'function fibonacci(n) {\n  // Your implementation here\n}',
  test_cases: [
    { input: '0', expected: '0' },
    { input: '1', expected: '1' },
    { input: '5', expected: '5' },
    { input: '10', expected: '55' },
  ],
  ai_generated: false,
  is_active: true,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

const mockMultipleChoiceQuestion = {
  id: 'mc-question-id',
  title: 'JavaScript Data Types',
  content: 'Which of the following is NOT a primitive data type in JavaScript?',
  question_type: QuestionType.MULTIPLE_CHOICE,
  difficulty_level: DifficultyLevel.BEGINNER,
  category: 'javascript',
  max_points: 10,
  options: {
    'A': 'string',
    'B': 'number',
    'C': 'object',
    'D': 'boolean',
  },
  correct_answer: 'C',
  ai_generated: false,
  is_active: true,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

describe('SkillAssessment', () => {
  const mockOnSubmit = jest.fn();
  const mockOnAutoSave = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Text Response Questions', () => {
    it('should render text response question correctly', () => {
      render(
        <SkillAssessment
          question={mockTextQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
          onAutoSave={mockOnAutoSave}
        />
      );

      expect(screen.getByText('Explain JavaScript Closures')).toBeInTheDocument();
      expect(screen.getByText('What are closures in JavaScript and how do they work?')).toBeInTheDocument();
      expect(screen.getByText('intermediate')).toBeInTheDocument();
      expect(screen.getByText('15 points')).toBeInTheDocument();
      expect(screen.getByRole('textbox', { name: /text response input/i })).toBeInTheDocument();
    });

    it('should handle text input', () => {
      render(
        <SkillAssessment
          question={mockTextQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      const textarea = screen.getByRole('textbox', { name: /text response input/i });
      const submitButton = screen.getByRole('button', { name: /submit answer/i });

      // Initially submit button should be disabled
      expect(submitButton).toBeDisabled();

      // Type response
      fireEvent.change(textarea, { 
        target: { value: 'Closures are functions that have access to variables from their outer scope...' }
      });

      // Submit button should now be enabled
      expect(submitButton).toBeEnabled();
    });

    it('should display character count', () => {
      render(
        <SkillAssessment
          question={mockTextQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      const textarea = screen.getByRole('textbox', { name: /text response input/i });
      
      expect(screen.getByText('0 characters')).toBeInTheDocument();

      fireEvent.change(textarea, { target: { value: 'Hello' } });

      expect(screen.getByText('5 characters')).toBeInTheDocument();
    });
  });

  describe('Multiple Choice Questions', () => {
    it('should render multiple choice question correctly', () => {
      render(
        <SkillAssessment
          question={mockMultipleChoiceQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      expect(screen.getByText('JavaScript Data Types')).toBeInTheDocument();
      expect(screen.getByText('Which of the following is NOT a primitive data type in JavaScript?')).toBeInTheDocument();
      expect(screen.getByText('beginner')).toBeInTheDocument();
      expect(screen.getByText('10 points')).toBeInTheDocument();

      // Check all options are rendered
      expect(screen.getByText('string')).toBeInTheDocument();
      expect(screen.getByText('number')).toBeInTheDocument();
      expect(screen.getByText('object')).toBeInTheDocument();
      expect(screen.getByText('boolean')).toBeInTheDocument();
    });

    it('should handle option selection', () => {
      render(
        <SkillAssessment
          question={mockMultipleChoiceQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      const submitButton = screen.getByRole('button', { name: /submit answer/i });
      
      // Initially submit button should be disabled
      expect(submitButton).toBeDisabled();

      // Select option C
      const optionC = screen.getByDisplayValue('C');
      fireEvent.click(optionC);

      expect(optionC).toBeChecked();
      expect(submitButton).toBeEnabled();
    });
  });

  describe('Coding Questions', () => {
    it('should render coding question correctly', () => {
      render(
        <SkillAssessment
          question={mockCodingQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      expect(screen.getByText('Implement Fibonacci')).toBeInTheDocument();
      expect(screen.getByText('Write a function that returns the nth Fibonacci number.')).toBeInTheDocument();
      expect(screen.getByText('advanced')).toBeInTheDocument();
      expect(screen.getByText('25 points')).toBeInTheDocument();
      expect(screen.getByText('Test Cases:')).toBeInTheDocument();
      expect(screen.getByRole('textbox', { name: /code editor/i })).toBeInTheDocument();
    });

    it('should display test cases correctly', () => {
      render(
        <SkillAssessment
          question={mockCodingQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      // Check test cases are displayed (using getAllByText for multiple elements)
      expect(screen.getAllByText('Input:')).toHaveLength(4);
      expect(screen.getAllByText('Expected Output:')).toHaveLength(4);
    });

    it('should handle code input', () => {
      render(
        <SkillAssessment
          question={mockCodingQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      const codeEditor = screen.getByRole('textbox', { name: /code editor/i });
      const submitButton = screen.getByRole('button', { name: /submit solution/i });

      // Code editor should have template
      expect(codeEditor).toHaveValue('function fibonacci(n) {\n  // Your implementation here\n}');

      // Type new code
      fireEvent.change(codeEditor, { 
        target: { value: 'function fibonacci(n) { return n <= 1 ? n : fibonacci(n-1) + fibonacci(n-2); }' }
      });

      expect(codeEditor).toHaveValue('function fibonacci(n) { return n <= 1 ? n : fibonacci(n-1) + fibonacci(n-2); }');
    });
  });

  describe('Accessibility Features', () => {
    it('should have proper ARIA labels for coding questions', () => {
      render(
        <SkillAssessment
          question={mockCodingQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      const codeEditor = screen.getByRole('textbox', { name: /code editor/i });
      expect(codeEditor).toHaveAttribute('aria-describedby', 'code-editor-help');
    });

    it('should have proper ARIA labels for multiple choice questions', () => {
      render(
        <SkillAssessment
          question={mockMultipleChoiceQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      const optionA = screen.getByDisplayValue('A');
      expect(optionA).toHaveAttribute('aria-describedby', 'option-A-description');
    });
  });

  describe('Difficulty Level Display', () => {
    it('should display correct styling for different difficulty levels', () => {
      const { rerender } = render(
        <SkillAssessment
          question={{ ...mockTextQuestion, difficulty_level: DifficultyLevel.BEGINNER }}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      expect(screen.getByText('beginner')).toHaveClass('bg-green-100', 'text-green-800');

      rerender(
        <SkillAssessment
          question={{ ...mockTextQuestion, difficulty_level: DifficultyLevel.EXPERT }}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      expect(screen.getByText('expert')).toHaveClass('bg-red-100', 'text-red-800');
    });
  });

  describe('Submission', () => {
    it('should call onSubmit with correct data for text questions', () => {
      render(
        <SkillAssessment
          question={mockTextQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      const textarea = screen.getByRole('textbox', { name: /text response input/i });
      const submitButton = screen.getByRole('button', { name: /submit answer/i });

      fireEvent.change(textarea, { 
        target: { value: 'Test response' }
      });

      fireEvent.click(submitButton);

      expect(mockOnSubmit).toHaveBeenCalledWith({
        response_text: 'Test response',
      });
    });

    it('should call onSubmit with correct data for multiple choice questions', () => {
      render(
        <SkillAssessment
          question={mockMultipleChoiceQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      const optionC = screen.getByDisplayValue('C');
      const submitButton = screen.getByRole('button', { name: /submit answer/i });

      fireEvent.click(optionC);
      fireEvent.click(submitButton);

      expect(mockOnSubmit).toHaveBeenCalledWith({
        selected_options: ['C'],
      });
    });

    it('should call onSubmit with correct data for coding questions', () => {
      render(
        <SkillAssessment
          question={mockCodingQuestion}
          onSubmit={mockOnSubmit}
          timeRemaining={1800}
        />
      );

      const codeEditor = screen.getByRole('textbox', { name: /code editor/i });
      const submitButton = screen.getByRole('button', { name: /submit solution/i });

      fireEvent.change(codeEditor, { 
        target: { value: 'function fibonacci(n) { return n; }' }
      });

      fireEvent.click(submitButton);

      expect(mockOnSubmit).toHaveBeenCalledWith({
        code_solution: 'function fibonacci(n) { return n; }',
      });
    });
  });
});