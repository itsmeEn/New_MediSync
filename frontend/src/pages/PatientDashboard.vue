<template>
  <q-layout view="hHh lpR fFf">
    <!-- Patient Portal Header -->
    <q-header class="bg-white text-teal-9 patient-header">
      <q-toolbar>
        <q-avatar size="40px" class="q-mr-md">
          <img :src="logoUrl" alt="MediSync Logo" />
        </q-avatar>

        <div class="header-content"></div>

        <q-space />

        <!-- Notification Icon -->
        <q-btn flat round icon="notifications" class="q-mr-sm" @click="navigateTo('/patient-notifications')">
          <q-badge v-if="unreadCount > 0" color="red" floating rounded>{{ unreadCount }}</q-badge>
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

    <!-- Main Content -->
    <q-page-container>
      <q-page class="patient-bg q-pa-md">
        
      
          
        <!-- Live Queue Status -->
        <div class="q-mb-lg">
          <div class="text-h6 text-weight-bold q-mb-md">Live Queue Status</div>
          <div class="row q-col-gutter-sm card-row items-stretch no-wrap">
            <!-- Now Serving Card (matched style with Queue Status card) -->
            <div class="col-6 col-xs-6 col-sm-6">
              <q-card class="bg-teal-7 text-white status-card touch-card uniform-card queue-card">
                <q-card-section>
                  <div class="text-caption text-weight-medium opacity-90">NOW SERVING</div>
                  <div class="text-h3 text-weight-bold q-my-sm">
                    {{ dashboardSummary?.nowServing ?? '—' }}
                  </div>
                </q-card-section>
              </q-card>
            </div>
            
            <!-- My Queue Status Card -->
            <div class="col-6 col-xs-6 col-sm-6">
              <q-card class="bg-teal-7 text-white status-card touch-card uniform-card queue-card">
                <q-card-section>
                  <div class="text-caption text-weight-medium opacity-90">MY QUEUE STATUS</div>
                  <div class="text-h5 text-weight-bold q-my-sm" :class="queueStatusSizeClass(dashboardSummary?.myQueueStatus)">
                    {{ dashboardSummary?.myQueueStatus ?? '—' }}
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
        
        <!-- Appointment History -->
        <div class="q-mb-xl">
          <div class="text-h6 text-weight-bold q-mb-md">Appointment History</div>
          <div class="row q-gutter-md card-row justify-center">
            <!-- Next Appointment Card -->
            <div class="col-12 col-sm-6">
              <q-card 
                class="cursor-pointer appt-card touch-card uniform-card"
                @click="openNextApptModal"
                :class="{ 'opacity-60': !nextAppointment }"
                flat
                bordered
              >
                <q-card-section class="q-pb-none">
                  <div class="text-caption text-weight-medium text-teal-7">NEXT APPOINTMENT</div>
                </q-card-section>
                <q-card-section>
                  <div class="text-subtitle1 text-weight-bold">
                    {{ nextAppointment ? getAppointmentTypeLabel(nextAppointment.type) : 'No upcoming appointments' }}
                  </div>
                  <div v-if="nextAppointment" class="text-body2 q-mt-xs">
                    Dr. {{ nextAppointment.doctor || 'Amelia Chen' }}
                    <br>
                    {{ formatShortDate(nextAppointment.date) }}, {{ formatTime(nextAppointment.time) }}
                  </div>
                  <div v-else class="text-body2 q-mt-xs">
                    Your upcoming appointment will appear here
                  </div>
                </q-card-section>
                <q-card-section class="q-pt-none">
                  <q-linear-progress 
                    color="teal-6" 
                    size="3px" 
                    :value="nextAppointment ? 1 : 0"
                  />
                </q-card-section>
              </q-card>
            </div>

            <!-- Last Appointment Card -->
            <div class="col-12 col-sm-6">
              <q-card flat bordered class="appt-card touch-card uniform-card">
                <q-card-section class="q-pb-none">
                  <div class="text-caption text-weight-medium text-teal-7">LAST APPOINTMENT</div>
                </q-card-section>
                <q-card-section>
                  <div class="text-subtitle1 text-weight-bold">
                    {{ lastAppointment ? getAppointmentTypeLabel(lastAppointment.type) : 'No previous appointments' }}
                  </div>
                  <div v-if="lastAppointment" class="text-body2 q-mt-xs">
                    Dr. {{ lastAppointment.doctor || 'Amelia Chen' }}
                    <br>
                    {{ formatShortDate(lastAppointment.date) }}, {{ formatTime(lastAppointment.time) }}
                  </div>
                  <div v-else class="text-body2 q-mt-xs">
                    Your appointment history will appear here
                  </div>
                </q-card-section>
                <q-card-section class="q-pt-none">
                  <q-linear-progress 
                    color="teal-6" 
                    size="3px" 
                    :value="lastAppointment ? 1 : 0"
                  />
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
      </q-page>
    </q-page-container>

    <!-- Fixed Bottom Navigation removed per request -->
     <PatientBottomNav />

    <!-- Mobile-Optimized Appointment Modal -->
    <q-dialog 
      v-model="showNextApptModal" 
      position="bottom"
      :maximized="$q.platform.is.mobile"
    >
      <q-card class="q-dialog-plugin">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Next Appointment Details</div>
          <q-space />
          <q-btn 
            icon="close" 
            flat 
            round 
            dense 
            v-close-popup 
            color="grey-7"
          />
        </q-card-section>

        <q-card-section v-if="nextAppointment">
          <q-list>
            <q-item>
              <q-item-section avatar>
                <q-icon name="category" color="teal" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Type</q-item-label>
                <q-item-label caption>{{ getAppointmentTypeLabel(nextAppointment.type || '') }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="business" color="teal" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Department</q-item-label>
                <q-item-label caption>{{ getDepartmentLabel(nextAppointment.department || '') }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="person" color="teal" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Doctor</q-item-label>
                <q-item-label caption>Dr. {{ nextAppointment.doctor || 'Amelia Chen' }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="event" color="teal" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Date</q-item-label>
                <q-item-label caption>{{ formatLongDate(nextAppointment.date || '') }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="schedule" color="teal" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Time</q-item-label>
                <q-item-label caption>{{ formatTime(nextAppointment.time || '') }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="description" color="teal" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Reason</q-item-label>
                <q-item-label caption>{{ nextAppointment.reason || '—' }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section avatar>
                <q-icon name="info" color="teal" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Status</q-item-label>
                <q-item-label caption class="text-teal-700">{{ capitalize(nextAppointment.status || 'Upcoming') }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn 
            flat 
            label="Close" 
            color="grey-7" 
            v-close-popup 
          />
          <q-btn 
            unelevated 
            label="View Details" 
            color="teal" 
            class="q-ml-sm"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'src/boot/axios'
import logoUrl from 'src/assets/logo.png'
import PatientBottomNav from 'src/components/PatientBottomNav.vue'

const router = useRouter()
// Footer state handled by shared PatientBottomNav component
const showUserMenu = ref(false)
const unreadCount = ref(0)

const userName = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    return u.full_name || u.email || 'User'
  } catch (error) {
    console.warn('Failed to parse user from localStorage:', error)
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

interface DashboardSummary {
  nowServing: string | number
  myQueueStatus: string
}

const dashboardSummary = ref<DashboardSummary | null>(null)

const navigateTo = (path: string) => {
  void router.push(path)
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  void router.push('/login')
}

// Appointment functionality
const showNextApptModal = ref(false)
// Use shared appointments store
import { useAppointmentsStore } from '../stores/appointments'
const appointmentsStore = useAppointmentsStore()
const nextAppointment = computed(() => appointmentsStore.nextAppointment)
const lastAppointment = computed(() => appointmentsStore.lastAppointment)

const getAppointmentTypeLabel = (type: string) => {
  const types: Record<string, string> = {
    'general': 'General Consultation',
    'specialist': 'Specialist Consultation',
    'follow_up': 'Follow-up Visit',
    'emergency': 'Emergency Visit'
  }
  return types[type] || 'General Consultation'
}

const getDepartmentLabel = (department: string) => {
  const departments: Record<string, string> = {
    'general': 'General Medicine',
    'cardiology': 'Cardiology',
    'neurology': 'Neurology',
    'pediatrics': 'Pediatrics'
  }
  return departments[department] || 'General Medicine'
}

const formatShortDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const formatLongDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const formatTime = (timeStr?: string) => {
  if (!timeStr) return ''
  const [hours = '0', minutes = '00'] = timeStr.split(':')
  const hour = parseInt(hours, 10)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour
  return `${displayHour}:${minutes} ${ampm}`
}

const capitalize = (str: string) => {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

// Reduce text size when status is specifically "Waiting-in-line"
const queueStatusSizeClass = (status?: string | null) => {
  const s = (status || '').toLowerCase().trim()
  return s === 'waiting-in-line' ? 'status-text-small' : ''
}

const openNextApptModal = () => {
  if (nextAppointment.value) {
    showNextApptModal.value = true
  }
}

// Combined onMounted hook for all initialization
onMounted(async () => {
  // Load dashboard summary
  try {
    const res = await api.get('/operations/patient/dashboard/summary/', { params: { department: 'OPD' } })
    dashboardSummary.value = res.data as DashboardSummary
  } catch (error: unknown) {
    console.warn('Failed to fetch dashboard summary', error)
    dashboardSummary.value = {
      nowServing: '',
      myQueueStatus: ''
    }
  }

  // Load appointments via store
  try {
    await appointmentsStore.loadAppointments()
  } catch (error: unknown) {
    console.warn('Failed to load appointments via store:', error)
  }

  // Initialize lucide icons from global CDN
  try {
    type Lucide = { createIcons: () => void }
    const lucideCandidate: unknown = (globalThis as Record<string, unknown>).lucide
    if (lucideCandidate && typeof (lucideCandidate as { createIcons?: unknown }).createIcons === 'function') {
      (lucideCandidate as Lucide).createIcons()
    }
  } catch (error: unknown) {
    console.warn('Lucide icons initialization error:', error)
  }
})

onUnmounted(() => {
})
</script>

<style scoped>
.status-number {
  font-size: 2.5rem;
  font-weight: 800;
  line-height: 1;
}
.action-tile {
  height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06);
}
.card, .status-card {
  border-radius: 0.75rem;
}
/* Shared queue status card styles to ensure consistency across cards */
.queue-card {
  /* identical dimensions across queue cards */
  width: 100%;
  min-height: 120px; /* desktop/tablet baseline */
  border-radius: 16px; /* match visual spec with Now Serving */
  /* matching shadow effect */
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
}
.queue-card .q-card__section {
  /* uniform padding across cards */
  padding: 16px;
}
/* Ensure cards visually align when stacked as row/column */
.card-row .queue-card {
  margin: 0; /* rely on row gutters for spacing */
}
/* Quick Actions removed */

/* Center cards within their container on non-mobile viewports */
.uniform-card {
  margin-left: auto;
  margin-right: auto;
}

/* Mobile-only enhancements for larger, touch-friendly status and appointment cards */
@media (max-width: 600px) {
  /* Preserve grid gutters so two status cards can sit side-by-side */
  .card-row { margin-left: 0; margin-right: 0; }

  .quick-actions-card {
    width: calc(100% - 4px);
    margin: 0 2px;
  }
  .status-card, .appt-card {
    border-radius: 16px;
    min-height: 96px;
  }
  /* Mobile: keep queue cards consistent with Now Serving */
  .queue-card {
    min-height: 96px;
    border-radius: 16px;
  }
  .touch-card {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  }
  .touch-card .q-card__section {
    padding: 14px 16px; /* align with Quick Actions, reduce indentation */
  }
  .queue-card .q-card__section {
    padding: 14px 16px; /* match touch-card section padding on mobile */
  }
  .status-card .text-caption,
  .appt-card .text-caption {
    font-size: 14px;
    letter-spacing: 0.2px;
  }
  .status-card .text-h3 {
    font-size: 2rem;
    line-height: 1.1;
  }
  .status-card .text-body2,
  .appt-card .text-body2 {
    font-size: 15px;
    line-height: 1.45;
  }
  .appt-card .text-subtitle1 {
    font-size: 1.1rem;
  }
  /* Shared mobile width/margin so all cards match Quick Actions */
  .uniform-card {
    --card-hpadding: 4px;
    width: calc(100% - var(--card-hpadding));
    margin: 0 calc(var(--card-hpadding) / 2);
  }
}

/* Specific override: shrink text when status is Waiting-in-line */
.text-h5.status-text-small { font-size: 1.1rem; line-height: 1.3; }
@media (max-width: 600px) {
  .text-h5.status-text-small { font-size: 1rem; }
}
</style>
<style scoped>
/* Ensure header content respects mobile safe areas and avoids overlap */
.patient-header {
  box-sizing: border-box;
  padding-left: 12px;
  padding-right: 12px;
  width: 100%;
}
@supports (padding: env(safe-area-inset-left)) {
  .patient-header {
    padding-left: calc(12px + env(safe-area-inset-left));
    padding-right: calc(12px + env(safe-area-inset-right));
  }
}
@media (max-width: 600px) {
  .patient-header {
    /* Slightly increase side padding on small screens for extra spacing */
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style>