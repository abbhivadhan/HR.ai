-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (works with Supabase Auth)
-- Note: id should match auth.users.id
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  first_name TEXT,
  last_name TEXT,
  user_type TEXT CHECK (user_type IN ('CANDIDATE', 'COMPANY', 'ADMIN')) NOT NULL,
  is_active BOOLEAN DEFAULT true,
  is_verified BOOLEAN DEFAULT false,
  phone TEXT,
  location TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view their own profile"
  ON users FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
  ON users FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Anyone can insert during registration"
  ON users FOR INSERT
  WITH CHECK (true);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  location TEXT,
  salary_range TEXT,
  job_type TEXT CHECK (job_type IN ('full-time', 'part-time', 'contract', 'internship')),
  status TEXT CHECK (status IN ('active', 'closed', 'draft')) DEFAULT 'active',
  skills TEXT[],
  requirements TEXT,
  benefits TEXT,
  posted_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view active jobs"
  ON jobs FOR SELECT
  USING (status = 'active');

CREATE POLICY "Companies can manage their own jobs"
  ON jobs FOR ALL
  USING (auth.uid() = company_id);

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
  candidate_id UUID REFERENCES users(id) ON DELETE CASCADE,
  status TEXT CHECK (status IN ('pending', 'reviewing', 'shortlisted', 'interviewed', 'offered', 'rejected', 'accepted')) DEFAULT 'pending',
  match_score INTEGER CHECK (match_score >= 0 AND match_score <= 100),
  applied_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  resume_url TEXT,
  cover_letter TEXT,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Candidates can view their own applications"
  ON applications FOR SELECT
  USING (auth.uid() = candidate_id);

CREATE POLICY "Companies can view applications for their jobs"
  ON applications FOR SELECT
  USING (auth.uid() IN (SELECT company_id FROM jobs WHERE id = job_id));

CREATE POLICY "Candidates can create applications"
  ON applications FOR INSERT
  WITH CHECK (auth.uid() = candidate_id);

-- Assessments table
CREATE TABLE IF NOT EXISTS assessments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  candidate_id UUID REFERENCES users(id) ON DELETE CASCADE,
  assessment_type TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  questions JSONB,
  answers JSONB,
  score INTEGER CHECK (score >= 0 AND score <= 100),
  status TEXT CHECK (status IN ('pending', 'in_progress', 'completed')) DEFAULT 'pending',
  time_limit INTEGER,
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Candidates can view their own assessments"
  ON assessments FOR SELECT
  USING (auth.uid() = candidate_id);

CREATE POLICY "Candidates can update their own assessments"
  ON assessments FOR UPDATE
  USING (auth.uid() = candidate_id);

-- Interviews table
CREATE TABLE IF NOT EXISTS interviews (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
  candidate_id UUID REFERENCES users(id) ON DELETE CASCADE,
  interviewer_id UUID REFERENCES users(id),
  interview_type TEXT CHECK (interview_type IN ('phone', 'video', 'in-person', 'ai-video')) NOT NULL,
  status TEXT CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')) DEFAULT 'scheduled',
  scheduled_at TIMESTAMP WITH TIME ZONE,
  duration INTEGER,
  meeting_link TEXT,
  notes TEXT,
  feedback JSONB,
  recording_url TEXT,
  transcript TEXT,
  ai_analysis JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Candidates can view their own interviews"
  ON interviews FOR SELECT
  USING (auth.uid() = candidate_id);

CREATE POLICY "Companies can view interviews for their jobs"
  ON interviews FOR SELECT
  USING (auth.uid() IN (SELECT company_id FROM jobs WHERE id = job_id));

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_jobs_company_id ON jobs(company_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_applications_job_id ON applications(job_id);
CREATE INDEX idx_applications_candidate_id ON applications(candidate_id);
CREATE INDEX idx_assessments_candidate_id ON assessments(candidate_id);
CREATE INDEX idx_interviews_candidate_id ON interviews(candidate_id);
CREATE INDEX idx_interviews_job_id ON interviews(job_id);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON assessments
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interviews_updated_at BEFORE UPDATE ON interviews
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
