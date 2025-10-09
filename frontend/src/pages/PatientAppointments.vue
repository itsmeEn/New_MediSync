<template>
  <q-layout view="hHh lpR fFf">
    <!-- Tailwind-based Header replicating Random.html -->
    <header class="bg-teal-800 p-4 md:p-6 shadow-lg">
      <div class="flex justify-between items-center max-w-7xl mx-auto">
        <!-- Left: Logo + Title -->
        <div class="flex items-center space-x-3 text-white">
          <img :src="logoUrl" alt="Project Logo" class="h-10 w-10 rounded-full bg-white object-cover flex-shrink-0" />
          <div>
            <p class="text-lg font-semibold leading-none">Patient Portal</p>
            <p class="text-sm font-light text-teal-300 leading-none">Healthcare Dashboard</p>
          </div>
        </div>
        
        <!-- Right: Notification Bell + User Profile -->
        <div class="flex items-center space-x-2">
          <button class="relative p-2 rounded-lg hover:bg-teal-700 text-white" @click="navigateTo('/patient-notifications')">
            <i data-lucide="bell" class="w-5 h-5"></i>
            <span v-if="unreadCount > 0" class="absolute -top-1 -right-1 bg-red-600 text-white text-xs rounded-full px-1">{{ unreadCount }}</span>
          </button>
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

    <q-page-container>
      <q-page class="bg-teal-50 q-pa-md pb-safe">
        <div class="max-w-7xl mx-auto">
          <!-- Page Title matching Random.html -->
          <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4 md:mb-6">Manage Your Appointments</h1>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Left: New Appointment card -->
            <div class="md:col-span-1">
              <div class="bg-teal-700 text-white rounded-xl shadow-xl p-6 flex flex-col justify-between h-full">
                <div>
                  <div class="flex items-center gap-3 mb-4">
                    <i data-lucide="calendar-plus" class="w-6 h-6"></i>
                    <p class="text-xl font-semibold">New Appointment</p>
                  </div>
                  <p class="text-sm text-teal-100">Schedule your next consultation, lab test, or procedure quickly.</p>
                </div>
                <div class="mt-6">
                  <button class="w-full bg-white text-teal-700 font-semibold px-4 py-3 rounded-lg shadow hover:shadow-md transition" @click="navigateTo('/patient-appointment-schedule')">Book Now</button>
                </div>
              </div>
            </div>

            <!-- Right: Upcoming list + filters -->
            <div class="md:col-span-2">
              <div class="bg-white rounded-xl shadow-xl p-6">
                <!-- Segmented pills container -->
                <div class="inline-flex border border-gray-300 rounded-xl overflow-hidden mb-4">
                  <button :class="['px-4 py-2 text-sm font-medium', selectedStatus === 'upcoming' ? 'bg-teal-600 text-white' : 'bg-white text-gray-700']" @click="selectedStatus = 'upcoming'">Upcoming</button>
                  <button :class="['px-4 py-2 text-sm font-medium border-l border-gray-300', selectedStatus === 'completed' ? 'bg-teal-600 text-white' : 'bg-white text-gray-700']" @click="selectedStatus = 'completed'">Completed</button>
                  <button :class="['px-4 py-2 text-sm font-medium border-l border-gray-300', selectedStatus === 'cancelled' ? 'bg-teal-600 text-white' : 'bg-white text-gray-700']" @click="selectedStatus = 'cancelled'">Cancelled</button>
                </div>

                <h2 class="text-xl font-semibold text-gray-900 mb-3">{{ capitalize(selectedStatus) }} Appointments ({{ filteredAppointments.length }})</h2>

                <!-- List -->
                <div class="space-y-3">
                  <div v-for="appt in filteredAppointments" :key="appt.id" class="bg-teal-50 rounded-lg p-4 shadow-sm border border-teal-100 hover:bg-teal-100/60 transition cursor-pointer" @click="openAppointment(appt)">
                    <div class="flex items-center justify-between">
                      <div class="flex-1">
                        <div class="flex gap-2">
                          <span class="w-1 rounded bg-teal-600"></span>
                          <div>
                            <p class="font-semibold text-gray-900">{{ appt.type || 'Appointment' }}</p>
                            <p class="text-sm text-gray-700">{{ appt.department }} | {{ formatDate(appt.date) }} at {{ appt.time }}</p>
                          </div>
                        </div>
                      </div>
                      <div class="flex items-center gap-2">
                        <q-btn dense round flat icon="edit" color="teal" v-if="appt.status === 'upcoming'" @click.stop="openEdit(appt)">
                          <q-tooltip>Edit</q-tooltip>
                        </q-btn>
                        <i data-lucide="chevron-right" class="w-5 h-5 text-teal-700"></i>
                      </div>
                    </div>
                  </div>

                  <div v-if="filteredAppointments.length === 0" class="text-center text-gray-500 text-sm py-6">
                    No appointments found.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </q-page>
    </q-page-container>

    <!-- Cancel Confirmation Modal -->
    <q-dialog v-model="showCancelDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">Cancel Appointment</div>
          <div class="text-caption">Are you sure you want to cancel this appointment?</div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right">
          <q-btn flat color="grey" label="Close" v-close-popup />
          <q-btn color="negative" label="Cancel Appointment" @click="confirmCancel" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Reschedule Modal -->
    <q-dialog v-model="showRescheduleDialog">
      <q-card style="min-width: 320px">
        <q-card-section>
          <div class="text-h6">Reschedule Appointment</div>
          <div class="text-caption">Do you want to reschedule with the same cancelled time or create a new appointment?</div>
        </q-card-section>
        <q-separator />
        <q-card-section>
          <div class="q-gutter-sm">
            <q-option-group v-model="rescheduleChoice" type="radio" :options="[
              { label: 'Same time, choose new date', value: 'same_time' },
              { label: 'Create new appointment', value: 'new_appt' }
            ]" />
            <div v-if="rescheduleChoice === 'same_time'" class="q-mt-sm">
              <q-input v-model="rescheduleDate" label="New Date" mask="####-##-##" placeholder="YYYY-MM-DD" />
            </div>
          </div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right">
          <q-btn flat color="grey" label="Close" v-close-popup />
          <q-btn color="primary" label="Save" @click="confirmReschedule" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Enhanced Cancellation Confirmation Modal -->
    <q-dialog v-model="showCancelDialog">
      <q-card style="min-width: 400px; max-width: 500px">
        <q-card-section class="text-center">
          <div class="text-h6 text-red-700 font-bold">Cancel Appointment</div>
          <div class="text-caption text-gray-600">Are you sure you want to cancel this appointment?</div>
        </q-card-section>
        <q-separator />
        <q-card-section v-if="selectedAppointment">
          <div class="space-y-3">
            <div class="flex justify-between items-center p-3 bg-red-50 rounded-lg">
              <span class="font-semibold text-red-800">Type:</span>
              <span class="text-gray-700">{{ getAppointmentTypeLabel(selectedAppointment.type) }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-red-50 rounded-lg">
              <span class="font-semibold text-red-800">Department:</span>
              <span class="text-gray-700">{{ getDepartmentLabel(selectedAppointment.department) }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-red-50 rounded-lg">
              <span class="font-semibold text-red-800">Date:</span>
              <span class="text-gray-700">{{ formatDate(selectedAppointment.date) }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-red-50 rounded-lg">
              <span class="font-semibold text-red-800">Time:</span>
              <span class="text-gray-700">{{ selectedAppointment.time }}</span>
            </div>
          </div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat color="grey-7" label="Keep Appointment" v-close-popup />
          <q-btn color="red" label="Yes, Cancel" @click="confirmCancel" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Reschedule Options Modal -->
    <q-dialog v-model="showRescheduleDialog">
      <q-card style="min-width: 400px; max-width: 500px">
        <q-card-section class="text-center">
          <div class="text-h6 text-teal-700 font-bold">Reschedule Options</div>
          <div class="text-caption text-gray-600">Do you want to reschedule with the same time or create a new appointment?</div>
        </q-card-section>
        <q-separator />
        <q-card-section>
          <div class="space-y-4">
            <q-btn 
              color="teal" 
              outline 
              class="w-full" 
              @click="rescheduleWithSameTime"
            >
              <div class="flex items-center gap-2">
                <i data-lucide="calendar" class="w-4 h-4"></i>
                <span>Reschedule with Same Time</span>
              </div>
            </q-btn>
            <q-btn 
              color="teal" 
              outline 
              class="w-full" 
              @click="createNewAppointment"
            >
              <div class="flex items-center gap-2">
                <i data-lucide="plus" class="w-4 h-4"></i>
                <span>Create New Appointment</span>
              </div>
            </q-btn>
          </div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat color="grey-7" label="Close" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Calendar Modal for Reschedule -->
    <q-dialog v-model="showCalendarDialog">
      <q-card style="min-width: 350px">
        <q-card-section class="text-center">
          <div class="text-h6 text-teal-700 font-bold">Select New Date</div>
          <div class="text-caption text-gray-600">Choose a new date for your appointment</div>
        </q-card-section>
        <q-separator />
        <q-card-section>
          <q-input 
            v-model="rescheduleDate" 
            label="New Date" 
            mask="####-##-##" 
            placeholder="YYYY-MM-DD"
            outlined
            color="teal"
          >
            <template #append>
              <q-icon name="event" class="cursor-pointer text-teal-600" />
            </template>
          </q-input>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat color="grey-7" label="Cancel" v-close-popup />
          <q-btn color="teal" label="Confirm Reschedule" @click="confirmRescheduleWithSameTime" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Edit Appointment Dialog -->
    <q-dialog v-model="showEditDialog">
      <q-card style="min-width: 350px; max-width: 500px">
        <q-card-section class="text-center">
          <div class="text-h6 text-teal-700 font-bold">Edit Appointment</div>
          <div class="text-caption text-gray-600">Update date and time for your upcoming appointment</div>
        </q-card-section>
        <q-separator />
        <q-card-section>
          <div class="q-gutter-md">
            <q-input v-model="editDate" label="New Date" mask="####-##-##" placeholder="YYYY-MM-DD" outlined color="teal" />
            <q-select 
              v-model="editTime" 
              :options="[...Array(24)].map((_, hour) => ({ label: `${String(hour).padStart(2,'0')}:00`, value: `${String(hour).padStart(2,'0')}:00` }))" 
              label="New Time" 
              outlined 
              color="teal" 
            />
          </div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat color="grey-7" label="Cancel" v-close-popup />
          <q-btn color="teal" label="Save Changes" @click="confirmEdit" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Success Tooltip -->
    <div v-if="showSuccessTooltip" class="fixed top-4 right-4 z-50 bg-teal-600 text-white px-6 py-3 rounded-lg shadow-lg transform transition-all duration-300 ease-in-out" :class="successTooltipClass">
      <div class="flex items-center space-x-2">
        <i data-lucide="check-circle" class="w-5 h-5"></i>
        <span class="font-semibold">{{ successMessage }}</span>
      </div>
    </div>

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
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'src/boot/axios'
import logoUrl from 'src/assets/logo.png'
import { useAppointmentsStore } from '../stores/appointments'

const router = useRouter()
// removed: const activeTab = ref('appointments')
const selectedStatus = ref<'upcoming' | 'completed' | 'cancelled'>('upcoming')
const search = ref('')
// const appointments = ref<Appointment[]>([])
const appointmentsStore = useAppointmentsStore()
const unreadCount = ref<number>(0)
const showUserMenu = ref(false)
const toggleUserMenu = () => { showUserMenu.value = !showUserMenu.value }

interface Appointment {
  id: number
  department: string
  type: string
  date: string
  time: string
  status: 'upcoming' | 'completed' | 'cancelled'
  archived?: boolean
}

const selectedAppointment = ref<Appointment | null>(null)
const showCancelDialog = ref(false)
const showRescheduleDialog = ref(false)
const showCalendarDialog = ref(false)
const rescheduleChoice = ref<'same_time' | 'new_appt'>('same_time')
const rescheduleDate = ref('')
const showSuccessTooltip = ref(false)
const successMessage = ref('')
const successTooltipClass = ref('')

// Edit modal state
const showEditDialog = ref(false)
const editDate = ref('')
const editTime = ref('')
const editingAppointmentId = ref<number | null>(null)

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

// Declare window interface for lucide
interface WindowWithLucide extends Window {
  lucide?: {
    createIcons(): void
  }
}

onMounted(async () => {
  await fetchAppointments()
  await fetchUnreadCount()
  try { ;(window as WindowWithLucide).lucide?.createIcons() } catch { /* ignore if lucide not available */ void 0 }
})

const fetchAppointments = async () => {
  try {
    await appointmentsStore.loadAppointments()
  } catch (e) {
    console.warn('Failed to load appointments', e)
  }
}

const fetchUnreadCount = async () => {
  try {
    const res = await api.get('/patient/notifications/unread-count/')
    unreadCount.value = res.data?.count ?? 0
  } catch {
    unreadCount.value = 0
  }
}

const filteredAppointments = computed(() => {
  const list = appointmentsStore.appointments
    .filter((a: Appointment) => !a.archived)
    .filter((a: Appointment) => a.status === selectedStatus.value)
    .filter((a: Appointment) => {
      const q = search.value.trim().toLowerCase()
      if (!q) return true
      return (
        a.department.toLowerCase().includes(q) ||
        a.type.toLowerCase().includes(q) ||
        formatDate(a.date).toLowerCase().includes(q) ||
        a.time.toLowerCase().includes(q)
      )
    })
  return list as unknown as Appointment[]
})


const formatDate = (iso: string) => {
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1)

const navigateTo = (path: string) => {
  void router.push(path)
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  void router.push('/')
}

function openAppointment(appt: Appointment) {
  selectedAppointment.value = appt
  if (appt.status === 'upcoming') {
    showCancelDialog.value = true
  } else if (appt.status === 'cancelled') {
    showRescheduleDialog.value = true
  }
}

async function confirmCancel() {
  if (!selectedAppointment.value) return
  await appointmentsStore.updateStatus(selectedAppointment.value.id, 'cancelled')
  showSuccessTooltipFunc('Appointment cancelled successfully!')
  selectedStatus.value = 'cancelled'
  showCancelDialog.value = false
  selectedAppointment.value = null
}

function rescheduleWithSameTime() {
  showRescheduleDialog.value = false
  showCalendarDialog.value = true
}

function createNewAppointment() {
  if (!selectedAppointment.value) return
  appointmentsStore.archiveAppointment(selectedAppointment.value.id)
  showRescheduleDialog.value = false
  selectedAppointment.value = null
  navigateTo('/patient-appointment-schedule')
}

function confirmReschedule() {
  if (rescheduleChoice.value === 'same_time') {
    rescheduleWithSameTime()
  } else if (rescheduleChoice.value === 'new_appt') {
    createNewAppointment()
  } else {
    showRescheduleDialog.value = false
  }
}

async function confirmRescheduleWithSameTime() {
  if (!selectedAppointment.value || !rescheduleDate.value) return
  await appointmentsStore.rescheduleSameTime(selectedAppointment.value.id, rescheduleDate.value)
  showSuccessTooltipFunc('Appointment rescheduled successfully!')
  selectedStatus.value = 'upcoming'
  showCalendarDialog.value = false
  selectedAppointment.value = null
  rescheduleDate.value = ''
}

// Edit: open and confirm
function openEdit(appt: Appointment) {
  editingAppointmentId.value = appt.id
  // Prefill with current values
  const d = new Date(appt.date)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  editDate.value = `${yyyy}-${mm}-${dd}`
  editTime.value = appt.time
  showEditDialog.value = true
}

async function confirmEdit() {
  if (!editingAppointmentId.value) return
  const isoDate = new Date(editDate.value).toISOString()
  await appointmentsStore.updateFields(editingAppointmentId.value, { date: isoDate, time: editTime.value })
  showSuccessTooltipFunc('Appointment updated successfully!')
  showEditDialog.value = false
  editingAppointmentId.value = null
}

// Success tooltip
const showSuccessTooltipFunc = (message: string) => {
  successMessage.value = message
  showSuccessTooltip.value = true
  successTooltipClass.value = 'translate-y-0 opacity-100'
  setTimeout(() => {
    successTooltipClass.value = 'translate-y-2 opacity-0'
    setTimeout(() => {
      showSuccessTooltip.value = false
    }, 300)
  }, 3000)
}

// Get appointment type label
const getAppointmentTypeLabel = (type: string) => {
  const typeMap: { [key: string]: string } = {
    'general-consultation': 'General Consultation',
    'follow-up': 'Follow-up Visit',
    'lab-test': 'Lab Test',
    'specialist-consultation': 'Specialist Consultation',
    'emergency': 'Emergency Visit',
    'vaccination': 'Vaccination',
    'physical-exam': 'Physical Examination',
    'mental-health': 'Mental Health Consultation'
  }
  return typeMap[type] || type
}

// Get department label
const getDepartmentLabel = (department: string) => {
  const deptMap: { [key: string]: string } = {
    'general-medicine': 'General Medicine',
    'cardiology': 'Cardiology',
    'dermatology': 'Dermatology',
    'orthopedics': 'Orthopedics',
    'pediatrics': 'Pediatrics',
    'gynecology': 'Gynecology',
    'neurology': 'Neurology',
    'oncology': 'Oncology',
    'emergency-medicine': 'Emergency Medicine'
  }
  return deptMap[department] || department
}
</script>

<style scoped>
/* subtle hover for list items */
.q-item:hover { background-color: #f9fafb; }
</style>