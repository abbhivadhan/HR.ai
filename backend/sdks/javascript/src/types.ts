/**
 * AI-HR Platform SDK Types
 * 
 * TypeScript type definitions for the AI-HR Platform API.
 */

export interface ClientConfig {
  apiKey?: string;
  accessToken?: string;
  baseURL?: string;
  apiVersion?: string;
  timeout?: number;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type: 'candidate' | 'company' | 'admin';
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
  avatar_url?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  refresh_token_expires_in?: number;
}

export interface Assessment {
  id: string;
  assessment_type: string;
  status: string;
  score?: number;
  time_limit_minutes?: number;
  total_questions?: number;
  completed_questions?: number;
  started_at?: string;
  completed_at?: string;
  session_token?: string;
}

export interface AssessmentStartRequest {
  assessmentType: string;
  jobId?: string;
  difficultyLevel?: 'beginner' | 'intermediate' | 'advanced';
}

export interface Job {
  id: string;
  title: string;
  company_name: string;
  description: string;
  location?: string;
  remote_allowed: boolean;
  salary_min?: number;
  salary_max?: number;
  currency: string;
  status: 'active' | 'inactive' | 'filled' | 'expired';
  posted_at?: string;
  expires_at?: string;
  required_skills?: string[];
}

export interface JobMatch {
  job_id: string;
  job_title: string;
  company_name: string;
  match_score: number;
  match_reasons: string[];
  location?: string;
  salary_range?: {
    min: number;
    max: number;
    currency: string;
  };
}

export interface Interview {
  id: string;
  job_id: string;
  interview_type: string;
  status: string;
  scheduled_at?: string;
  started_at?: string;
  completed_at?: string;
  join_url?: string;
}

export interface Webhook {
  id: string;
  url: string;
  events: string[];
  is_active: boolean;
  status: string;
  created_at: string;
  description?: string;
  last_delivery_at?: string;
  success_rate: number;
  total_deliveries: number;
  failed_deliveries: number;
}

export interface WebhookCreateRequest {
  url: string;
  events: string[];
  secret?: string;
  description?: string;
  is_active?: boolean;
}

export interface WebhookEvent {
  id: string;
  event_type: string;
  timestamp: string;
  data: Record<string, any>;
  user_id?: string;
}

export interface APIUsageStats {
  total_requests: number;
  requests_by_endpoint: Record<string, number>;
  requests_by_method: Record<string, number>;
  average_response_time: number;
  error_rate: number;
  rate_limit_hits: number;
  last_24h_requests: number;
}

export interface Question {
  id: string;
  question_text: string;
  question_type: string;
  options?: string[];
  correct_answer?: string;
  points: number;
  time_limit_seconds?: number;
}

export interface SandboxRequest {
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  query_params?: Record<string, string>;
  body?: Record<string, any>;
  api_version?: string;
}

export interface SandboxResponse {
  status_code: number;
  headers: Record<string, string>;
  body: Record<string, any>;
  execution_time_ms: number;
  api_version: string;
  request_id: string;
}

export interface RateLimitInfo {
  current_limits: {
    requests_per_hour: number;
    requests_per_minute: number;
    concurrent_requests: number;
  };
  current_usage: {
    requests_this_hour: number;
    requests_this_minute: number;
    concurrent_requests: number;
  };
  reset_times: {
    hourly_reset: string;
    minute_reset: string;
  };
  upgrade_options?: Record<string, any>;
}

export interface WebhookDelivery {
  id: string;
  webhook_id: string;
  event_type: string;
  payload: Record<string, any>;
  status_code?: number;
  response_body?: string;
  delivery_time_ms?: number;
  attempts: number;
  max_attempts: number;
  next_retry_at?: string;
  delivered_at?: string;
  created_at: string;
}

// Event type constants
export const WebhookEventTypes = {
  USER_REGISTERED: 'user.registered',
  USER_VERIFIED: 'user.verified',
  ASSESSMENT_STARTED: 'assessment.started',
  ASSESSMENT_COMPLETED: 'assessment.completed',
  INTERVIEW_SCHEDULED: 'interview.scheduled',
  INTERVIEW_COMPLETED: 'interview.completed',
  JOB_POSTED: 'job.posted',
  JOB_APPLICATION: 'job.application',
  MATCH_FOUND: 'match.found',
  NOTIFICATION_SENT: 'notification.sent'
} as const;

export type WebhookEventType = typeof WebhookEventTypes[keyof typeof WebhookEventTypes];