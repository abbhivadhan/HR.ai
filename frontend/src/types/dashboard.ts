export interface DashboardStats {
  totalApplications?: number;
  activeJobs?: number;
  interviewsScheduled?: number;
  assessmentsCompleted?: number;
  matchingJobs?: number;
  profileViews?: number;
  responseRate?: number;
  averageScore?: number;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }[];
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  actionUrl?: string;
}

export interface CandidateRecommendation {
  id: string;
  jobTitle: string;
  companyName: string;
  matchScore: number;
  location: string;
  salaryRange: string;
  postedDate: Date;
  skills: string[];
}

export interface CompanyAnalytics {
  jobPostings: {
    total: number;
    active: number;
    filled: number;
    expired: number;
  };
  applications: {
    total: number;
    pending: number;
    reviewed: number;
    shortlisted: number;
    hired: number;
  };
  candidates: {
    totalViewed: number;
    averageScore: number;
    topSkills: string[];
  };
  performance: {
    averageTimeToHire: number;
    applicationRate: number;
    interviewToHireRatio: number;
  };
}

export interface AdminMetrics {
  users: {
    total: number;
    candidates: number;
    companies: number;
    activeToday: number;
    newThisWeek: number;
  };
  platform: {
    totalJobs: number;
    totalApplications: number;
    totalAssessments: number;
    totalInterviews: number;
  };
  engagement: {
    dailyActiveUsers: number;
    averageSessionTime: number;
    bounceRate: number;
  };
  revenue: {
    monthlyRecurring: number;
    totalRevenue: number;
    churnRate: number;
  };
}

export interface TimeSeriesData {
  date: string;
  value: number;
}

export interface SkillDistribution {
  skill: string;
  count: number;
  percentage: number;
}