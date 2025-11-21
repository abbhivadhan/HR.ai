export enum AssessmentType {
  TECHNICAL = 'technical',
  BEHAVIORAL = 'behavioral',
  COGNITIVE = 'cognitive',
  PERSONALITY = 'personality',
  CODING = 'coding'
}

export enum QuestionType {
  MULTIPLE_CHOICE = 'multiple_choice',
  CODING = 'coding',
  TEXT_RESPONSE = 'text_response',
  TRUE_FALSE = 'true_false',
  RATING_SCALE = 'rating_scale'
}

export enum DifficultyLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert'
}

export enum AssessmentStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  EXPIRED = 'expired',
  CANCELLED = 'cancelled'
}

export interface Question {
  id: string;
  title: string;
  content: string;
  question_type: QuestionType;
  difficulty_level: DifficultyLevel;
  category: string;
  tags?: string[];
  options?: Record<string, string>;
  correct_answer?: string;
  explanation?: string;
  code_template?: string;
  test_cases?: Array<{
    input: string;
    expected: string;
  }>;
  max_points: number;
  time_limit_seconds?: number;
  ai_generated: boolean;
  generation_prompt?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AssessmentQuestion {
  id: string;
  question_id: string;
  order_index: number;
  points: number;
  time_limit_seconds?: number;
  question: Question;
}

export interface Assessment {
  id: string;
  candidate_id: string;
  job_posting_id?: string;
  title: string;
  description?: string;
  assessment_type: AssessmentType;
  status: AssessmentStatus;
  duration_minutes: number;
  total_questions: number;
  passing_score: number;
  started_at?: string;
  completed_at?: string;
  expires_at?: string;
  total_score?: number;
  percentage_score?: number;
  passed?: boolean;
  ai_analysis?: {
    overall_score: number;
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
    confidence_level: number;
  };
  skill_scores?: Record<string, number>;
  created_at: string;
  updated_at: string;
  questions: AssessmentQuestion[];
}

export interface AssessmentResponse {
  id: string;
  assessment_id: string;
  question_id: string;
  response_text?: string;
  selected_options?: string[];
  code_solution?: string;
  started_at?: string;
  submitted_at?: string;
  time_spent_seconds?: number;
  points_earned?: number;
  is_correct?: boolean;
  ai_feedback?: string;
  ai_score_breakdown?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface AssessmentSession {
  assessment: Assessment;
  current_question_index: number;
  time_remaining_seconds: number;
  responses: AssessmentResponse[];
}

export interface StartAssessmentResponse {
  assessment_id: string;
  session_token: string;
  expires_at: string;
  first_question: Question;
}

export interface SubmitResponseRequest {
  question_id: string;
  response: {
    response_text?: string;
    selected_options?: string[];
    code_solution?: string;
  };
}

export interface NextQuestionResponse {
  question?: Question;
  question_index: number;
  total_questions: number;
  time_remaining_seconds: number;
  is_last_question: boolean;
}

export interface CompleteAssessmentResponse {
  assessment_id: string;
  total_score: number;
  percentage_score: number;
  passed: boolean;
  skill_scores: Record<string, number>;
  ai_analysis: {
    overall_score: number;
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
    confidence_level: number;
  };
}

export interface AssessmentResults {
  assessment: {
    id: string;
    title: string;
    assessment_type: string;
    total_score: number;
    percentage_score: number;
    passed: boolean;
    completed_at: string;
  };
  skill_scores: Record<string, number>;
  ai_analysis: {
    overall_score: number;
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
    confidence_level: number;
  };
  responses: Array<{
    question: {
      id: string;
      title: string;
      content: string;
      category: string;
      max_points: number;
    };
    response: {
      response_text?: string;
      selected_options?: string[];
      code_solution?: string;
      points_earned: number;
      is_correct: boolean;
      ai_feedback?: string;
    };
  }>;
}

export interface GenerateQuestionsRequest {
  job_title: string;
  required_skills: string[];
  difficulty_level: DifficultyLevel;
  question_count: number;
  question_types: QuestionType[];
}

export interface CreateAssessmentRequest {
  candidate_id: string;
  job_posting_id?: string;
  title: string;
  description?: string;
  assessment_type: AssessmentType;
  duration_minutes: number;
  passing_score: number;
  question_ids: string[];
}