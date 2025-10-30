<template>
  <q-layout view="lHh Lpr lFf">
    <!-- Patient Portal Header -->
    <q-header class="bg-white text-teal-9">
      <q-toolbar>
        <q-avatar size="40px" class="q-mr-md">
          <img :src="logoUrl" alt="MediSync Logo" />
        </q-avatar>
        
        <div class="header-content"></div>

        <q-space />

        <!-- Notification Icon -->
        <q-btn flat round icon="notifications" class="q-mr-sm">
          <q-badge color="red" floating>3</q-badge>
        </q-btn>

        <!-- User Menu -->
        <q-btn flat round>
          <q-avatar size="32px" color="white" text-color="primary">
            {{ userInitials }}
          </q-avatar>
          <q-menu v-model="showUserMenu">
            <q-list style="min-width: 200px">
              <q-item clickable @click="navigateTo('/patient-settings')">
                <q-item-section avatar>
                  <q-icon name="settings" />
                </q-item-section>
                <q-item-section>Settings</q-item-section>
              </q-item>
              <q-item clickable @click="logout">
                <q-item-section avatar>
                  <q-icon name="logout" />
                </q-item-section>
                <q-item-section>Logout</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-page-container>
       <q-page class="patient-bg q-pa-md pb-safe">
         <div class="max-w-4xl mx-auto">
           <div class="text-h5 text-weight-bold q-mb-md">
             Medical Records & General Requests
           </div>

           <div class="q-gutter-md">
             <!-- Request Form Panel -->
             <q-card>
               <q-card-section>
                 <div class="row items-center q-mb-md">
                   <q-avatar color="amber-1" text-color="amber" icon="description" size="48px" class="q-mr-md" />
                   <div>
                     <div class="text-h6 text-weight-bold">
                       Request Your Medical Records
                     </div>
                     <div class="text-caption">
                       Use this form to securely request your medical records
                     </div>
                   </div>
                 </div>
                 
                 <q-form ref="formRef" @submit="onSubmit" @reset="onReset" class="q-gutter-md">
                   <!-- Request Type -->
                   <q-select
                     v-model="form.requestType"
                     :options="requestTypeOptions"
                     outlined
                     label="Type of Request"
                     color="teal"
                     placeholder="Select request type"
                     :rules="[val => !!val || 'Please select a request type']"
                     behavior="menu"
                   >
                     <template #prepend>
                       <q-icon name="description" color="teal" />
                     </template>
                   </q-select>

                   <!-- Recipient -->
                   <q-select
                     v-model="form.recipient"
                     :options="recipientOptions"
                     outlined
                     label="Recipient (Doctor/Nurse)"
                     color="teal"
                     use-input
                     fill-input
                     input-debounce="200"
                     emit-value
                     map-options
                     :loading="isLoadingRecipients"
                     :error="!!recipientError"
                     :error-message="recipientError || ''"
                     :rules="[val => !!val || 'Please select a recipient']"
                   >
                     <template #prepend>
                       <q-icon name="person" color="teal" />
                     </template>
                     <template #option="scope">
                       <q-item v-if="(scope.opt as any).type === 'header'" dense class="bg-grey-2">
                         <q-item-section>
                           <div class="text-caption text-grey-7">{{ (scope.opt as any).label }}</div>
                         </q-item-section>
                       </q-item>
                       <q-item v-else v-bind="scope.itemProps">
                         <q-item-section>
                           <q-item-label>{{ (scope.opt as StaffOption).label }}</q-item-label>
                           <q-item-label caption>
                             <span v-if="(scope.opt as StaffOption).group === 'current'" class="text-positive">Current</span>
                             <span v-else class="text-grey-7">Historical</span>
                             • {{ (scope.opt as StaffOption).role === 'nurse' ? 'Nurse' : 'Doctor' }}
                             <span v-if="(scope.opt as StaffOption).specialization"> • {{ (scope.opt as StaffOption).specialization }}</span>
                             <span v-if="(scope.opt as StaffOption).department"> • {{ (scope.opt as StaffOption).department }}</span>
                           </q-item-label>
                         </q-item-section>
                       </q-item>
                     </template>
                   </q-select>

                   <!-- Additional Details -->
                   <q-input
                     v-model="form.details"
                     type="textarea"
                     outlined
                     label="Additional Details (Optional)"
                     color="teal"
                     placeholder="Enter additional details about your request"
                     rows="3"
                     autogrow
                   >
                     <template #prepend>
                       <q-icon name="message" color="teal" />
                     </template>
                   </q-input>

                   <!-- Urgency -->
                   <q-select
                     v-model="form.urgency"
                     :options="urgencyOptions"
                     outlined
                     label="Urgency"
                     color="teal"
                     behavior="menu"
                   >
                     <template #prepend>
                       <q-icon name="priority_high" color="teal" />
                     </template>
                   </q-select>

                   <!-- Submit Button -->
                   <q-btn
                     type="submit"
                     color="teal"
                     class="full-width"
                     label="Submit Record Request"
                     :loading="isSubmitting"
                     unelevated
                     size="lg"
                   />
                 </q-form>
               </q-card-section>
             </q-card>

             <!-- History/Status Panel -->
             <q-card>
               <q-card-section>
                 <div class="row items-center q-mb-md">
                   <q-avatar color="grey-3" text-color="grey-7" icon="history" size="48px" class="q-mr-md" />
                   <div>
                     <div class="text-h6 text-weight-bold">
                       Request History
                     </div>
                   </div>
                 </div>
                 
                 <div v-if="recentRequests.length === 0" class="text-center q-py-xl">
                   <q-icon name="description" size="64px" color="grey-4" class="q-mb-md" />
                   <div class="text-h6 text-weight-medium q-mb-sm">
                     No recent requests
                   </div>
                   <div class="text-body2">
                     Your submitted requests will appear here
                   </div>
                 </div>
                 
                 <q-list v-else separator>
                   <q-item
                     v-for="request in recentRequests" 
                     :key="request.id"
                     class="q-pa-md"
                   >
                     <q-item-section side>
                       <q-icon 
                         :name="request.status === 'pending' ? 'schedule' : 
                                request.status === 'approved' ? 'check_circle' : 
                                request.status === 'rejected' ? 'cancel' : 'help'"
                         :color="request.status === 'pending' ? 'orange' : 
                                request.status === 'approved' ? 'green' : 
                                request.status === 'rejected' ? 'red' : 'grey'"
                         size="md"
                       />
                     </q-item-section>
                     
                     <q-item-section>
                       <q-item-label class="text-weight-medium">
                         {{ request.type }}
                       </q-item-label>
                       <q-item-label caption>
                         Status: {{ request.status.charAt(0).toUpperCase() + request.status.slice(1) }}
                       </q-item-label>
                       <q-item-label caption>
                         Date: {{ formatDate(request.createdAt) }}
                       </q-item-label>
                     </q-item-section>
                     
                     <q-item-section side>
                       <q-badge 
                         :color="request.status === 'pending' ? 'orange' : 
                                request.status === 'approved' ? 'green' : 
                                request.status === 'rejected' ? 'red' : 'grey'"
                         :label="request.status"
                       />
                     </q-item-section>
                   </q-item>
                 </q-list>
               </q-card-section>
             </q-card>
           </div>
         </div>
       </q-page>
     </q-page-container>

    <PatientBottomNav />
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'src/boot/axios'
import logoUrl from 'src/assets/logo.png'
import PatientBottomNav from 'src/components/PatientBottomNav.vue'

const router = useRouter()
const unreadCount = ref<number>(0)
const isSubmitting = ref(false)
const formRef = ref()
const showUserMenu = ref(false)

const userName = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    return u.full_name || u.email || 'User'
  } catch {
    return 'User'
  }
})

const userInitials = computed(() => {
  const name = userName.value || ''
  const parts = name.trim().split(/\s+/)
  if (parts.length === 0) return 'U'
  const initials = parts.slice(0, 2).map((p: string) => p[0]?.toUpperCase() ?? '').join('')
  return initials || (name[0]?.toUpperCase() ?? 'U')
})

// Form data
const form = ref({
  requestType: '',
  recipient: 'Dr. Amelia Chen',
  details: '',
  urgency: 'medium'
})

// Form options
const requestTypeOptions = [
  { label: 'Full Medical Records (Last 5 Years)', value: 'full_records' },
  { label: 'Specific Lab Results Only', value: 'lab_results' },
  { label: 'Immunization History', value: 'immunization' },
  { label: 'General Inquiry', value: 'general_inquiry' }
]

const urgencyOptions = [
  { label: 'Low', value: 'low' },
  { label: 'Medium', value: 'medium' },
  { label: 'High', value: 'high' },
  { label: 'Urgent', value: 'urgent' }
]

// Interface for medical request
interface MedicalRequest {
  id: number
  type: string
  recipient: string
  details: string
  status: string
  createdAt: string
  description?: string
  urgency?: string
  updatedAt?: string
}

// Recipient options typing
type StaffRole = 'doctor' | 'nurse' | 'historical_doctor'
type StaffGroup = 'current' | 'historical'
interface StaffOption {
  label: string
  value: string
  id?: number
  role: StaffRole
  group: StaffGroup
  hospitalName?: string
  specialization?: string
  department?: string
}

// Interface for backend API response
interface ApiMedicalRequest {
  id: number
  request_type?: string
  type?: string
  reason?: string
  status: string
  created_at?: string
  createdAt?: string
  urgency?: string
  updated_at?: string
}

// Recent requests
const recentRequests = ref<MedicalRequest[]>([])

// Recipient data state
const recipientOptions = ref<(StaffOption | { type: 'header'; label: string })[]>([])
const isLoadingRecipients = ref<boolean>(false)
const recipientError = ref<string | null>(null)
const HIST_CACHE_KEY = 'patient:historical_doctors'
const HIST_CACHE_TTL_MS = 10 * 60 * 1000 // 10 minutes

// Backend payload shapes
interface ApiDoctor {
  id: number
  full_name: string
  hospital_name?: string
  specialization?: string
}

interface ApiNurse {
  id: number
  full_name: string
  hospital_name?: string
  department?: string
}

function hasMessage(x: unknown): x is { message: unknown } {
  return typeof x === 'object' && x !== null && 'message' in x
}

function getErrorMessage(e: unknown, fallback = 'Unexpected error'): string {
  if (typeof e === 'string') return e
  if (hasMessage(e) && typeof e.message === 'string') return e.message
  return fallback
}

// Backend integration helpers
const toUiItem = (item: ApiMedicalRequest): MedicalRequest => ({
  id: item.id,
  type: item.request_type || item.type || form.value.requestType,
  recipient: form.value.recipient,
  details: item.reason || '',
  status: item.status,
  createdAt: item.created_at || item.createdAt || new Date().toISOString(),
  urgency: item.urgency || 'medium'
})

// Recipient fetching and merging
async function fetchCurrentStaff(): Promise<StaffOption[]> {
  const results: StaffOption[] = []
  try {
    const [docRes, nurseRes] = await Promise.all([
      api.get('/operations/availability/doctors/free/?include_email=false'),
      api.get('/operations/availability/nurses/')
    ])
    // Backend already scopes by user's hospital; do not over-filter
    const doctors = (docRes.data?.doctors || []) as ApiDoctor[]
    const nurses = (nurseRes.data?.nurses || []) as ApiNurse[]
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
    for (const n of nurses) {
      results.push({
        label: n.full_name,
        value: n.full_name,
        id: n.id,
        role: 'nurse',
        group: 'current',
        hospitalName: n.hospital_name || '',
        department: n.department || ''
      })
    }
  } catch (e: unknown) {
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
    void 0
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
  } catch (e: unknown) {
    // If history fails, return empty to avoid blocking current staff
    console.warn('Failed to fetch historical doctors', e)
    return []
  }
}

async function loadRecipients() {
  isLoadingRecipients.value = true
  recipientError.value = null
  try {
    const [currentStaff, historical] = await Promise.all([
      fetchCurrentStaff(),
      fetchHistoricalDoctors()
    ])

    const currentHeader = { type: 'header' as const, label: 'Current Hospital Staff' }
    const historicalHeader = { type: 'header' as const, label: 'Historical Consultations' }

    // Exclude duplicates: if a historical doctor is also current, keep the current entry and drop the historical duplicate
    const currentNames = new Set(currentStaff.map((s) => s.label))
    const historicalFiltered = historical.filter((h) => !currentNames.has(h.label))

    const combined: (StaffOption | { type: 'header'; label: string })[] = []
    combined.push(currentHeader, ...currentStaff)
    if (historicalFiltered.length > 0) {
      combined.push(historicalHeader, ...historicalFiltered)
    }
    recipientOptions.value = combined
    // If no recipient selected yet, pick first current entry if available
    if (!form.value.recipient) {
      const first = currentStaff.at(0)
      if (first) {
        form.value.recipient = first.value
      }
    }
  } catch (e: unknown) {
    recipientError.value = getErrorMessage(e, 'Failed to load recipients')
    recipientOptions.value = []
  } finally {
    isLoadingRecipients.value = false
  }
}

async function loadRequests() {
  try {
    const res = await api.get('/operations/medical-requests/')
    const items = Array.isArray(res.data) ? res.data : []
    recentRequests.value = items.slice(0, 5).map(toUiItem)
  } catch (e) {
    console.warn('Failed to load medical requests', e)
    recentRequests.value = []
  }
}

// Form submission
const onSubmit = async () => {
  try {
    isSubmitting.value = true
    
    // Validate form
    if (!formRef.value) return
    const valid = await formRef.value.validate()
    if (!valid) return

    // Build backend payload
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const patientId = user.id
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
      // General inquiry -> minimal set
      Object.assign(requested_records, { progress_notes: true })
    }

    const payload = {
      patient_id: patientId,
      request_type: form.value.requestType,
      requested_records,
      reason: form.value.details,
      urgency: form.value.urgency
    }

    const res = await api.post('/operations/medical-requests/', payload)
    const created = res.data
    // Prepend to UI list
    recentRequests.value = [toUiItem(created), ...recentRequests.value].slice(0, 5)
    
    // Reset form
    onReset()
    
    // Show success message
    alert('Request submitted successfully! Your doctor and nurse were notified.')
    
  } catch (error) {
    console.error('Error submitting request:', error)
    alert('Error submitting request. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

const onReset = () => {
  form.value = {
    requestType: '',
    recipient: 'Dr. Amelia Chen',
    details: '',
    urgency: 'medium'
  }
  if (formRef.value) {
    formRef.value.resetValidation()
  }
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

const navigateTo = (path: string) => { void router.push(path) }

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  void router.push('/login')
}

onMounted(async () => {
  // Declare window interface for lucide
  interface WindowWithLucide extends Window {
    lucide?: {
      createIcons(): void
    }
  }
  
  try { 
    (window as WindowWithLucide).lucide?.createIcons() 
  } catch (e) { 
    console.warn('lucide icons init failed', e) 
  }
  
  try {
    const res = await api.get('/patient/notifications/unread-count/')
    unreadCount.value = res.data?.count ?? 0
  } catch (e) { 
    console.warn('unread count fetch failed', e)
    unreadCount.value = 0 
  }
  
  await loadRequests()
  await loadRecipients()
})
</script>

<style scoped>
</style>