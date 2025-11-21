'use client';

import React, { useState, useEffect } from 'react';
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { 
  NotificationPreference, 
  NotificationCategory 
} from '../../types/notification';
import { notificationService } from '../../services/notificationService';

interface NotificationPreferencesProps {
  onClose: () => void;
}

export const NotificationPreferences: React.FC<NotificationPreferencesProps> = ({
  onClose
}) => {
  const [preferences, setPreferences] = useState<Record<NotificationCategory, NotificationPreference>>({} as any);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Load preferences on mount
  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      const response = await notificationService.getPreferences();
      
      // Convert array to object keyed by category
      const prefsMap: Record<NotificationCategory, NotificationPreference> = {} as any;
      
      // Initialize with default preferences for all categories
      Object.values(NotificationCategory).forEach(category => {
        prefsMap[category] = {
          id: '',
          user_id: '',
          category,
          email_enabled: true,
          sms_enabled: false,
          push_enabled: true,
          in_app_enabled: true,
          immediate: true,
          daily_digest: false,
          weekly_digest: false,
          created_at: '',
        };
      });

      // Override with actual preferences
      response.preferences.forEach(pref => {
        prefsMap[pref.category] = pref;
      });

      setPreferences(prefsMap);
    } catch (error) {
      console.error('Failed to load preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const updatePreference = (
    category: NotificationCategory,
    field: keyof NotificationPreference,
    value: boolean
  ) => {
    setPreferences(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [field]: value
      }
    }));
  };

  const savePreferences = async () => {
    try {
      setSaving(true);
      
      // Save each category's preferences
      const savePromises = Object.entries(preferences).map(([category, pref]) =>
        notificationService.updatePreference(category as NotificationCategory, pref)
      );

      await Promise.all(savePromises);
      onClose();
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setSaving(false);
    }
  };

  const getCategoryLabel = (category: NotificationCategory): string => {
    switch (category) {
      case NotificationCategory.JOB_MATCH:
        return 'Job Matches';
      case NotificationCategory.ASSESSMENT_REMINDER:
        return 'Assessment Reminders';
      case NotificationCategory.INTERVIEW_SCHEDULED:
        return 'Interview Scheduling';
      case NotificationCategory.APPLICATION_UPDATE:
        return 'Application Updates';
      case NotificationCategory.SYSTEM_ALERT:
        return 'System Alerts';
      case NotificationCategory.SECURITY_ALERT:
        return 'Security Alerts';
      default:
        return category;
    }
  };

  if (loading) {
    return (
      <div className="p-4 text-center">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-2 text-sm text-gray-500">Loading preferences...</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-semibold text-gray-900">Notification Preferences</h4>
        <button
          onClick={onClose}
          className="p-1 text-gray-500 hover:text-gray-700 rounded"
        >
          <XMarkIcon className="h-4 w-4" />
        </button>
      </div>

      <div className="space-y-6">
        {Object.entries(preferences).map(([category, pref]) => (
          <div key={category} className="border-b border-gray-200 pb-4 last:border-b-0">
            <h5 className="font-medium text-gray-900 mb-3">
              {getCategoryLabel(category as NotificationCategory)}
            </h5>

            {/* Delivery Methods */}
            <div className="grid grid-cols-2 gap-4 mb-3">
              <div className="space-y-2">
                <h6 className="text-sm font-medium text-gray-700">Delivery Methods</h6>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={pref.email_enabled}
                    onChange={(e) => updatePreference(
                      category as NotificationCategory,
                      'email_enabled',
                      e.target.checked
                    )}
                    className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">Email</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={pref.sms_enabled}
                    onChange={(e) => updatePreference(
                      category as NotificationCategory,
                      'sms_enabled',
                      e.target.checked
                    )}
                    className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">SMS</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={pref.push_enabled}
                    onChange={(e) => updatePreference(
                      category as NotificationCategory,
                      'push_enabled',
                      e.target.checked
                    )}
                    className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">Push</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={pref.in_app_enabled}
                    onChange={(e) => updatePreference(
                      category as NotificationCategory,
                      'in_app_enabled',
                      e.target.checked
                    )}
                    className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">In-App</span>
                </label>
              </div>

              {/* Frequency */}
              <div className="space-y-2">
                <h6 className="text-sm font-medium text-gray-700">Frequency</h6>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={pref.immediate}
                    onChange={(e) => updatePreference(
                      category as NotificationCategory,
                      'immediate',
                      e.target.checked
                    )}
                    className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">Immediate</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={pref.daily_digest}
                    onChange={(e) => updatePreference(
                      category as NotificationCategory,
                      'daily_digest',
                      e.target.checked
                    )}
                    className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">Daily Digest</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={pref.weekly_digest}
                    onChange={(e) => updatePreference(
                      category as NotificationCategory,
                      'weekly_digest',
                      e.target.checked
                    )}
                    className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">Weekly Digest</span>
                </label>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Save Button */}
      <div className="flex justify-end mt-6 pt-4 border-t border-gray-200">
        <button
          onClick={savePreferences}
          disabled={saving}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          ) : (
            <CheckIcon className="h-4 w-4 mr-2" />
          )}
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  );
};