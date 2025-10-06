/**
 * Capacitor Boot File
 * Handles platform-specific initialization and core setup
 */

import { boot } from 'quasar/wrappers';
import { Capacitor } from '@capacitor/core';
import { getEnvironmentInfo } from '../utils/capacitorUtils';

// Platform-specific initialization
export default boot(() => {
  const envInfo = getEnvironmentInfo();

  console.log('🚀 Capacitor Boot - Environment Info:', envInfo);

  // Only initialize on native platforms
  if (envInfo.isNative) {
    initializeNativePlatform();
  }

  // Initialize web-specific features
  if (envInfo.isWeb) {
    initializeWebFeatures();
  }

  // Setup global error handlers
  setupGlobalErrorHandlers();

  console.log('✅ Capacitor Boot - Initialization complete');
});

/**
 * Initialize native platform
 */
function initializeNativePlatform(): void {
  console.log('🔌 Initializing native platform...');

  const platform = Capacitor.getPlatform();
  console.log(`📱 Running on ${platform} platform`);

  // Platform-specific initialization
  if (platform === 'ios') {
    console.log('🍎 iOS platform detected');
  } else if (platform === 'android') {
    console.log('🤖 Android platform detected');
  }

  console.log('✅ Native platform initialized');
}

/**
 * Initialize web-specific features
 */
function initializeWebFeatures(): void {
  console.log('🌐 Initializing web-specific features...');

  // Web-specific initialization
  // Add any web-only features here

  console.log('✅ Web features initialized');
}

/**
 * Setup global error handlers
 */
function setupGlobalErrorHandlers(): void {
  console.log('🛡️ Setting up global error handlers...');

  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.error('🚨 Unhandled promise rejection:', event.reason);

    // Prevent the default browser behavior
    event.preventDefault();
  });

  // Handle uncaught errors
  window.addEventListener('error', (event) => {
    console.error('🚨 Uncaught error:', event.error);
  });

  console.log('✅ Global error handlers configured');
}

/**
 * Utility function to check if running in development mode
 */
export function isDevelopment(): boolean {
  return process.env.NODE_ENV === 'development';
}

/**
 * Utility function to get platform-specific configuration
 */
export function getPlatformConfig() {
  const platform = Capacitor.getPlatform();
  const envInfo = getEnvironmentInfo();

  return {
    platform,
    isNative: envInfo.isNative,
    isWeb: envInfo.isWeb,
    isIOS: envInfo.isIOS,
    isAndroid: envInfo.isAndroid,
    isDev: isDevelopment(),
    isCapacitor: Capacitor.isNativePlatform(),
    plugins: {
      // Check for commonly available plugins
      available: [] as string[],
    },
  };
}

/**
 * Export platform info for use in other parts of the app
 */
export const platformInfo = getPlatformConfig();
