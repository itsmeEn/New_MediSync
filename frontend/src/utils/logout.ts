import type { Router } from 'vue-router';
import { api } from 'boot/axios';

/**
 * Perform a robust logout:
 * - Clear auth-related storage
 * - Reset axios auth header and baseURL override
 * - Navigate to login with a safe fallback
 */
export async function performLogout(router: Router): Promise<void> {
  // Clear tokens and user info
  try {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    // Remove any persisted API base override (will be re-optimized on boot)
    localStorage.removeItem('API_BASE_URL');
  } catch {
    // Non-blocking: storage clearing failures shouldn't stop logout
  }

  // Clear axios auth header to avoid stale state
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api.defaults.headers as any).common = {
      ...(api.defaults.headers?.common || {}),
      Authorization: undefined,
    };
  } catch {
    // Non-blocking: header reset failures shouldn't stop logout
  }

  // Prefer in-app navigation with safe fallbacks
  try {
    await router.replace('/login');
  } catch {
    try {
      window.location.assign('/login');
    } catch {
      window.location.href = '/login';
    }
  }
}