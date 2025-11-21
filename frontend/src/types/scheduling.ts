/**
 * Smart Scheduling Types
 */

export interface SchedulingPreference {
  id: number;
  user_id: number;
  timezone: string;
  buffer_minutes: number;
  working_hours: WorkingHours;
  calendar_integrations: CalendarIntegration[];
  auto_accept: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkingHours {
  [day: string]: {
    start: string;
    end: string;
  };
}

export interface CalendarIntegration {
  provider: string;
  token: string;
  calendar_id: string;
  refresh_token?: string;
}

export interface ScheduledEvent {
  id: number;
  interview_id?: number;
  organizer_id: number;
  participant_id: number;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  timezone: string;
  meeting_url?: string;
  status: string;
  reminder_sent: boolean;
  created_at: string;
  updated_at: string;
}

export interface TimeSlotSuggestion {
  start_time: string;
  end_time: string;
  score: number;
  reason: string;
}

export interface AvailabilityResponse {
  suggested_slots: TimeSlotSuggestion[];
  conflicts: any[];
}
