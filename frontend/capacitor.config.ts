import type { EnhancedCapacitorConfig } from './src/types/capacitor';
import { validateIOSConfig, validateAndroidConfig } from './src/utils/capacitorUtils';

const config: EnhancedCapacitorConfig = {
  appId: 'com.medisync.app',
  appName: 'MediSync',
  webDir: 'dist/spa',

  // Enhanced server configuration with proper type safety
  server: {
    hostname: 'localhost',
    androidScheme: 'https',
    iosScheme: 'capacitor',
    allowNavigation: [
      'http://localhost:8000',
      'http://172.20.29.202:8000',
      'http://192.168.55.101:8000',
      'http://192.168.1.100:8000',
      'http://10.0.2.2:8000',
    ],
    cleartext: true,
  },

  // Enhanced iOS configuration with comprehensive options
  ios: {
    scheme: 'MediSync',
    contentInset: 'never',
    scrollEnabled: true,
    allowsLinkPreview: false,
    loggingBehavior: 'debug',
    preferredContentMode: 'mobile',
    handleApplicationNotifications: true,
    webContentsDebuggingEnabled: true,
    initialFocus: true,
    limitsNavigationsToAppBoundDomains: false,
  },

  // Enhanced Android configuration with security and performance settings
  android: {
    allowMixedContent: true,
    webContentsDebuggingEnabled: true,
    captureInput: false,
    loggingBehavior: 'debug',
    initialFocus: true,
    minWebViewVersion: 60,
    useLegacyBridge: false,
    resolveServiceWorkerRequests: true,
    adjustMarginsForEdgeToEdge: 'auto',
  },

  // Enhanced plugin configuration with comprehensive settings
  plugins: {
    CapacitorHttp: {
      enabled: true,
    },
    SplashScreen: {
      launchShowDuration: 3000,
      launchAutoHide: true,
      launchFadeOutDuration: 300,
      backgroundColor: '#ffffff',
      androidSplashResourceName: 'splash',
      androidScaleType: 'CENTER_CROP',
      showSpinner: true,
      androidSpinnerStyle: 'large',
      iosSpinnerStyle: 'small',
      spinnerColor: '#007AFF',
      splashFullScreen: true,
      splashImmersive: true,
      useDialog: false,
    },
    Keyboard: {
      resize: 'body',
      style: 'light',
      resizeOnFullScreen: true,
    },
    StatusBar: {
      style: 'light',
      backgroundColor: '#007AFF',
      overlaysWebView: false,
    },
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },
    LocalNotifications: {
      smallIcon: 'ic_stat_icon_config_sample',
      iconColor: '#007AFF',
      sound: 'beep.wav',
    },
    Camera: {
      iosImageWillSave: true,
      iosImageSaveToGallery: false,
      androidImageSaveToGallery: false,
    },
  },

  // Global configuration
  loggingBehavior: 'debug',
  backgroundColor: '#ffffff',
  initialFocus: true,

  // Include essential plugins
  includePlugins: [
    '@capacitor/app',
    '@capacitor/haptics',
    '@capacitor/keyboard',
    '@capacitor/status-bar',
    '@capacitor/splash-screen',
    '@capacitor/network',
    '@capacitor/device',
    '@capacitor/camera',
    '@capacitor/filesystem',
    '@capacitor/preferences',
    '@capacitor/push-notifications',
    '@capacitor/local-notifications',
  ],
};

// Validate configurations
if (config.ios) {
  validateIOSConfig(config.ios);
}

if (config.android) {
  validateAndroidConfig(config.android);
}

export default config;
