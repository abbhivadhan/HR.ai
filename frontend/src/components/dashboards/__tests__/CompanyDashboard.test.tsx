import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CompanyDashboard from '../CompanyDashboard';

// Mock the dashboard service
jest.mock('../../../services/dashboardService', () => ({
  getCompanyAnalytics: jest.fn(),
  getCompanyJobPostings: jest.fn(),
  getCompanyApplications: jest.fn(),
  getHiringFunnelData: jest.fn(),
  getApplicationTrendsData: jest.fn(),
  getSkillsInDemandData: jest.fn(),
  getNotifications: jest.fn(),
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

describe('CompanyDashboard', () => {
  const mockCompanyId = 'test-company-id';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders dashboard header correctly', async () => {
    render(<CompanyDashboard companyId={mockCompanyId} />);
    
    expect(screen.getByText('Company Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Manage your hiring pipeline and track performance')).toBeInTheDocument();
  });

  it('displays post job button in header', () => {
    render(<CompanyDashboard companyId={mockCompanyId} />);
    
    expect(screen.getByText('Post Job')).toBeInTheDocument();
  });

  it('renders stats cards with correct titles', async () => {
    render(<CompanyDashboard companyId={mockCompanyId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Active Jobs')).toBeInTheDocument();
      expect(screen.getByText('Total Applications')).toBeInTheDocument();
      expect(screen.getByText('Avg. Time to Hire')).toBeInTheDocument();
      expect(screen.getByText('Candidates Hired')).toBeInTheDocument();
    });
  });

  it('renders job postings section', async () => {
    render(<CompanyDashboard companyId={mockCompanyId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Active Job Postings')).toBeInTheDocument();
    });
  });

  it('renders recent applications section', async () => {
    render(<CompanyDashboard companyId={mockCompanyId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Recent Applications')).toBeInTheDocument();
    });
  });

  it('renders hiring funnel chart', async () => {
    render(<CompanyDashboard companyId={mockCompanyId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Hiring Funnel')).toBeInTheDocument();
    });
  });

  it('renders application trends chart', async () => {
    render(<CompanyDashboard companyId={mockCompanyId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Application Trends')).toBeInTheDocument();
    });
  });

  it('renders skills in demand chart', async () => {
    render(<CompanyDashboard companyId={mockCompanyId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Top Skills in Demand')).toBeInTheDocument();
    });
  });

  it('renders performance metrics section', async () => {
    render(<CompanyDashboard companyId={mockCompanyId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Performance Metrics')).toBeInTheDocument();
    });
  });

  it('renders quick actions section', async () => {
    render(<CompanyDashboard companyId={mockCompanyId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Quick Actions')).toBeInTheDocument();
      expect(screen.getByText('Post New Job')).toBeInTheDocument();
      expect(screen.getByText('Review Applications')).toBeInTheDocument();
      expect(screen.getByText('View Analytics')).toBeInTheDocument();
      expect(screen.getByText('Schedule Interviews')).toBeInTheDocument();
    });
  });
});