'use client';

import React from 'react';
import { CheckIcon, ArrowTopRightOnSquareIcon, ClockIcon } from '@heroicons/react/24/outline';
import { Notification, NotificationPriority, NotificationCategory } from '../../types/notification';

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: string) => void;
  getCategoryIcon: (category: NotificationCategory) => React.ReactNode;
  getPriorityColor: (priority: NotificationPriority) => string;
}

export const NotificationItem: React.FC<NotificationItemProps> = ({
  notification,
  onMarkAsRead,
  getCategoryIcon,
  getPriorityColor
}) => {
  const isUnread = !notification.read_at;
  const timeAgo = getTimeAgo(new Date(notification.created_at));

  const handleClick = () => {
    if (isUnread) {
      onMarkAsRead(notification.id);
    }

    // Handle notification action based on data
    if (notification.data) {
      const data = typeof notification.data === 'string' 
        ? JSON.parse(notification.data) 
        : notification.data;

      switch (data.action) {
        case 'view_job':
          window.open(`/jobs/${data.job_id}`, '_blank');
          break;
        case 'take_assessment':
          window.open(`/assessments/${data.assessment_id}`, '_blank');
          break;
        case 'join_interview':
          window.open(`/interviews/${data.interview_id}`, '_blank');
          break;
        case 'view_application':
          window.open(`/applications/${data.application_id}`, '_blank');
          break;
        default:
          // Default action - go to dashboard
          window.open('/dashboard', '_blank');
      }
    }
  };

  return (
    <div
      className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
        isUnread ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
      }`}
      onClick={handleClick}
    >
      <div className="flex items-start space-x-3">
        {/* Category Icon */}
        <div className="flex-shrink-0 text-lg">
          {getCategoryIcon(notification.category)}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className={`text-sm font-medium ${isUnread ? 'text-gray-900' : 'text-gray-700'}`}>
                {notification.title}
              </h4>
              <p className={`text-sm mt-1 ${isUnread ? 'text-gray-700' : 'text-gray-500'}`}>
                {notification.message}
              </p>
            </div>

            {/* Priority indicator */}
            <div className={`flex-shrink-0 ml-2 ${getPriorityColor(notification.priority)}`}>
              <div className={`w-2 h-2 rounded-full ${
                notification.priority === NotificationPriority.URGENT ? 'bg-red-500' :
                notification.priority === NotificationPriority.HIGH ? 'bg-orange-500' :
                notification.priority === NotificationPriority.MEDIUM ? 'bg-yellow-500' :
                'bg-gray-400'
              }`} />
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between mt-2">
            <div className="flex items-center text-xs text-gray-500">
              <ClockIcon className="h-3 w-3 mr-1" />
              {timeAgo}
            </div>

            <div className="flex items-center space-x-2">
              {/* Action indicator */}
              {notification.data && (
                <ArrowTopRightOnSquareIcon className="h-3 w-3 text-gray-400" />
              )}

              {/* Read status */}
              {isUnread ? (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onMarkAsRead(notification.id);
                  }}
                  className="text-blue-600 hover:text-blue-800 p-1 rounded"
                  title="Mark as read"
                >
                  <CheckIcon className="h-3 w-3" />
                </button>
              ) : (
                <div className="w-2 h-2 rounded-full bg-gray-300" title="Read" />
              )}
            </div>
          </div>

          {/* Additional data display */}
          {notification.data && (
            <div className="mt-2 text-xs text-gray-500">
              {renderNotificationData(notification)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function getTimeAgo(date: Date): string {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return 'Just now';
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes}m ago`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours}h ago`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays}d ago`;
  }

  return date.toLocaleDateString();
}

function renderNotificationData(notification: Notification): React.ReactNode {
  if (!notification.data) return null;

  const data = typeof notification.data === 'string' 
    ? JSON.parse(notification.data) 
    : notification.data;

  switch (notification.category) {
    case NotificationCategory.JOB_MATCH:
      return (
        <div className="flex items-center space-x-2">
          {data.company_name && <span>at {data.company_name}</span>}
          {data.match_score && <span>• {data.match_score}% match</span>}
          {data.location && <span>• {data.location}</span>}
        </div>
      );

    case NotificationCategory.ASSESSMENT_REMINDER:
      return (
        <div className="flex items-center space-x-2">
          {data.assessment_type && <span>{data.assessment_type}</span>}
          {data.deadline && <span>• Due: {new Date(data.deadline).toLocaleDateString()}</span>}
        </div>
      );

    case NotificationCategory.INTERVIEW_SCHEDULED:
      return (
        <div className="flex items-center space-x-2">
          {data.interview_date && <span>{new Date(data.interview_date).toLocaleDateString()}</span>}
          {data.interview_time && <span>at {data.interview_time}</span>}
        </div>
      );

    case NotificationCategory.APPLICATION_UPDATE:
      return (
        <div className="flex items-center space-x-2">
          {data.company_name && <span>at {data.company_name}</span>}
          {data.status && (
            <span className={`px-2 py-1 rounded-full text-xs ${
              data.status === 'accepted' ? 'bg-green-100 text-green-800' :
              data.status === 'rejected' ? 'bg-red-100 text-red-800' :
              'bg-yellow-100 text-yellow-800'
            }`}>
              {data.status}
            </span>
          )}
        </div>
      );

    default:
      return null;
  }
}