'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ChartBarIcon, LightBulbIcon } from '@heroicons/react/24/outline';
import { AssessmentResults } from '../../types/assessment';
import assessmentService from '../../services/assessmentService';

interface ResultsDisplayProps {
  assessmentId: string;
}

const SkillScoreChart: React.FC<{ skillScores: Record<string, number> }> = ({ skillScores }) => {
  return (
    <div className="space-y-4">
      {Object.entries(skillScores).map(([skill, score]) => (
        <div key={skill} className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-700 capitalize">
              {skill.replace('_', ' ')}
            </span>
            <span className={`text-sm font-semibold ${assessmentService.getScoreColor(score)}`}>
              {score.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${
                score >= 80 ? 'bg-green-500' :
                score >= 60 ? 'bg-yellow-500' :
                'bg-red-500'
              }`}
              style={{ width: `${Math.min(score, 100)}%` }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  );
};

const AIInsights: React.FC<{ 
  analysis: AssessmentResults['ai_analysis'] 
}> = ({ analysis }) => {
  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <div className="text-center">
        <div className={`text-4xl font-bold ${assessmentService.getScoreColor(analysis.overall_score)}`}>
          {analysis.overall_score.toFixed(1)}%
        </div>
        <p className="text-gray-600 mt-1">Overall AI Assessment Score</p>
        <div className="mt-2">
          <div className="flex items-center justify-center space-x-1">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className={`w-3 h-3 rounded-full ${
                  i < Math.floor(analysis.confidence_level * 5)
                    ? 'bg-blue-500'
                    : 'bg-gray-300'
                }`}
              ></div>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Confidence: {(analysis.confidence_level * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      {/* Strengths */}
      {analysis.strengths.length > 0 && (
        <div>
          <h4 className="font-semibold text-green-700 mb-3 flex items-center">
            <span className="mr-2">✅</span>
            Strengths
          </h4>
          <ul className="space-y-2">
            {analysis.strengths.map((strength, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start">
                <span className="text-green-500 mr-2 mt-0.5">•</span>
                {strength}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Areas for Improvement */}
      {analysis.weaknesses.length > 0 && (
        <div>
          <h4 className="font-semibold text-orange-700 mb-3 flex items-center">
            <ChartBarIcon className="w-5 h-5 mr-2" />
            Areas for Improvement
          </h4>
          <ul className="space-y-2">
            {analysis.weaknesses.map((weakness, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start">
                <span className="text-orange-500 mr-2 mt-0.5">•</span>
                {weakness}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <div>
          <h4 className="font-semibold text-blue-700 mb-3 flex items-center">
            <LightBulbIcon className="w-5 h-5 mr-2" />
            Recommendations
          </h4>
          <ul className="space-y-2">
            {analysis.recommendations.map((recommendation, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start">
                <span className="text-blue-500 mr-2 mt-0.5">•</span>
                {recommendation}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

const QuestionReview: React.FC<{ 
  responses: AssessmentResults['responses'] 
}> = ({ responses }) => {
  const [expandedQuestions, setExpandedQuestions] = useState<Set<string>>(new Set());

  const toggleQuestion = (questionId: string) => {
    const newExpanded = new Set(expandedQuestions);
    if (newExpanded.has(questionId)) {
      newExpanded.delete(questionId);
    } else {
      newExpanded.add(questionId);
    }
    setExpandedQuestions(newExpanded);
  };

  return (
    <div className="space-y-4">
      {responses.map((item, index) => {
        const isExpanded = expandedQuestions.has(item.question.id);
        const isCorrect = item.response.is_correct;
        
        return (
          <div
            key={item.question.id}
            className={`border rounded-lg p-4 ${
              isCorrect ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
            }`}
          >
            <div
              className="flex items-center justify-between cursor-pointer"
              onClick={() => toggleQuestion(item.question.id)}
            >
              <div className="flex items-center space-x-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-sm font-medium ${
                  isCorrect ? 'bg-green-500' : 'bg-red-500'
                }`}>
                  {isCorrect ? '✓' : '✗'}
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">
                    Question {index + 1}: {item.question.title}
                  </h4>
                  <p className="text-sm text-gray-600">
                    {item.response.points_earned.toFixed(1)} / {item.question.max_points} points
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-500 capitalize">
                  {item.question.category}
                </span>
                <svg
                  className={`w-5 h-5 text-gray-400 transition-transform ${
                    isExpanded ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>

            {isExpanded && (
              <div className="mt-4 pt-4 border-t border-gray-200 space-y-4">
                {/* Question Content */}
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Question:</h5>
                  <p className="text-gray-700 whitespace-pre-wrap">{item.question.content}</p>
                </div>

                {/* User Response */}
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Your Answer:</h5>
                  <div className="bg-white p-3 rounded border">
                    {item.response.selected_options && (
                      <p className="text-gray-700">
                        Selected: {item.response.selected_options.join(', ')}
                      </p>
                    )}
                    {item.response.response_text && (
                      <p className="text-gray-700 whitespace-pre-wrap">
                        {item.response.response_text}
                      </p>
                    )}
                    {item.response.code_solution && (
                      <pre className="text-sm font-mono text-gray-700 overflow-x-auto">
                        {item.response.code_solution}
                      </pre>
                    )}
                  </div>
                </div>

                {/* AI Feedback */}
                {item.response.ai_feedback && (
                  <div>
                    <h5 className="font-medium text-gray-900 mb-2">AI Feedback:</h5>
                    <div className="bg-blue-50 p-3 rounded border border-blue-200">
                      <p className="text-blue-800 text-sm">{item.response.ai_feedback}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ assessmentId }) => {
  const router = useRouter();
  const [results, setResults] = useState<AssessmentResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'questions'>('overview');

  useEffect(() => {
    const loadResults = async () => {
      try {
        setLoading(true);
        const resultsData = await assessmentService.getAssessmentResults(assessmentId);
        setResults(resultsData);
      } catch (error) {
        console.error('Error loading results:', error);
        setError(error instanceof Error ? error.message : 'Failed to load results');
      } finally {
        setLoading(false);
      }
    };

    loadResults();
  }, [assessmentId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading results...</p>
        </div>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Results Not Available</h2>
          <p className="text-gray-600 mb-4">{error || 'Results not found'}</p>
          <button
            onClick={() => router.push('/assessments')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Assessments
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Assessment Results
              </h1>
              <p className="text-gray-600 mt-1">{results.assessment.title}</p>
              <p className="text-sm text-gray-500">
                Completed on {new Date(results.assessment.completed_at).toLocaleDateString()}
              </p>
            </div>
            
            <div className="text-right">
              <div className={`text-3xl font-bold ${assessmentService.getScoreColor(results.assessment.percentage_score)}`}>
                {results.assessment.percentage_score.toFixed(1)}%
              </div>
              <div className={`text-lg font-medium ${
                results.assessment.passed ? 'text-green-600' : 'text-red-600'
              }`}>
                {results.assessment.passed ? 'PASSED' : 'FAILED'}
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-6 border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'overview', label: 'Overview' },
                { id: 'details', label: 'Skill Breakdown' },
                { id: 'questions', label: 'Question Review' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Score Summary */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Score Summary</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Score:</span>
                  <span className="font-semibold">
                    {results.assessment.total_score} points
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Percentage:</span>
                  <span className={`font-semibold ${assessmentService.getScoreColor(results.assessment.percentage_score)}`}>
                    {results.assessment.percentage_score.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Status:</span>
                  <span className={`font-semibold ${
                    results.assessment.passed ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {results.assessment.passed ? 'Passed' : 'Failed'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Assessment Type:</span>
                  <span className="font-semibold capitalize">
                    {results.assessment.assessment_type.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>

            {/* AI Insights */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Analysis</h3>
              <AIInsights analysis={results.ai_analysis} />
            </div>
          </div>
        )}

        {activeTab === 'details' && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Skill Breakdown</h3>
            <SkillScoreChart skillScores={results.skill_scores} />
          </div>
        )}

        {activeTab === 'questions' && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Question Review</h3>
            <QuestionReview responses={results.responses} />
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="max-w-6xl mx-auto px-4 pb-8">
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => router.push('/assessments')}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Back to Assessments
          </button>
          <button
            onClick={() => window.print()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Print Results
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;