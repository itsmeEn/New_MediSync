import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from 'src/boot/axios'

export interface StaffOption {
  label: string
  value: string
  id?: number
  role: 'doctor' | 'nurse' | 'historical_doctor'
  group: 'current' | 'historical'
  hospitalName?: string
  specialization?: string
  department?: string
}

export type RecipientOption = StaffOption | { type: 'header'; label: string }

export interface ApiMedicalRequest {
  id: number
  request_type?: string
  type?: string
  reason?: string
  status: string
  created_at?: string
  createdAt?: string
  urgency?: string
  updated_at?: string
  request_reference_number?: string
}

export interface MedicalRequestUiItem {
  id: number
  type: string
  recipient: string
  details: string
  status: string
  createdAt: string
  urgency?: string
}

function isRecord(obj: unknown): obj is Record<string, unknown> {
  return typeof obj === 'object' && obj !== null
}

function hasStringMessage(x: unknown): x is { message: string } {
  return isRecord(x) && typeof (x as { message?: unknown }).message === 'string'
}

function getErrorMessage(e: unknown, fallback = 'Unexpected error'): string {
  if (typeof e === 'string') return e
  if (hasStringMessage(e)) return e.message
  return fallback
}

export const useMedicalRequestStore = defineStore('medicalRequest', () => {
  const form = ref({
    requestType: '',
    recipient: '',
    details: '',
    purpose: '',
    dateRangeStart: '',
    dateRangeEnd: ''
  })

  const recipientOptions = ref<RecipientOption[]>([])
  const isLoadingRecipients = ref(false)
  const recipientError = ref<string | null>(null)
  const recentRequests = ref<MedicalRequestUiItem[]>([])
  const isSubmitting = ref(false)
  const requestReferenceNumber = ref<string>('')
  const expectedProcessingTime = ref<string>('3-5 business days')

  const HIST_CACHE_KEY = 'patient:historical_doctors'
  const HIST_CACHE_TTL_MS = 10 * 60 * 1000

  const toUiItem = (item: ApiMedicalRequest): MedicalRequestUiItem => ({
    id: item.id,
    type: item.request_type || item.type || form.value.requestType,
    recipient: form.value.recipient,
    details: item.reason || '',
    status: item.status,
    createdAt: item.created_at || item.createdAt || new Date().toISOString(),
    urgency: item.urgency || 'medium'
  })

  async function fetchCurrentStaff(): Promise<StaffOption[]> {
    const results: StaffOption[] = []
    try {
      const docRes = await api.get('/operations/availability/doctors/free/?include_email=false')
      const doctors = (docRes.data?.doctors || []) as Array<{ id: number; full_name: string; hospital_name?: string; specialization?: string }>
      for (const d of doctors) {
        results.push({
          label: d.full_name,
          value: d.full_name,
          id: d.id,
          role: 'doctor',
          group: 'current',
          hospitalName: d.hospital_name || '',
          specialization: d.specialization || ''
        })
      }
    } catch (e) {
      throw new Error(getErrorMessage(e, 'Failed to fetch current staff'))
    }
    return results
  }

  function readHistoricalCache(): StaffOption[] | null {
    try {
      const raw = sessionStorage.getItem(HIST_CACHE_KEY)
      if (!raw) return null
      const parsed = JSON.parse(raw)
      if (!parsed || !parsed.ts || !parsed.items) return null
      if (Date.now() - parsed.ts > HIST_CACHE_TTL_MS) return null
      return parsed.items as StaffOption[]
    } catch {
      return null
    }
  }

  function writeHistoricalCache(items: StaffOption[]): void {
    try {
      sessionStorage.setItem(HIST_CACHE_KEY, JSON.stringify({ ts: Date.now(), items }))
    } catch {
      /* no-op */
    }
  }

  async function fetchHistoricalDoctors(): Promise<StaffOption[]> {
    const cached = readHistoricalCache()
    if (cached) return cached
    try {
      const res = await api.get('/operations/patient/appointments/')
      const resultsCandidate = (res.data as { results?: unknown })?.results
      const list: Array<{ doctor_id?: number; doctor_name?: string }> = Array.isArray(resultsCandidate)
        ? (resultsCandidate as Array<{ doctor_id?: number; doctor_name?: string }>)
        : []
      const byId = new Map<number, { id: number; name: string }>()
      for (const a of list) {
        const did = a.doctor_id
        const dname = a.doctor_name
        if (did && dname && !byId.has(did)) {
          byId.set(did, { id: did, name: dname })
        }
      }
      const items: StaffOption[] = Array.from(byId.values()).map((d) => ({
        label: d.name,
        value: d.name,
        id: d.id,
        role: 'historical_doctor',
        group: 'historical'
      }))
      writeHistoricalCache(items)
      return items
    } catch (e) {
      console.warn('Failed to fetch historical doctors', e)
      return []
    }
  }

  async function loadRecipients(): Promise<void> {
    isLoadingRecipients.value = true
    recipientError.value = null
    try {
      const [currentRes, historicalRes] = await Promise.allSettled([
        fetchCurrentStaff(),
        fetchHistoricalDoctors()
      ])
      const currentStaff = currentRes.status === 'fulfilled' ? currentRes.value : []
      const historical = historicalRes.status === 'fulfilled' ? historicalRes.value : []

      const currentHeader = { type: 'header' as const, label: 'Current Doctors' }
      const historicalHeader = { type: 'header' as const, label: 'Previously Consulted Doctors' }

      const currentNames = new Set(currentStaff.map((s) => s.label))
      const historicalFiltered = historical.filter((h) => !currentNames.has(h.label))

      const combined: RecipientOption[] = []
      if (currentStaff.length > 0) combined.push(currentHeader, ...currentStaff)
      if (historicalFiltered.length > 0) combined.push(historicalHeader, ...historicalFiltered)

      if (combined.length === 0) {
        recipientError.value = 'No recipients available. Try again later.'
      }
      recipientOptions.value = combined

      const isStaffOption = (opt: RecipientOption): opt is StaffOption => !('type' in opt)
      if (!form.value.recipient && combined.length > 0) {
        const firstStaff = combined.find((opt): opt is StaffOption => isStaffOption(opt))
        if (firstStaff) {
          form.value.recipient = firstStaff.value
        }
      }
    } catch (e) {
      recipientError.value = getErrorMessage(e, 'Failed to load recipients')
      recipientOptions.value = []
    } finally {
      isLoadingRecipients.value = false
    }
  }

  async function loadRequests(): Promise<void> {
    try {
      const res = await api.get('/operations/medical-requests/')
      const items = Array.isArray(res.data) ? res.data : []
      recentRequests.value = items.slice(0, 5).map(toUiItem)
    } catch (e) {
      console.warn('Failed to load medical requests', e)
      recentRequests.value = []
    }
  }

  function normalizeDate(val?: string | null): string | null {
    if (!val) return null
    if (/^\d{4}-\d{2}-\d{2}$/.test(val)) return val
    const d = new Date(val)
    if (isNaN(d.getTime())) return null
    return d.toISOString().slice(0, 10)
  }

  async function submit(): Promise<ApiMedicalRequest | null> {
    try {
      isSubmitting.value = true
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      let patientIdNum: number | undefined = undefined
      try {
        const candidate = (user?.id ?? user?.user_id ?? user?.patient_profile?.user?.id) as unknown
        if (candidate != null) patientIdNum = Number(candidate)
      } catch { /* ignore */ }
      if (!Number.isFinite(patientIdNum)) {
        try {
          const prof = await api.get('/users/profile/')
          const candidate = (prof?.data?.user?.id ?? prof?.data?.id) as unknown
          if (candidate != null) patientIdNum = Number(candidate)
        } catch { /* ignore */ }
      }
      if (!Number.isFinite(patientIdNum)) {
        throw new Error('Unable to identify patient. Please re-login.')
      }

      const requested_records: Record<string, boolean> = {}
      if (form.value.requestType === 'full_records') {
        Object.assign(requested_records, {
          intake_assessment: true,
          graphic_flow_sheets: true,
          mar: true,
          education_records: true,
          discharge_summary: true,
          history_physical: true,
          progress_notes: true,
          provider_orders: true,
          operative_reports: true
        })
      } else if (form.value.requestType === 'lab_results') {
        Object.assign(requested_records, { progress_notes: true })
      } else if (form.value.requestType === 'immunization') {
        Object.assign(requested_records, { provider_orders: true })
      } else {
        Object.assign(requested_records, { progress_notes: true })
      }

      const payload: Record<string, unknown> = {
        patient_id: patientIdNum,
        request_type: form.value.requestType,
        requested_records,
        reason: form.value.details
      }

      if (form.value.requestType === 'medical_certificate') {
        payload.purpose = form.value.purpose || ''
        if (form.value.dateRangeStart) payload.requested_date_range_start = normalizeDate(form.value.dateRangeStart) || null
        if (form.value.dateRangeEnd) payload.requested_date_range_end = normalizeDate(form.value.dateRangeEnd) || null
      }

      try {
        const isStaffOption = (opt: RecipientOption): opt is StaffOption => !('type' in opt)
        const selected = recipientOptions.value.find((opt): opt is StaffOption => isStaffOption(opt) && (opt.label === form.value.recipient || String(opt.id || '') === String(form.value.recipient)))
        if (selected && (selected.role === 'historical_doctor' || selected.role === 'doctor') && typeof selected.id === 'number') {
          payload.attending_doctor_id = selected.id
        }
      } catch { /* non-blocking */ }

      const res = await api.post('/operations/medical-requests/', payload)
      const created: ApiMedicalRequest = res.data
      requestReferenceNumber.value = created.request_reference_number || `MC-${created.id}`
      recentRequests.value = [toUiItem(created), ...recentRequests.value].slice(0, 5)
      reset(false)
      return created
    } catch (e) {
      console.error('Error submitting request:', e)
      throw e
    } finally {
      isSubmitting.value = false
    }
  }

  function prepopulateFromQuery(query: Record<string, unknown>): void {
    if (typeof query.type === 'string') form.value.requestType = query.type
    // Accept doctor_name or doctor_id for recipient prefill
    const name = typeof query.doctor_name === 'string' ? query.doctor_name : ''
    const idStr = typeof query.doctor_id === 'string' || typeof query.doctor_id === 'number'
      ? String(query.doctor_id)
      : ''
    // Attempt to match by name first; id if available after recipients load
    if (name) form.value.recipient = name
    else if (idStr) form.value.recipient = idStr
  }

  function setAppointmentContext(opts: { doctorId?: number; doctorName?: string; type?: string }): void {
    if (opts.type) form.value.requestType = opts.type
    if (opts.doctorName) form.value.recipient = opts.doctorName
    else if (opts.doctorId != null) form.value.recipient = String(opts.doctorId)
  }

  function reset(resetRequests = true): void {
    form.value = {
      requestType: '',
      recipient: '',
      details: '',
      purpose: '',
      dateRangeStart: '',
      dateRangeEnd: ''
    }
    if (resetRequests) recentRequests.value = []
  }

  return {
    form,
    recipientOptions,
    isLoadingRecipients,
    recipientError,
    recentRequests,
    isSubmitting,
    requestReferenceNumber,
    expectedProcessingTime,
    loadRecipients,
    loadRequests,
    submit,
    prepopulateFromQuery,
    setAppointmentContext,
    reset
  }
})