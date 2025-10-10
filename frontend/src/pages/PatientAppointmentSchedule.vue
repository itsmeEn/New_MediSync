<template>
  <q-layout view="lHh Lpr lFf">
    <!-- Patient Portal Header -->
    <q-header class="bg-primary text-white">
      <q-toolbar>
        <q-avatar size="40px" class="q-mr-md">
          <img :src="logoUrl" alt="MediSync Logo" />
        </q-avatar>
        
        <div class="header-content">
          <div class="text-h6 text-weight-bold">Patient Portal</div>
          <div class="text-caption">Healthcare Dashboard</div>
        </div>

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
      <q-page class="bg-grey-1 q-pa-md pb-safe">
        <div class="max-w-4xl mx-auto">
          <!-- Enhanced Appointment Form -->
          <q-card class="q-mb-md">
            <q-card-section>
              <div class="row items-center q-mb-md">
                <q-btn flat color="teal-700" icon="arrow_back" label="Back" @click="navigateTo('/patient-appointments')" class="q-mb-md" />
              </div>
              
              <div class="row items-center q-mb-md">
                <q-avatar color="teal-1" text-color="teal" icon="event_available" size="48px" class="q-mr-md" />
                <div>
                  <div class="text-h6 text-weight-bold">
                    {{ isReschedule ? 'Reschedule Appointment' : 'Schedule New Appointment' }}
                  </div>
                  <div class="text-caption text-grey-6">
                    Please fill out all the required information
                  </div>
                </div>
              </div>

              <q-form ref="formRef" @submit="onSubmit" class="q-gutter-md">
                <!-- Appointment Type -->
                <q-select 
                  v-model="form.type" 
                  :options="typeOptions" 
                  label="Appointment Type" 
                  emit-value 
                  map-options 
                  :rules="[val => !!val || 'Type is required']"
                  outlined
                  color="teal"
                  behavior="menu"
                />

                <!-- Department -->
                <q-select 
                  v-model="form.department" 
                  :options="departmentOptions" 
                  label="Department" 
                  emit-value 
                  map-options 
                  :rules="[val => !!val || 'Department is required']"
                  outlined
                  color="teal"
                  behavior="menu"
                />

                <!-- Date and Time Row -->
                <div class="row q-gutter-md">
                  <!-- Date -->
                  <div class="col-12 col-md-6">
                    <q-input 
                      v-model="form.date" 
                      label="Date (mm/dd/yyyy)"
                      :rules="[val => !!val || 'Date is required']"
                      outlined
                      color="teal"
                      readonly
                    >
                      <template #append>
                        <q-icon name="event" class="cursor-pointer">
                          <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                            <q-date v-model="form.date" mask="MM/DD/YYYY" color="teal" today-btn minimal>
                              <div class="row items-center justify-end">
                                <q-btn v-close-popup label="Close" color="primary" flat />
                              </div>
                            </q-date>
                          </q-popup-proxy>
                        </q-icon>
                      </template>
                    </q-input>
                  </div>

                  <!-- Time -->
                  <div class="col-12 col-md-6">
                    <q-select 
                      v-model="form.time" 
                      :options="timeOptions" 
                      label="Time (24-hour format)" 
                      emit-value 
                      map-options 
                      :rules="[val => !!val || 'Time is required']"
                      outlined
                      color="teal"
                      behavior="menu"
                    />
                  </div>
                </div>

                <!-- Reason -->
                <q-input 
                  v-model="form.reason" 
                  label="Reason for Appointment" 
                  type="textarea" 
                  :rules="[val => !!val || 'Reason is required']"
                  outlined
                  color="teal"
                  rows="3"
                  autogrow
                  placeholder="Please describe the reason for your appointment"
                />

                <!-- Action Buttons -->
                <div class="row q-gutter-sm q-mt-md">
                  <div class="col-12">
                    <q-btn 
                      type="submit" 
                      color="teal" 
                      size="lg"
                      class="full-width q-mb-sm"
                      :label="isReschedule ? 'Reschedule Appointment' : 'Schedule Appointment'"
                      unelevated
                    />
                  </div>
                  <div class="col-12">
                    <q-btn 
                      flat 
                      color="grey-7" 
                      size="lg"
                      class="full-width"
                      label="Cancel" 
                      @click="navigateTo('/patient-appointments')"
                    />
                  </div>
                </div>
              </q-form>
            </q-card-section>
          </q-card>
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
    <q-tooltip v-if="showSuccessTooltip" class="bg-green-500 text-white">
      Appointment scheduled successfully!
    </q-tooltip>

    <!-- Bottom Navigation -->
    <q-footer class="bg-white text-dark border-t">
      <q-tabs
        v-model="currentTab"
        dense
        class="text-grey-6"
        active-color="teal"
        indicator-color="teal"
        align="justify"
      >
        <q-tab
          name="home"
          icon="home"
          label="Home"
          @click="navigateTo('/patient-dashboard')"
        />
        <q-tab
          name="appointments"
          icon="event"
          label="Appointments"
          @click="navigateTo('/patient-appointments')"
        />
        <q-tab
          name="queue"
          icon="schedule"
          label="Queue"
          @click="navigateTo('/patient-queue')"
        />
        <q-tab
          name="notifications"
          icon="notifications"
          label="Notifications"
          @click="navigateTo('/patient-notifications')"
        >
          <q-badge
            v-if="unreadCount > 0"
            color="red"
            floating
            rounded
          >
            {{ unreadCount }}
          </q-badge>
        </q-tab>
      </q-tabs>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from 'src/boot/axios'
import type { Appointment } from 'src/stores/appointments'
import logoUrl from 'src/assets/logo.svg'

const router = useRouter()
const route = useRoute()
const formRef = ref()
const showUserMenu = ref(false)
const unreadCount = ref<number>(0)
const showConfirm = ref(false)
const showSuccessTooltip = ref(false)
const successMessage = ref('')
const successTooltipClass = ref('')
const currentTab = ref('appointments')

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