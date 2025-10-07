/**
 * Capacitor Configuration Utilities
 * Implementation of type guards and validation helpers
 */

import type { EnhancedIOSConfig, EnhancedAndroidConfig } from '../types/capacitor';

// Extend Window interface to include Capacitor
declare global {
  interface Window {
    Capacitor?: {
      getPlatform: () => string;
      isPluginAvailable: (name: string) => boolean;
      isNativePlatform: () => boolean;
    };
  }
}

// Type guards for runtime validation
export const isIOSPlatform = (platform: string): boolean => platform === 'ios';

export const isAndroidPlatform = (platform: string): boolean => platform === 'android';

export const isWebPlatform = (platform: string): boolean => platform === 'web';

export const isNativePlatform = (platform: string): boolean =>
  isIOSPlatform(platform) || isAndroidPlatform(platform);

// Configuration validation helpers
export const validateIOSConfig = (config: EnhancedIOSConfig): boolean => {
  if (
    config.contentInset &&
    !['automatic', 'scrollableAxes', 'never', 'always'].includes(config.contentInset)
  ) {
    console.warn(`Invalid iOS contentInset value: ${config.contentInset}`);
    return false;
  }

  if (
    config.preferredContentMode &&
    !['recommended', 'desktop', 'mobile'].includes(config.preferredContentMode)
  ) {
    console.warn(`Invalid iOS preferredContentMode value: ${config.preferredContentMode}`);
    return false;
  }

  if (config.loggingBehavior && !['none', 'debug', 'production'].includes(config.loggingBehavior)) {
    console.warn(`Invalid iOS loggingBehavior value: ${config.loggingBehavior}`);
    return false;
  }

  if (
    config.buildOptions?.signingStyle &&
    !['automatic', 'manual'].includes(config.buildOptions.signingStyle)
  ) {
    console.warn(`Invalid iOS signingStyle value: ${config.buildOptions.signingStyle}`);
    return false;
  }

  return true;
};

export const validateAndroidConfig = (config: EnhancedAndroidConfig): boolean => {
  if (config.minWebViewVersion && config.minWebViewVersion < 55) {
    console.warn(`Android minWebViewVersion must be at least 55, got: ${config.minWebViewVersion}`);
    return false;
  }

  if (config.minHuaweiWebViewVersion && config.minHuaweiWebViewVersion < 10) {
    console.warn(
      `Android minHuaweiWebViewVersion must be at least 10, got: ${config.minHuaweiWebViewVersion}`,
    );
    return false;
  }

  if (
    config.buildOptions?.releaseType &&
    !['AAB', 'APK'].includes(config.buildOptions.releaseType)
  ) {
    console.warn(`Invalid Android releaseType value: ${config.buildOptions.releaseType}`);
    return false;
  }

  if (
    config.buildOptions?.signingType &&
    !['apksigner', 'jarsigner'].includes(config.buildOptions.signingType)
  ) {
    console.warn(`Invalid Android signingType value: ${config.buildOptions.signingType}`);
    return false;
  }

  if (
    config.adjustMarginsForEdgeToEdge &&
    !['auto', 'force', 'disable'].includes(config.adjustMarginsForEdgeToEdge)
  ) {
    console.warn(
      `Invalid Android adjustMarginsForEdgeToEdge value: ${config.adjustMarginsForEdgeToEdge}`,
    );
    return false;
  }

  if (config.loggingBehavior && !['none', 'debug', 'production'].includes(config.loggingBehavior)) {
    console.warn(`Invalid Android loggingBehavior value: ${config.loggingBehavior}`);
    return false;
  }

  return true;
};

// Platform detection utilities
export const getCurrentPlatform = (): string => {
  if (typeof window !== 'undefined') {
    // Check if running in Capacitor
    if (window.Capacitor) {
      return window.Capacitor.getPlatform();
    }
    // Fallback to web
    return 'web';
  }
  // Server-side or Node.js environment
  return 'unknown';
};

// Configuration merger utility
export const mergeCapacitorConfig = <T extends Record<string, unknown>>(
  baseConfig: T,
  platformConfig: Partial<T>,
): T => {
  // Simple merge for most properties
  const merged = {
    ...baseConfig,
    ...platformConfig,
  };

  // Handle plugins separately if both configs have them
  if (
    'plugins' in baseConfig &&
    'plugins' in platformConfig &&
    baseConfig.plugins &&
    platformConfig.plugins &&
    typeof baseConfig.plugins === 'object' &&
    typeof platformConfig.plugins === 'object'
  ) {
    return {
      ...merged,
      plugins: {
        ...(baseConfig.plugins as Record<string, unknown>),
        ...(platformConfig.plugins as Record<string, unknown>),
      },
    } as T;
  }

  return merged as T;
};

// Plugin availability checker
export const isPluginAvailable = (pluginName: string): boolean => {
  if (typeof window !== 'undefined' && window.Capacitor) {
    return window.Capacitor.isPluginAvailable(pluginName);
  }
  return false;
};

// Safe plugin execution wrapper
export const executePluginSafely = async <T>(
  pluginName: string,
  operation: () => Promise<T>,
  fallback?: () => Promise<T>,
): Promise<T | null> => {
  try {
    if (isPluginAvailable(pluginName)) {
      return await operation();
    } else if (fallback) {
      console.warn(`Plugin ${pluginName} not available, using fallback`);
      return await fallback();
    } else {
      console.warn(`Plugin ${pluginName} not available and no fallback provided`);
      return null;
    }
  } catch (error) {
    console.error(`Error executing plugin ${pluginName}:`, error);
    if (fallback) {
      try {
        return await fallback();
      } catch (fallbackError) {
        console.error(`Fallback also failed for plugin ${pluginName}:`, fallbackError);
        return null;
      }
    }
    return null;
  }
};

// Environment detection
export const getEnvironmentInfo = () => {
  const platform = getCurrentPlatform();
  const isNative = isNativePlatform(platform);
  const isWeb = isWebPlatform(platform);

  return {
    platform,
    isNative,
    isWeb,
    isIOS: isIOSPlatform(platform),
    isAndroid: isAndroidPlatform(platform),
    isCapacitor: typeof window !== 'undefined' && !!window.Capacitor,
    userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
  };
};
