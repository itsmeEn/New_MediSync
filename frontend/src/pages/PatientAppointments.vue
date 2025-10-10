<template>
  <q-layout view="lHh Lpr lFf">
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

    <q-page-container>
      <q-page class="bg-grey-1 q-pa-md">
        <!-- Mobile-First Content -->
        <div class="q-pa-md">
          <!-- Page Title -->
          <div class="q-mb-lg">
            <div class="text-h4 text-teal-8 text-weight-bold q-mb-xs">
              Manage Your Appointments
            </div>
            <div class="text-grey-6">
              View and manage your upcoming, completed, and cancelled appointments
            </div>
          </div>

          <!-- New Appointment Card -->
          <q-card class="q-mb-lg" flat bordered>
            <q-card-section class="row items-center">
              <q-avatar size="48px" color="teal" text-color="white" icon="add" />
              
              <div class="col q-ml-md">
                <div class="text-h6 text-teal-8">Schedule New Appointment</div>
                <div class="text-grey-6">Book your next medical appointment</div>
              </div>
              
              <q-btn 
                unelevated 
                color="teal" 
                label="Book Now" 
                icon-right="arrow_forward"
                @click="navigateTo('/patient-appointment-schedule')"
              />
            </q-card-section>
          </q-card>

          <!-- Mobile-Optimized Filter Tabs -->
          <q-card flat bordered class="q-mb-lg">
            <q-tabs 
              v-model="selectedStatus" 
              dense 
              class="text-teal-8"
              active-color="teal"
              indicator-color="teal"
              align="justify"
            >
              <q-tab name="upcoming" label="Upcoming" />
              <q-tab name="completed" label="Completed" />
              <q-tab name="cancelled" label="Cancelled" />
            </q-tabs>
          </q-card>

          <!-- Search Bar -->
          <q-input 
            v-model="search" 
            outlined 
            placeholder="Search appointments..." 
            class="q-mb-lg"
            color="teal"
          >
            <template v-slot:prepend>
              <q-icon name="search" />
            </template>
          </q-input>

          <!-- Pull to Refresh -->
          <q-pull-to-refresh @refresh="onRefresh">
            <!-- Mobile-Optimized Appointments List -->
            <q-card flat bordered>
              <q-card-section>
                <div class="text-h6 text-grey-8 q-mb-md">
                  {{ capitalize(selectedStatus) }} Appointments
                </div>
                
                <q-list separator v-if="filteredAppointments.length > 0">
                  <q-item 
                    v-for="appt in filteredAppointments" 
                    :key="appt.id"
                    clickable
                    @click="openAppointment(appt)"
                    class="q-pa-md"
                  >
                    <q-item-section avatar>
                      <q-avatar 
                        size="12px" 
                        :color="appt.status === 'upcoming' ? 'green' : appt.status === 'completed' ? 'blue' : 'red'"
                      />
                    </q-item-section>

                    <q-item-section>
                      <q-item-label class="text-weight-medium">
                        {{ getDepartmentLabel(appt.department) }}
                      </q-item-label>
                      <q-item-label caption>
                        {{ getAppointmentTypeLabel(appt.type) }}
                      </q-item-label>
                      <q-item-label caption class="row items-center q-gutter-md q-mt-xs">
                        <div class="row items-center">
                          <q-icon name="event" size="16px" class="q-mr-xs" />
                          {{ formatDate(appt.date) }}
                        </div>
                        <div class="row items-center">
                          <q-icon name="schedule" size="16px" class="q-mr-xs" />
                          {{ appt.time }}
                        </div>
                      </q-item-label>
                    </q-item-section>

                    <q-item-section side v-if="appt.status === 'upcoming'">
                      <q-btn 
                        flat 
                        round 
                        dense 
                        icon="edit" 
                        color="teal" 
                        @click.stop="openEdit(appt)"
                      >
                        <q-tooltip>Edit</q-tooltip>
                      </q-btn>
                    </q-item-section>

                    <q-item-section side>
                      <q-icon name="chevron_right" color="teal" />
                    </q-item-section>
                  </q-item>
                </q-list>

                <div v-else class="text-center text-grey-6 q-py-xl">
                  <q-icon name="event_busy" size="48px" class="q-mb-md" />
                  <div>No appointments found.</div>
                </div>
              </q-card-section>
            </q-card>
          </q-pull-to-refresh>
        </div>
      </q-page>
    </q-page-container>

    <!-- Mobile-Optimized Cancel Confirmation Modal -->
    <q-dialog 
      v-model="showCancelDialog"
      position="bottom"
      :maximized="$q.platform.is.mobile"
    >
      <q-card class="q-dialog-plugin">
        <q-card-section class="row items-center q-pb-none">
          <q-icon name="warning" color="red" size="24px" />
          <div class="text-h6 q-ml-sm">Cancel Appointment</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="grey-7" />
        </q-card-section>

        <q-card-section>
          <div class="text-body2 q-mb-md">
            Are you sure you want to cancel this appointment?
          </div>
          
          <q-list v-if="selectedAppointment" bordered>
            <q-item>
              <q-item-section avatar>
                <q-icon name="category" color="red" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Type</q-item-label>
                <q-item-label caption>{{ getAppointmentTypeLabel(selectedAppointment.type) }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section avatar>
                <q-icon name="business" color="red" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Department</q-item-label>
                <q-item-label caption>{{ getDepartmentLabel(selectedAppointment.department) }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section avatar>
                <q-icon name="event" color="red" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Date & Time</q-item-label>
                <q-item-label caption>{{ formatDate(selectedAppointment.date) }} at {{ selectedAppointment.time }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Keep Appointment" color="grey-7" v-close-popup />
          <q-btn unelevated label="Yes, Cancel" color="red" @click="confirmCancel" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Mobile-Optimized Reschedule Modal -->
    <q-dialog 
      v-model="showRescheduleDialog"
      position="bottom"
      :maximized="$q.platform.is.mobile"
    >
      <q-card class="q-dialog-plugin">
        <q-card-section class="row items-center q-pb-none">
          <q-icon name="schedule" color="teal" size="24px" />
          <div class="text-h6 q-ml-sm">Reschedule Options</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="grey-7" />
        </q-card-section>

        <q-card-section>
          <div class="text-body2 q-mb-md">
            Choose how you'd like to reschedule your appointment:
          </div>
          
          <div class="q-gutter-md">
            <q-btn 
              unelevated 
              color="teal" 
              icon="event" 
              label="Reschedule with Same Time"
              class="full-width"
              @click="rescheduleWithSameTime"
            />
            
            <q-btn 
              unelevated 
              color="teal" 
              icon="add" 
              label="Create New Appointment"
              class="full-width"
              @click="createNewAppointment"
            />
          </div>
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Close" color="grey-7" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Mobile-Optimized Enhanced Cancellation Modal -->
    <q-dialog 
      v-model="showEnhancedCancelDialog"
      position="bottom"
      :maximized="$q.platform.is.mobile"
    >
      <q-card class="q-dialog-plugin">
        <q-card-section class="row items-center q-pb-none">
          <q-icon name="cancel" color="red" size="24px" />
          <div class="text-h6 q-ml-sm">Cancel Options</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="grey-7" />
        </q-card-section>

        <q-card-section>
          <div class="text-body2 q-mb-md">
            What would you like to do with this appointment?
          </div>
          
          <div class="q-gutter-md">
            <q-btn 
              unelevated 
              color="orange" 
              icon="schedule" 
              label="Cancel and Reschedule"
              class="full-width"
              @click="cancellationChoice = 'reschedule'; confirmEnhancedCancel()"
            />
            
            <q-btn 
              unelevated 
              color="red" 
              icon="cancel" 
              label="Cancel Only"
              class="full-width"
              @click="cancellationChoice = 'cancel_only'; confirmEnhancedCancel()"
            />
          </div>
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Close" color="grey-7" v-close-popup />
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

    <!-- Mobile-Optimized Calendar Modal -->
    <q-dialog 
      v-model="showCalendarModal"
      position="bottom"
      :maximized="$q.platform.is.mobile"
    >
      <q-card class="q-dialog-plugin">
        <q-card-section class="row items-center q-pb-none">
          <q-icon name="event" color="teal" size="24px" />
          <div class="text-h6 q-ml-sm">Select New Date</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="grey-7" />
        </q-card-section>

        <q-card-section>
          <q-date 
            v-model="selectedDate" 
            :options="dateOptions"
            color="teal"
            class="full-width"
            :landscape="$q.screen.gt.xs"
          />
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancel" color="grey-7" v-close-popup />
          <q-btn unelevated label="Confirm Date" color="teal" @click="confirmDateSelection" />
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

    <!-- Mobile-Optimized Edit Appointment Modal -->
    <q-dialog 
      v-model="showEditDialog"
      position="bottom"
      :maximized="$q.platform.is.mobile"
    >
      <q-card class="q-dialog-plugin">
        <q-card-section class="row items-center q-pb-none">
          <q-icon name="edit" color="teal" size="24px" />
          <div class="text-h6 q-ml-sm">Edit Appointment</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="grey-7" />
        </q-card-section>

        <q-card-section>
          <q-form class="q-gutter-md">
            <q-input 
              v-model="editForm.date" 
              label="Date" 
              mask="####-##-##" 
              placeholder="YYYY-MM-DD"
              outlined
              :rules="[val => !!val || 'Date is required']"
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date v-model="editForm.date" mask="YYYY-MM-DD">
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            
            <q-input 
              v-model="editForm.time" 
              label="Time" 
              mask="##:##" 
              placeholder="HH:MM"
              outlined
              :rules="[val => !!val || 'Time is required']"
            >
              <template v-slot:append>
                <q-icon name="access_time" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-time v-model="editForm.time" mask="HH:mm" format24h>
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-time>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            
            <q-input 
              v-model="editForm.notes" 
              label="Notes" 
              type="textarea" 
              outlined
              rows="3"
              placeholder="Add any additional notes..."
            />
          </q-form>
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancel" color="grey-7" v-close-popup />
          <q-btn unelevated label="Save Changes" color="teal" @click="saveEdit" />
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
        />
        <q-tab 
          name="requests" 
          icon="medical_services" 
          label="Requests"
          @click="navigateTo('/patient-medical-request')"
          no-caps
        />
      </q-tabs>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'src/boot/axios'
import { useAppointmentsStore } from '../stores/appointments'
import logoUrl from 'src/assets/logo.svg'

const router = useRouter()
// removed: const activeTab = ref('appointments')
const selectedStatus = ref<'upcoming' | 'completed' | 'cancelled'>('upcoming')
const search = ref('')
// const appointments = ref<Appointment[]>([])
const appointmentsStore = useAppointmentsStore()
const unreadCount = ref<number>(0)
const showUserMenu = ref(false)
const currentTab = ref('appointments')

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
const showEnhancedCancelDialog = ref(false)
const showCalendarDialog = ref(false)
const showCalendarModal = ref(false)
const rescheduleDate = ref('')
const selectedDate = ref('')
const showSuccessTooltip = ref(false)
const successMessage = ref('')
const successTooltipClass = ref('')
const cancellationChoice = ref('')

// Edit modal state
const showEditDialog = ref(false)
const editForm = ref({
  date: '',
  time: '',
  notes: ''
})
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

// Pull to refresh function
const onRefresh = async (done: () => void) => {
  try {
    await fetchAppointments()
    await fetchUnreadCount()
  } catch (error) {
    console.warn('Failed to refresh data', error)
  } finally {
    done()
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
  editForm.value.date = `${yyyy}-${mm}-${dd}`
  editForm.value.time = appt.time
  editForm.value.notes = ''
  showEditDialog.value = true
}

async function saveEdit() {
  if (!editingAppointmentId.value) return
  try {
    const isoDate = new Date(editForm.value.date).toISOString()
    await appointmentsStore.updateFields(editingAppointmentId.value, { 
      date: isoDate, 
      time: editForm.value.time
    })
    showSuccessTooltipFunc('Appointment updated successfully!')
    showEditDialog.value = false
    await fetchAppointments()
  } catch (error) {
    console.error('Error updating appointment:', error)
  }
  editingAppointmentId.value = null
}

function confirmEnhancedCancel() {
  if (cancellationChoice.value === 'reschedule') {
    showEnhancedCancelDialog.value = false
    showRescheduleDialog.value = true
  } else if (cancellationChoice.value === 'cancel_only') {
    showEnhancedCancelDialog.value = false
    void confirmCancel()
  }
}

function confirmDateSelection() {
  if (!selectedDate.value) return
  rescheduleDate.value = selectedDate.value
  showCalendarModal.value = false
  void confirmRescheduleWithSameTime()
}

const dateOptions = (date: string) => {
  const today = new Date()
  const selectedDateObj = new Date(date)
  return selectedDateObj >= today
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