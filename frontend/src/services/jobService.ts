import axios from 'axios'
import { JobPosting, JobApplication, JobSearchFilters, JobSearchResponse, CandidateProfile } from '@/types/job'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const jobService = {
  // Job Posting Management
  async createJob(jobData: Partial<JobPosting>): Promise<JobPosting> {
    const response = await api.post('/jobs/create', jobData)
    return response.data
  },

  async updateJob(jobId: string, jobData: Partial<JobPosting>): Promise<JobPosting> {
    const response = await api.put(`/jobs/${jobId}`, jobData)
    return response.data
  },

  async getJob(jobId: string): Promise<JobPosting> {
    const response = await api.get(`/jobs/${jobId}`)
    return response.data
  },

  async deleteJob(jobId: string): Promise<void> {
    await api.delete(`/jobs/${jobId}`)
  },

  async getCompanyJobs(companyId?: string): Promise<JobPosting[]> {
    const response = await api.get('/jobs/company', {
      params: companyId ? { company_id: companyId } : {}
    })
    return response.data
  },

  // Job Search
  async searchJobs(filters: JobSearchFilters, page = 1, perPage = 20): Promise<JobSearchResponse> {
    const response = await api.get('/jobs/search', {
      params: {
        ...filters,
        page,
        per_page: perPage,
      }
    })
    return response.data
  },

  async getFeaturedJobs(): Promise<JobPosting[]> {
    const response = await api.get('/jobs/featured')
    return response.data
  },

  async getRecommendedJobs(): Promise<JobPosting[]> {
    const response = await api.get('/jobs/recommended')
    return response.data
  },

  // Job Applications
  async applyToJob(jobId: string, applicationData: {
    cover_letter?: string
    resume_url?: string
    screening_questions?: Record<string, any>
  }): Promise<JobApplication> {
    const response = await api.post(`/jobs/${jobId}/apply`, applicationData)
    return response.data
  },

  async getJobApplications(jobId: string): Promise<JobApplication[]> {
    const response = await api.get(`/jobs/${jobId}/applications`)
    return response.data
  },

  async getCandidateApplications(): Promise<JobApplication[]> {
    const response = await api.get('/applications/candidate')
    return response.data
  },

  async updateApplicationStatus(applicationId: string, status: string, notes?: string): Promise<JobApplication> {
    const response = await api.put(`/applications/${applicationId}/status`, {
      status,
      recruiter_notes: notes
    })
    return response.data
  },

  async getApplication(applicationId: string): Promise<JobApplication> {
    const response = await api.get(`/applications/${applicationId}`)
    return response.data
  },

  // Candidate Profiles
  async getCandidateProfile(candidateId: string): Promise<CandidateProfile> {
    const response = await api.get(`/candidates/${candidateId}`)
    return response.data
  },

  async searchCandidates(filters: {
    skills?: string[]
    experience_level?: string
    location?: string
    availability?: string
  }): Promise<CandidateProfile[]> {
    const response = await api.get('/candidates/search', { params: filters })
    return response.data
  },

  // Saved Jobs
  async saveJob(jobId: string, notes?: string): Promise<void> {
    await api.post(`/jobs/${jobId}/save`, { notes })
  },

  async unsaveJob(jobId: string): Promise<void> {
    await api.delete(`/jobs/${jobId}/save`)
  },

  async getSavedJobs(): Promise<JobPosting[]> {
    const response = await api.get('/jobs/saved')
    return response.data
  },

  // Analytics
  async getJobAnalytics(jobId: string): Promise<{
    views: number
    applications: number
    conversion_rate: number
    top_sources: Array<{ source: string; count: number }>
  }> {
    const response = await api.get(`/jobs/${jobId}/analytics`)
    return response.data
  }
}