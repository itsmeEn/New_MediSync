<template>
  <q-layout view="hHh lpR fFf">
    <!-- Tailwind-based Header replicating Random.html -->
    <header class="bg-teal-800 p-4 md:p-6 shadow-lg">
      <div class="flex justify-between items-center max-w-7xl mx-auto">
        <!-- App Title/Logo -->
        <div class="flex items-center space-x-3 text-white">
          <!-- Project Logo -->
          <img :src="logoUrl" alt="Project Logo" class="h-10 w-10 rounded-full bg-white object-cover flex-shrink-0" />
          <div>
            <p class="text-lg font-semibold leading-none">Patient Portal</p>
            <p class="text-sm font-light text-teal-300 leading-none">Healthcare Dashboard</p>
          </div>
        </div>
        
        <!-- User Profile Section (Right Side) -->
        <div class="flex items-center space-x-4">
          <!-- Notification Bell -->
          <button class="relative p-2 text-white hover:text-teal-200 transition duration-150" @click="navigateTo('/patient-notifications')">
            <i data-lucide="bell" class="w-6 h-6"></i>
            <span class="absolute top-0 right-0 block h-2.5 w-2.5 rounded-full ring-2 ring-teal-800 bg-red-500"></span>
          </button>
          
          <!-- User Profile Button -->
          <div class="relative">
            <button class="flex items-center space-x-2 bg-teal-700 hover:bg-teal-600 p-2 rounded-lg shadow-md transition-all duration-300 hover:scale-105" @click="toggleUserMenu">
              <div class="h-8 w-8 bg-white text-teal-800 rounded-full flex items-center justify-center font-bold text-sm">
                {{ userInitials }}
              </div>
              <div class="text-left">
                <p class="text-sm font-semibold text-white leading-none">{{ userName }}</p>
                <p class="text-xs text-teal-300 leading-none">Patient</p>
              </div>
              <i data-lucide="chevron-down" class="w-4 h-4 text-white transition-transform duration-200" :class="{ 'rotate-180': showUserMenu }"></i>
            </button>

            <!-- Dropdown Menu -->
            <div v-show="showUserMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-2xl py-2 z-50 border border-gray-100">
              <a href="#" @click.prevent="navigateTo('/patient-settings'); toggleUserMenu()" class="flex items-center space-x-3 px-4 py-3 text-sm text-gray-700 hover:bg-teal-50 transition-colors duration-200">
                <i data-lucide="settings" class="w-4 h-4 text-teal-600"></i>
                <span>Settings</span>
              </a>
              <a href="#" @click.prevent="navigateTo('/patient-settings#faq'); toggleUserMenu()" class="flex items-center space-x-3 px-4 py-3 text-sm text-gray-700 hover:bg-teal-50 transition-colors duration-200">
                <i data-lucide="help-circle" class="w-4 h-4 text-teal-600"></i>
                <span>FAQ</span>
              </a>
              <div class="border-t border-gray-100 my-2"></div>
              <a href="#" @click.prevent="logout(); toggleUserMenu()" class="flex items-center space-x-3 px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors duration-200">
                <i data-lucide="log-out" class="w-4 h-4"></i>
                <span>Logout</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <q-page-container>
      <q-page class="bg-teal-50 q-pa-none pb-safe">
        <main class="flex-grow min-h-screen overflow-y-auto w-full p-4 md:p-8 max-w-7xl mx-auto pb-safe">
          <!-- Quick Access Tiles -->
          <section class="mt-4">
            <div class="grid grid-cols-2 gap-6">
              <!-- Queue Status -->
              <div class="action-tile card bg-white text-teal-800 border-b-4 border-teal-600 transform hover:scale-[1.02] transition duration-300 cursor-pointer shadow-md" @click="navigateTo('/patient-queue')">
                <div class="p-3 bg-teal-100 rounded-xl mb-2">
                  <i data-lucide="list-ordered" class="w-8 h-8"></i>
                </div>
                <p class="text-base font-bold text-gray-800 mt-2">Queue Status</p>
              </div>

              <!-- Appointments -->
              <div class="action-tile card bg-white text-teal-800 border-b-4 border-teal-600 transform hover:scale-[1.02] transition duration-300 cursor-pointer shadow-md" @click="navigateTo('/patient-appointments')">
                <div class="p-3 bg-teal-100 rounded-xl mb-2">
                  <i data-lucide="calendar-check" class="w-8 h-8"></i>
                </div>
                <p class="text-base font-bold text-gray-800 mt-2">Appointments</p>
              </div>

              <!-- Notifications -->
              <div class="action-tile card bg-white text-teal-800 border-b-4 border-teal-600 transform hover:scale-[1.02] transition duration-300 cursor-pointer shadow-md" @click="navigateTo('/patient-notifications')">
                <div class="p-3 bg-teal-100 rounded-xl mb-2">
                  <i data-lucide="bell" class="w-8 h-8"></i>
                </div>
                <p class="text-base font-bold text-gray-800 mt-2">Notifications</p>
              </div>
              
              <!-- Medical Requests -->
              <div class="action-tile card bg-white text-teal-800 border-b-4 border-teal-600 transform hover:scale-[1.02] transition duration-300 cursor-pointer shadow-md" @click="navigateTo('/patient-medical-request')">
                <div class="p-3 bg-teal-100 rounded-xl mb-2">
                  <i data-lucide="message-square" class="w-8 h-8"></i>
                </div>
                <p class="text-base font-bold text-gray-800 mt-2">Medical Request</p>
              </div>
            </div>
          </section>
          
          <!-- Live Queue Status -->
          <section class="mt-8">
            <h2 class="text-xl font-bold text-gray-700 mb-3">Live Queue Status</h2>
            <div class="grid grid-cols-2 gap-4">
              <!-- Now Serving Card -->
              <div class="status-card bg-teal-600 text-white p-4 shadow-xl rounded-xl">
                <p class="text-xs font-medium uppercase tracking-wider opacity-90 mb-1">Now Serving</p>
                <p class="status-number text-white">{{ dashboardSummary?.nowServing ?? '—' }}</p>
                <p class="text-sm font-semibold mt-1">{{ dashboardSummary?.currentPatient ?? '—' }}</p>
              </div>
              <!-- My Queue Status Card -->
              <div class="status-card bg-teal-700 text-white p-4 shadow-xl rounded-xl">
                <p class="text-xs font-medium uppercase tracking-wider opacity-90 mb-1">My Queue Status</p>
                <p class="status-number text-white">{{ dashboardSummary?.myPosition ?? '—' }}</p>
                <p class="text-sm font-semibold mt-1">{{ userName }}</p>
              </div>
            </div>
          </section>
          
          <!-- Appointment History -->
          <section class="mt-8">
            <h2 class="text-xl font-bold text-gray-700 mb-3">Appointment History</h2>
            <div class="grid grid-cols-2 gap-4">
              <!-- Next Appointment Card -->
              <div
                class="bg-white p-4 rounded-xl shadow-md border-l-4 border-teal-600 cursor-pointer"
                @click="openNextApptModal"
                :class="{ 'opacity-60 cursor-default': !nextAppointment }"
              >
                <p class="text-xs font-medium uppercase tracking-wider text-teal-700 mb-1">Next Appointment</p>
                <p class="text-lg font-extrabold text-gray-900">
                  {{ nextAppointment ? getAppointmentTypeLabel(nextAppointment.type) : 'No upcoming appointments' }}
                </p>
                <p v-if="nextAppointment" class="text-sm text-gray-600 mt-1">
                  Dr. {{ nextAppointment.doctor || 'Amelia Chen' }}
                  |
                  {{ formatShortDate(nextAppointment.date) }}, {{ formatTime(nextAppointment.time) }}
                </p>
                <p v-else class="text-sm text-gray-500 mt-1">Your upcoming appointment will appear here</p>
              </div>

              <!-- Last Appointment Card -->
              <div class="bg-white p-4 rounded-xl shadow-md border-l-4 border-teal-600">
                <p class="text-xs font-medium uppercase tracking-wider text-teal-700 mb-1">Last Appointment</p>
                <p class="text-lg font-extrabold text-gray-900">
                  {{ lastAppointment ? getAppointmentTypeLabel(lastAppointment.type) : 'No previous appointments' }}
                </p>
                <p v-if="lastAppointment" class="text-sm text-gray-600 mt-1">
                  Dr. {{ lastAppointment.doctor || 'Amelia Chen' }}
                  |
                  {{ formatShortDate(lastAppointment.date) }}, {{ formatTime(lastAppointment.time) }}
                </p>
                <p v-else class="text-sm text-gray-500 mt-1">Your appointment history will appear here</p>
              </div>
            </div>
          </section>
        </main>
      </q-page>
    </q-page-container>

    <!-- Bottom Navigation with closer spacing -->
    <nav class="fixed bottom-0 left-0 right-0 bg-teal-800 text-white z-40 shadow-lg" style="padding-bottom: env(safe-area-inset-bottom);">
      <div class="flex justify-center px-2 py-2">
        <div class="flex items-center space-x-8">
          <button class="flex flex-col items-center text-white hover:bg-teal-700 p-2 rounded-lg transition-colors" @click="navigateTo('/patient-queue')">
            <i data-lucide="list-ordered" class="w-5 h-5"></i>
            <span class="text-xs mt-1">Queue</span>
          </button>
          <button class="flex flex-col items-center text-white hover:bg-teal-700 p-2 rounded-lg transition-colors" @click="navigateTo('/patient-appointments')">
            <i data-lucide="calendar-check" class="w-5 h-5"></i>
            <span class="text-xs mt-1">Appointments</span>
          </button>
          <button class="flex flex-col items-center text-white hover:bg-teal-700 p-2 rounded-lg transition-colors" @click="navigateTo('/patient-dashboard')">
            <i data-lucide="home" class="w-5 h-5"></i>
            <span class="text-xs mt-1">Home</span>
          </button>
          <button class="flex flex-col items-center text-white hover:bg-teal-700 p-2 rounded-lg transition-colors" @click="navigateTo('/patient-notifications')">
            <i data-lucide="bell" class="w-5 h-5"></i>
            <span class="text-xs mt-1">Alerts</span>
          </button>
          <button class="flex flex-col items-center text-white hover:bg-teal-700 p-2 rounded-lg transition-colors" @click="navigateTo('/patient-medical-request')">
            <i data-lucide="message-square" class="w-5 h-5"></i>
            <span class="text-xs mt-1">Requests</span>
          </button>
        </div>
      </div>
    </nav>

    <!-- Next Appointment Modal -->
    <q-dialog v-model="showNextApptModal" persistent>
      <q-card class="w-[560px] max-w-full rounded-2xl">
        <q-card-section>
          <div class="text-xl font-bold text-teal-700">Next Appointment Details</div>
        </q-card-section>
        <q-card-section>
          <div class="rounded-xl border border-teal-200 bg-teal-50 p-4">
            <p class="text-teal-800 font-semibold mb-3">Appointment Information:</p>
            <div class="space-y-3">
              <div class="flex justify-between items-center p-3 bg-white rounded-lg">
                <span class="font-semibold text-teal-800">Type:</span>
                <span class="text-gray-700">{{ getAppointmentTypeLabel(nextAppointment?.type || '') }}</span>
              </div>
              
              <div class="flex justify-between items-center p-3 bg-white rounded-lg">
                <span class="font-semibold text-teal-800">Department:</span>
                <span class="text-gray-700">{{ getDepartmentLabel(nextAppointment?.department || '') }}</span>
              </div>
              
              <div class="flex justify-between items-center p-3 bg-white rounded-lg">
                <span class="font-semibold text-teal-800">Doctor:</span>
                <span class="text-gray-700">Dr. {{ (nextAppointment && nextAppointment.doctor) || 'Amelia Chen' }}</span>
              </div>
              
              <div class="flex justify-between items-center p-3 bg-white rounded-lg">
                <span class="font-semibold text-teal-800">Date:</span>
                <span class="text-gray-700">{{ formatLongDate(nextAppointment?.date || '') }}</span>
              </div>
              
              <div class="flex justify-between items-center p-3 bg-white rounded-lg">
                <span class="font-semibold text-teal-800">Time:</span>
                <span class="text-gray-700">{{ formatTime(nextAppointment?.time || '') }}</span>
              </div>
              
              <div class="flex justify-between items-center p-3 bg-white rounded-lg">
                <span class="font-semibold text-teal-800">Reason:</span>
                <span class="text-gray-700">{{ nextAppointment?.reason || '—' }}</span>
              </div>
              
              <div class="flex justify-between items-center p-3 bg-white rounded-lg">
                <span class="font-semibold text-teal-800">Status:</span>
                <span class="text-teal-700 font-medium">{{ capitalize(nextAppointment?.status || 'Upcoming') }}</span>
              </div>
            </div>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn color="primary" label="Close" class="px-6" @click="showNextApptModal = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'src/boot/axios'
import logoUrl from 'src/assets/logo.png'

const router = useRouter()

const showUserMenu = ref(false)
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

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