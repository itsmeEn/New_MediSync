<template>
  <div v-if="props.showDebug" class="mobile-debug-panel">
    <q-card class="debug-card">
      <q-card-section>
        <div class="text-h6">Mobile Login Debug Info</div>
        <div class="text-caption">
          Platform: {{ isMobile ? 'Mobile (Capacitor)' : 'Web Browser' }}
        </div>
      </q-card-section>

      <q-card-section>
        <div class="debug-section">
          <div class="debug-label">API Base URL:</div>
          <div class="debug-value">{{ apiBaseUrl }}</div>
        </div>

        <div class="debug-section">
          <div class="debug-label">Network Status:</div>
          <div
            class="debug-value"
            :class="{ 'text-positive': isOnline, 'text-negative': !isOnline }"
          >
            {{ isOnline ? 'Online' : 'Offline' }}
          </div>
        </div>

        <div class="debug-section">
          <div class="debug-label">User Agent:</div>
          <div class="debug-value debug-small">{{ userAgent }}</div>
        </div>

        <div class="debug-section">
          <div class="debug-label">Connectivity Tests:</div>
          <div class="debug-value">
            <q-btn
              v-if="!connectivityTested"
              size="sm"
              color="primary"
              @click="testConnectivity"
              :loading="testingConnectivity"
            >
              Test Connectivity
            </q-btn>
            <div v-else>
              <div
                v-for="result in connectivityResults"
                :key="result.endpoint"
                class="connectivity-result"
              >
                <q-icon
                  :name="result.success ? 'check_circle' : 'error'"
                  :color="result.success ? 'positive' : 'negative'"
                  size="sm"
                />
                <span class="q-ml-sm">{{ result.endpoint }}</span>
                <span class="text-caption q-ml-sm">({{ result.responseTime }}ms)</span>
              </div>
            </div>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Copy Debug Info" @click="copyDebugInfo" />
        <q-btn flat label="Close" @click="emit('close')" />
      </q-card-actions>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { api } from '../boot/axios';
import { findBestEndpoint, getNetworkInfo } from '../utils/mobileConnectivity';

interface ConnectivityResult {
  success: boolean;
  endpoint: string;
  responseTime?: number;
  error?: string;
}

const props = defineProps<{
  showDebug: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const $q = useQuasar();

const connectivityTested = ref(false);
const testingConnectivity = ref(false);
const connectivityResults = ref<ConnectivityResult[]>([]);

const isMobile = computed(() => !!(window as { Capacitor?: unknown }).Capacitor);
const isOnline = computed(() => navigator.onLine);
const apiBaseUrl = computed(() => api.defaults.baseURL);
const userAgent = computed(() => navigator.userAgent);

const testConnectivity = async () => {
  testingConnectivity.value = true;
  connectivityTested.value = true;

  try {
    const result = await findBestEndpoint();
    if (result) {
      connectivityResults.value = [result];
    } else {
      connectivityResults.value = [];
      $q.notify({
        type: 'negative',
        message: 'No working endpoints found',
        caption: 'Check your network connection and server status',
      });
    }
  } catch (error) {
    console.error('Connectivity test failed:', error);
    $q.notify({
      type: 'negative',
      message: 'Connectivity test failed',
      caption: error instanceof Error ? error.message : 'Unknown error',
    });
  } finally {
    testingConnectivity.value = false;
  }
};

const copyDebugInfo = () => {
  const debugInfo = {
    platform: isMobile.value ? 'Mobile (Capacitor)' : 'Web Browser',
    apiBaseUrl: apiBaseUrl.value,
    networkStatus: isOnline.value ? 'Online' : 'Offline',
    userAgent: userAgent.value,
    connectivityResults: connectivityResults.value,
    timestamp: new Date().toISOString(),
    networkInfo: getNetworkInfo(),
  };

  const debugString = JSON.stringify(debugInfo, null, 2);

  navigator.clipboard
    .writeText(debugString)
    .then(() => {
      $q.notify({
        type: 'positive',
        message: 'Debug info copied to clipboard',
        timeout: 2000,
      });
    })
    .catch((error) => {
      console.error('Failed to copy debug info:', error);
      $q.notify({
        type: 'negative',
        message: 'Failed to copy debug info',
        timeout: 2000,
      });
    });
};

onMounted(() => {
  if (isMobile.value) {
    console.log('📱 Mobile debug panel mounted');
  }
});
</script>

<style scoped>
.mobile-debug-panel {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.debug-card {
  max-width: 500px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
}

.debug-section {
  margin-bottom: 16px;
}

.debug-label {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.debug-value {
  color: #666;
  word-break: break-all;
}

.debug-small {
  font-size: 12px;
}

.connectivity-result {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

@media (max-width: 768px) {
  .mobile-debug-panel {
    padding: 10px;
  }

  .debug-card {
    max-height: 90vh;
  }
}
</style>
