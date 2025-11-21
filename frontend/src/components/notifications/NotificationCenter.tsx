'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  BellIcon, 
  XMarkIcon, 
  CheckIcon, 
  CheckCircleIcon, 
  Cog6ToothIcon, 
  FunnelIcon,
  BriefcaseIcon,
  DocumentTextIcon,
  VideoCameraIcon,
  ClipboardDocumentIcon,
  ExclamationTriangleIcon,
  LockClosedIcon,
  SpeakerWaveIcon 
} from '@heroicons/react/24/outline';
import { 
  Notification, 
  NotificationCategory, 
  NotificationPriority,
  NotificationListResponse 
} from '../../types/notification';
import { notificationService } from '../../services/notificationService';
import { NotificationItem } from './NotificationItem';
import { NotificationPreferences } from './NotificationPreferences';

interface NotificationCenterProps {
  userId?: string;
  className?: string;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({
  userId,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [filter, setFilter] = useState<{
    category?: NotificationCategory;
    unreadOnly: boolean;
  }>({ unreadOnly: false });
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Load notifications
  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response: NotificationListResponse = await notificationService.getNotifications(
        50, 0, filter.unreadOnly, filter.category
      );
      setNotifications(response.notifications);
      setUnreadCount(response.unread_count);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  // Setup WebSocket connection for real-time updates
  useEffect(() => {
    if (userId) {
      wsRef.current = notificationService.connectToNotifications(
        userId,
        (data) => {
          if (data.type === 'notification') {
            loadNotifications(); // Reload notifications when new ones arrive
          }
        }
      );

      return () => {
        if (wsRef.current) {
          wsRef.current.close();
        }
      };
    }
  }, [userId]);

  // Load notifications on mount and filter changes
  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen, filter]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await notificationService.markAsRead(notificationId);
      setNotifications(prev => 
        prev.map(n => 
          n.id === notificationId 
            ? { ...n, read_at: new Date().toISOString(), status: 'read' as any }
            : n
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead(filter.category);
      setNotifications(prev => 
        prev.map(n => ({ 
          ...n, 
          read_at: new Date().toISOString(), 
          status: 'read' as any 
        }))
      );
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  };

  const getPriorityColor = (priority: NotificationPriority) => {
    switch (priority) {
      case NotificationPriority.URGENT:
        return 'text-red-600';
      case NotificationPriority.HIGH:
        return 'text-orange-600';
      case NotificationPriority.MEDIUM:
        return 'text-yellow-600';
      case NotificationPriority.LOW:
        return 'text-gray-600';
      default:
        return 'text-gray-600';
    }
  };

  const getCategoryIcon = (category: NotificationCategory) => {
    switch (category) {
      case NotificationCategory.JOB_MATCH:
        return <BriefcaseIcon className="w-5 h-5" />;
      case NotificationCategory.ASSESSMENT_REMINDER:
        return <DocumentTextIcon className="w-5 h-5" />;
      case NotificationCategory.INTERVIEW_SCHEDULED:
        return <VideoCameraIcon className="w-5 h-5" />;
      case NotificationCategory.APPLICATION_UPDATE:
        return <ClipboardDocumentIcon className="w-5 h-5" />;
      case NotificationCategory.SYSTEM_ALERT:
        return <ExclamationTriangleIcon className="w-5 h-5" />;
      case NotificationCategory.SECURITY_ALERT:
        return <LockClosedIcon className="w-5 h-5" />;
      default:
        return <SpeakerWaveIcon className="w-5 h-5" />;
    }
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Notification Bell */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg transition-colors"
        aria-label="Notifications"
      >
        <BellIcon className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-hidden">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowPreferences(!showPreferences)}
                  className="p-1 text-gray-500 hover:text-gray-700 rounded"
                  title="Preferences"
                >
                  <Cog6ToothIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 text-gray-500 hover:text-gray-700 rounded"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Filters */}
            <div className="flex items-center justify-between mt-3">
              <div className="flex items-center space-x-2">
                <FunnelIcon className="h-4 w-4 text-gray-500" />
                <select
                  value={filter.category || ''}
                  onChange={(e) => setFilter(prev => ({ 
                    ...prev, 
                    category: e.target.value as NotificationCategory || undefined 
                  }))}
                  className="text-sm border border-gray-300 rounded px-2 py-1"
                >
                  <option value="">All Categories</option>
                  <option value={NotificationCategory.JOB_MATCH}>Job Matches</option>
                  <option value={NotificationCategory.ASSESSMENT_REMINDER}>Assessments</option>
                  <option value={NotificationCategory.INTERVIEW_SCHEDULED}>Interviews</option>
                  <option value={NotificationCategory.APPLICATION_UPDATE}>Applications</option>
                  <option value={NotificationCategory.SYSTEM_ALERT}>System</option>
                  <option value={NotificationCategory.SECURITY_ALERT}>Security</option>
                </select>
                <label className="flex items-center text-sm">
                  <input
                    type="checkbox"
                    checked={filter.unreadOnly}
                    onChange={(e) => setFilter(prev => ({ 
                      ...prev, 
                      unreadOnly: e.target.checked 
                    }))}
                    className="mr-1"
                  />
                  Unread only
                </label>
              </div>
              
              {unreadCount > 0 && (
                <button
                  onClick={handleMarkAllAsRead}
                  className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
                >
                  <CheckCircleIcon className="h-4 w-4 mr-1" />
                  Mark all read
                </button>
              )}
            </div>
          </div>

          {/* Preferences Panel */}
          {showPreferences && (
            <div className="border-b border-gray-200">
              <NotificationPreferences onClose={() => setShowPreferences(false)} />
            </div>
          )}

          {/* Notifications List */}
          <div className="max-h-64 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-500">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2">Loading notifications...</p>
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                <BellIcon className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                <p>No notifications found</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {notifications.map((notification) => (
                  <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onMarkAsRead={handleMarkAsRead}
                    getCategoryIcon={getCategoryIcon}
                    getPriorityColor={getPriorityColor}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="p-3 border-t border-gray-200 text-center">
              <button className="text-sm text-blue-600 hover:text-blue-800">
                View all notifications
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};