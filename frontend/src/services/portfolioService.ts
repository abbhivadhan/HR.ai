/**
 * Portfolio API Service
 */
import axios from 'axios';
import {
  Portfolio,
  PortfolioProject,
  Achievement,
  VideoUploadResponse
} from '@/types/portfolio';

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

export const portfolioService = {
  // Portfolio
  async getMyPortfolio(): Promise<Portfolio> {
    const response = await api.get('/api/portfolio/me');
    return response.data;
  },

  async updatePortfolio(data: Partial<Portfolio>): Promise<Portfolio> {
    const response = await api.put('/api/portfolio/me', data);
    return response.data;
  },

  async getUserPortfolio(userId: number): Promise<Portfolio> {
    const response = await api.get(`/api/portfolio/${userId}`);
    return response.data;
  },

  // Video Upload
  async getVideoUploadUrl(
    fileName: string,
    fileSize: number,
    contentType: string = 'video/mp4'
  ): Promise<VideoUploadResponse> {
    const response = await api.post('/api/portfolio/video-upload', {
      file_name: fileName,
      file_size: fileSize,
      content_type: contentType,
    });
    return response.data;
  },

  async uploadVideo(file: File): Promise<string> {
    // Get presigned URL
    const uploadData = await this.getVideoUploadUrl(
      file.name,
      file.size,
      file.type
    );

    // Upload to S3
    await axios.put(uploadData.upload_url, file, {
      headers: {
        'Content-Type': file.type,
      },
    });

    return uploadData.video_url;
  },

  // Projects
  async getProjects(): Promise<PortfolioProject[]> {
    const response = await api.get('/api/portfolio/projects');
    return response.data;
  },

  async addProject(data: Omit<PortfolioProject, 'id' | 'portfolio_id' | 'created_at'>): Promise<PortfolioProject> {
    const response = await api.post('/api/portfolio/projects', data);
    return response.data;
  },

  async updateProject(id: number, data: Partial<PortfolioProject>): Promise<PortfolioProject> {
    const response = await api.put(`/api/portfolio/projects/${id}`, data);
    return response.data;
  },

  async deleteProject(id: number): Promise<void> {
    await api.delete(`/api/portfolio/projects/${id}`);
  },

  // Achievements
  async getAchievements(): Promise<Achievement[]> {
    const response = await api.get('/api/portfolio/achievements');
    return response.data;
  },

  async addAchievement(data: Omit<Achievement, 'id' | 'portfolio_id' | 'created_at'>): Promise<Achievement> {
    const response = await api.post('/api/portfolio/achievements', data);
    return response.data;
  },
};
