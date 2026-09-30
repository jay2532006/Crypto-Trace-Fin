import { UserSession, UserRole } from '@/types/auth';
import { apiClient } from './api-client';

export const PRESET_USERS = [
  {
    id: '1',
    username: 'investigator1',
    fullName: 'Inspector R. Sharma',
    role: 'INVESTIGATOR' as UserRole,
    unit: 'Cyber Crime Police Station, Mumbai',
    password: 'Password@123',
  },
  {
    id: '2',
    username: 'supervisor1',
    fullName: 'ACP V. Deshmukh',
    role: 'SUPERVISOR' as UserRole,
    unit: 'I4C Cyber Coordination Directorate',
    password: 'Password@123',
  },
  {
    id: '3',
    username: 'admin1',
    fullName: 'System Administrator',
    role: 'ADMINISTRATOR' as UserRole,
    unit: 'MHA CIS Division',
    password: 'Password@123',
  },
  {
    id: '4',
    username: 'sahyog_service',
    fullName: 'SAHYOG Ingestion Agent',
    role: 'INTEGRATION_SERVICE' as UserRole,
    unit: 'I4C Gateway',
    password: 'ServiceSecret@2026',
  },
];

export const getCurrentSession = (): UserSession | null => {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem('user_session');
    if (raw) {
      return JSON.parse(raw);
    }
  } catch (e) {
    console.error('Error reading current session:', e);
  }
  return null;
};

export const loginUser = async (username: string, password?: string): Promise<UserSession> => {
  const pwd = password || 'Password@123';
  try {
    const res = await apiClient.post('/api/v1/auth/login', { username, password: pwd });
    const data = res.data;
    const session: UserSession = {
      username: data.username || username,
      fullName: data.user?.full_name || data.full_name || username,
      role: data.role as UserRole,
      unit: data.unit || 'LEA Cyber Crime Cell',
      token: data.access_token,
    };

    if (typeof window !== 'undefined') {
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user_session', JSON.stringify(session));
    }
    return session;
  } catch (err) {
    // Graceful offline fallback during local testing if backend is temporarily paused
    console.warn('Backend login endpoint unavailable, using local persona:', err);
    const matched = PRESET_USERS.find((u) => u.username === username) || PRESET_USERS[0];
    const session: UserSession = {
      username: matched.username,
      fullName: matched.fullName,
      role: matched.role,
      unit: matched.unit,
      token: 'dev-token-offline-fallback',
    };
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', session.token!);
      localStorage.setItem('user_session', JSON.stringify(session));
    }
    return session;
  }
};

export const logoutUser = async () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_session');
  }
};
