/**
 * Portfolio Types
 */

export interface Portfolio {
  id: number;
  user_id: number;
  video_intro_url?: string;
  video_duration?: number;
  headline?: string;
  bio?: string;
  template_id: string;
  is_public: boolean;
  view_count: number;
  created_at: string;
  updated_at: string;
}

export interface PortfolioProject {
  id: number;
  portfolio_id: number;
  title: string;
  description?: string;
  technologies: string[];
  media_urls: string[];
  code_snippets: CodeSnippet[];
  live_url?: string;
  github_url?: string;
  display_order: number;
  created_at: string;
}

export interface CodeSnippet {
  language: string;
  code: string;
  description?: string;
}

export interface Achievement {
  id: number;
  portfolio_id: number;
  badge_type: string;
  title: string;
  description?: string;
  issuer?: string;
  date_earned?: string;
  verification_url?: string;
  icon?: string;
  created_at: string;
}

export interface VideoUploadResponse {
  upload_url: string;
  video_url: string;
  expires_in: number;
}
