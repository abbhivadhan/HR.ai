/**
 * Career Coach Types
 */

export interface CareerPlan {
  id: number;
  user_id: number;
  current_role?: string;
  target_role: string;
  target_salary?: number;
  timeline_months?: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface CoachConversation {
  id: number;
  career_plan_id: number;
  user_id: number;
  messages: ChatMessage[];
  topic?: string;
  created_at: string;
  updated_at: string;
}

export interface SkillGap {
  id: number;
  career_plan_id: number;
  skill_name: string;
  current_level: number;
  required_level: number;
  priority: 'high' | 'medium' | 'low';
  learning_resources: LearningResource[];
  status: string;
  created_at: string;
}

export interface LearningResource {
  title: string;
  url: string;
  type: string;
  duration?: string;
}

export interface CareerMilestone {
  id: number;
  career_plan_id: number;
  title: string;
  description?: string;
  target_date?: string;
  completed: boolean;
  completed_at?: string;
  created_at: string;
}

export interface CareerPathRecommendation {
  role: string;
  description: string;
  required_skills: string[];
  average_salary: number;
  growth_potential: string;
  timeline_months: number;
  steps: string[];
}

export interface SalaryInsight {
  role: string;
  min_salary: number;
  max_salary: number;
  median_salary: number;
  location: string;
  experience_level: string;
}

export interface ChatResponse {
  message: ChatMessage;
  suggestions: string[];
}
