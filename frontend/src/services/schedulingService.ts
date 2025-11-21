/**
 * Smart Scheduling API Service
 */
import axios from 'axios';
import {
  SchedulingPreference,
  ScheduledEvent,
  AvailabilityResponse,
  TimeSlotSuggestion
} from '@/types/scheduling';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const schedulingService = {
  // Preferences
  async getPreferences(): Promise<SchedulingPreference> {
    const response = await api.get('/api/scheduling/preferences');
    return response.data;
  },

  async updatePreferences(data: Partial<SchedulingPreference>): Promise<SchedulingPreference> {
    const response = await api.put('/api/scheduling/preferences', data);
    return response.data;
  },

  // Find Times
  async findOptimalTimes(data: {
    participant_ids: number[];
    duration_minutes: number;
    preferred_dates: string[];
    timezone?: string;
  }): Promise<AvailabilityResponse> {
    const response = await api.post('/api/scheduling/find-times', data);
    return response.data;
  },

  // Events
  async createEvent(data: {
    participant_id: number;
    title: string;
    start_time: string;
    end_time: string;
    description?: string;
    timezone?: string;
    meeting_url?: string;
    interview_id?: number;
  }): Promise<ScheduledEvent> {
    const response = await api.post('/api/scheduling/events', data);
    return response.data;
  },

  async getEvents(): Promise<ScheduledEvent[]> {
    const response = await api.get('/api/scheduling/events');
    return response.data;
  },

  async getEvent(id: number): Promise<ScheduledEvent> {
    const response = await api.get(`/api/scheduling/events/${id}`);
    return response.data;
  },

  async updateEvent(id: number, data: Partial<ScheduledEvent>): Promise<ScheduledEvent> {
    const response = await api.put(`/api/scheduling/events/${id}`, data);
    return response.data;
  },

  async cancelEvent(id: number): Promise<void> {
    await api.delete(`/api/scheduling/events/${id}`);
  },
};
