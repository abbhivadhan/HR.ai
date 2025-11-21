/**
 * Resume Builder Types
 */

export interface Resume {
  id: number;
  user_id: number;
  title: string;
  template_id: string;
  content: ResumeContent;
  ats_score?: number;
  keywords: string[];
  is_primary: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface ResumeContent {
  summary?: string;
  experience?: WorkExperience[];
  education?: Education[];
  skills?: string[];
  certifications?: Certification[];
  projects?: Project[];
}

export interface WorkExperience {
  company: string;
  position: string;
  location?: string;
  start_date: string;
  end_date?: string;
  current: boolean;
  description: string;
  achievements: string[];
}

export interface Education {
  institution: string;
  degree: string;
  field: string;
  start_date: string;
  end_date?: string;
  gpa?: number;
}

export interface Certification {
  name: string;
  issuer: string;
  date: string;
  credential_id?: string;
  url?: string;
}

export interface Project {
  name: string;
  description: string;
  technologies: string[];
  url?: string;
}

export interface AIContentSuggestion {
  section: string;
  original: string;
  suggested: string;
  reason: string;
  impact: 'high' | 'medium' | 'low';
}

export interface ATSOptimization {
  id: number;
  resume_id: number;
  job_id?: number;
  score: number;
  suggestions: ATSSuggestion[];
  missing_keywords: string[];
  formatting_issues: FormattingIssue[];
  created_at: string;
}

export interface ATSSuggestion {
  type: string;
  message: string;
  priority: string;
}

export interface FormattingIssue {
  issue: string;
  location: string;
  fix: string;
}

export interface ResumeTemplate {
  id: string;
  name: string;
  description: string;
  preview_url: string;
}
