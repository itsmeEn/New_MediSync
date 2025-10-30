import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.medisync.app',
  appName: 'MediSync Frontend',
  webDir: 'dist/spa',
  server: {
    androidScheme: 'https',
  },
};

export default config;