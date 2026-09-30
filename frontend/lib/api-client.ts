/**
 * TraceX Sahyog - Live API Client
 *
 * Full-featured HTTP client connecting Next.js frontend to FastAPI backend.
 * - Handles Next.js proxy rewrites (/api/* -> http://127.0.0.1:8765/api/*)
 * - Automatically attaches Bearer JWT authentication from localStorage
 * - Formats JSON request/response bodies with Axios-compatible { data } envelope
 * - Throws structured API errors with status and detail
 */

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  ok: boolean;
  headers: Headers;
}

export class ApiError extends Error {
  response?: {
    status: number;
    data: any;
  };

  constructor(message: string, status?: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    if (status !== undefined) {
      this.response = { status, data };
    }
  }
}

function getBaseUrl(): string {
  if (typeof window !== 'undefined') {
    return process.env.NEXT_PUBLIC_API_URL || '';
  }
  return process.env.BACKEND_URL || 'http://127.0.0.1:8765';
}

function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    return localStorage.getItem('token') || localStorage.getItem('auth_token') || null;
  } catch {
    return null;
  }
}

async function request<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const baseUrl = getBaseUrl();
  const url = endpoint.startsWith('http')
    ? endpoint
    : `${baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

  const headers = new Headers(options.headers || {});

  // Automatically inject JSON Content-Type if not set and body is present
  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  // Automatically inject Bearer token if not explicitly provided
  const token = getAuthToken();
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    let data: any = null;
    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      data = await res.json();
    } else if (contentType.includes('text/')) {
      data = await res.text();
    } else {
      // Blob / buffer / stream (e.g. PDF report download)
      data = await res.blob();
    }

    if (!res.ok) {
      const errorMsg =
        (data && typeof data === 'object' && (data.detail || data.message || data.error)) ||
        `HTTP ${res.status}: ${res.statusText || 'Request failed'}`;
      throw new ApiError(
        typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg),
        res.status,
        data
      );
    }

    return {
      data: data as T,
      status: res.status,
      ok: res.ok,
      headers: res.headers,
    };
  } catch (err: any) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(err?.message || 'Network request failed', 0, null);
  }
}

export const apiClient = {
  get: <T = any>(url: string, config?: RequestInit) =>
    request<T>(url, { method: 'GET', ...config }),

  post: <T = any>(url: string, body?: any, config?: RequestInit) =>
    request<T>(url, {
      method: 'POST',
      body: body !== undefined && !(body instanceof FormData) ? JSON.stringify(body) : body,
      ...config,
    }),

  put: <T = any>(url: string, body?: any, config?: RequestInit) =>
    request<T>(url, {
      method: 'PUT',
      body: body !== undefined && !(body instanceof FormData) ? JSON.stringify(body) : body,
      ...config,
    }),

  patch: <T = any>(url: string, body?: any, config?: RequestInit) =>
    request<T>(url, {
      method: 'PATCH',
      body: body !== undefined && !(body instanceof FormData) ? JSON.stringify(body) : body,
      ...config,
    }),

  delete: <T = any>(url: string, config?: RequestInit) =>
    request<T>(url, { method: 'DELETE', ...config }),
};
