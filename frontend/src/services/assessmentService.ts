import { 
  Assessment, 
  Question, 
  AssessmentResponse,
  StartAssessmentResponse,
  SubmitResponseRequest,
  NextQuestionResponse,
  CompleteAssessmentResponse,
  AssessmentResults,
  GenerateQuestionsRequest,
  CreateAssessmentRequest,
  QuestionType,
  DifficultyLevel
} from '../types/assessment';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class AssessmentService {
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

  // Question management
  async getQuestions(params?: {
    category?: string;
    difficulty?: DifficultyLevel;
    question_type?: QuestionType;
    limit?: number;
  }): Promise<Question[]> {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.append('category', params.category);
    if (params?.difficulty) searchParams.append('difficulty', params.difficulty);
    if (params?.question_type) searchParams.append('question_type', params.question_type);
    if (params?.limit) searchParams.append('limit', params.limit.toString());

    const response = await fetch(
      `${API_BASE_URL}/assessments/questions?${searchParams}`,
      {
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<Question[]>(response);
  }

  async getQuestion(questionId: string): Promise<Question> {
    const response = await fetch(
      `${API_BASE_URL}/assessments/questions/${questionId}`,
      {
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<Question>(response);
  }

  async createQuestion(questionData: Partial<Question>): Promise<Question> {
    const response = await fetch(
      `${API_BASE_URL}/assessments/questions`,
      {
        method: 'POST',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(questionData)
      }
    );

    return this.handleResponse<Question>(response);
  }

  async generateQuestions(request: GenerateQuestionsRequest): Promise<Question[]> {
    const response = await fetch(
      `${API_BASE_URL}/assessments/questions/generate`,
      {
        method: 'POST',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(request)
      }
    );

    return this.handleResponse<Question[]>(response);
  }

  // Assessment management
  async getAssessments(): Promise<Assessment[]> {
    const response = await fetch(
      `${API_BASE_URL}/assessments/`,
      {
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<Assessment[]>(response);
  }

  async getAssessment(assessmentId: string): Promise<Assessment> {
    const response = await fetch(
      `${API_BASE_URL}/assessments/${assessmentId}`,
      {
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<Assessment>(response);
  }

  async createAssessment(assessmentData: CreateAssessmentRequest): Promise<Assessment> {
    const response = await fetch(
      `${API_BASE_URL}/assessments/`,
      {
        method: 'POST',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(assessmentData)
      }
    );

    return this.handleResponse<Assessment>(response);
  }

  // Assessment session management
  async startAssessment(assessmentId: string): Promise<StartAssessmentResponse> {
    const response = await fetch(
      `${API_BASE_URL}/assessments/${assessmentId}/start`,
      {
        method: 'POST',
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<StartAssessmentResponse>(response);
  }

  async submitResponse(
    assessmentId: string, 
    responseData: SubmitResponseRequest
  ): Promise<AssessmentResponse> {
    const response = await fetch(
      `${API_BASE_URL}/assessments/${assessmentId}/responses`,
      {
        method: 'POST',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(responseData)
      }
    );

    return this.handleResponse<AssessmentResponse>(response);
  }

  async saveDraftResponse(
    assessmentId: string, 
    responseData: SubmitResponseRequest
  ): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/assessments/${assessmentId}/draft-responses`,
      {
        method: 'POST',
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(responseData)
      }
    );

    if (!response.ok) {
      throw new Error('Failed to save draft response');
    }
  }

  async getNextQuestion(
    assessmentId: string, 
    currentIndex: number
  ): Promise<NextQuestionResponse> {
    const response = await fetch(
      `${API_BASE_URL}/assessments/${assessmentId}/next-question?current_index=${currentIndex}`,
      {
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<NextQuestionResponse>(response);
  }

  async completeAssessment(assessmentId: string): Promise<CompleteAssessmentResponse> {
    const response = await fetch(
      `${API_BASE_URL}/assessments/${assessmentId}/complete`,
      {
        method: 'POST',
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<CompleteAssessmentResponse>(response);
  }

  async getAssessmentResults(assessmentId: string): Promise<AssessmentResults> {
    const response = await fetch(
      `${API_BASE_URL}/assessments/${assessmentId}/results`,
      {
        headers: await this.getAuthHeaders()
      }
    );

    return this.handleResponse<AssessmentResults>(response);
  }

  // Utility methods
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

  calculateProgress(currentIndex: number, totalQuestions: number): number {
    return Math.round((currentIndex / totalQuestions) * 100);
  }

  getDifficultyColor(difficulty: DifficultyLevel): string {
    switch (difficulty) {
      case DifficultyLevel.BEGINNER:
        return 'text-green-600 bg-green-100';
      case DifficultyLevel.INTERMEDIATE:
        return 'text-yellow-600 bg-yellow-100';
      case DifficultyLevel.ADVANCED:
        return 'text-orange-600 bg-orange-100';
      case DifficultyLevel.EXPERT:
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  }

  getScoreColor(percentage: number): string {
    if (percentage >= 90) return 'text-green-600';
    if (percentage >= 80) return 'text-blue-600';
    if (percentage >= 70) return 'text-yellow-600';
    if (percentage >= 60) return 'text-orange-600';
    return 'text-red-600';
  }
}

export const assessmentService = new AssessmentService();
export default assessmentService;