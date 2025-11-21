# Company Dashboard Enhancement Plan

## Current State
The CompanyDashboard component exists with:
- Stats cards (Active Jobs, Applications, Time to Hire, Hired)
- Job postings list
- Recent applications
- Charts (Hiring Funnel, Application Trends, Skills in Demand)
- Quick Actions buttons (non-functional)

## Missing Pages & Features

### Priority 1: Core Functionality
1. **Post Job Page** (`/dashboard/jobs/new`)
   - Job posting form
   - Job details, requirements, benefits
   - Preview before publishing

2. **Job Management Page** (`/dashboard/jobs`)
   - List all jobs
   - Edit/pause/close jobs
   - View applications per job

3. **Applications Review Page** (`/dashboard/applications`)
   - Filter by job, status, match score
   - Candidate profiles
   - Accept/reject actions
   - Schedule interviews

4. **Candidate Profile View** (`/dashboard/candidates/[id]`)
   - Full candidate details
   - Resume/portfolio
   - Assessment scores
   - Interview history
   - Actions (shortlist, interview, offer, reject)

### Priority 2: Enhanced Features
5. **Analytics Page** (`/dashboard/analytics`)
   - Detailed metrics
   - Custom date ranges
   - Export reports
   - Hiring trends

6. **Interview Scheduling** (`/dashboard/interviews`)
   - Calendar view
   - Schedule/reschedule
   - Video interview links
   - Interview feedback

7. **Team Management** (`/dashboard/team`)
   - Add team members
   - Assign roles/permissions
   - Collaboration features

8. **Company Settings** (`/dashboard/settings`)
   - Company profile
   - Branding
   - Notification preferences
   - Billing

## Implementation Strategy
1. Create routing structure
2. Build reusable components (forms, tables, filters)
3. Add navigation/routing to existing buttons
4. Implement pages one by one
5. Add dark mode support
6. Test all workflows

## Status: Planning Complete - Ready for Implementation
