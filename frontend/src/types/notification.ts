export interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  category: NotificationCategory;
  priority: NotificationPriority;
  status: NotificationStatus;
  title: string;
  message: string;
  data?: Record<string, any>;
  sent_at?: string;
  delivered_at?: string;
  read_at?: string;
  failed_at?: string;
  failure_reason?: string;
  created_at: string;
  updated_at?: string;
  expires_at?: string;
}

export enum NotificationType {
  EMAIL = 'email',
  SMS = 'sms',
  PUSH = 'push',
  IN_APP = 'in_app'
}

export enum NotificationCategory {
  JOB_MATCH = 'job_match',
  ASSESSMENT_REMINDER = 'assessment_reminder',
  INTERVIEW_SCHEDULED = 'interview_scheduled',
  APPLICATION_UPDATE = 'application_update',
  SYSTEM_ALERT = 'system_alert',
  SECURITY_ALERT = 'security_alert'
}

export enum NotificationPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent'
}

export enum NotificationStatus {
  PENDING = 'pending',
  SENT = 'sent',
  DELIVERED = 'delivered',
  FAILED = 'failed',
  READ = 'read'
}

export interface NotificationPreference {
  id: string;
  user_id: string;
  category: NotificationCategory;
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  in_app_enabled: boolean;
  immediate: boolean;
  daily_digest: boolean;
  weekly_digest: boolean;
  created_at: string;
  updated_at?: string;
}

export interface NotificationStats {
  total_sent: number;
  total_delivered: number;
  total_failed: number;
  total_read: number;
  delivery_rate: number;
  read_rate: number;
}

export interface NotificationListResponse {
  notifications: Notification[];
  total: number;
  unread_count: number;
}

export interface SendNotificationRequest {
  template_name?: string;
  title?: string;
  message?: string;
  category: NotificationCategory;
  type: NotificationType;
  priority?: NotificationPriority;
  user_ids: string[];
  template_variables?: Record<string, any>;
  expires_at?: string;
}