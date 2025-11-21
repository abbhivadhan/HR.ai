'use client';

import React, { useState } from 'react';

interface TestCase {
  input: string;
  expected: string;
  description?: string;
}

interface TestResult {
  passed: boolean;
  error?: string;
  output?: string;
  executionTime?: number;
}

interface TestRunnerProps {
  testCases: TestCase[];
  code: string;
  onRunTests: (code: string) => Promise<{ passed: boolean; results: TestResult[] }>;
  isRunning: boolean;
}

const TestRunner: React.FC<TestRunnerProps> = ({ 
  testCases, 
  code, 
  onRunTests, 
  isRunning 
}) => {
  const [results, setResults] = useState<{ passed: boolean; results: TestResult[] } | null>(null);
  const [expandedTests, setExpandedTests] = useState<Set<number>>(new Set());

  const handleRunTests = async () => {
    try {
      const testResults = await onRunTests(code);
      setResults(testResults);
    } catch (error) {
      console.error('Test execution failed:', error);
      setResults({
        passed: false,
        results: testCases.map(() => ({ 
          passed: false, 
          error: 'Test execution failed' 
        }))
      });
    }
  };

  const toggleTestExpansion = (index: number) => {
    const newExpanded = new Set(expandedTests);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedTests(newExpanded);
  };

  const getTestStatusIcon = (result: TestResult) => {
    if (result.passed) {
      return <span className="text-green-600 text-lg">✅</span>;
    }
    return <span className="text-red-600 text-lg">❌</span>;
  };

  const getOverallStatus = () => {
    if (!results) return null;
    
    const passedCount = results.results.filter(r => r.passed).length;
    const totalCount = results.results.length;
    
    return (
      <div className={`p-4 rounded-lg border ${
        results.passed 
          ? 'bg-green-50 border-green-200' 
          : 'bg-red-50 border-red-200'
      }`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center">
            {results.passed ? (
              <span className="text-green-600 font-semibold mr-2">Success</span>
            ) : (
              <span className="text-red-600 font-semibold mr-2">Warning</span>
            )}
            <h4 className={`font-medium ${
              results.passed ? 'text-green-800' : 'text-red-800'
            }`}>
              {results.passed ? 'All Tests Passed!' : 'Some Tests Failed'}
            </h4>
          </div>
          <div className={`text-sm font-medium ${
            results.passed ? 'text-green-700' : 'text-red-700'
          }`}>
            {passedCount}/{totalCount} passed
          </div>
        </div>
        
        {!results.passed && (
          <p className="text-sm text-red-700">
            Review the failed tests below and update your code accordingly.
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Test Cases Display */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-gray-900">Test Cases</h4>
          <button
            onClick={handleRunTests}
            disabled={!code.trim() || isRunning}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isRunning ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Running Tests...
              </span>
            ) : (
              'Run All Tests'
            )}
          </button>
        </div>
        
        <div className="space-y-3">
          {testCases.map((testCase, index) => (
            <div key={index} className="bg-white p-3 rounded border">
              <div className="flex items-center justify-between">
                <div className="text-sm font-mono space-y-1 flex-1">
                  <div>
                    <span className="text-gray-600 font-medium">Input:</span>{' '}
                    <span className="text-blue-600">{testCase.input}</span>
                  </div>
                  <div>
                    <span className="text-gray-600 font-medium">Expected:</span>{' '}
                    <span className="text-green-600">{testCase.expected}</span>
                  </div>
                  {testCase.description && (
                    <div className="text-gray-500 text-xs mt-1">
                      {testCase.description}
                    </div>
                  )}
                </div>
                
                {results && results.results[index] && (
                  <div className="ml-4 flex items-center space-x-2">
                    {getTestStatusIcon(results.results[index])}
                    <button
                      onClick={() => toggleTestExpansion(index)}
                      className="text-xs text-gray-500 hover:text-gray-700"
                      aria-label={`${expandedTests.has(index) ? 'Hide' : 'Show'} test details`}
                    >
                      {expandedTests.has(index) ? 'Hide' : 'Details'}
                    </button>
                  </div>
                )}
              </div>
              
              {/* Expanded test details */}
              {results && results.results[index] && expandedTests.has(index) && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="text-sm space-y-2">
                    {results.results[index].output && (
                      <div>
                        <span className="font-medium text-gray-700">Actual Output:</span>
                        <div className="font-mono text-blue-600 bg-blue-50 p-2 rounded mt-1">
                          {results.results[index].output}
                        </div>
                      </div>
                    )}
                    
                    {results.results[index].error && (
                      <div>
                        <span className="font-medium text-red-700">Error:</span>
                        <div className="font-mono text-red-600 bg-red-50 p-2 rounded mt-1">
                          {results.results[index].error}
                        </div>
                      </div>
                    )}
                    
                    {results.results[index].executionTime && (
                      <div className="text-xs text-gray-500">
                        Execution time: {results.results[index].executionTime}ms
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Overall Results */}
      {results && getOverallStatus()}
    </div>
  );
};

export default TestRunner;