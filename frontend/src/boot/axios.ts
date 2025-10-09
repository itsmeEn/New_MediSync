import { defineBoot } from '#q-app/wrappers';
import axios, { type AxiosInstance } from 'axios';
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

  // For web browsers, use the current hostname
  const host = window.location?.hostname || 'localhost';
  const webEndpoint = `http://${host}:8000/api`;
  return webEndpoint;
};

// Async endpoint testing for mobile optimization (called after boot)
export const optimizeEndpointForMobile = async (): Promise<void> => {
  const platform = getPlatformInfo();

  if (!platform.isCapacitor) {
    return; // Only optimize for mobile
  }

  const mobileEndpoints = [
    'http://172.20.29.202:8000/api',
    'http://10.0.2.2:8000/api',
    'http://192.168.55.101:8000/api',
    'http://192.168.1.100:8000/api',
    'http://localhost:8000/api',
  ];

  try {
    const workingEndpoint = await testMobileEndpoints(mobileEndpoints);
    if (workingEndpoint !== api.defaults.baseURL) {
      api.defaults.baseURL = workingEndpoint;
      localStorage.setItem('API_BASE_URL', workingEndpoint);
    }
  } catch {
    // Endpoint optimization failed silently
  }
};

// Test mobile endpoints for connectivity
const testMobileEndpoints = async (endpoints: string[]): Promise<string> => {
  for (const endpoint of endpoints) {
    try {
      // Quick connectivity test with short timeout
      const testResponse = await axios.get(`${endpoint}/users/profile/`, {
        timeout: 3000,
        validateStatus: () => true, // Accept any status for connectivity test
      });

      if (testResponse.status < 500) {
        return endpoint;
      }
    } catch {
      // Endpoint test failed silently
    }
  }

  // Fallback to first endpoint if none are reachable
  return endpoints[0] || 'http://localhost:8000/api';
};

// Create axios instance with platform-specific configuration
const timeoutConfig = getTimeoutConfig();
const api = axios.create({
  baseURL: resolveBaseURL(),
  timeout: timeoutConfig.timeout,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
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
  (error) => {
    return Promise.reject(new Error(error.message || 'Request failed'));
  },
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Do not attempt refresh on auth endpoints
    const url = originalRequest?.url || '';
    const isAuthEndpoint =
      url.includes('/users/login/') ||
      url.includes('/users/register/') ||
      url.includes('/users/forgot-password/') ||
      url.includes('/users/reset-password') ||
      url.includes('/users/token/refresh/');

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
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

          originalRequest.headers.Authorization = `Bearer ${access}`;
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

    return Promise.reject(new Error(error.message || 'Response failed'));
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
});

export { api };
