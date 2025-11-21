import axios from 'axios';
import { 
  DashboardStats, 
  CandidateRecommendation, 
  CompanyAnalytics, 
  AdminMetrics,
  Notification,
  ChartData,
  TimeSeriesData,
  SkillDistribution
} from '../types/dashboard';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class DashboardService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  constructor() {
    // Add auth token to requests
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Candidate Dashboard APIs
  async getCandidateStats(candidateId: string): Promise<DashboardStats> {
    const response = await this.api.get(`/candidates/${candidateId}/stats`);
    return response.data;
  }

  async getCandidateRecommendations(candidateId: string): Promise<CandidateRecommendation[]> {
    const response = await this.api.get(`/candidates/${candidateId}/recommendations`);
    return response.data;
  }

  async getCandidateSkillScores(candidateId: string): Promise<ChartData> {
    const response = await this.api.get(`/candidates/${candidateId}/skill-scores`);
    return response.data;
  }

  async getCandidateApplicationTrends(candidateId: string): Promise<ChartData> {
    const response = await this.api.get(`/candidates/${candidateId}/application-trends`);
    return response.data;
  }

  // Company Dashboard APIs
  async getCompanyAnalytics(companyId: string): Promise<CompanyAnalytics> {
    const response = await this.api.get(`/companies/${companyId}/analytics`);
    return response.data;
  }

  async getCompanyJobPostings(companyId: string) {
    const response = await this.api.get(`/companies/${companyId}/job-postings`);
    return response.data;
  }

  async getCompanyApplications(companyId: string) {
    const response = await this.api.get(`/companies/${companyId}/applications`);
    return response.data;
  }

  async getHiringFunnelData(companyId: string): Promise<ChartData> {
    const response = await this.api.get(`/companies/${companyId}/hiring-funnel`);
    return response.data;
  }

  async getApplicationTrendsData(companyId: string): Promise<ChartData> {
    const response = await this.api.get(`/companies/${companyId}/application-trends`);
    return response.data;
  }

  async getSkillsInDemandData(companyId: string): Promise<ChartData> {
    const response = await this.api.get(`/companies/${companyId}/skills-demand`);
    return response.data;
  }

  // Admin Dashboard APIs
  async getAdminMetrics(): Promise<AdminMetrics> {
    const response = await this.api.get('/admin/metrics');
    return response.data;
  }

  async getSystemAlerts() {
    const response = await this.api.get('/admin/system/alerts');
    return response.data;
  }

  async getRecentActivity() {
    const response = await this.api.get('/admin/activity/recent');
    return response.data;
  }

  async getUserGrowthData(): Promise<ChartData> {
    const response = await this.api.get('/admin/analytics/user-growth');
    return response.data;
  }

  async getRevenueData(): Promise<ChartData> {
    const response = await this.api.get('/admin/analytics/revenue');
    return response.data;
  }

  async getPlatformUsageData(): Promise<ChartData> {
    const response = await this.api.get('/admin/analytics/platform-usage');
    return response.data;
  }

  async getUserTypeDistribution(): Promise<ChartData> {
    const response = await this.api.get('/admin/analytics/user-distribution');
    return response.data;
  }

  // Notifications APIs
  async getNotifications(userId: string): Promise<Notification[]> {
    const response = await this.api.get(`/users/${userId}/notifications`);
    return response.data;
  }

  async markNotificationAsRead(notificationId: string): Promise<void> {
    await this.api.patch(`/notifications/${notificationId}/read`);
  }

  async markAllNotificationsAsRead(userId: string): Promise<void> {
    await this.api.patch(`/users/${userId}/notifications/read-all`);
  }

  async dismissNotification(notificationId: string): Promise<void> {
    await this.api.delete(`/notifications/${notificationId}`);
  }

  // Real-time updates
  async subscribeToNotifications(userId: string, callback: (notification: Notification) => void) {
    // WebSocket connection for real-time notifications
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
    const ws = new WebSocket(`${wsUrl}/notifications/${userId}`);
    
    ws.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      callback(notification);
    };

    return ws;
  }

  // Analytics and Reporting
  async exportDashboardData(type: 'candidate' | 'company' | 'admin', id: string, format: 'csv' | 'pdf') {
    const response = await this.api.get(`/analytics/export/${type}/${id}`, {
      params: { format },
      responseType: 'blob'
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `dashboard-${type}-${id}.${format}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }

  // Utility methods
  async refreshDashboardData(type: 'candidate' | 'company' | 'admin', id: string) {
    await this.api.post(`/analytics/refresh/${type}/${id}`);
  }

  async getDashboardConfig(userId: string) {
    const response = await this.api.get(`/users/${userId}/dashboard-config`);
    return response.data;
  }

  async updateDashboardConfig(userId: string, config: any) {
    const response = await this.api.put(`/users/${userId}/dashboard-config`, config);
    return response.data;
  }
}

export default new DashboardService();