import { defineBoot } from '#q-app/wrappers';
import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { getPlatformInfo, getTimeoutConfig } from 'src/utils/asyncErrorHandler';

declare module 'vue' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
    $api: AxiosInstance;
  }
}

// Initial endpoint resolution (synchronous for boot)
const resolveBaseURL = (): string => {
  const override = localStorage.getItem('API_BASE_URL');
  if (override) {
    return override.replace(/\/$/, '');
  }

  const platform = getPlatformInfo();

  if (platform.isCapacitor) {
    // For mobile devices, use primary endpoint initially
    const mobileEndpoints = [
      'http://172.20.29.202:8000/api', // Current network IP
      'http://10.0.2.2:8000/api', // Android emulator
      'http://192.168.55.101:8000/api', // Alternative development IP
      'http://192.168.1.100:8000/api', // Alternative common IP
      'http://localhost:8000/api', // Fallback
    ];

    return mobileEndpoints[0] || 'http://localhost:8000/api';
  }

  // For web browsers, use the current hostname and adjust port during dev
  const host = window.location?.hostname || 'localhost';
  const frontPort = window.location?.port || '';
  // If running on a dev port (non-empty), prefer backend 8001; otherwise 8000
  const backendPort = frontPort ? '8001' : '8000';
  const webEndpoint = `http://${host}:${backendPort}/api`;
  return webEndpoint;
};

// Connectivity test helper: probes a stable PUBLIC or auth endpoint and treats 404 as NOT reachable
const testConnectivity = async (endpoint: string): Promise<boolean> => {
  try {
    // Probe the login endpoint with GET; it should respond 405 (Method Not Allowed)
    // This avoids generating 401 Unauthorized logs from protected resources.
    const probeUrl = `${endpoint}/users/login/`;
    const testResponse = await axios.get(probeUrl, {
      // Use a short timeout to avoid hanging when port is closed
      timeout: 2500,
      validateStatus: () => true,
    });
    // Consider 2xx, 401, 403, 405 as reachable; 404 means wrong baseURL
    return (
      (testResponse.status >= 200 && testResponse.status < 300) ||
      testResponse.status === 401 ||
      testResponse.status === 403 ||
      testResponse.status === 405
    );
  } catch {
    // Network errors (like ECONNREFUSED) will land here
    return false;
  }
};

// Mobile endpoints to probe when running under Capacitor
const MOBILE_ENDPOINTS = [
  'http://172.20.29.202:8000/api', // Current network IP
  'http://10.0.2.2:8000/api', // Android emulator
  'http://192.168.55.101:8000/api', // Alternative development IP
  'http://192.168.1.100:8000/api', // Alternative common IP
  'http://localhost:8000/api', // Fallback
];

// Web fallback testing: prefer :8001, fall back to :8000 if unreachable
const resolveWebEndpointWithFallback = async (): Promise<string> => {
  const host = window.location?.hostname || 'localhost';
  const frontPort = window.location?.port || '';
  const primary = `http://${host}:${frontPort ? '8001' : '8000'}/api`;
  const fallback = `http://${host}:8000/api`;

  // If primary is already :8000 (non-dev), return it directly
  if (!frontPort) {
    return primary;
  }

  // Test :8001, then fallback to :8000
  const okPrimary = await testConnectivity(primary);
  if (okPrimary) {
    return primary;
  }
  const okFallback = await testConnectivity(fallback);
  if (okFallback) {
    return fallback;
  }
  // As last resort, return primary to avoid undefined baseURL
  return primary;
};

// Test a list of mobile endpoints and pick the first reachable
const resolveMobileEndpointWithFallback = async (): Promise<string> => {
  for (const endpoint of MOBILE_ENDPOINTS) {
    const ok = await testConnectivity(endpoint);
    if (ok) {
      return endpoint;
    }
  }
  return MOBILE_ENDPOINTS[0] || 'http://localhost:8000/api';
};

// Unified async optimizer: works for both web and mobile
export const optimizeEndpoint = async (): Promise<void> => {
  const platform = getPlatformInfo();

  try {
    let workingEndpoint: string | null = null;

    if (platform.isCapacitor) {
      workingEndpoint = await resolveMobileEndpointWithFallback();
    } else {
      workingEndpoint = await resolveWebEndpointWithFallback();
    }

    if (workingEndpoint && workingEndpoint !== api.defaults.baseURL) {
      api.defaults.baseURL = workingEndpoint;
      localStorage.setItem('API_BASE_URL', workingEndpoint);
      console.log('API base URL optimized to:', workingEndpoint);
    }
  } catch (e) {
    // Fail silently to avoid blocking app startup
    console.warn('Endpoint optimization failed:', e);
  }
};

// Create axios instance with platform-specific configuration
const timeoutConfig = getTimeoutConfig();
const api = axios.create({
  baseURL: resolveBaseURL(),
  timeout: timeoutConfig.timeout,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');

    // Avoid attaching tokens to auth-related endpoints
    const url = config.url || '';
    const isAuthEndpoint =
      url.includes('/users/login/') ||
      url.includes('/users/register/') ||
      url.includes('/users/forgot-password/') ||
      url.includes('/users/reset-password') ||
      url.includes('/users/token/refresh/');

    if (token && !isAuthEndpoint) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Adding auth token to request:', config.url);
    } else if (!token) {
      console.warn('No access token found for request:', config.url);
    } else if (isAuthEndpoint) {
      console.log('Skipping auth header for auth endpoint:', config.url);
    }

    return config;
  },
  (error: Error) => {
    // Preserve original Axios error to keep response/details for downstream handlers
    return Promise.reject(error);
  },
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

    // Do not attempt refresh on auth endpoints
    const url = originalRequest?.url || '';
    const isAuthEndpoint =
      url.includes('/users/login/') ||
      url.includes('/users/register/') ||
      url.includes('/users/forgot-password/') ||
      url.includes('/users/reset-password') ||
      url.includes('/users/token/refresh/');

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !isAuthEndpoint) {
      console.log('401 Unauthorized detected, attempting token refresh...');
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          console.log('Attempting to refresh token...');
          const response = await axios.post(`${api.defaults.baseURL}/users/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);
          console.log('Token refreshed successfully');

          // Retry the original request; request interceptor will attach the new token
          return api(originalRequest);
        } else {
          console.warn('No refresh token found');
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // Refresh token failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      }

    // Preserve original Axios error so callers can inspect status and response body
    return Promise.reject(error);
  },
);

export default defineBoot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
  // ^ ^ ^ this will allow to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API

  // Kick off async endpoint optimization and fallback logic
  // This runs after boot without requiring user interaction
  void optimizeEndpoint();
});

export { api };
