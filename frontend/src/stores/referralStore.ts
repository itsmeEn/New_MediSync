import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';

// Helper to safely read error detail from Axios-like errors
interface AxiosErrorLike { response?: { data?: { detail?: string } } }
const getErrorDetail = (err: unknown): string | undefined =>
  (err as AxiosErrorLike)?.response?.data?.detail;

export type UrgencyLevel = 'low' | 'medium' | 'high' | 'critical';

export interface PatientBrief {
  id: number;
  full_name: string;
  hospital?: string;
  department?: string;
}

export interface DoctorBrief {
  id: number;
  full_name: string;
  specialization?: string;
  hospital?: string;
  department?: string;
  is_available?: boolean;
  next_available_time?: string | null;
}

export interface ReferralFilters {
  specialization?: string;
  hospital?: string;
  department?: string;
}

export interface CreateReferralPayload {
  patient_id: number;
  doctor_id: number;
  urgency: UrgencyLevel;
  notes?: string;
}

export const useReferralStore = defineStore('referrals', () => {
  // Core state
  const selectedPatient = ref<PatientBrief | null>(null);
  const selectedDoctor = ref<DoctorBrief | null>(null);
  const filters = ref<ReferralFilters>({});

  // Listing and statuses
  const availableDoctors = ref<DoctorBrief[]>([]);
  const loadingDoctors = ref(false);
  const sendingReferral = ref(false);
  const error = ref<string | null>(null);
  const referralStatus = ref<'idle' | 'queued' | 'sent' | 'failed'>('idle');

  // Derived
  const readyToRefer = computed(
    () => !!selectedPatient.value && !!selectedDoctor.value,
  );

  const setPatient = (patient: PatientBrief | null) => {
    selectedPatient.value = patient;
  };

  const setFilters = (next: ReferralFilters) => {
    filters.value = { ...filters.value, ...next };
  };

  const clearDoctorSelection = () => {
    selectedDoctor.value = null;
  };

  const loadAvailableDoctors = async () => {
    loadingDoctors.value = true;
    error.value = null;
    try {
      const params: Record<string, string> = {};
      if (filters.value.specialization) params.specialization = filters.value.specialization;
      if (filters.value.hospital) params.hospital = filters.value.hospital;
      if (filters.value.department) params.department = filters.value.department;

      // Real-time availability is surfaced via is_available and next_available_time
      const { data } = await api.get('/operations/referrals/available-doctors/', { params });
      availableDoctors.value = (data || []) as DoctorBrief[];
    } catch (e: unknown) {
      console.error('Failed to load available doctors', e);
      error.value = 'Failed to load available doctors';
      availableDoctors.value = [];
    } finally {
      loadingDoctors.value = false;
    }
  };

  const sendReferral = async (payload: CreateReferralPayload) => {
    sendingReferral.value = true;
    referralStatus.value = 'queued';
    error.value = null;
    try {
      const { data } = await api.post('/operations/referrals/', payload);
      referralStatus.value = 'sent';
      return data;
    } catch (e: unknown) {
      console.error('Failed to send referral', e);
      referralStatus.value = 'failed';
      const detail = getErrorDetail(e);
      error.value = detail || 'Failed to send referral';
      throw e;
    } finally {
      sendingReferral.value = false;
    }
  };

  // Polling fallback for availability (updates every 10s)
  let availabilityTimer: number | null = null;
  const startAvailabilityPolling = () => {
    stopAvailabilityPolling();
    availabilityTimer = window.setInterval(() => {
      void (async () => {
        try {
          const params: Record<string, string> = {};
          if (filters.value.specialization) params.specialization = filters.value.specialization;
          if (filters.value.hospital) params.hospital = filters.value.hospital;
          if (filters.value.department) params.department = filters.value.department;
          const { data } = await api.get('/operations/referrals/available-doctors/', { params });
          availableDoctors.value = (data || []) as DoctorBrief[];
        } catch (err) {
          console.warn('Availability polling error', err);
        }
      })();
    }, 10000);
  };

  const stopAvailabilityPolling = () => {
    if (availabilityTimer) {
      window.clearInterval(availabilityTimer);
      availabilityTimer = null;
    }
  };

  return {
    // state
    selectedPatient,
    selectedDoctor,
    filters,
    availableDoctors,
    loadingDoctors,
    sendingReferral,
    error,
    referralStatus,

    // getters
    readyToRefer,

    // actions
    setPatient,
    setFilters,
    clearDoctorSelection,
    loadAvailableDoctors,
    sendReferral,
    startAvailabilityPolling,
    stopAvailabilityPolling,
  };
});