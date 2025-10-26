<template>
  <div class="hospital-selection">
    <label for="hospital_select">Select Your Affiliated Hospital *</label>
    <div class="select-wrapper">
      <select
        id="hospital_select"
        :disabled="loading"
        v-model="internalValue"
        required
        @change="onSelect"
      >
        <option value="">Select hospital</option>
        <option v-for="h in hospitals" :key="h.id" :value="h.id">
          {{ h.official_name }} — {{ h.address }}
        </option>
      </select>
      <span v-if="loading" class="loading-indicator">Loading hospitals…</span>
    </div>
    <small v-if="errorText" class="error-text">{{ errorText }}</small>
    <small v-if="successText" class="success-text">{{ successText }}</small>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { api } from '../boot/axios';
import type { AxiosResponse } from 'axios';

/**
 * HospitalSelection component
 * - Always fetches active hospitals from public endpoint
 * - Provides loading indicator, error messaging, and immediate feedback upon selection
 * - Persists selected hospital via localStorage and exposes v-model for parent integration
 */

interface HospitalItem { id: number; official_name: string; address: string }

const props = defineProps<{ modelValue: string | number }>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void;
  (e: 'loaded', hospitals: HospitalItem[]): void;
}>();

const $q = useQuasar();
const hospitals = ref<HospitalItem[]>([]);
const loading = ref(false);
const errorText = ref('');
const successText = ref('');
const internalValue = ref<string | number>(props.modelValue ?? '');

const LOCAL_STORAGE_KEY = 'selected_hospital_id';

const fetchHospitals = async () => {
  errorText.value = '';
  successText.value = '';
  loading.value = true;

  try {
    const endpoint = '/admin/hospitals/';
    const { executeWithRetry, classifyError } = await import('../utils/asyncErrorHandler');
    const result = await executeWithRetry(() =>
      api.get(endpoint, { params: { status: 'active' } }),
    );

    if (result.success) {
      type HospitalsListResponse = { hospitals: HospitalItem[] };
      const resp = result.data as AxiosResponse<HospitalsListResponse> | undefined;
      const items = resp?.data?.hospitals ?? [];

      // Validate, deduplicate by id, and sort by official_name
      const byId = new Map<number, HospitalItem>();
      for (const h of items) {
        if (!h) continue;
        const valid = typeof h.id === 'number' && typeof h.official_name === 'string' && typeof h.address === 'string';
        if (!valid) continue;
        if (!byId.has(h.id)) byId.set(h.id, h);
      }
      hospitals.value = Array.from(byId.values()).sort((a, b) => a.official_name.localeCompare(b.official_name));

      emit('loaded', hospitals.value);

      if (!hospitals.value.length) {
        errorText.value = 'No active hospitals found. Please try again later.';
      } else {
        successText.value = `Loaded ${hospitals.value.length} hospital${hospitals.value.length > 1 ? 's' : ''}.`;
        // Restore persisted selection if present
        const persisted = localStorage.getItem(LOCAL_STORAGE_KEY);
        if (persisted && !internalValue.value) {
          internalValue.value = Number(persisted);
          emit('update:modelValue', internalValue.value);
        }
      }
    } else {
      const err = result.error || classifyError(new Error('Unknown error'));
      console.error('[HospitalSelection] Failed to load hospitals', err);
      errorText.value = 'Failed to load hospitals. Please retry.';
    }
  } catch (e) {
    console.error('[HospitalSelection] Unexpected error while loading hospitals', e);
    errorText.value = 'Failed to load hospitals. Please retry.';
  } finally {
    loading.value = false;
  }
};

const onSelect = () => {
  successText.value = '';
  if (!internalValue.value) {
    errorText.value = 'Please select your hospital.';
    return;
  }
  localStorage.setItem(LOCAL_STORAGE_KEY, String(internalValue.value));
  emit('update:modelValue', internalValue.value);
  $q.notify({ type: 'positive', message: 'Hospital selected.' });
  successText.value = 'Selection saved.';
};

watch(() => props.modelValue, (v) => { internalValue.value = v ?? ''; });

onMounted(fetchHospitals);
</script>

<style scoped>
.hospital-selection { margin-bottom: 20px; }
.select-wrapper { position: relative; }
.loading-indicator { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); font-size: 12px; color: #666; }
.error-text { color: #e74c3c; }
.success-text { color: #27ae60; }
</style>