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
    localStorage.removeItem('role');
    localStorage.removeItem('profile_picture');
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
    // No need to delete a top-level Authorization; axios uses common/method-specific headers
  } catch {
    // Non-blocking: header reset failures shouldn't stop logout
  }

  // Prefer in-app navigation with safe fallbacks
  try {
    await router.replace('/login');
  } catch {
    // Fallback based on router mode
    const mode = process.env.VUE_ROUTER_MODE;
    if (mode === 'hash') {
      try {
        // Ensure hash-mode navigation even if router instance is not available
        window.location.hash = '#/login';
      } catch {
        window.location.href = '/#/login';
      }
    } else {
      try {
        window.location.assign('/login');
      } catch {
        window.location.href = '/login';
      }
    }
  }
}