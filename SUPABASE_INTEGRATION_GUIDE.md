# Supabase Integration Guide

## Overview
This guide covers integrating Supabase as the backend database and authentication provider for the AI-HR Platform.

## Prerequisites
1. Create a Supabase account at https://supabase.com
2. Create a new Supabase project
3. Get your project URL and anon key from Project Settings > API

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=your_supabase_project_url
```

### Backend (.env)
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

## Database Schema

The following tables need to be created in Supabase:

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  first_name TEXT,
  last_name TEXT,
  user_type TEXT CHECK (user_type IN ('CANDIDATE', 'COMPANY', 'ADMIN')),
  is_active BOOLEAN DEFAULT true,
  is_verified BOOLEAN DEFAULT false,
  verification_token TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Jobs Table
```sql
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID REFERENCES users(id),
  title TEXT NOT NULL,
  description TEXT,
  location TEXT,
  salary_range TEXT,
  job_type TEXT,
  status TEXT DEFAULT 'active',
  skills TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Applications Table
```sql
CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  job_id UUID REFERENCES jobs(id),
  candidate_id UUID REFERENCES users(id),
  status TEXT DEFAULT 'pending',
  match_score INTEGER,
  applied_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  resume_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Assessments Table
```sql
CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  candidate_id UUID REFERENCES users(id),
  title TEXT NOT NULL,
  score INTEGER,
  total_questions INTEGER,
  correct_answers INTEGER,
  time_spent INTEGER,
  completed_at TIMESTAMP WITH TIME ZONE,
  category TEXT,
  difficulty TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Interviews Table
```sql
CREATE TABLE interviews (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  job_id UUID REFERENCES jobs(id),
  candidate_id UUID REFERENCES users(id),
  scheduled_date TIMESTAMP WITH TIME ZONE,
  duration INTEGER,
  status TEXT DEFAULT 'scheduled',
  type TEXT,
  meeting_link TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Row Level Security (RLS)

Enable RLS on all tables and create policies:

```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY "Users can read own data" ON users
  FOR SELECT USING (auth.uid() = id);

-- Users can update their own data
CREATE POLICY "Users can update own data" ON users
  FOR UPDATE USING (auth.uid() = id);

-- Anyone can read active jobs
CREATE POLICY "Anyone can read active jobs" ON jobs
  FOR SELECT USING (status = 'active');

-- Companies can manage their own jobs
CREATE POLICY "Companies can manage own jobs" ON jobs
  FOR ALL USING (auth.uid() = company_id);

-- Candidates can read their own applications
CREATE POLICY "Candidates can read own applications" ON applications
  FOR SELECT USING (auth.uid() = candidate_id);

-- Candidates can create applications
CREATE POLICY "Candidates can create applications" ON applications
  FOR INSERT WITH CHECK (auth.uid() = candidate_id);
```

## Deployment Steps

### 1. Set up Supabase Project
- Create project in Supabase dashboard
- Run SQL migrations to create tables
- Configure RLS policies
- Set up authentication providers (email/password)

### 2. Configure Environment Variables
- Add Supabase credentials to Vercel/deployment platform
- Update frontend and backend .env files

### 3. Deploy Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### 4. Deploy Backend (Optional - if using separate backend)
- Deploy to Railway, Render, or similar
- Or use Supabase Edge Functions

### 5. Test Deployment
- Test authentication flow
- Test CRUD operations
- Verify RLS policies work correctly

## Migration from Current Setup

1. Export existing data (if any)
2. Create Supabase tables
3. Import data to Supabase
4. Update API calls to use Supabase client
5. Test thoroughly before going live

## Monitoring

- Use Supabase Dashboard for database monitoring
- Set up logging and error tracking
- Monitor API usage and performance

## Security Checklist

- ✅ Enable RLS on all tables
- ✅ Use service role key only on backend
- ✅ Use anon key on frontend
- ✅ Validate all user inputs
- ✅ Implement rate limiting
- ✅ Enable 2FA for admin accounts
- ✅ Regular security audits

## Support

For issues:
- Supabase Docs: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
