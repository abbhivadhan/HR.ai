import {
  Interview,
  InterviewSession,
  InterviewQuestion,
  InterviewAnalysis,
  CreateInterviewRequest,
  UpdateInterviewRequest,
  SessionJoinResponse,
  QuestionGenerationRequest,
  FollowUpRequest,
  QuestionResponseRequest,
  InterviewType,
  InterviewStatus
} from '../types/interview';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class InterviewService {
  private async getAuthHeaders(): Promise<HeadersInit> {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
  }

  // Interview management
  async createInterview(interviewData: CreateInterviewRequest): Promise<Interview> {
    const response = await fetch(`${API_BASE_URL}/interviews/`, {
      method: 'POST',
      headers: await this.getAuthHeaders(),
      body: JSON.stringify(interviewData)
    });

    return this.handleResponse<Interview>(response);
  }

  async getInterviews(params?: {
    status_filter?: InterviewStatus;
    interview_type?: InterviewType;
    candidate_id?: string;
    company_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<Interview[]> {
    const searchParams = new URLSearchParams();
    if (params?.status_filter) searchParams.append('status_filter', params.status_filter);
    if (params?.interview_type) searchParams.append('interview_type', params.interview_type);
    if (params?.candidate_id) searchParams.append('candidate_id', params.candidate_id);
    if (params?.company_id) searchParams.append('company_id', params.company_id);
    if (params?.skip) searchParams.append('skip', params.skip.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());

    const response = await fetch(
      `${API_BASE_URL}/interviews/?${searchParams}`,
      {
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<Interview[]>(response);
  }

  async getInterview(interviewId: string): Promise<Interview> {
    const response = await fetch(
      `${API_BASE_URL}/interviews/${interviewId}`,
      {
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<Interview>(response);
  }

  async updateInterview(interviewId: string, updateData: UpdateInterviewRequest): Promise<Interview> {
    const response = await fetch(
      `${API_BASE_URL}/interviews/${interviewId}`,
      {
        method: 'PUT',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(updateData)
      }
    );

    return this.handleResponse<Interview>(response);
  }

  async cancelInterview(interviewId: string): Promise<{ message: string }> {
    const response = await fetch(
      `${API_BASE_URL}/interviews/${interviewId}`,
      {
        method: 'DELETE',
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<{ message: string }>(response);
  }

  // Session management
  async createSession(interviewId: string): Promise<InterviewSession> {
    const response = await fetch(
      `${API_BASE_URL}/interviews/${interviewId}/session`,
      {
        method: 'POST',
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<InterviewSession>(response);
  }

  async getSessions(interviewId: string): Promise<InterviewSession[]> {
    const response = await fetch(
      `${API_BASE_URL}/interviews/${interviewId}/sessions`,
      {
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<InterviewSession[]>(response);
  }

  async joinSession(sessionToken: string): Promise<SessionJoinResponse> {
    const response = await fetch(
      `${API_BASE_URL}/interviews/session/${sessionToken}/join`,
      {
        method: 'POST',
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<SessionJoinResponse>(response);
  }

  // Question management
  async generateQuestions(
    interviewId: string, 
    request: QuestionGenerationRequest = {}
  ): Promise<InterviewQuestion[]> {
    const response = await fetch(
      `${API_BASE_URL}/interviews/${interviewId}/questions/generate`,
      {
        method: 'POST',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(request)
      }
    );

    return this.handleResponse<InterviewQuestion[]>(response);
  }

  async getQuestions(interviewId: string, includeResponses: boolean = false): Promise<InterviewQuestion[]> {
    const response = await fetch(
      `${API_BASE_URL}/interviews/${interviewId}/questions?include_responses=${includeResponses}`,
      {
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<InterviewQuestion[]>(response);
  }

  async generateFollowUpQuestion(
    interviewId: string, 
    request: FollowUpRequest
  ): Promise<InterviewQuestion> {
    const response = await fetch(
      `${API_BASE_URL}/interviews/${interviewId}/questions/follow-up`,
      {
        method: 'POST',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(request)
      }
    );

    return this.handleResponse<InterviewQuestion>(response);
  }

  async submitQuestionResponse(
    questionId: string, 
    responseData: QuestionResponseRequest
  ): Promise<{ message: string }> {
    const response = await fetch(
      `${API_BASE_URL}/interviews/questions/${questionId}/response`,
      {
        method: 'PUT',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(responseData)
      }
    );

    return this.handleResponse<{ message: string }>(response);
  }

  // Utility methods
  formatDuration(minutes: number): string {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  }

  formatTimeRemaining(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    } else {
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
  }

  getStatusColor(status: InterviewStatus): string {
    switch (status) {
      case InterviewStatus.SCHEDULED:
        return 'text-blue-600 bg-blue-100';
      case InterviewStatus.IN_PROGRESS:
        return 'text-green-600 bg-green-100';
      case InterviewStatus.COMPLETED:
        return 'text-gray-600 bg-gray-100';
      case InterviewStatus.CANCELLED:
        return 'text-red-600 bg-red-100';
      case InterviewStatus.NO_SHOW:
        return 'text-orange-600 bg-orange-100';
      case InterviewStatus.TECHNICAL_ISSUES:
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  }

  getTypeLabel(type: InterviewType): string {
    switch (type) {
      case InterviewType.AI_SCREENING:
        return 'AI Screening';
      case InterviewType.AI_TECHNICAL:
        return 'AI Technical';
      case InterviewType.AI_BEHAVIORAL:
        return 'AI Behavioral';
      case InterviewType.HUMAN_FINAL:
        return 'Final Interview';
      default:
        return type;
    }
  }

  isInterviewStartable(interview: Interview): boolean {
    const now = new Date();
    const scheduledTime = new Date(interview.scheduled_at);
    const timeDiff = scheduledTime.getTime() - now.getTime();
    
    // Allow starting 15 minutes before scheduled time
    return timeDiff <= 15 * 60 * 1000 && interview.status === InterviewStatus.SCHEDULED;
  }

  calculateProgress(currentQuestionIndex: number, totalQuestions: number): number {
    if (totalQuestions === 0) return 0;
    return Math.round(((currentQuestionIndex + 1) / totalQuestions) * 100);
  }

  getConnectionQualityLabel(quality?: number): string {
    if (!quality) return 'Unknown';
    if (quality >= 0.8) return 'Excellent';
    if (quality >= 0.6) return 'Good';
    if (quality >= 0.4) return 'Fair';
    return 'Poor';
  }

  getConnectionQualityColor(quality?: number): string {
    if (!quality) return 'text-gray-500';
    if (quality >= 0.8) return 'text-green-500';
    if (quality >= 0.6) return 'text-blue-500';
    if (quality >= 0.4) return 'text-yellow-500';
    return 'text-red-500';
  }
}

export const interviewService = new InterviewService();
export default interviewService;