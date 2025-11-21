import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AdminDashboard from '../AdminDashboard';

// Mock the dashboard service
jest.mock('../../../services/dashboardService', () => ({
  getAdminMetrics: jest.fn(),
  getSystemAlerts: jest.fn(),
  getRecentActivity: jest.fn(),
  getUserGrowthData: jest.fn(),
  getRevenueData: jest.fn(),
  getPlatformUsageData: jest.fn(),
  getUserTypeDistribution: jest.fn(),
  getNotifications: jest.fn(),
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

describe('AdminDashboard', () => {
  const mockAdminId = 'test-admin-id';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders dashboard header correctly', async () => {
    render(<AdminDashboard adminId={mockAdminId} />);
    
    expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Platform monitoring and management')).toBeInTheDocument();
  });

  it('displays system alerts button in header', () => {
    render(<AdminDashboard adminId={mockAdminId} />);
    
    // Use getByRole to find the button specifically
    const alertButton = screen.getByRole('button', { name: /system alerts/i });
    expect(alertButton).toBeInTheDocument();
  });

  it('renders stats cards with correct titles', async () => {
    render(<AdminDashboard adminId={mockAdminId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Total Users')).toBeInTheDocument();
      expect(screen.getByText('Active Today')).toBeInTheDocument();
      expect(screen.getByText('Monthly Revenue')).toBeInTheDocument();
      expect(screen.getByText('System Health')).toBeInTheDocument();
    });
  });

  it('renders system alerts section', async () => {
    render(<AdminDashboard adminId={mockAdminId} />);
    
    await waitFor(() => {
      // Look for the heading specifically
      const alertsHeading = screen.getByRole('heading', { name: /system alerts/i });
      expect(alertsHeading).toBeInTheDocument();
    });
  });

  it('renders user growth chart', async () => {
    render(<AdminDashboard adminId={mockAdminId} />);
    
    await waitFor(() => {
      expect(screen.getByText('User Growth')).toBeInTheDocument();
    });
  });

  it('renders revenue trends chart', async () => {
    render(<AdminDashboard adminId={mockAdminId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Revenue Trends')).toBeInTheDocument();
    });
  });

  it('renders platform usage chart', async () => {
    render(<AdminDashboard adminId={mockAdminId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Platform Usage')).toBeInTheDocument();
    });
  });

  it('renders user distribution chart', async () => {
    render(<AdminDashboard adminId={mockAdminId} />);
    
    await waitFor(() => {
      expect(screen.getByText('User Distribution')).toBeInTheDocument();
    });
  });

  it('renders recent platform activity section', async () => {
    render(<AdminDashboard adminId={mockAdminId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Recent Platform Activity')).toBeInTheDocument();
    });
  });

  it('renders key performance indicators section', async () => {
    render(<AdminDashboard adminId={mockAdminId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Key Performance Indicators')).toBeInTheDocument();
    });
  });

  it('renders admin actions section', async () => {
    render(<AdminDashboard adminId={mockAdminId} />);
    
    await waitFor(() => {
      expect(screen.getByText('Admin Actions')).toBeInTheDocument();
      expect(screen.getByText('Manage Users')).toBeInTheDocument();
      expect(screen.getByText('System Monitoring')).toBeInTheDocument();
      expect(screen.getByText('Analytics Reports')).toBeInTheDocument();
      expect(screen.getByText('Billing Management')).toBeInTheDocument();
    });
  });
});