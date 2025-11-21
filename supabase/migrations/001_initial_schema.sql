-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  first_name TEXT,
  last_name TEXT,
  user_type TEXT CHECK (user_type IN ('CANDIDATE', 'COMPANY', 'ADMIN')) NOT NULL,
  is_active BOOLEAN DEFAULT true,
  is_verified BOOLEAN DEFAULT false,
  verification_token TEXT,
  phone TEXT,
  location TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Jobs table
CREATE TABLE jobs (
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

-- Applications table
CREATE TABLE applications (
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
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(job_id, candidate_id)
);

-- Assessments table
CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  candidate_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  score INTEGER CHECK (score >= 0 AND score <= 100),
  total_questions INTEGER,
  correct_answers INTEGER,
  time_spent INTEGER,
  completed_at TIMESTAMP WITH TIME ZONE,
  category TEXT,
  difficulty TEXT CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
  questions JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Interviews table
CREATE TABLE interviews (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
  candidate_id UUID REFERENCES users(id) ON DELETE CASCADE,
  company_id UUID REFERENCES users(id) ON DELETE CASCADE,
  scheduled_date TIMESTAMP WITH TIME ZONE,
  duration INTEGER,
  status TEXT CHECK (status IN ('scheduled', 'completed', 'cancelled', 'in-progress')) DEFAULT 'scheduled',
  type TEXT CHECK (type IN ('video', 'phone', 'in-person', 'ai-video')),
  meeting_link TEXT,
  notes TEXT,
  feedback JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notifications table
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  read BOOLEAN DEFAULT false,
  action_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User profiles table (extended info)
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  bio TEXT,
  skills TEXT[],
  experience_years INTEGER,
  education TEXT,
  certifications TEXT[],
  portfolio_url TEXT,
  linkedin_url TEXT,
  github_url TEXT,
  resume_url TEXT,
  preferences JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Company profiles table
CREATE TABLE company_profiles (
  id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  company_name TEXT NOT NULL,
  industry TEXT,
  company_size TEXT,
  website TEXT,
  description TEXT,
  logo_url TEXT,
  founded_year INTEGER,
  headquarters TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_jobs_company_id ON jobs(company_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_applications_job_id ON applications(job_id);
CREATE INDEX idx_applications_candidate_id ON applications(candidate_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_assessments_candidate_id ON assessments(candidate_id);
CREATE INDEX idx_interviews_candidate_id ON interviews(candidate_id);
CREATE INDEX idx_interviews_job_id ON interviews(job_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(read);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can read own data" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
  FOR UPDATE USING (auth.uid() = id);

-- RLS Policies for jobs table
CREATE POLICY "Anyone can read active jobs" ON jobs
  FOR SELECT USING (status = 'active' OR auth.uid() = company_id);

CREATE POLICY "Companies can create jobs" ON jobs
  FOR INSERT WITH CHECK (auth.uid() = company_id);

CREATE POLICY "Companies can update own jobs" ON jobs
  FOR UPDATE USING (auth.uid() = company_id);

CREATE POLICY "Companies can delete own jobs" ON jobs
  FOR DELETE USING (auth.uid() = company_id);

-- RLS Policies for applications table
CREATE POLICY "Candidates can read own applications" ON applications
  FOR SELECT USING (auth.uid() = candidate_id OR auth.uid() IN (SELECT company_id FROM jobs WHERE id = job_id));

CREATE POLICY "Candidates can create applications" ON applications
  FOR INSERT WITH CHECK (auth.uid() = candidate_id);

CREATE POLICY "Candidates can update own applications" ON applications
  FOR UPDATE USING (auth.uid() = candidate_id);

CREATE POLICY "Companies can update applications for their jobs" ON applications
  FOR UPDATE USING (auth.uid() IN (SELECT company_id FROM jobs WHERE id = job_id));

-- RLS Policies for assessments table
CREATE POLICY "Candidates can read own assessments" ON assessments
  FOR SELECT USING (auth.uid() = candidate_id);

CREATE POLICY "Candidates can create assessments" ON assessments
  FOR INSERT WITH CHECK (auth.uid() = candidate_id);

-- RLS Policies for interviews table
CREATE POLICY "Users can read own interviews" ON interviews
  FOR SELECT USING (auth.uid() = candidate_id OR auth.uid() = company_id);

CREATE POLICY "Companies can create interviews" ON interviews
  FOR INSERT WITH CHECK (auth.uid() = company_id);

CREATE POLICY "Companies can update interviews" ON interviews
  FOR UPDATE USING (auth.uid() = company_id);

-- RLS Policies for notifications table
CREATE POLICY "Users can read own notifications" ON notifications
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own notifications" ON notifications
  FOR UPDATE USING (auth.uid() = user_id);

-- RLS Policies for user_profiles table
CREATE POLICY "Users can read own profile" ON user_profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
  FOR ALL USING (auth.uid() = id);

-- RLS Policies for company_profiles table
CREATE POLICY "Anyone can read company profiles" ON company_profiles
  FOR SELECT USING (true);

CREATE POLICY "Companies can update own profile" ON company_profiles
  FOR ALL USING (auth.uid() = id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interviews_updated_at BEFORE UPDATE ON interviews
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_profiles_updated_at BEFORE UPDATE ON company_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
