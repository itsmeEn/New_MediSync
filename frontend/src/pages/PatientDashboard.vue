<template>
  <q-layout view="hHh lpR fFf">
    <!-- Patient Portal Header -->
    <q-header class="bg-blue-8 text-white" style="height: 70px;">
      <q-toolbar class="q-px-md" style="height: 70px;">
        <q-avatar size="40px" class="q-mr-md">
          <img :src="logoUrl" alt="Logo" />
        </q-avatar>
        
        <div class="column q-mr-auto">
          <div class="text-h6 text-weight-medium">Patient Portal</div>
          <div class="text-caption opacity-80">Healthcare Dashboard</div>
        </div>

        <!-- Notification Icon -->
        <q-btn flat round icon="notifications" class="q-mr-sm" @click="navigateTo('/patient/notifications')">
          <q-badge v-if="unreadCount > 0" color="red" floating rounded>{{ unreadCount }}</q-badge>
        </q-btn>

        <!-- User Menu -->
        <q-btn flat round class="q-ml-sm" @click="showUserMenu = !showUserMenu">
          <q-avatar size="32px" class="bg-white text-blue-8">
            <div class="text-weight-bold">{{ userInitials }}</div>
          </q-avatar>
        </q-btn>

        <!-- User Dropdown Menu -->
        <q-menu v-model="showUserMenu" anchor="bottom right" self="top right" class="q-mt-xs">
          <q-list style="min-width: 200px">
            <q-item-label header class="text-grey-7">{{ userName }}</q-item-label>
            <q-separator />
            <q-item clickable v-close-popup @click="navigateTo('/patient/settings')">
              <q-item-section avatar>
                <q-icon name="settings" />
              </q-item-section>
              <q-item-section>Settings</q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="logout">
              <q-item-section avatar>
                <q-icon name="logout" />
              </q-item-section>
              <q-item-section>Logout</q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-toolbar>
    </q-header>

    <!-- Main Content -->
    <q-page-container>
      <q-page class="bg-grey-1 q-pa-md">
        <!-- Quick Access Tiles -->
        <div class="q-mb-lg">
          <div class="row q-gutter-md">
            <!-- Queue Status -->
            <div class="col-6 col-sm-3">
              <q-card 
                class="action-card cursor-pointer" 
                @click="navigateTo('/patient-queue')"
                flat
                bordered
              >
                <q-card-section class="text-center q-pa-lg">
                  <q-icon 
                    name="format_list_numbered" 
                    size="48px" 
                    color="teal-6" 
                    class="q-mb-sm"
                  />
                  <div class="text-subtitle2 text-weight-bold text-grey-8">
                    Queue Status
                  </div>
                </q-card-section>
                <q-card-section class="q-pt-none">
                  <q-linear-progress 
                    color="teal-6" 
                    size="4px" 
                    :value="0.3" 
                    class="q-mt-sm"
                  />
                </q-card-section>
              </q-card>
            </div>

            <!-- Appointments -->
            <div class="col-6 col-sm-3">
              <q-card 
                class="action-card cursor-pointer" 
                @click="navigateTo('/patient-appointments')"
                flat
                bordered
              >
                <q-card-section class="text-center q-pa-lg">
                  <q-icon 
                    name="event" 
                    size="48px" 
                    color="teal-6" 
                    class="q-mb-sm"
                  />
                  <div class="text-subtitle2 text-weight-bold text-grey-8">
                    Appointments
                  </div>
                </q-card-section>
                <q-card-section class="q-pt-none">
                  <q-linear-progress 
                    color="teal-6" 
                    size="4px" 
                    :value="0.7" 
                    class="q-mt-sm"
                  />
                </q-card-section>
              </q-card>
            </div>

            <!-- Notifications -->
            <div class="col-6 col-sm-3">
              <q-card 
                class="action-card cursor-pointer" 
                @click="navigateTo('/patient-notifications')"
                flat
                bordered
              >
                <q-card-section class="text-center q-pa-lg">
                  <q-icon 
                    name="notifications" 
                    size="48px" 
                    color="teal-6" 
                    class="q-mb-sm"
                  />
                  <div class="text-subtitle2 text-weight-bold text-grey-8">
                    Notifications
                  </div>
                  <q-badge 
                    v-if="notificationCount > 0" 
                    color="red" 
                    floating
                  >
                    {{ notificationCount }}
                  </q-badge>
                </q-card-section>
                <q-card-section class="q-pt-none">
                  <q-linear-progress 
                    color="teal-6" 
                    size="4px" 
                    :value="0.5" 
                    class="q-mt-sm"
                  />
                </q-card-section>
              </q-card>
            </div>
            
            <!-- Medical Requests -->
            <div class="col-6 col-sm-3">
              <q-card 
                class="action-card cursor-pointer" 
                @click="navigateTo('/patient-medical-request')"
                flat
                bordered
              >
                <q-card-section class="text-center q-pa-lg">
                  <q-icon 
                    name="medical_services" 
                    size="48px" 
                    color="teal-6" 
                    class="q-mb-sm"
                  />
                  <div class="text-subtitle2 text-weight-bold text-grey-8">
                    Medical Request
                  </div>
                </q-card-section>
                <q-card-section class="q-pt-none">
                  <q-linear-progress 
                    color="teal-6" 
                    size="4px" 
                    :value="0.2" 
                    class="q-mt-sm"
                  />
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
          
        <!-- Live Queue Status -->
        <div class="q-mb-lg">
          <div class="text-h6 text-weight-bold text-grey-8 q-mb-md">Live Queue Status</div>
          <div class="row q-gutter-md">
            <!-- Now Serving Card -->
            <div class="col-6">
              <q-card class="bg-teal-6 text-white">
                <q-card-section>
                  <div class="text-caption text-weight-medium opacity-90">NOW SERVING</div>
                  <div class="text-h3 text-weight-bold q-my-sm">
                    {{ dashboardSummary?.nowServing ?? '—' }}
                  </div>
                  <div class="text-body2 text-weight-medium">
                    {{ dashboardSummary?.currentPatient ?? '—' }}
                  </div>
                </q-card-section>
              </q-card>
            </div>
            
            <!-- My Queue Status Card -->
            <div class="col-6">
              <q-card class="bg-teal-7 text-white">
                <q-card-section>
                  <div class="text-caption text-weight-medium opacity-90">MY QUEUE STATUS</div>
                  <div class="text-h3 text-weight-bold q-my-sm">
                    {{ dashboardSummary?.myPosition ?? '—' }}
                  </div>
                  <div class="text-body2 text-weight-medium">
                    {{ userName }}
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
        
        <!-- Appointment History -->
        <div class="q-mb-xl">
          <div class="text-h6 text-weight-bold text-grey-8 q-mb-md">Appointment History</div>
          <div class="row q-gutter-md">
            <!-- Next Appointment Card -->
            <div class="col-6">
              <q-card 
                class="cursor-pointer"
                @click="openNextApptModal"
                :class="{ 'opacity-60': !nextAppointment }"
                flat
                bordered
              >
                <q-card-section class="q-pb-none">
                  <div class="text-caption text-weight-medium text-teal-7">NEXT APPOINTMENT</div>
                </q-card-section>
                <q-card-section>
                  <div class="text-subtitle1 text-weight-bold text-grey-9">
                    {{ nextAppointment ? getAppointmentTypeLabel(nextAppointment.type) : 'No upcoming appointments' }}
                  </div>
                  <div v-if="nextAppointment" class="text-body2 text-grey-6 q-mt-xs">
                    Dr. {{ nextAppointment.doctor || 'Amelia Chen' }}
                    <br>
                    {{ formatShortDate(nextAppointment.date) }}, {{ formatTime(nextAppointment.time) }}
                  </div>
                  <div v-else class="text-body2 text-grey-5 q-mt-xs">
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
            <div class="col-6">
              <q-card flat bordered>
                <q-card-section class="q-pb-none">
                  <div class="text-caption text-weight-medium text-teal-7">LAST APPOINTMENT</div>
                </q-card-section>
                <q-card-section>
                  <div class="text-subtitle1 text-weight-bold text-grey-9">
                    {{ lastAppointment ? getAppointmentTypeLabel(lastAppointment.type) : 'No previous appointments' }}
                  </div>
                  <div v-if="lastAppointment" class="text-body2 text-grey-6 q-mt-xs">
                    Dr. {{ lastAppointment.doctor || 'Amelia Chen' }}
                    <br>
                    {{ formatShortDate(lastAppointment.date) }}, {{ formatTime(lastAppointment.time) }}
                  </div>
                  <div v-else class="text-body2 text-grey-5 q-mt-xs">
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

    <!-- Mobile-First Bottom Navigation -->
    <q-footer class="bg-teal-8">
      <q-tabs 
        v-model="currentTab" 
        dense 
        class="text-white"
        active-color="white"
        indicator-color="transparent"
        align="justify"
      >
        <q-tab 
          name="queue" 
          icon="format_list_numbered" 
          label="Queue"
          @click="navigateTo('/patient-queue')"
          no-caps
        />
        <q-tab 
          name="appointments" 
          icon="event" 
          label="Appointments"
          @click="navigateTo('/patient-appointments')"
          no-caps
        />
        <q-tab 
          name="home" 
          icon="home" 
          label="Home"
          @click="navigateTo('/patient-dashboard')"
          no-caps
        />
        <q-tab 
          name="notifications" 
          icon="notifications" 
          label="Alerts"
          @click="navigateTo('/patient-notifications')"
          no-caps
        >
          <q-badge 
            v-if="notificationCount > 0" 
            color="red" 
            floating
          >
            {{ notificationCount }}
          </q-badge>
        </q-tab>
        <q-tab 
          name="requests" 
          icon="medical_services" 
          label="Requests"
          @click="navigateTo('/patient-medical-request')"
          no-caps
        />
      </q-tabs>
    </q-footer>

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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'src/boot/axios'
import logoUrl from 'src/assets/logo.svg'

const router = useRouter()
const currentTab = ref('home')
const notificationCount = ref(3)
const showUserMenu = ref(false)
const unreadCount = ref(3)

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

interface DashboardSummary {
  nowServing: string | number
  currentPatient: string
  myPosition: string | number
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

const openNextApptModal = () => {
  if (nextAppointment.value) {
    showNextApptModal.value = true
  }
}

// Combined onMounted hook for all initialization
onMounted(async () => {
  // Load dashboard summary
  try {
    const res = await api.get('/patient/dashboard/summary/')
    dashboardSummary.value = res.data as DashboardSummary
  } catch (err) {
    console.warn('Failed to fetch dashboard summary', err)
    dashboardSummary.value = {
      nowServing: '001',
      currentPatient: userName.value,
      myPosition: '005'
    }
  }

  // Load appointments via store
  try {
    await appointmentsStore.loadAppointments()
  } catch (error) {
    console.warn('Failed to load appointments via store:', error)
  }

  // Initialize lucide icons from global CDN
  try {
    (window as { lucide?: { createIcons(): void } }).lucide?.createIcons()
  } catch {
    // ignore if lucide not available
  }
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
</style>