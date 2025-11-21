'use client';

import { SkillGap } from '@/types/career';
import { 
  ArrowTrendingUpIcon, 
  BookOpenIcon, 
  CheckCircleIcon 
} from '@heroicons/react/24/outline';
import AnimatedCard from '@/components/ui/AnimatedCard';

interface SkillGapAnalysisProps {
  skillGaps: SkillGap[];
}

export function SkillGapAnalysis({ skillGaps }: SkillGapAnalysisProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 dark:text-green-400';
      case 'learning':
        return 'text-blue-600 dark:text-blue-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Skill Gap Analysis
        </h2>
        <div className="text-sm text-gray-600 dark:text-gray-400">
          {skillGaps.length} skills identified
        </div>
      </div>

      <div className="grid gap-4">
        {skillGaps.map((gap) => (
          <AnimatedCard key={gap.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {gap.skill_name}
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(gap.priority)}`}>
                    {gap.priority} priority
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                  <span className={getStatusColor(gap.status)}>
                    {gap.status === 'completed' && <CheckCircleIcon className="w-4 h-4 inline mr-1" />}
                    {gap.status}
                  </span>
                </div>
              </div>
            </div>

            {/* Skill Level Progress */}
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600 dark:text-gray-400">Current Level</span>
                <span className="text-gray-600 dark:text-gray-400">Required Level</span>
              </div>
              <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="absolute h-full bg-purple-600 rounded-full transition-all"
                  style={{ width: `${(gap.current_level / gap.required_level) * 100}%` }}
                />
              </div>
              <div className="flex justify-between text-xs mt-1 text-gray-500 dark:text-gray-400">
                <span>Level {gap.current_level}</span>
                <span>Level {gap.required_level}</span>
              </div>
            </div>

            {/* Learning Resources */}
            {gap.learning_resources && gap.learning_resources.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <BookOpenIcon className="w-4 h-4 text-purple-600" />
                  <h4 className="font-medium text-gray-900 dark:text-white">
                    Learning Resources
                  </h4>
                </div>
                <div className="space-y-2">
                  {gap.learning_resources.map((resource: any, index: number) => (
                    <a
                      key={index}
                      href={resource.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {resource.title}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {resource.type}
                            {resource.duration && ` • ${resource.duration}`}
                          </p>
                        </div>
                        <ArrowTrendingUpIcon className="w-5 h-5 text-purple-600" />
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            )}
          </AnimatedCard>
        ))}
      </div>

      {skillGaps.length === 0 && (
        <div className="text-center py-12">
          <CheckCircleIcon className="w-16 h-16 text-green-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            No skill gaps identified yet. Create a career plan to get started!
          </p>
        </div>
      )}
    </div>
  );
}
