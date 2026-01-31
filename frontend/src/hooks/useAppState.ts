import { useState, useCallback } from 'react';

export interface Notification {
  id: string;
  title: string;
  description: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: Date;
  read: boolean;
}

export interface AppSettings {
  notificationsEnabled: {
    routeUpdates: boolean;
    capacityAlerts: boolean;
    driverStatus: boolean;
    systemHealth: boolean;
  };
  security: {
    twoFactorAuth: boolean;
    auditLogging: boolean;
    autoSessionTimeout: boolean;
  };
  theme: 'dark' | 'light';
  timezone: string;
}

const mockNotifications: Notification[] = [
  {
    id: '1',
    title: 'Route 101 Optimized',
    description: 'Route 101 has been optimized, reducing travel time by 15%',
    type: 'success',
    timestamp: new Date(Date.now() - 5 * 60000),
    read: false,
  },
  {
    id: '2',
    title: 'Capacity Alert',
    description: 'Route 103 is at 95% capacity. Consider splitting the route.',
    type: 'warning',
    timestamp: new Date(Date.now() - 15 * 60000),
    read: false,
  },
  {
    id: '3',
    title: 'Driver Check-in',
    description: 'Driver Ahmed Al-Hassan has checked in for Route 101',
    type: 'info',
    timestamp: new Date(Date.now() - 25 * 60000),
    read: false,
  },
];

/**
 * Hook for managing app notifications
 */
export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  }, []);

  const dismissNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const id = Date.now().toString();
    setNotifications(prev => [
      { ...notification, id, timestamp: new Date() },
      ...prev
    ]);
    return id;
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  return {
    notifications,
    unreadCount,
    markAsRead,
    dismissNotification,
    addNotification,
  };
}

/**
 * Hook for managing app settings
 */
export function useAppSettings() {
  const [settings, setSettings] = useState<AppSettings>({
    notificationsEnabled: {
      routeUpdates: true,
      capacityAlerts: true,
      driverStatus: false,
      systemHealth: true,
    },
    security: {
      twoFactorAuth: true,
      auditLogging: true,
      autoSessionTimeout: false,
    },
    theme: 'dark',
    timezone: 'GST',
  });

  const [hasChanges, setHasChanges] = useState(false);

  const updateSettings = useCallback((updates: Partial<AppSettings>) => {
    setSettings(prev => ({ ...prev, ...updates }));
    setHasChanges(true);
  }, []);

  const saveSettings = useCallback(() => {
    // Simulate API call to save settings
    localStorage.setItem('appSettings', JSON.stringify(settings));
    setHasChanges(false);
    return true;
  }, [settings]);

  const resetToDefaults = useCallback(() => {
    setSettings({
      notificationsEnabled: {
        routeUpdates: true,
        capacityAlerts: true,
        driverStatus: false,
        systemHealth: true,
      },
      security: {
        twoFactorAuth: true,
        auditLogging: true,
        autoSessionTimeout: false,
      },
      theme: 'dark',
      timezone: 'GST',
    });
    setHasChanges(false);
  }, []);

  return {
    settings,
    hasChanges,
    updateSettings,
    saveSettings,
    resetToDefaults,
  };
}

/**
 * Hook for managing filter state
 */
export interface FilterOptions {
  status?: string;
  zone?: string;
  driver?: string;
  minStudents?: number;
  maxStudents?: number;
}

export function useRouteFilters() {
  const [filters, setFilters] = useState<FilterOptions>({});
  const [isOpen, setIsOpen] = useState(false);

  const updateFilter = useCallback((key: keyof FilterOptions, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({});
  }, []);

  const toggleOpen = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  return {
    filters,
    isOpen,
    setIsOpen,
    updateFilter,
    clearFilters,
    toggleOpen,
  };
}

/**
 * Get system status data
 */
export interface SystemStatus {
  api: { status: 'connected' | 'disconnected'; latency: number };
  database: { status: 'healthy' | 'degraded' | 'down'; size: string };
  storage: { used: string; total: string; percentage: number };
}

export function getSystemStatus(): SystemStatus {
  return {
    api: { status: 'connected', latency: 45 },
    database: { status: 'healthy', size: '2.4GB' },
    storage: { used: '34GB', total: '50GB', percentage: 68 },
  };
}
