/**
 * AI Interview Service
 * Handles communication with backend AI interview analysis endpoints
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export interface ResponseAnalysis {
  overall_score: number
  metrics: {
    word_count: number
    duration: number
    words_per_minute: number
    filler_word_count: number
    filler_word_ratio: number
  }
  analysis: {
    sentiment: any
    clarity_score: number
    confidence_score: number
    structure_score: number
  }
  content: {
    technical_terms: string[]
    key_points: string[]
    filler_words: string[]
  }
  feedback: {
    strengths: string[]
    improvements: string[]
  }
}

export interface FullInterviewAnalysis {
  overall_score: number
  total_questions: number
  aggregate_metrics: {
    total_words: number
    total_duration: number
    avg_words_per_minute: number
    consistency_score: number
  }
  performance: {
    improvement_trend: string
    best_question: any
    needs_improvement: any
  }
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  question_scores: Array<{
    question_number: number
    score: number
    type: string
  }>
}

class AIInterviewService {
  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token')
    }
    return null
  }

  private async fetchWithAuth(url: string, options: RequestInit = {}) {
    const token = this.getAuthToken()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  /**
   * Analyze a single interview response
   */
  async analyzeResponse(
    transcript: string,
    question: string,
    duration: number,
    questionType: string = 'general'
  ): Promise<ResponseAnalysis> {
    try {
      const response = await this.fetchWithAuth(
        `${API_BASE_URL}/interviews/ai-video/analyze-response`,
        {
          method: 'POST',
          body: JSON.stringify({
            transcript,
            question,
            duration,
            question_type: questionType,
          }),
        }
      )

      return response.analysis
    } catch (error) {
      console.error('Error analyzing response:', error)
      throw error
    }
  }

  /**
   * Analyze complete interview
   */
  async analyzeFullInterview(
    interviewId: string,
    responses: any[]
  ): Promise<FullInterviewAnalysis> {
    try {
      const response = await this.fetchWithAuth(
        `${API_BASE_URL}/interviews/ai-video/analyze-full-interview`,
        {
          method: 'POST',
          body: JSON.stringify({
            interview_id: interviewId,
            responses,
          }),
        }
      )

      return response.analysis
    } catch (error) {
      console.error('Error analyzing full interview:', error)
      throw error
    }
  }

  /**
   * Get saved interview analysis
   */
  async getInterviewAnalysis(interviewId: string): Promise<FullInterviewAnalysis> {
    try {
      const response = await this.fetchWithAuth(
        `${API_BASE_URL}/interviews/ai-video/${interviewId}/analysis`
      )

      return response.analysis
    } catch (error) {
      console.error('Error retrieving analysis:', error)
      throw error
    }
  }


}

export const aiInterviewService = new AIInterviewService()
