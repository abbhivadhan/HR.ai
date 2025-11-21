/**
 * AI-HR Platform JavaScript SDK Client
 * 
 * Main client class for interacting with the AI-HR Platform API.
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
  AIHRException,
  AuthenticationError,
  ValidationError,
  NotFoundError,
  RateLimitError,
  ServerError
} from './exceptions';
import {
  User,
  Assessment,
  Job,
  JobMatch,
  Interview,
  Webhook,
  APIUsageStats,
  ClientConfig,
  LoginResponse,
  WebhookCreateRequest,
  AssessmentStartRequest
} from './types';

/**
 * AI-HR Platform API Client
 * 
 * Provides a convenient interface for interacting with the AI-HR Platform API.
 * 
 * @example
 * ```typescript
 * import { AIHRClient } from '@aihr/platform-sdk';
 * 
 * // Initialize client
 * const client = new AIHRClient({
 *   apiKey: 'your_api_key',
 *   baseURL: 'https://api.aihr-platform.com'
 * });
 * 
 * // Authenticate user
 * const loginResponse = await client.auth.login('user@example.com', 'password');
 * 
 * // Start assessment
 * const assessment = await client.assessments.start({ assessmentType: 'technical' });
 * 
 * // Get job recommendations
 * const matches = await client.matching.getRecommendations();
 * ```
 */
export class AIHRClient {
  private httpClient: AxiosInstance;
  private accessToken?: string;

  // API endpoints
  public readonly auth: AuthAPI;
  public readonly users: UsersAPI;
  public readonly assessments: AssessmentsAPI;
  public readonly jobs: JobsAPI;
  public readonly matching: MatchingAPI;
  public readonly interviews: InterviewsAPI;
  public readonly webhooks: WebhooksAPI;
  public readonly analytics: AnalyticsAPI;

  constructor(config: ClientConfig) {
    // Initialize HTTP client
    this.httpClient = axios.create({
      baseURL: config.baseURL || 'https://api.aihr-platform.com',
      timeout: config.timeout || 30000,
      headers: {
        'User-Agent': '@aihr/platform-sdk/1.0.0',
        'Content-Type': 'application/json',
        'API-Version': config.apiVersion || '1.1',
        ...(config.apiKey && { 'X-API-Key': config.apiKey }),
        ...(config.accessToken && { 'Authorization': `Bearer ${config.accessToken}` })
      }
    });

    // Set access token if provided
    if (config.accessToken) {
      this.accessToken = config.accessToken;
    }

    // Setup response interceptor for error handling
    this.httpClient.interceptors.response.use(
      (response) => response,
      (error) => this.handleError(error)
    );

    // Initialize API endpoints
    this.auth = new AuthAPI(this);
    this.users = new UsersAPI(this);
    this.assessments = new AssessmentsAPI(this);
    this.jobs = new JobsAPI(this);
    this.matching = new MatchingAPI(this);
    this.interviews = new InterviewsAPI(this);
    this.webhooks = new WebhooksAPI(this);
    this.analytics = new AnalyticsAPI(this);
  }

  /**
   * Set access token for authentication
   */
  setAccessToken(token: string): void {
    this.accessToken = token;
    this.httpClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  /**
   * Clear access token
   */
  clearAccessToken(): void {
    this.accessToken = undefined;
    delete this.httpClient.defaults.headers.common['Authorization'];
  }

  /**
   * Make HTTP request
   */
  async request<T = any>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    data?: any,
    params?: Record<string, any>
  ): Promise<T> {
    const response: AxiosResponse<T> = await this.httpClient.request({
      method,
      url: endpoint,
      data,
      params
    });

    return response.data;
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: AxiosError): never {
    if (error.response) {
      const { status, data } = error.response;
      const message = (data as any)?.detail || `HTTP ${status}`;

      switch (status) {
        case 401:
          throw new AuthenticationError(message);
        case 403:
          throw new AuthenticationError(message);
        case 404:
          throw new NotFoundError(message);
        case 422:
          throw new ValidationError(message, (data as any)?.errors);
        case 429:
          const retryAfter = parseInt(error.response.headers['retry-after'] || '60');
          throw new RateLimitError(message, retryAfter);
        case 500:
        case 502:
        case 503:
        case 504:
          throw new ServerError(message);
        default:
          throw new AIHRException(message, status);
      }
    } else if (error.request) {
      throw new AIHRException('Network error: No response received');
    } else {
      throw new AIHRException(`Request error: ${error.message}`);
    }
  }
}

/**
 * Authentication API endpoints
 */
class AuthAPI {
  constructor(private client: AIHRClient) {}

  /**
   * Register a new user
   */
  async register(
    email: string,
    password: string,
    firstName: string,
    lastName: string,
    userType: 'candidate' | 'company' = 'candidate'
  ): Promise<User> {
    return this.client.request<User>('POST', '/api/auth/register', {
      email,
      password,
      first_name: firstName,
      last_name: lastName,
      user_type: userType
    });
  }

  /**
   * Login user and get tokens
   */
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await this.client.request<LoginResponse>('POST', '/api/auth/login', {
      email,
      password
    });

    // Set access token in client
    if (response.access_token) {
      this.client.setAccessToken(response.access_token);
    }

    return response;
  }

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<LoginResponse> {
    const response = await this.client.request<LoginResponse>('POST', '/api/auth/refresh', {
      refresh_token: refreshToken
    });

    // Update access token in client
    if (response.access_token) {
      this.client.setAccessToken(response.access_token);
    }

    return response;
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    await this.client.request('POST', '/api/auth/logout');
    this.client.clearAccessToken();
  }
}

/**
 * Assessment API endpoints
 */
class AssessmentsAPI {
  constructor(private client: AIHRClient) {}

  /**
   * Start a new assessment
   */
  async start(request: AssessmentStartRequest): Promise<Assessment> {
    return this.client.request<Assessment>('POST', '/api/assessments/start', {
      assessment_type: request.assessmentType,
      job_id: request.jobId,
      difficulty_level: request.difficultyLevel || 'intermediate'
    });
  }

  /**
   * Get assessment details
   */
  async get(assessmentId: string): Promise<Assessment> {
    return this.client.request<Assessment>('GET', `/api/assessments/${assessmentId}`);
  }

  /**
   * Submit answer to assessment question
   */
  async submitResponse(
    assessmentId: string,
    questionId: string,
    answer: string | string[] | Record<string, any>
  ): Promise<any> {
    return this.client.request('POST', `/api/assessments/${assessmentId}/submit`, {
      question_id: questionId,
      answer
    });
  }

  /**
   * Complete assessment and get results
   */
  async complete(assessmentId: string): Promise<any> {
    return this.client.request('POST', `/api/assessments/${assessmentId}/complete`);
  }
}

/**
 * Job API endpoints
 */
class JobsAPI {
  constructor(private client: AIHRClient) {}

  /**
   * Search for jobs
   */
  async search(params: {
    query?: string;
    location?: string;
    remote?: boolean;
    salaryMin?: number;
    salaryMax?: number;
    limit?: number;
    offset?: number;
  } = {}): Promise<Job[]> {
    const response = await this.client.request<{ jobs: Job[] }>('GET', '/api/jobs/search', undefined, {
      limit: 20,
      offset: 0,
      ...params
    });
    return response.jobs;
  }

  /**
   * Get job details
   */
  async get(jobId: string): Promise<Job> {
    return this.client.request<Job>('GET', `/api/jobs/${jobId}`);
  }

  /**
   * Apply for a job
   */
  async apply(jobId: string, coverLetter?: string): Promise<any> {
    return this.client.request('POST', `/api/jobs/${jobId}/apply`, {
      cover_letter: coverLetter
    });
  }
}

/**
 * Job matching API endpoints
 */
class MatchingAPI {
  constructor(private client: AIHRClient) {}

  /**
   * Get job recommendations for current user
   */
  async getRecommendations(params: {
    limit?: number;
    minScore?: number;
  } = {}): Promise<JobMatch[]> {
    const response = await this.client.request<{ recommendations: JobMatch[] }>(
      'GET',
      '/api/matching/recommendations',
      undefined,
      {
        limit: 10,
        min_score: 0.5,
        ...params
      }
    );
    return response.recommendations;
  }

  /**
   * Get match score for specific job
   */
  async getMatchScore(jobId: string): Promise<any> {
    return this.client.request('GET', `/api/matching/score/${jobId}`);
  }
}

/**
 * Interview API endpoints
 */
class InterviewsAPI {
  constructor(private client: AIHRClient) {}

  /**
   * Schedule an interview
   */
  async schedule(
    jobId: string,
    interviewType: string = 'ai_video',
    preferredTime?: Date
  ): Promise<Interview> {
    return this.client.request<Interview>('POST', '/api/interviews/schedule', {
      job_id: jobId,
      interview_type: interviewType,
      preferred_time: preferredTime?.toISOString()
    });
  }

  /**
   * Join an interview session
   */
  async join(interviewId: string): Promise<any> {
    return this.client.request('GET', `/api/interviews/${interviewId}/join`);
  }

  /**
   * Get interview results
   */
  async getResults(interviewId: string): Promise<any> {
    return this.client.request('GET', `/api/interviews/${interviewId}/results`);
  }
}

/**
 * Webhook API endpoints
 */
class WebhooksAPI {
  constructor(private client: AIHRClient) {}

  /**
   * Create a webhook endpoint
   */
  async create(request: WebhookCreateRequest): Promise<Webhook> {
    return this.client.request<Webhook>('POST', '/api/webhooks', request);
  }

  /**
   * List all webhooks
   */
  async list(): Promise<Webhook[]> {
    return this.client.request<Webhook[]>('GET', '/api/webhooks');
  }

  /**
   * Get webhook details
   */
  async get(webhookId: string): Promise<Webhook> {
    return this.client.request<Webhook>('GET', `/api/webhooks/${webhookId}`);
  }

  /**
   * Update webhook endpoint
   */
  async update(webhookId: string, updates: Partial<WebhookCreateRequest>): Promise<Webhook> {
    return this.client.request<Webhook>('PUT', `/api/webhooks/${webhookId}`, updates);
  }

  /**
   * Delete webhook endpoint
   */
  async delete(webhookId: string): Promise<void> {
    await this.client.request('DELETE', `/api/webhooks/${webhookId}`);
  }

  /**
   * Test webhook endpoint
   */
  async test(webhookId: string): Promise<any> {
    return this.client.request('POST', `/api/webhooks/${webhookId}/test`);
  }
}

/**
 * User API endpoints
 */
class UsersAPI {
  constructor(private client: AIHRClient) {}

  /**
   * Get current user profile
   */
  async getProfile(): Promise<User> {
    return this.client.request<User>('GET', '/api/users/profile');
  }

  /**
   * Update user profile
   */
  async updateProfile(updates: Partial<User>): Promise<User> {
    return this.client.request<User>('PUT', '/api/users/profile', updates);
  }
}

/**
 * Analytics API endpoints
 */
class AnalyticsAPI {
  constructor(private client: AIHRClient) {}

  /**
   * Get dashboard analytics data
   */
  async getDashboardData(): Promise<any> {
    return this.client.request('GET', '/api/analytics/dashboard');
  }

  /**
   * Get API usage statistics
   */
  async getUsageStats(): Promise<APIUsageStats> {
    return this.client.request<APIUsageStats>('GET', '/api/developer/usage-stats');
  }
}