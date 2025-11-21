export enum InterviewType {
  AI_SCREENING = 'ai_screening',
  AI_TECHNICAL = 'ai_technical',
  AI_BEHAVIORAL = 'ai_behavioral',
  HUMAN_FINAL = 'human_final'
}

export enum InterviewStatus {
  SCHEDULED = 'scheduled',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  NO_SHOW = 'no_show',
  TECHNICAL_ISSUES = 'technical_issues'
}

export enum SessionStatus {
  WAITING = 'waiting',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECORDING = 'recording',
  PAUSED = 'paused',
  ENDED = 'ended',
  ERROR = 'error'
}

export enum QuestionCategory {
  TECHNICAL = 'technical',
  BEHAVIORAL = 'behavioral',
  SITUATIONAL = 'situational',
  COMPANY_CULTURE = 'company_culture',
  PROBLEM_SOLVING = 'problem_solving'
}

export interface Interview {
  id: string;
  job_application_id: string;
  candidate_id: string;
  company_id: string;
  interview_type: InterviewType;
  title: string;
  description?: string;
  scheduled_at: string;
  duration_minutes: number;
  timezone: string;
  status: InterviewStatus;
  started_at?: string;
  completed_at?: string;
  ai_interviewer_persona?: string;
  difficulty_level: string;
  focus_areas: string[];
  max_questions: number;
  allow_retakes: boolean;
  recording_enabled: boolean;
  overall_score?: number;
  recommendation?: string;
  created_at: string;
  updated_at: string;
}

export interface InterviewSession {
  id: string;
  interview_id: string;
  session_token: string;
  room_id: string;
  status: SessionStatus;
  joined_at?: string;
  started_at?: string;
  ended_at?: string;
  connection_quality?: number;
  audio_quality?: number;
  video_quality?: number;
  latency_ms?: number;
  recording_url?: string;
  recording_duration?: number;
  error_count: number;
  reconnection_attempts: number;
  created_at: string;
}

export interface InterviewQuestion {
  id: string;
  interview_id: string;
  question_text: string;
  category: QuestionCategory;
  difficulty_level: string;
  expected_duration: number;
  question_order: number;
  is_follow_up: boolean;
  parent_question_id?: string;
  skill_focus: string[];
  context_data: Record<string, any>;
  asked_at?: string;
  answered_at?: string;
  candidate_response?: string;
  response_score?: number;
  created_at: string;
}

export interface InterviewAnalysis {
  id: string;
  interview_id: string;
  overall_score: number;
  technical_score?: number;
  communication_score: number;
  confidence_score: number;
  skill_scores?: Record<string, number>;
  personality_traits?: Record<string, number>;
  behavioral_indicators?: Record<string, number>;
  speech_pace?: number;
  filler_word_count: number;
  clarity_score?: number;
  vocabulary_complexity?: number;
  emotion_timeline?: Record<string, any>;
  engagement_score?: number;
  eye_contact_percentage?: number;
  gesture_analysis?: Record<string, any>;
  questions_answered: number;
  average_response_time?: number;
  question_scores?: Record<string, any>;
  strengths: string[];
  areas_for_improvement: string[];
  recommendations?: string;
  red_flags: string[];
  analysis_confidence: number;
  data_quality_score?: number;
  processed_at: string;
  processing_duration?: number;
  ai_model_version?: string;
  created_at: string;
  updated_at: string;
}

// Request/Response types
export interface CreateInterviewRequest {
  job_application_id: string;
  interview_type: InterviewType;
  title: string;
  description?: string;
  scheduled_at: string;
  duration_minutes?: number;
  timezone?: string;
  ai_interviewer_persona?: string;
  difficulty_level?: string;
  focus_areas?: string[];
  max_questions?: number;
  allow_retakes?: boolean;
  recording_enabled?: boolean;
}

export interface UpdateInterviewRequest {
  title?: string;
  description?: string;
  scheduled_at?: string;
  duration_minutes?: number;
  status?: InterviewStatus;
  ai_interviewer_persona?: string;
  difficulty_level?: string;
  focus_areas?: string[];
  max_questions?: number;
  allow_retakes?: boolean;
  recording_enabled?: boolean;
}

export interface SessionJoinResponse {
  session_id: string;
  room_id: string;
  peer_id: string;
  signaling_server: string;
  ice_servers: RTCIceServer[];
  session_config: {
    recording_enabled: boolean;
    max_duration: number;
  };
}

export interface QuestionGenerationRequest {
  regenerate?: boolean;
  focus_areas?: string[];
  difficulty_override?: string;
  question_count_override?: number;
}

export interface FollowUpRequest {
  parent_question_id: string;
  candidate_response: string;
}

export interface QuestionResponseRequest {
  response: string;
  duration?: number;
  audio_analysis?: Record<string, any>;
  video_analysis?: Record<string, any>;
}

// WebRTC signaling types
export interface SignalingMessage {
  type: 'offer' | 'answer' | 'ice-candidate' | 'connection-state' | 'quality-report';
  from_peer?: string;
  to_peer?: string;
  sdp?: string;
  candidate?: string;
  sdpMid?: string;
  sdpMLineIndex?: number;
  state?: string;
  quality?: {
    connection_quality?: number;
    audio_quality?: number;
    video_quality?: number;
    latency_ms?: number;
  };
  timestamp?: string;
}

export interface WebSocketMessage {
  type: 'signaling' | 'peer_connection_state' | 'session_ended' | 'question_update' | 'interview_update';
  data?: any;
  peer_id?: string;
  state?: string;
  reason?: string;
  timestamp?: string;
}

// UI state types
export interface VideoSettings {
  camera: boolean;
  microphone: boolean;
  speaker: boolean;
  cameraDeviceId?: string;
  microphoneDeviceId?: string;
  speakerDeviceId?: string;
}

export interface ConnectionQuality {
  overall: 'excellent' | 'good' | 'fair' | 'poor';
  video: number;
  audio: number;
  latency: number;
  bandwidth: number;
}

export interface InterviewState {
  interview?: Interview;
  session?: InterviewSession;
  questions: InterviewQuestion[];
  currentQuestionIndex: number;
  isRecording: boolean;
  timeRemaining: number;
  connectionQuality: ConnectionQuality;
  videoSettings: VideoSettings;
  isConnected: boolean;
  error?: string;
}