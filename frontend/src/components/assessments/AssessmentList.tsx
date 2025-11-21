'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Assessment, AssessmentStatus, AssessmentType } from '../../types/assessment';
import assessmentService from '../../services/assessmentService';

const AssessmentCard: React.FC<{ 
  assessment: Assessment;
  onStart: (id: string) => void;
  onViewResults: (id: string) => void;
}> = ({ assessment, onStart, onViewResults }) => {
  const getStatusColor = (status: AssessmentStatus) => {
    switch (status) {
      case AssessmentStatus.NOT_STARTED:
        return 'bg-blue-100 text-blue-800';
      case AssessmentStatus.IN_PROGRESS:
        return 'bg-yellow-100 text-yellow-800';
      case AssessmentStatus.COMPLETED:
        return 'bg-green-100 text-green-800';
      case AssessmentStatus.EXPIRED:
        return 'bg-red-100 text-red-800';
      case AssessmentStatus.CANCELLED:
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: AssessmentType) => {
    switch (type) {
      case AssessmentType.TECHNICAL:
        return 'TECH';
      case AssessmentType.BEHAVIORAL:
        return 'BEH';
      case AssessmentType.COGNITIVE:
        return 'COG';
      case AssessmentType.PERSONALITY:
        return 'PER';
      case AssessmentType.CODING:
        return 'CODE';
      default:
        return 'TEST';
    }
  };

  const canStart = assessment.status === AssessmentStatus.NOT_STARTED || 
                   assessment.status === AssessmentStatus.IN_PROGRESS;
  const isCompleted = assessment.status === AssessmentStatus.COMPLETED;
  const isExpired = assessment.status === AssessmentStatus.EXPIRED;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getTypeIcon(assessment.assessment_type)}</span>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{assessment.title}</h3>
            <p className="text-sm text-gray-600 capitalize">
              {assessment.assessment_type.replace('_', ' ')} Assessment
            </p>
          </div>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(assessment.status)}`}>
          {assessment.status.replace('_', ' ').toUpperCase()}
        </span>
      </div>

      {assessment.description && (
        <p className="text-gray-700 mb-4 line-clamp-2">{assessment.description}</p>
      )}

      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div>
          <span className="text-gray-500">Duration:</span>
          <span className="ml-2 font-medium">{assessment.duration_minutes} minutes</span>
        </div>
        <div>
          <span className="text-gray-500">Questions:</span>
          <span className="ml-2 font-medium">{assessment.total_questions}</span>
        </div>
        <div>
          <span className="text-gray-500">Passing Score:</span>
          <span className="ml-2 font-medium">{assessment.passing_score}%</span>
        </div>
        {assessment.expires_at && (
          <div>
            <span className="text-gray-500">Expires:</span>
            <span className="ml-2 font-medium">
              {new Date(assessment.expires_at).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>

      {/* Progress for in-progress assessments */}
      {assessment.status === AssessmentStatus.IN_PROGRESS && assessment.started_at && (
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Progress</span>
            <span>Started {new Date(assessment.started_at).toLocaleDateString()}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '30%' }}></div>
          </div>
        </div>
      )}

      {/* Results for completed assessments */}
      {isCompleted && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex justify-between items-center">
            <div>
              <span className="text-sm text-gray-600">Final Score:</span>
              <span className={`ml-2 font-semibold ${assessmentService.getScoreColor(assessment.percentage_score || 0)}`}>
                {assessment.percentage_score?.toFixed(1)}%
              </span>
            </div>
            <div className={`text-sm font-medium ${
              assessment.passed ? 'text-green-600' : 'text-red-600'
            }`}>
              {assessment.passed ? 'PASSED' : 'FAILED'}
            </div>
          </div>
          {assessment.completed_at && (
            <p className="text-xs text-gray-500 mt-1">
              Completed on {new Date(assessment.completed_at).toLocaleDateString()}
            </p>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex space-x-3">
        {canStart && !isExpired && (
          <button
            onClick={() => onStart(assessment.id)}
            className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
              assessment.status === AssessmentStatus.NOT_STARTED
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-yellow-600 text-white hover:bg-yellow-700'
            }`}
          >
            {assessment.status === AssessmentStatus.NOT_STARTED ? 'Start Assessment' : 'Continue'}
          </button>
        )}
        
        {isCompleted && (
          <button
            onClick={() => onViewResults(assessment.id)}
            className="flex-1 py-2 px-4 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors"
          >
            View Results
          </button>
        )}
        
        {isExpired && (
          <div className="flex-1 py-2 px-4 bg-gray-100 text-gray-500 rounded-lg font-medium text-center">
            Expired
          </div>
        )}
      </div>
    </div>
  );
};

const AssessmentList: React.FC = () => {
  const router = useRouter();
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<AssessmentStatus | 'all'>('all');

  useEffect(() => {
    const loadAssessments = async () => {
      try {
        setLoading(true);
        const data = await assessmentService.getAssessments();
        setAssessments(data);
      } catch (error) {
        console.error('Error loading assessments:', error);
        setError(error instanceof Error ? error.message : 'Failed to load assessments');
      } finally {
        setLoading(false);
      }
    };

    loadAssessments();
  }, []);

  const handleStartAssessment = (assessmentId: string) => {
    router.push(`/assessments/${assessmentId}/test`);
  };

  const handleViewResults = (assessmentId: string) => {
    router.push(`/assessments/${assessmentId}/results`);
  };

  const filteredAssessments = assessments.filter(assessment => 
    filter === 'all' || assessment.status === filter
  );

  const getFilterCounts = () => {
    const counts = {
      all: assessments.length,
      [AssessmentStatus.NOT_STARTED]: 0,
      [AssessmentStatus.IN_PROGRESS]: 0,
      [AssessmentStatus.COMPLETED]: 0,
      [AssessmentStatus.EXPIRED]: 0,
    };

    assessments.forEach(assessment => {
      if (assessment.status in counts) {
        counts[assessment.status as keyof typeof counts]++;
      }
    });

    return counts;
  };

  const filterCounts = getFilterCounts();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading assessments...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Assessments</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Assessments</h1>
          <p className="text-gray-600">
            Complete your assessments to showcase your skills to potential employers.
          </p>
        </div>

        {/* Filters */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-2">
            {[
              { key: 'all', label: 'All Assessments' },
              { key: AssessmentStatus.NOT_STARTED, label: 'Not Started' },
              { key: AssessmentStatus.IN_PROGRESS, label: 'In Progress' },
              { key: AssessmentStatus.COMPLETED, label: 'Completed' },
              { key: AssessmentStatus.EXPIRED, label: 'Expired' },
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setFilter(key as any)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filter === key
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                {label} ({filterCounts[key as keyof typeof filterCounts] || 0})
              </button>
            ))}
          </div>
        </div>

        {/* Assessment Grid */}
        {filteredAssessments.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center text-gray-400 font-bold text-lg mx-auto mb-4">
              TEST
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {filter === 'all' ? 'No assessments available' : `No ${filter.replace('_', ' ')} assessments`}
            </h3>
            <p className="text-gray-600">
              {filter === 'all' 
                ? 'Check back later for new assessment opportunities.'
                : 'Try selecting a different filter to see other assessments.'
              }
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAssessments.map(assessment => (
              <AssessmentCard
                key={assessment.id}
                assessment={assessment}
                onStart={handleStartAssessment}
                onViewResults={handleViewResults}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AssessmentList;