import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TestRunner from '../TestRunner';

const mockTestCases = [
  { input: '5', expected: '120', description: 'Calculate factorial of 5' },
  { input: '0', expected: '1', description: 'Calculate factorial of 0' },
  { input: '3', expected: '6', description: 'Calculate factorial of 3' },
];

const mockCode = 'function factorial(n) { return n <= 1 ? 1 : n * factorial(n - 1); }';

describe('TestRunner', () => {
  const mockOnRunTests = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render test cases correctly', () => {
    render(
      <TestRunner
        testCases={mockTestCases}
        code={mockCode}
        onRunTests={mockOnRunTests}
        isRunning={false}
      />
    );

    expect(screen.getByText('Test Cases')).toBeInTheDocument();
    expect(screen.getByText('Calculate factorial of 5')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('120')).toBeInTheDocument();
  });

  it('should show run tests button', () => {
    render(
      <TestRunner
        testCases={mockTestCases}
        code={mockCode}
        onRunTests={mockOnRunTests}
        isRunning={false}
      />
    );

    const runButton = screen.getByRole('button', { name: /run all tests/i });
    expect(runButton).toBeInTheDocument();
    expect(runButton).toBeEnabled();
  });

  it('should disable run button when no code', () => {
    render(
      <TestRunner
        testCases={mockTestCases}
        code=""
        onRunTests={mockOnRunTests}
        isRunning={false}
      />
    );

    const runButton = screen.getByRole('button', { name: /run all tests/i });
    expect(runButton).toBeDisabled();
  });

  it('should show loading state when running', () => {
    render(
      <TestRunner
        testCases={mockTestCases}
        code={mockCode}
        onRunTests={mockOnRunTests}
        isRunning={true}
      />
    );

    expect(screen.getByText('Running Tests...')).toBeInTheDocument();
    const runButton = screen.getByRole('button', { name: /running tests/i });
    expect(runButton).toBeDisabled();
  });

  it('should call onRunTests when button is clicked', async () => {
    mockOnRunTests.mockResolvedValue({
      passed: true,
      results: [
        { passed: true, output: '120' },
        { passed: true, output: '1' },
        { passed: true, output: '6' },
      ],
    });

    render(
      <TestRunner
        testCases={mockTestCases}
        code={mockCode}
        onRunTests={mockOnRunTests}
        isRunning={false}
      />
    );

    const runButton = screen.getByRole('button', { name: /run all tests/i });
    fireEvent.click(runButton);

    expect(mockOnRunTests).toHaveBeenCalledWith(mockCode);
  });

  it('should display successful test results', async () => {
    const mockResults = {
      passed: true,
      results: [
        { passed: true, output: '120' },
        { passed: true, output: '1' },
        { passed: true, output: '6' },
      ],
    };

    mockOnRunTests.mockResolvedValue(mockResults);

    render(
      <TestRunner
        testCases={mockTestCases}
        code={mockCode}
        onRunTests={mockOnRunTests}
        isRunning={false}
      />
    );

    const runButton = screen.getByRole('button', { name: /run all tests/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText('All Tests Passed!')).toBeInTheDocument();
    });

    expect(screen.getByText('3/3 passed')).toBeInTheDocument();
    expect(screen.getByText('Success')).toBeInTheDocument();
  });

  it('should display failed test results', async () => {
    const mockResults = {
      passed: false,
      results: [
        { passed: true, output: '120' },
        { passed: false, output: '0', error: 'Expected 1, got 0' },
        { passed: true, output: '6' },
      ],
    };

    mockOnRunTests.mockResolvedValue(mockResults);

    render(
      <TestRunner
        testCases={mockTestCases}
        code={mockCode}
        onRunTests={mockOnRunTests}
        isRunning={false}
      />
    );

    const runButton = screen.getByRole('button', { name: /run all tests/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText('Some Tests Failed')).toBeInTheDocument();
    });

    expect(screen.getByText('2/3 passed')).toBeInTheDocument();
    expect(screen.getByText('⚠️')).toBeInTheDocument();
  });

  it('should expand test details when details button is clicked', async () => {
    const mockResults = {
      passed: false,
      results: [
        { passed: false, output: '0', error: 'Expected 120, got 0', executionTime: 5 },
        { passed: true, output: '1' },
        { passed: true, output: '6' },
      ],
    };

    mockOnRunTests.mockResolvedValue(mockResults);

    render(
      <TestRunner
        testCases={mockTestCases}
        code={mockCode}
        onRunTests={mockOnRunTests}
        isRunning={false}
      />
    );

    const runButton = screen.getByRole('button', { name: /run all tests/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText('Some Tests Failed')).toBeInTheDocument();
    });

    const detailsButton = screen.getAllByText('Details')[0];
    fireEvent.click(detailsButton);

    expect(screen.getByText('Actual Output:')).toBeInTheDocument();
    expect(screen.getByText('Error:')).toBeInTheDocument();
    expect(screen.getByText('Expected 120, got 0')).toBeInTheDocument();
    expect(screen.getByText('Execution time: 5ms')).toBeInTheDocument();
  });

  it('should handle test execution errors', async () => {
    mockOnRunTests.mockRejectedValue(new Error('Test execution failed'));

    render(
      <TestRunner
        testCases={mockTestCases}
        code={mockCode}
        onRunTests={mockOnRunTests}
        isRunning={false}
      />
    );

    const runButton = screen.getByRole('button', { name: /run all tests/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText('Some Tests Failed')).toBeInTheDocument();
    });

    expect(screen.getByText('0/3 passed')).toBeInTheDocument();
  });

  it('should show correct status icons', async () => {
    const mockResults = {
      passed: false,
      results: [
        { passed: true },
        { passed: false },
        { passed: true },
      ],
    };

    mockOnRunTests.mockResolvedValue(mockResults);

    render(
      <TestRunner
        testCases={mockTestCases}
        code={mockCode}
        onRunTests={mockOnRunTests}
        isRunning={false}
      />
    );

    const runButton = screen.getByRole('button', { name: /run all tests/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText('Some Tests Failed')).toBeInTheDocument();
    });

    // Check for success and failure icons
    expect(screen.getAllByText('✅')).toHaveLength(2); // Two passing tests
    expect(screen.getAllByText('❌')).toHaveLength(1); // One failing test
  });
});