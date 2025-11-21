export interface JobPosting {
  id: string
  company_id: string
  title: string
  description: string
  summary?: string
  job_type: JobType
  experience_level: string
  department?: string
  location?: string
  remote_type: RemoteType
  salary_min?: number
  salary_max?: number
  salary_currency: string
  benefits: string[]
  requirements?: string
  responsibilities?: string
  qualifications?: string
  application_deadline?: string
  max_applications?: number
  application_instructions?: string
  status: JobStatus
  is_featured: boolean
  is_urgent: boolean
  slug?: string
  meta_description?: string
  tags: string[]
  posted_at?: string
  expires_at?: string
  created_at: string
  updated_at: string
  view_count: number
  application_count: number
  company?: Company
  required_skills?: Skill[]
  applications?: JobApplication[]
}

export interface JobApplication {
  id: string
  job_posting_id: string
  candidate_id: string
  status: ApplicationStatus
  cover_letter?: string
  resume_url?: string
  screening_questions?: string
  ai_match_score?: number
  recruiter_notes?: string
  applied_at: string
  reviewed_at?: string
  status_updated_at: string
  last_contact_at?: string
  next_followup_at?: string
  created_at: string
  updated_at: string
  job_posting?: JobPosting
  candidate?: CandidateProfile
}

export interface CandidateProfile {
  id: string
  user_id: string
  first_name: string
  last_name: string
  email: string
  resume_url?: string
  skills: Skill[]
  experience_years: number
  education: Education[]
  certifications: Certification[]
  preferred_locations: string[]
  salary_expectation?: SalaryRange
  availability?: string
  profile_picture?: string
  bio?: string
}

export interface Company {
  id: string
  company_name: string
  industry: string
  company_size: string
  website?: string
  description?: string
  logo_url?: string
  verified: boolean
}

export interface Skill {
  id: string
  name: string
  category: string
  level?: string
}

export interface Education {
  id: string
  institution: string
  degree: string
  field_of_study: string
  start_date: string
  end_date?: string
  grade?: string
}

export interface Certification {
  id: string
  name: string
  issuing_organization: string
  issue_date: string
  expiration_date?: string
  credential_id?: string
  credential_url?: string
}

export interface SalaryRange {
  min: number
  max: number
  currency: string
}

export enum JobType {
  FULL_TIME = "full_time",
  PART_TIME = "part_time",
  CONTRACT = "contract",
  TEMPORARY = "temporary",
  INTERNSHIP = "internship",
  FREELANCE = "freelance"
}

export enum RemoteType {
  ONSITE = "onsite",
  REMOTE = "remote",
  HYBRID = "hybrid"
}

export enum JobStatus {
  DRAFT = "draft",
  ACTIVE = "active",
  PAUSED = "paused",
  EXPIRED = "expired",
  FILLED = "filled",
  CANCELLED = "cancelled"
}

export enum ApplicationStatus {
  PENDING = "pending",
  REVIEWING = "reviewing",
  SHORTLISTED = "shortlisted",
  INTERVIEWED = "interviewed",
  OFFERED = "offered",
  ACCEPTED = "accepted",
  REJECTED = "rejected",
  WITHDRAWN = "withdrawn"
}

export interface JobSearchFilters {
  query?: string
  location?: string
  remote_type?: RemoteType[]
  job_type?: JobType[]
  experience_level?: string[]
  salary_min?: number
  salary_max?: number
  skills?: string[]
  company_size?: string[]
  posted_within?: number // days
  sort_by?: 'relevance' | 'date' | 'salary' | 'company'
  sort_order?: 'asc' | 'desc'
}

export interface JobSearchResponse {
  jobs: JobPosting[]
  total: number
  page: number
  per_page: number
  total_pages: number
  filters_applied: JobSearchFilters
}