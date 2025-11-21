import { 
  type Notification, 
  type NotificationListResponse, 
  type NotificationPreference, 
  type NotificationStats,
  type NotificationCategory,
  type SendNotificationRequest
} from '../types/notification';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class NotificationService {
  private async fetchWithAuth(url: string, options: RequestInit = {}) {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  // Get user notifications
  async getNotifications(
    limit: number = 50,
    offset: number = 0,
    unreadOnly: boolean = false,
    category?: NotificationCategory
  ): Promise<NotificationListResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
      unread_only: unreadOnly.toString(),
    });

    if (category) {
      params.append('category', category);
    }

    return this.fetchWithAuth(`/notifications?${params}`);
  }

  // Get specific notification
  async getNotification(notificationId: string): Promise<Notification> {
    return this.fetchWithAuth(`/notifications/${notificationId}`);
  }

  // Mark notification as read
  async markAsRead(notificationId: string): Promise<Notification> {
    return this.fetchWithAuth(`/notifications/${notificationId}/mark-read`, {
      method: 'POST',
    });
  }

  // Mark all notifications as read
  async markAllAsRead(category?: NotificationCategory): Promise<{ success: boolean; message: string }> {
    const params = category ? `?category=${category}` : '';
    return this.fetchWithAuth(`/notifications/mark-all-read${params}`, {
      method: 'POST',
    });
  }

  // Get notification preferences
  async getPreferences(): Promise<{ preferences: NotificationPreference[] }> {
    return this.fetchWithAuth('/notifications/preferences/');
  }

  // Update notification preference
  async updatePreference(
    category: NotificationCategory,
    preferences: Partial<NotificationPreference>
  ): Promise<NotificationPreference> {
    return this.fetchWithAuth(`/notifications/preferences/${category}`, {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  }

  // Get notification statistics
  async getStats(category?: NotificationCategory, days: number = 30): Promise<NotificationStats> {
    const params = new URLSearchParams({ days: days.toString() });
    if (category) {
      params.append('category', category);
    }

    return this.fetchWithAuth(`/notifications/stats?${params}`);
  }

  // Admin: Send notification
  async sendNotification(request: SendNotificationRequest): Promise<{ success: boolean; message: string }> {
    return this.fetchWithAuth('/notifications/send', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Admin: Get platform stats
  async getAdminStats(category?: NotificationCategory, days: number = 30): Promise<NotificationStats> {
    const params = new URLSearchParams({ days: days.toString() });
    if (category) {
      params.append('category', category);
    }

    return this.fetchWithAuth(`/notifications/admin/stats?${params}`);
  }

  // Real-time notifications via WebSocket
  connectToNotifications(userId: string, onNotification: (notification: any) => void): WebSocket {
    const wsUrl = `ws://localhost:8000/api/notifications/ws/${userId}`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onNotification(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return ws;
  }

  // Request notification permission (for push notifications)
  async requestNotificationPermission(): Promise<NotificationPermission> {
    if (!('Notification' in window)) {
      throw new Error('This browser does not support notifications');
    }

    if (Notification.permission === 'granted') {
      return 'granted';
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      return permission;
    }

    return Notification.permission;
  }

  // Show browser notification
  showBrowserNotification(title: string, options?: NotificationOptions): void {
    if (Notification.permission === 'granted') {
      new Notification(title, {
        icon: '/icon-192x192.png',
        badge: '/badge-72x72.png',
        ...options,
      });
    }
  }

  // Register service worker for push notifications
  async registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered:', registration);
        return registration;
      } catch (error) {
        console.error('Service Worker registration failed:', error);
        return null;
      }
    }
    return null;
  }

  // Subscribe to push notifications
  async subscribeToPush(registration: ServiceWorkerRegistration): Promise<PushSubscription | null> {
    try {
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY,
      });

      // Send subscription to server
      await this.fetchWithAuth('/notifications/push-subscription', {
        method: 'POST',
        body: JSON.stringify({
          subscription: subscription.toJSON(),
        }),
      });

      return subscription;
    } catch (error) {
      console.error('Failed to subscribe to push notifications:', error);
      return null;
    }
  }
}

export const notificationService = new NotificationService();