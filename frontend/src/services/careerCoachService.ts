/**
 * Career Coach API Service
 */
import axios from 'axios';
import {
  CareerPlan,
  CoachConversation,
  ChatResponse,
  SkillGap,
  CareerMilestone,
  CareerPathRecommendation,
  SalaryInsight
} from '@/types/career';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const careerCoachService = {
  // Career Plans
  async createCareerPlan(data: {
    current_role?: string;
    target_role: string;
    target_salary?: number;
    timeline_months?: number;
  }): Promise<CareerPlan> {
    const response = await api.post('/api/career-coach/plans', data);
    return response.data;
  },

  async getCareerPlans(): Promise<CareerPlan[]> {
    const response = await api.get('/api/career-coach/plans');
    return response.data;
  },

  async getCareerPlan(id: number): Promise<CareerPlan> {
    const response = await api.get(`/api/career-coach/plans/${id}`);
    return response.data;
  },

  // Conversations
  async createConversation(data: {
    career_plan_id: number;
    topic?: string;
    initial_message: string;
  }): Promise<CoachConversation> {
    const response = await api.post('/api/career-coach/conversations', data);
    return response.data;
  },

  async chat(conversationId: number, message: string): Promise<ChatResponse> {
    const response = await api.post('/api/career-coach/chat', {
      conversation_id: conversationId,
      message,
    });
    return response.data;
  },

  // Recommendations
  async getCareerRecommendations(planId: number): Promise<CareerPathRecommendation[]> {
    const response = await api.get(`/api/career-coach/plans/${planId}/recommendations`);
    return response.data;
  },

  async getSalaryInsights(
    role: string,
    location: string = 'United States',
    experienceLevel: string = 'mid'
  ): Promise<SalaryInsight> {
    const response = await api.get('/api/career-coach/salary-insights', {
      params: { role, location, experience_level: experienceLevel },
    });
    return response.data;
  },

  // Skill Gaps
  async getSkillGaps(planId: number): Promise<SkillGap[]> {
    const response = await api.get(`/api/career-coach/plans/${planId}/skill-gaps`);
    return response.data;
  },
};
