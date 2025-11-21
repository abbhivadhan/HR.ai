import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { NotificationCenter } from '../NotificationCenter';
import { notificationService } from '../../../services/notificationService';
import { NotificationCategory, NotificationPriority, NotificationStatus, NotificationType } from '../../../types/notification';

// Mock the notification service
jest.mock('../../../services/notificationService', () => ({
  notificationService: {
    getNotifications: jest.fn(),
    markAsRead: jest.fn(),
    markAllAsRead: jest.fn(),
    connectToNotifications: jest.fn(),
  },
}));

const mockNotifications = [
  {
    id: '1',
    user_id: 'user1',
    type: NotificationType.IN_APP,
    category: NotificationCategory.JOB_MATCH,
    priority: NotificationPriority.HIGH,
    status: NotificationStatus.PENDING,
    title: 'New Job Match',
    message: 'A new job matches your skills',
    created_at: new Date().toISOString(),
    read_at: null,
  },
  {
    id: '2',
    user_id: 'user1',
    type: NotificationType.EMAIL,
    category: NotificationCategory.ASSESSMENT_REMINDER,
    priority: NotificationPriority.MEDIUM,
    status: NotificationStatus.READ,
    title: 'Assessment Reminder',
    message: 'Complete your assessment',
    created_at: new Date().toISOString(),
    read_at: new Date().toISOString(),
  },
];

describe('NotificationCenter', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (notificationService.getNotifications as jest.Mock).mockResolvedValue({
      notifications: mockNotifications,
      total: 2,
      unread_count: 1,
    });
    (notificationService.connectToNotifications as jest.Mock).mockReturnValue({
      close: jest.fn(),
    });
  });

  it('renders notification bell with unread count', async () => {
    render(<NotificationCenter userId="user1" />);
    
    const bellButton = screen.getByRole('button', { name: /notifications/i });
    expect(bellButton).toBeInTheDocument();
  });

  it('opens notification dropdown when bell is clicked', async () => {
    render(<NotificationCenter userId="user1" />);
    
    const bellButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(bellButton);
    
    await waitFor(() => {
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });
  });

  it('displays notifications when dropdown is opened', async () => {
    render(<NotificationCenter userId="user1" />);
    
    const bellButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(bellButton);
    
    await waitFor(() => {
      expect(screen.getByText('New Job Match')).toBeInTheDocument();
      expect(screen.getByText('Assessment Reminder')).toBeInTheDocument();
    });
  });

  it('shows unread count badge', async () => {
    render(<NotificationCenter userId="user1" />);
    
    // Click to open dropdown first, which triggers loading notifications
    const bellButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(bellButton);
    
    await waitFor(() => {
      const badge = screen.getByText('1');
      expect(badge).toBeInTheDocument();
    });
  });

  it('calls markAsRead when notification is clicked', async () => {
    (notificationService.markAsRead as jest.Mock).mockResolvedValue({});
    
    render(<NotificationCenter userId="user1" />);
    
    const bellButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(bellButton);
    
    await waitFor(() => {
      const notification = screen.getByText('New Job Match');
      fireEvent.click(notification);
    });
    
    expect(notificationService.markAsRead).toHaveBeenCalledWith('1');
  });

  it('calls markAllAsRead when mark all read button is clicked', async () => {
    (notificationService.markAllAsRead as jest.Mock).mockResolvedValue({});
    
    render(<NotificationCenter userId="user1" />);
    
    const bellButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(bellButton);
    
    await waitFor(() => {
      const markAllButton = screen.getByText(/mark all read/i);
      fireEvent.click(markAllButton);
    });
    
    expect(notificationService.markAllAsRead).toHaveBeenCalled();
  });

  it('filters notifications by category', async () => {
    render(<NotificationCenter userId="user1" />);
    
    const bellButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(bellButton);
    
    await waitFor(() => {
      const categoryFilter = screen.getByDisplayValue('All Categories');
      fireEvent.change(categoryFilter, { target: { value: NotificationCategory.JOB_MATCH } });
    });
    
    expect(notificationService.getNotifications).toHaveBeenCalledWith(
      50, 0, false, NotificationCategory.JOB_MATCH
    );
  });

  it('shows empty state when no notifications', async () => {
    (notificationService.getNotifications as jest.Mock).mockResolvedValue({
      notifications: [],
      total: 0,
      unread_count: 0,
    });
    
    render(<NotificationCenter userId="user1" />);
    
    const bellButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(bellButton);
    
    await waitFor(() => {
      expect(screen.getByText('No notifications found')).toBeInTheDocument();
    });
  });

  it('shows loading state while fetching notifications', async () => {
    (notificationService.getNotifications as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({
        notifications: [],
        total: 0,
        unread_count: 0,
      }), 100))
    );
    
    render(<NotificationCenter userId="user1" />);
    
    const bellButton = screen.getByRole('button', { name: /notifications/i });
    fireEvent.click(bellButton);
    
    expect(screen.getByText('Loading notifications...')).toBeInTheDocument();
  });
});