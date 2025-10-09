/**
 * Mobile Connectivity Utilities
 * Handles network testing and endpoint discovery for mobile devices
 */

import { api } from '../boot/axios';

export interface ConnectivityTestResult {
  success: boolean;
  endpoint: string;
  error?: string;
  responseTime?: number;
}

export interface MobileEndpoint {
  url: string;
  description: string;
  priority: number;
}

/**
 * Common mobile endpoints to test
 */
const MOBILE_ENDPOINTS: MobileEndpoint[] = [
  {
    url: 'http://172.20.29.202:8000/api',
    description: 'Current network IP (172.20.29.202)',
    priority: 1,
  },
  {
    url: 'http://10.0.2.2:8000/api',
    description: 'Android emulator host',
    priority: 2,
  },
  {
    url: 'http://192.168.55.101:8000/api',
    description: 'Alternative development IP (192.168.55.101)',
    priority: 3,
  },
  {
    url: 'http://192.168.1.100:8000/api',
    description: 'Alternative common IP (192.168.1.100)',
    priority: 4,
  },
  {
    url: 'http://localhost:8000/api',
    description: 'Localhost fallback',
    priority: 5,
  },
];

/**
 * Test connectivity to a specific endpoint
 */
export async function testEndpoint(endpoint: string): Promise<ConnectivityTestResult> {
  const startTime = Date.now();

  try {
    // Create a temporary axios instance for testing
    const testApi = api.create({
      baseURL: endpoint,
      timeout: 5000, // 5 second timeout
    });

    // Test with a simple GET request to an existing endpoint
    await testApi.get('/users/profile/', {
      validateStatus: (status) => status < 500, // Accept any status < 500 as working
    });
    const responseTime = Date.now() - startTime;

    console.log(`✅ Endpoint ${endpoint} is reachable (${responseTime}ms)`);

    return {
      success: true,
      endpoint,
      responseTime,
    };
  } catch (error) {
    const responseTime = Date.now() - startTime;
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';

    console.log(`❌ Endpoint ${endpoint} failed (${responseTime}ms): ${errorMessage}`);

    return {
      success: false,
      endpoint,
      error: errorMessage,
      responseTime,
    };
  }
}

/**
 * Find the best working endpoint for mobile devices
 */
export async function findBestEndpoint(): Promise<ConnectivityTestResult | null> {
  console.log('🔍 Testing mobile connectivity to find best endpoint...');

  // Sort endpoints by priority
  const sortedEndpoints = [...MOBILE_ENDPOINTS].sort((a, b) => a.priority - b.priority);

  for (const endpointConfig of sortedEndpoints) {
    console.log(`🧪 Testing ${endpointConfig.description}: ${endpointConfig.url}`);

    const result = await testEndpoint(endpointConfig.url);

    if (result.success) {
      console.log(`🎯 Found working endpoint: ${endpointConfig.url}`);
      return result;
    }
  }

  console.log('❌ No working endpoints found');
  return null;
}

/**
 * Update the global API base URL to the best working endpoint
 */
export async function updateApiEndpoint(): Promise<boolean> {
  const isMobile = !!(window as { Capacitor?: unknown }).Capacitor;

  if (!isMobile) {
    console.log('🌐 Web browser detected, skipping mobile endpoint discovery');
    return true;
  }

  const bestEndpoint = await findBestEndpoint();

  if (bestEndpoint) {
    api.defaults.baseURL = bestEndpoint.endpoint;
    console.log(`🔄 Updated API base URL to: ${bestEndpoint.endpoint}`);
    return true;
  }

  return false;
}

/**
 * Check if device is online
 */
export function isOnline(): boolean {
  return navigator.onLine;
}

/**
 * Get network connection info for debugging
 */
export function getNetworkInfo(): Record<string, unknown> {
  const isMobile = !!(window as { Capacitor?: unknown }).Capacitor;

  return {
    platform: isMobile ? 'Mobile (Capacitor)' : 'Web Browser',
    online: isOnline(),
    userAgent: navigator.userAgent,
    currentEndpoint: api.defaults.baseURL,
    timestamp: new Date().toISOString(),
  };
}
