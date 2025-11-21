/**
 * Resume Builder API Service
 */
import axios from 'axios';
import {
  Resume,
  AIContentSuggestion,
  ATSOptimization,
  ResumeTemplate
} from '@/types/resume';

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

export const resumeBuilderService = {
  // Resumes
  async createResume(data: {
    title: string;
    template_id: string;
    content: any;
  }): Promise<Resume> {
    const response = await api.post('/api/resume-builder/resumes', data);
    return response.data;
  },

  async getResumes(): Promise<Resume[]> {
    const response = await api.get('/api/resume-builder/resumes');
    return response.data;
  },

  async getResume(id: number): Promise<Resume> {
    const response = await api.get(`/api/resume-builder/resumes/${id}`);
    return response.data;
  },

  async updateResume(id: number, data: Partial<Resume>): Promise<Resume> {
    const response = await api.put(`/api/resume-builder/resumes/${id}`, data);
    return response.data;
  },

  async deleteResume(id: number): Promise<void> {
    await api.delete(`/api/resume-builder/resumes/${id}`);
  },

  // AI Features
  async getAISuggestions(resumeId: number, section: string): Promise<AIContentSuggestion[]> {
    const response = await api.get(`/api/resume-builder/resumes/${resumeId}/suggestions`, {
      params: { section },
    });
    return response.data;
  },

  async optimizeForATS(
    resumeId: number,
    jobId?: number,
    jobDescription?: string
  ): Promise<ATSOptimization> {
    const response = await api.post(`/api/resume-builder/resumes/${resumeId}/optimize`, {
      job_id: jobId,
      job_description: jobDescription,
    });
    return response.data;
  },

  // Export
  async exportResume(resumeId: number, format: 'pdf' | 'docx' | 'txt'): Promise<{ file_url: string }> {
    const response = await api.post(`/api/resume-builder/resumes/${resumeId}/export`, {
      format,
    });
    return response.data;
  },

  // Templates
  async getTemplates(): Promise<ResumeTemplate[]> {
    const response = await api.get('/api/resume-builder/templates');
    return response.data;
  },
};
