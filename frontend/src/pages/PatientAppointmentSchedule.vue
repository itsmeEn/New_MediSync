<template>
  <q-layout view="hHh lpR fFf">
    <!-- Header (aligned to Random.html) -->
    <header class="bg-teal-800 p-4 md:p-6 shadow-lg">
      <div class="flex justify-between items-center max-w-7xl mx-auto">
        <!-- Logo + Title -->
        <div class="flex items-center space-x-3 text-white">
          <img :src="logoUrl" alt="Project Logo" class="h-10 w-10 rounded-full bg-white object-cover flex-shrink-0" />
          <div>
            <p class="text-lg font-semibold leading-none">{{ isReschedule ? 'Reschedule Appointment' : 'Schedule Appointment' }}</p>
            <p class="text-sm font-light text-teal-300 leading-none">Book your visit</p>
          </div>
        </div>
        <!-- Right: Notification + User -->
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
            <!-- Dropdown -->
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
        <div class="max-w-4xl mx-auto">
          <!-- Enhanced Appointment Form -->
          <div class="bg-white rounded-xl shadow-xl p-6 md:p-8">
            <div class="mb-4">
              <q-btn flat color="teal-700" icon="arrow_back" label="Back" @click="navigateTo('/patient-appointments')" />
            </div>
            <div class="text-center mb-8">
              <h1 class="text-2xl font-bold text-teal-700 mb-2">{{ isReschedule ? 'Reschedule Appointment' : 'Schedule New Appointment' }}</h1>
              <p class="text-gray-600">Please fill out all the required information</p>
            </div>

            <q-form ref="formRef" @submit="onSubmit" class="space-y-6">
              <!-- Appointment Type -->
              <div class="relative">
                <label class="block text-sm font-semibold text-teal-600 mb-2">Appointment Type</label>
                <q-select 
                  v-model="form.type" 
                  :options="typeOptions" 
                  label="Select Appointment Type" 
                  emit-value 
                  map-options 
                  :rules="[val => !!val || 'Type is required']"
                  class="w-full"
                  outlined
                  color="teal"
                />
              </div>

              <!-- Department -->
              <div class="relative">
                <label class="block text-sm font-semibold text-teal-600 mb-2">Department</label>
                <q-select 
                  v-model="form.department" 
                  :options="departmentOptions" 
                  label="Select Department" 
                  emit-value 
                  map-options 
                  :rules="[val => !!val || 'Department is required']"
                  class="w-full"
                  outlined
                  color="teal"
                />
              </div>

              <!-- Date and Time Row -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Date -->
                <div class="relative">
                  <label class="block text-sm font-semibold text-teal-600 mb-2">Date</label>
                  <q-input 
                    v-model="form.date" 
                    label="mm/dd/yyyy"
                    :rules="[val => !!val || 'Date is required']"
                    outlined
                    color="teal"
                    readonly
                  >
                    <template #append>
                      <q-icon name="event" class="cursor-pointer text-teal-600">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                          <q-date v-model="form.date" mask="MM/DD/YYYY" color="teal" />
                        </q-popup-proxy>
                      </q-icon>
                    </template>
                  </q-input>
                </div>

                <!-- Time -->
                <div class="relative">
                  <label class="block text-sm font-semibold text-teal-600 mb-2">Time (24-hour format)</label>
                  <q-select 
                    v-model="form.time" 
                    :options="timeOptions" 
                    label="Select Time" 
                    emit-value 
                    map-options 
                    :rules="[val => !!val || 'Time is required']"
                    outlined
                    color="teal"
                  />
                </div>
              </div>

              <!-- Reason -->
              <div class="relative">
                <label class="block text-sm font-semibold text-teal-600 mb-2">Reason for Appointment</label>
                <q-input 
                  v-model="form.reason" 
                  label="Please describe the reason for your appointment" 
                  type="textarea" 
                  :rules="[val => !!val || 'Reason is required']"
                  outlined
                  color="teal"
                  rows="3"
                />
              </div>

              <!-- Action Buttons -->
              <div class="flex flex-col sm:flex-row gap-4 pt-6">
                <q-btn 
                  type="submit" 
                  color="teal" 
                  size="lg"
                  class="flex-1"
                  :label="isReschedule ? 'Reschedule Appointment' : 'Schedule Appointment'"
                />
                <q-btn 
                  flat 
                  color="grey-7" 
                  size="lg"
                  class="flex-1"
                  label="Cancel" 
                  @click="navigateTo('/patient-appointments')"
                />
              </div>
            </q-form>
          </div>
        </div>
      </q-page>
    </q-page-container>

    <!-- Enhanced Confirmation Summary Modal -->
    <q-dialog v-model="showConfirm">
      <q-card style="min-width: 400px; max-width: 500px">
        <q-card-section class="text-center">
          <div class="text-h6 text-teal-700 font-bold">{{ isReschedule ? 'Reschedule Appointment' : 'Confirm Appointment' }}</div>
          <div class="text-caption text-gray-600">Please review the details and confirm</div>
        </q-card-section>
        <q-separator />
        <q-card-section>
          <div class="space-y-3">
            <div class="flex justify-between items-center p-3 bg-teal-50 rounded-lg">
              <span class="font-semibold text-teal-800">Type:</span>
              <span class="text-gray-700">{{ labelFor(typeOptions, form.type) }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-teal-50 rounded-lg">
              <span class="font-semibold text-teal-800">Department:</span>
              <span class="text-gray-700">{{ labelFor(departmentOptions, form.department) }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-teal-50 rounded-lg">
              <span class="font-semibold text-teal-800">Doctor:</span>
              <span class="text-gray-700">Dr. Amelia Chen</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-teal-50 rounded-lg">
              <span class="font-semibold text-teal-800">Date:</span>
              <span class="text-gray-700">{{ formatDisplayDate(form.date) }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-teal-50 rounded-lg">
              <span class="font-semibold text-teal-800">Time:</span>
              <span class="text-gray-700">{{ form.time }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-teal-50 rounded-lg">
              <span class="font-semibold text-teal-800">Reason:</span>
              <span class="text-gray-700">{{ form.reason || '—' }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-teal-50 rounded-lg">
              <span class="font-semibold text-teal-800">Status:</span>
              <span class="text-teal-700 font-medium">Upcoming</span>
            </div>
          </div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat color="grey-7" label="Edit" v-close-popup />
          <q-btn color="teal" :label="isReschedule ? 'Reschedule' : 'Confirm'" @click="confirmSchedule" />
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
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from 'src/boot/axios'
import type { Appointment } from 'src/stores/appointments'
import logoUrl from 'src/assets/logo.png'

const router = useRouter()
const route = useRoute()
const formRef = ref()
const showUserMenu = ref(false)
const unreadCount = ref<number>(0)
const showConfirm = ref(false)
const showSuccessTooltip = ref(false)
const successMessage = ref('')
const successTooltipClass = ref('')

const form = ref({
  type: '',
  department: '',
  date: '',
  time: '',
  reason: ''
})

const isReschedule = computed(() => {
  return !!route.query.id
})

const typeOptions = [
  { label: 'General Consultation', value: 'general-consultation' },
  { label: 'Follow-up Visit', value: 'follow-up' },
  { label: 'Lab Test', value: 'lab-test' },
  { label: 'Specialist Consultation', value: 'specialist-consultation' },
  { label: 'Emergency Visit', value: 'emergency' },
  { label: 'Vaccination', value: 'vaccination' },
  { label: 'Physical Examination', value: 'physical-exam' },
  { label: 'Mental Health Consultation', value: 'mental-health' }
]

const departmentOptions = [
  { label: 'General Medicine', value: 'general-medicine' },
  { label: 'Cardiology', value: 'cardiology' },
  { label: 'Dermatology', value: 'dermatology' },
  { label: 'Orthopedics', value: 'orthopedics' },
  { label: 'Pediatrics', value: 'pediatrics' },
  { label: 'Gynecology', value: 'gynecology' },
  { label: 'Neurology', value: 'neurology' },
  { label: 'Oncology', value: 'oncology' },
  { label: 'Emergency Medicine', value: 'emergency-medicine' }
]

// Generate 24-hour time options with 1-hour intervals
const timeOptions = computed(() => {
  const times = []
  for (let hour = 0; hour < 24; hour++) {
    const timeString = hour.toString().padStart(2, '0') + ':00'
    const displayTime = hour === 0 ? '12:00 AM' : 
                       hour < 12 ? `${hour}:00 AM` : 
                       hour === 12 ? '12:00 PM' : 
                       `${hour - 12}:00 PM`
    times.push({ label: displayTime, value: timeString })
  }
  return times
})

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

const toggleUserMenu = () => { showUserMenu.value = !showUserMenu.value }

// Initialize appointments database if not exists
const initializeAppointmentsDB = () => {
  if (!localStorage.getItem('appointments')) {
    const defaultAppointments = [
      {
        id: 1,
        type: 'general-consultation',
        department: 'general-medicine',
        date: new Date(Date.now() + 86400000).toISOString(),
        time: '09:00',
        reason: 'Regular checkup',
        status: 'upcoming'
      },
      {
        id: 2,
        type: 'follow-up',
        department: 'cardiology',
        date: new Date(Date.now() - 172800000).toISOString(),
        time: '14:00',
        reason: 'Follow-up on heart condition',
        status: 'completed'
      }
    ]
    localStorage.setItem('appointments', JSON.stringify(defaultAppointments))
  }
}

// Get appointments from localStorage
const getAppointments = (): Appointment[] => {
  const appointments = localStorage.getItem('appointments')
  return appointments ? JSON.parse(appointments) : []
}

// Save appointment to localStorage
const saveAppointment = (appointment: Partial<Appointment>): Appointment => {
  const appointments = getAppointments()
  const newAppointment: Appointment = {
    id: Date.now(),
    department: appointment.department || '',
    type: appointment.type || '',
    date: appointment.date || '',
    time: appointment.time || '',
    status: 'upcoming' as const
  }
  
  // Add optional properties if they exist
  if (appointment.reason) newAppointment.reason = appointment.reason
  if (appointment.doctor) newAppointment.doctor = appointment.doctor
  if (appointment.archived !== undefined) newAppointment.archived = appointment.archived
  
  appointments.push(newAppointment)
  localStorage.setItem('appointments', JSON.stringify(appointments))
  return newAppointment
}

// Update appointment in localStorage
const updateAppointment = (id: number, updates: Partial<Appointment>): boolean => {
  const appointments = getAppointments()
  const index = appointments.findIndex((a: Appointment) => a.id === id)
  if (index !== -1 && appointments[index]) {
    Object.assign(appointments[index], updates)
    localStorage.setItem('appointments', JSON.stringify(appointments))
    return true
  }
  return false
}

// Show success tooltip
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

// Format date for display
const formatDisplayDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

function toISOFromMDY(mdy: string): string {
  const parts = mdy?.split('/') ?? []
  if (parts.length === 3) {
    const [mm, dd, yyyy] = parts
    const y = Number(yyyy), m = Number(mm), d = Number(dd)
    if (!Number.isNaN(y) && !Number.isNaN(m) && !Number.isNaN(d)) {
      const dt = new Date(y, m - 1, d)
      return dt.toISOString()
    }
  }
  const dt = new Date(mdy)
  return isNaN(dt.getTime()) ? new Date().toISOString() : dt.toISOString()
}

function toMDYFromISO(iso: string): string {
  const dt = new Date(iso)
  if (isNaN(dt.getTime())) return iso
  const mm = String(dt.getMonth() + 1).padStart(2, '0')
  const dd = String(dt.getDate()).padStart(2, '0')
  const yyyy = dt.getFullYear()
  return `${mm}/${dd}/${yyyy}`
}

onMounted(() => {
  initializeAppointmentsDB()
  
  // If rescheduling, prefill form using existing appointment from localStorage
  const id = route.query.id
  if (id) {
    const appointments = getAppointments()
    const appt = appointments.find((a: Appointment) => String(a.id) === String(id))
    if (appt) {
      form.value.type = appt.type
      form.value.department = appt.department
      form.value.time = appt.time
      form.value.date = toMDYFromISO(appt.date)
      form.value.reason = appt.reason || ''
    }
  }
  
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
  
  void fetchUnreadCount()
})

const fetchUnreadCount = async () => {
  try {
    const res = await api.get('/patient/notifications/unread-count/')
    unreadCount.value = res.data?.count ?? 0
  } catch {
    unreadCount.value = 0
  }
}

const onSubmit = async () => {
  const valid = await formRef.value?.validate?.()
  if (valid === false) return
  // open confirmation
  showConfirm.value = true
}

const confirmSchedule = async () => {
  try {
    const payload = { ...form.value, date: toISOFromMDY(form.value.date) }
    await api.post('/appointments/schedule/', payload)
    showSuccessTooltipFunc('Appointment successfully booked!')
  } catch (e) {
    console.warn('Failed to schedule appointment via API, saving locally', e)
    const id = route.query.id
    if (id) {
      const success = updateAppointment(Number(id), {
        type: form.value.type,
        department: form.value.department,
        date: toISOFromMDY(form.value.date),
        time: form.value.time,
        reason: form.value.reason,
        status: 'upcoming'
      })
      if (success) {
        showSuccessTooltipFunc('Appointment successfully rescheduled!')
      }
    } else {
      saveAppointment({
        type: form.value.type,
        department: form.value.department,
        date: toISOFromMDY(form.value.date),
        time: form.value.time,
        reason: form.value.reason
      })
      showSuccessTooltipFunc('Appointment successfully booked!')
    }
  }
  showConfirm.value = false
  
  // Navigate back to appointments after a short delay
  setTimeout(() => {
    void router.push('/patient-appointments')
  }, 1500)
}

const navigateTo = (path: string) => {
  void router.push(path)
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  void router.push('/login')
}

function labelFor(options: Array<{label:string,value:string}>, value: string) {
  const opt = options.find(o => o.value === value)
  return opt ? opt.label : value
}
</script>

<style scoped>
.card { border-radius: 0.75rem; }
</style>