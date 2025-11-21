'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  UserGroupIcon,
  BuildingOfficeIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  ShieldCheckIcon,
  ServerIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';
import DashboardCard from './DashboardCard';
import StatsCard from './StatsCard';
import ChartCard from './ChartCard';
import NotificationCenter from './NotificationCenter';
import { 
  AdminMetrics, 
  Notification, 
  ChartData,
  TimeSeriesData 
} from '../../types/dashboard';

interface AdminDashboardProps {
  adminId: string;
}

interface SystemAlert {
  id: string;
  type: 'error' | 'warning' | 'info';
  title: string;
  description: string;
  timestamp: Date;
  resolved: boolean;
}

interface RecentActivity {
  id: string;
  type: 'user_registration' | 'job_posting' | 'assessment_completed' | 'system_event';
  description: string;
  timestamp: Date;
  userId?: string;
  metadata?: any;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ adminId }) => {
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [systemAlerts, setSystemAlerts] = useState<SystemAlert[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [userGrowthData, setUserGrowthData] = useState<ChartData>({ labels: [], datasets: [] });
  const [revenueData, setRevenueData] = useState<ChartData>({ labels: [], datasets: [] });
  const [platformUsageData, setPlatformUsageData] = useState<ChartData>({ labels: [], datasets: [] });
  const [userTypeDistribution, setUserTypeDistribution] = useState<ChartData>({ labels: [], datasets: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, [adminId]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('access_token');
      
      const metricsResponse = await fetch(`${API_URL}/api/dashboard/admin/metrics`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (metricsResponse.ok) {
        const data = await metricsResponse.json();
        setMetrics(data.metrics);
      }

      const alertsResponse = await fetch(`${API_URL}/api/dashboard/admin/alerts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (alertsResponse.ok) {
        const data = await alertsResponse.json();
        setSystemAlerts(data.alerts || []);
      }

      setRecentActivity([
        {
          id: '1',
          type: 'user_registration',
          description: 'New company registration: TechStartup Inc.',
          timestamp: new Date(Date.now() - 900000)
        },
        {
          id: '2',
          type: 'job_posting',
          description: 'Job posted: Senior React Developer at BigCorp',
          timestamp: new Date(Date.now() - 1800000)
        },
        {
          id: '3',
          type: 'assessment_completed',
          description: 'Assessment completed: JavaScript fundamentals',
          timestamp: new Date(Date.now() - 2700000)
        },
        {
          id: '4',
          type: 'system_event',
          description: 'AI model retrained with new data',
          timestamp: new Date(Date.now() - 3600000)
        }
      ]);

      // All demo data removed - dashboards will show empty states until real data is available from API

    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = (notificationId: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
    );
  };

  const handleMarkAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const handleDismissNotification = (notificationId: string) => {
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
  };

  const handleResolveAlert = (alertId: string) => {
    setSystemAlerts(prev => 
      prev.map(alert => alert.id === alertId ? { ...alert, resolved: true } : alert)
    );
  };

  const getAlertColor = (type: SystemAlert['type']) => {
    switch (type) {
      case 'error':
        return 'text-red-600 bg-red-100 border-red-200';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'info':
        return 'text-blue-600 bg-blue-100 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getActivityIcon = (type: RecentActivity['type']) => {
    switch (type) {
      case 'user_registration':
        return <UserGroupIcon className="w-4 h-4 text-green-600" />;
      case 'job_posting':
        return <BuildingOfficeIcon className="w-4 h-4 text-blue-600" />;
      case 'assessment_completed':
        return <ChartBarIcon className="w-4 h-4 text-purple-600" />;
      case 'system_event':
        return <ServerIcon className="w-4 h-4 text-gray-600" />;
      default:
        return <GlobeAltIcon className="w-4 h-4 text-gray-600" />;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <p className="text-gray-600 mt-1">Platform monitoring and management</p>
          </div>
          <div className="flex items-center space-x-4">
            <NotificationCenter
              notifications={notifications}
              onMarkAsRead={handleMarkAsRead}
              onMarkAllAsRead={handleMarkAllAsRead}
              onDismiss={handleDismissNotification}
            />
            <button className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
              <ExclamationTriangleIcon className="w-5 h-5" />
              <span>System Alerts</span>
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Users"
            value={formatNumber(metrics?.users.total || 0)}
            icon={<UserGroupIcon className="w-6 h-6" />}
            color="blue"
            change={{ value: 12, type: 'increase', period: 'this month' }}
            loading={loading}
          />
          <StatsCard
            title="Active Today"
            value={formatNumber(metrics?.users.activeToday || 0)}
            icon={<ChartBarIcon className="w-6 h-6" />}
            color="green"
            change={{ value: 8, type: 'increase', period: 'yesterday' }}
            loading={loading}
          />
          <StatsCard
            title="Monthly Revenue"
            value={formatCurrency(metrics?.revenue.monthlyRecurring || 0)}
            icon={<CurrencyDollarIcon className="w-6 h-6" />}
            color="purple"
            change={{ value: 15, type: 'increase', period: 'last month' }}
            loading={loading}
          />
          <StatsCard
            title="System Health"
            value="98.5%"
            icon={<ShieldCheckIcon className="w-6 h-6" />}
            color="green"
            change={{ value: 0.2, type: 'increase', period: 'this week' }}
            loading={loading}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* System Alerts */}
            <DashboardCard
              title="System Alerts"
              actions={
                <button className="text-sm text-blue-600 hover:text-blue-800">
                  View All
                </button>
              }
            >
              <div className="space-y-3">
                {systemAlerts.filter(alert => !alert.resolved).length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <ShieldCheckIcon className="w-12 h-12 mx-auto mb-2 text-green-500" />
                    <p>All systems operational</p>
                  </div>
                ) : (
                  systemAlerts.filter(alert => !alert.resolved).map((alert) => (
                    <motion.div
                      key={alert.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className={`p-4 rounded-lg border ${getAlertColor(alert.type)}`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h4 className="font-semibold">{alert.title}</h4>
                          <p className="text-sm mt-1">{alert.description}</p>
                          <p className="text-xs mt-2 opacity-75">
                            {alert.timestamp.toLocaleString()}
                          </p>
                        </div>
                        <button
                          onClick={() => handleResolveAlert(alert.id)}
                          className="ml-4 px-3 py-1 bg-white bg-opacity-50 rounded text-sm hover:bg-opacity-75 transition-colors"
                        >
                          Resolve
                        </button>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>
            </DashboardCard>

            {/* User Growth Chart */}
            <ChartCard
              title="User Growth"
              data={userGrowthData}
              type="line"
              height={300}
              description="Monthly user registration trends"
              loading={loading}
            />

            {/* Revenue Chart */}
            <ChartCard
              title="Revenue Trends"
              data={revenueData}
              type="bar"
              height={250}
              description="Monthly recurring revenue over time"
              loading={loading}
            />

            {/* Recent Activity */}
            <DashboardCard
              title="Recent Platform Activity"
              actions={
                <button className="text-sm text-blue-600 hover:text-blue-800">
                  View Logs
                </button>
              }
            >
              <div className="space-y-3">
                {recentActivity.map((activity) => (
                  <motion.div
                    key={activity.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded transition-colors"
                  >
                    <div className="flex-shrink-0">
                      {getActivityIcon(activity.type)}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">{activity.description}</p>
                      <p className="text-xs text-gray-500">
                        {activity.timestamp.toLocaleString()}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </DashboardCard>
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            {/* Platform Usage */}
            <ChartCard
              title="Platform Usage"
              data={platformUsageData}
              type="doughnut"
              height={300}
              description="Distribution of platform activities"
              loading={loading}
            />

            {/* User Type Distribution */}
            <ChartCard
              title="User Distribution"
              data={userTypeDistribution}
              type="pie"
              height={250}
              description="Breakdown of user types on the platform"
              loading={loading}
            />

            {/* Key Metrics */}
            <DashboardCard title="Key Performance Indicators">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Daily Active Users</span>
                  <span className="font-semibold">{formatNumber(metrics?.engagement.dailyActiveUsers || 0)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Avg. Session Time</span>
                  <span className="font-semibold">{metrics?.engagement.averageSessionTime}min</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Bounce Rate</span>
                  <span className="font-semibold">{metrics?.engagement.bounceRate}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Churn Rate</span>
                  <span className="font-semibold">{metrics?.revenue.churnRate}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Revenue</span>
                  <span className="font-semibold">{formatCurrency(metrics?.revenue.totalRevenue || 0)}</span>
                </div>
              </div>
            </DashboardCard>

            {/* Quick Actions */}
            <DashboardCard title="Admin Actions">
              <div className="space-y-3">
                <button className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-50 rounded-lg transition-colors">
                  <UserGroupIcon className="w-5 h-5 text-blue-600" />
                  <span className="text-gray-900">Manage Users</span>
                </button>
                <button className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-50 rounded-lg transition-colors">
                  <ServerIcon className="w-5 h-5 text-green-600" />
                  <span className="text-gray-900">System Monitoring</span>
                </button>
                <button className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-50 rounded-lg transition-colors">
                  <ChartBarIcon className="w-5 h-5 text-purple-600" />
                  <span className="text-gray-900">Analytics Reports</span>
                </button>
                <button className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-50 rounded-lg transition-colors">
                  <CurrencyDollarIcon className="w-5 h-5 text-yellow-600" />
                  <span className="text-gray-900">Billing Management</span>
                </button>
              </div>
            </DashboardCard>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;