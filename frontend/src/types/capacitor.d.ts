/**
 * Enhanced Capacitor Configuration Types
 * Extends the base CapacitorConfig with additional type safety and platform-specific options
 */

import type { CapacitorConfig as BaseCapacitorConfig } from '@capacitor/cli';

// Enhanced iOS Configuration with strict typing
export interface EnhancedIOSConfig {
  /** Custom path to the native iOS project */
  path?: string;

  /** iOS build scheme to use (usually matches your app's target in Xcode) */
  scheme?: string;

  /** User agent override for iOS WebView */
  overrideUserAgent?: string;

  /** String to append to the original user agent */
  appendUserAgent?: string;

  /** Background color of the WebView */
  backgroundColor?: string;

  /** Enable zooming within the WebView */
  zoomEnabled?: boolean;

  /** Configure scroll view's content inset adjustment behavior */
  contentInset?: 'automatic' | 'scrollableAxes' | 'never' | 'always';

  /** Configure whether the scroll view is scrollable */
  scrollEnabled?: boolean;

  /** Custom linker flags for compiling Cordova plugins */
  cordovaLinkerFlags?: string[];

  /** Allow destination previews when pressing on links */
  allowsLinkPreview?: boolean;

  /** Logging behavior for iOS builds */
  loggingBehavior?: 'none' | 'debug' | 'production';

  /** Allowlist of plugins to include during sync */
  includePlugins?: string[];

  /** Limits navigations to app-bound domains */
  limitsNavigationsToAppBoundDomains?: boolean;

  /** Content mode for the web view */
  preferredContentMode?: 'recommended' | 'desktop' | 'mobile';

  /** Handle local/push notifications */
  handleApplicationNotifications?: boolean;

  /** Enable debuggable web content for release builds */
  webContentsDebuggingEnabled?: boolean;

  /** Whether to give the webview initial focus */
  initialFocus?: boolean;

  /** Build options for iOS */
  buildOptions?: {
    /** Signing style for distribution builds */
    signingStyle?: 'automatic' | 'manual';
    /** Export method for xcodebuild */
    exportMethod?: 'app-store-connect' | 'ad-hoc' | 'enterprise' | 'development';
    /** Certificate for signing */
    signingCertificate?: string;
    /** Provisioning profile */
    provisioningProfile?: string;
  };
}

// Enhanced Android Configuration
export interface EnhancedAndroidConfig {
  /** Custom path to the native Android project */
  path?: string;

  /** User agent override for Android WebView */
  overrideUserAgent?: string;

  /** String to append to the original user agent */
  appendUserAgent?: string;

  /** Background color of the WebView */
  backgroundColor?: string;

  /** Enable zooming within the WebView */
  zoomEnabled?: boolean;

  /** Enable mixed content (development only) */
  allowMixedContent?: boolean;

  /** Enable simpler keyboard with limitations */
  captureInput?: boolean;

  /** Always enable debuggable web content */
  webContentsDebuggingEnabled?: boolean;

  /** Logging behavior for Android builds */
  loggingBehavior?: 'none' | 'debug' | 'production';

  /** Allowlist of plugins to include during sync */
  includePlugins?: string[];

  /** Android flavor to use */
  flavor?: string;

  /** Whether to give the webview initial focus */
  initialFocus?: boolean;

  /** Minimum supported WebView version */
  minWebViewVersion?: number;

  /** Minimum supported Huawei WebView version */
  minHuaweiWebViewVersion?: number;

  /** Build options for Android */
  buildOptions?: {
    keystorePath?: string;
    keystorePassword?: string;
    keystoreAlias?: string;
    keystoreAliasPassword?: string;
    releaseType?: 'AAB' | 'APK';
    signingType?: 'apksigner' | 'jarsigner';
  };

  /** Use legacy JavaScript interface */
  useLegacyBridge?: boolean;

  /** Handle service worker requests through Capacitor bridge */
  resolveServiceWorkerRequests?: boolean;

  /** Adjust margins for edge-to-edge display */
  adjustMarginsForEdgeToEdge?: 'auto' | 'force' | 'disable';
}

// Enhanced Server Configuration
export interface EnhancedServerConfig {
  /** Local hostname of the device */
  hostname?: string;

  /** Local scheme on iOS */
  iosScheme?: string;

  /** Local scheme on Android */
  androidScheme?: string;

  /** URL to load the app from */
  url?: string;

  /** Clear session data on app restart */
  cleartext?: boolean;

  /** Allow navigation to external URLs */
  allowNavigation?: string[];

  /** Error page path */
  errorPath?: string;
}

// Enhanced Plugin Configuration
export interface EnhancedPluginsConfig {
  /** Capacitor HTTP plugin configuration */
  CapacitorHttp?: {
    enabled?: boolean;
  };

  /** Splash Screen plugin configuration */
  SplashScreen?: {
    launchShowDuration?: number;
    launchAutoHide?: boolean;
    launchFadeOutDuration?: number;
    backgroundColor?: string;
    androidSplashResourceName?: string;
    androidScaleType?: 'CENTER_CROP' | 'CENTER_INSIDE' | 'FIT_XY';
    showSpinner?: boolean;
    androidSpinnerStyle?: 'large' | 'small' | 'large_inverse' | 'small_inverse';
    iosSpinnerStyle?: 'large' | 'small';
    spinnerColor?: string;
    splashFullScreen?: boolean;
    splashImmersive?: boolean;
    layoutName?: string;
    useDialog?: boolean;
  };

  /** Keyboard plugin configuration */
  Keyboard?: {
    resize?: 'body' | 'ionic' | 'native';
    style?: 'dark' | 'light';
    resizeOnFullScreen?: boolean;
  };

  /** Status Bar plugin configuration */
  StatusBar?: {
    style?: 'light' | 'dark' | 'default';
    backgroundColor?: string;
    overlaysWebView?: boolean;
  };

  /** Push Notifications plugin configuration */
  PushNotifications?: {
    presentationOptions?: ('badge' | 'sound' | 'alert')[];
  };

  /** Local Notifications plugin configuration */
  LocalNotifications?: {
    smallIcon?: string;
    iconColor?: string;
    sound?: string;
  };

  /** Camera plugin configuration */
  Camera?: {
    iosImageWillSave?: boolean;
    iosImageSaveToGallery?: boolean;
    androidImageSaveToGallery?: boolean;
  };

  /** Device plugin configuration */
  Device?: {
    iosCustomUserAgent?: string;
    androidCustomUserAgent?: string;
  };

  /** Network plugin configuration */
  Network?: {
    iosCustomUserAgent?: string;
    androidCustomUserAgent?: string;
  };
}

// Main Enhanced Capacitor Configuration
export interface EnhancedCapacitorConfig
  extends Omit<BaseCapacitorConfig, 'ios' | 'android' | 'server' | 'plugins'> {
  /** Enhanced iOS configuration */
  ios?: EnhancedIOSConfig;

  /** Enhanced Android configuration */
  android?: EnhancedAndroidConfig;

  /** Enhanced server configuration */
  server?: EnhancedServerConfig;

  /** Enhanced plugins configuration */
  plugins?: EnhancedPluginsConfig;

  /** Include plugins allowlist */
  includePlugins?: string[];

  /** Cordova preferences */
  cordova?: {
    preferences?: Record<string, string>;
    staticPlugins?: string[];
  };

  /** Build configuration */
  build?: {
    /** Development server configuration */
    dev?: {
      watchers?: {
        ignored?: string[];
      };
    };
  };
}

// Type guards for runtime validation
export declare const isIOSPlatform: (platform: string) => boolean;
export declare const isAndroidPlatform: (platform: string) => boolean;
export declare const isWebPlatform: (platform: string) => boolean;
export declare const isNativePlatform: (platform: string) => boolean;

// Configuration validation helpers
export declare const validateIOSConfig: (config: EnhancedIOSConfig) => boolean;
export declare const validateAndroidConfig: (config: EnhancedAndroidConfig) => boolean;

// Export the enhanced configuration type as default
export type { EnhancedCapacitorConfig as CapacitorConfig };
