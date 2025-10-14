<template>
  <q-layout view="hHh lpR fFf">
    <!-- Patient Portal Header -->
    <q-header class="bg-blue-8 text-white" style="height: 70px;">
      <q-toolbar class="q-px-md" style="height: 70px;">
        <q-avatar size="40px" class="q-mr-md">
          <img :src="logoUrl" alt="Logo" />
        </q-avatar>
        
        <div class="column q-mr-auto"></div>

        <!-- Notification Icon -->
        <q-btn flat round icon="notifications" class="q-mr-sm" @click="navigateTo('/patient-notifications')">
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
            <q-item clickable v-close-popup @click="navigateTo('/patient-settings')">
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
        <div class="q-pa-md">
          <!-- Page Title -->
          <div class="q-mb-md">
            <div class="text-h5 text-weight-bold text-grey-8">Live Queue & Wait Time</div>
          </div>

          <!-- Queue Status Banner -->
          <q-banner 
            v-if="!queueStatus.is_open" 
            class="bg-red-1 text-red-8 q-mb-md" 
            rounded
          >
            <template v-slot:avatar>
              <q-icon name="warning" color="red" />
            </template>
            Queue is currently closed. Please check back during operating hours.
          </q-banner>

          <q-banner 
            v-else-if="!isQueueAvailable" 
            class="bg-orange-1 text-orange-8 q-mb-md" 
            rounded
          >
            <template v-slot:avatar>
              <q-icon name="schedule" color="orange" />
            </template>
            Queue is not available at this time. Operating hours: {{ queueScheduleText }}
          </q-banner>

          <!-- Current Status Cards -->
          <div class="row q-gutter-md q-mb-md">
            <div class="col-12 col-sm-6">
              <q-card class="bg-teal-6 text-white">
                <q-card-section class="q-pa-md">
                  <div class="text-caption text-weight-medium text-uppercase q-mb-xs">Now Serving</div>
                  <div class="text-h4 text-weight-bold">{{ nowServing || '—' }}</div>
                  <div class="text-body2 text-weight-medium q-mt-xs">{{ currentPatient || '—' }}</div>
                </q-card-section>
              </q-card>
            </div>
            <div class="col-12 col-sm-6">
              <q-card :class="myPosition ? 'bg-teal-7 text-white' : 'bg-grey-4 text-grey-8'">
                <q-card-section class="q-pa-md">
                  <div class="text-caption text-weight-medium text-uppercase q-mb-xs">Your Queue Status</div>
                  <div class="text-h4 text-weight-bold">{{ myPosition || 'Not in queue' }}</div>
                  <div class="text-body2 text-weight-medium q-mt-xs">
                    {{ myPosition ? `Estimated Wait: ~${estimatedWaitMins} mins` : 'Join the queue to get your position' }}
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <!-- Join Queue Section -->
          <q-card v-if="!myPosition" class="q-mb-md">
            <q-card-section>
              <div class="row items-center q-mb-md">
                <q-icon name="add_circle" color="primary" size="20px" class="q-mr-sm" />
                <div class="text-h6 text-weight-bold">Join Queue</div>
              </div>

              <div class="text-body2 text-grey-7 q-mb-md">
                Join the queue to secure your position and receive real-time updates on your wait time.
              </div>

              <div class="row q-gutter-md">
                <div class="col">
                  <q-select
                    v-model="selectedDepartment"
                    :options="departmentOptions"
                    label="Select Department"
                    outlined
                    emit-value
                    map-options
                    :disable="!queueStatus.is_open || !isQueueAvailable"
                  />
                </div>
                <div class="col-auto">
                  <q-btn
                    color="primary"
                    icon="add"
                    label="Join Queue"
                    @click="joinQueue"
                    :loading="joiningQueue"
                    :disable="!selectedDepartment || !queueStatus.is_open || !isQueueAvailable"
                    unelevated
                    class="full-height"
                  />
                </div>
              </div>

              <div v-if="queueStatus.is_open && isQueueAvailable" class="text-caption text-grey-6 q-mt-sm">
                Current queue length: {{ queueEntries.length }} patients
              </div>
            </q-card-section>
          </q-card>

          <!-- Current Queue -->
          <q-card class="q-mb-md">
            <q-card-section>
              <div class="row items-center q-mb-md">
                <q-icon name="format_list_numbered" color="teal" size="20px" class="q-mr-sm" />
                <div class="text-h6 text-weight-bold">Current Queue</div>
                <q-space />
                <q-badge color="teal" :label="`Position: ${myPosition || '—'}`" />
              </div>

              <q-list separator>
                <q-item
                  v-for="entry in queueEntries"
                  :key="entry.id"
                  class="q-pa-md"
                >
                  <q-item-section avatar>
                    <q-icon
                      name="person"
                      :color="entry.isCurrent ? 'teal' : 'grey-5'"
                      size="24px"
                    />
                  </q-item-section>
                  
                  <q-item-section>
                    <q-item-label class="text-weight-medium">{{ entry.name }} ({{ entry.number }})</q-item-label>
                    <q-item-label caption>{{ entry.isMe ? 'You' : entry.department }}</q-item-label>
                  </q-item-section>
                  
                  <q-item-section side>
                    <div class="text-right">
                      <div class="text-caption text-grey-6">~{{ entry.etaMins }} mins</div>
                      <q-badge
                        v-if="entry.isCurrent"
                        color="orange"
                        label="Next"
                        class="q-mt-xs"
                      />
                      <q-badge
                        v-else-if="entry.isMe"
                        color="grey-6"
                        label="You"
                        class="q-mt-xs"
                      />
                    </div>
                  </q-item-section>
                </q-item>
                
                <q-item v-if="queueEntries.length === 0">
                  <q-item-section class="text-center text-grey-6">
                    No queue data available.
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>

          <!-- Queue Alerts & Info -->
          <q-card>
            <q-card-section>
              <div class="row items-center q-mb-md">
                <q-icon name="info" color="grey-6" size="20px" class="q-mr-sm" />
                <div class="text-h6 text-weight-bold">Queue Alerts & Info</div>
              </div>

              <div class="text-body2 text-grey-7 q-mb-md">
                Request a text message alert when you are the <strong>next patient</strong> in line.
              </div>

              <q-banner class="bg-orange-1 text-orange-8 q-mb-md" rounded>
                <template v-slot:avatar>
                  <q-icon name="schedule" color="orange" />
                </template>
                Current estimated total wait time: ~{{ estimatedWaitMins }} minutes.
              </q-banner>

              <q-btn
                color="indigo"
                icon="sms"
                label="Activate SMS Alert"
                class="full-width"
                @click="activateSMSAlert"
                :disable="smsAlertActive"
                unelevated
              />

              <div v-if="smsAlertActive" class="text-center q-mt-md">
                <q-badge color="green" icon="check_circle" label="SMS Alert Active" />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </q-page>
    </q-page-container>

    <!-- Bottom Navigation -->
    <q-footer class="bg-teal-8 text-white">
      <q-tabs
        v-model="currentTab"
        dense
        class="text-white"
        active-color="white"
        indicator-color="white"
        align="justify"
      >
        <q-tab name="queue" icon="format_list_numbered" label="Queue" @click="navigateTo('/patient-queue')" />
  <q-tab name="appointments" icon="event" label="Appointments" @click="navigateTo('/patient-appointment-schedule')" />
        <q-tab name="home" icon="home" label="Home" @click="navigateTo('/patient-dashboard')" />
        <q-tab name="notifications" icon="notifications" @click="navigateTo('/patient-notifications')">
          <template v-slot:default>
            <div class="row items-center no-wrap">
              <div>Alerts</div>
              <q-badge color="red" floating>!</q-badge>
            </div>
          </template>
        </q-tab>
        <q-tab name="requests" icon="chat" label="Requests" @click="navigateTo('/patient-medical-request')" />
      </q-tabs>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { api } from 'src/boot/axios'
import logoUrl from 'src/assets/logo.svg'

const router = useRouter()
const $q = useQuasar()

// Navigation and UI state
const currentTab = ref('queue')
const smsAlertActive = ref(false)
const showUserMenu = ref(false)
const unreadCount = ref(0)

// Queue data
const nowServing = ref<string | number>('')
const currentPatient = ref<string>('')
const myPosition = ref<string | number>('')
const estimatedWaitMins = ref<number>(0)
const progressValue = ref<number>(0)

// New queue management state
const joiningQueue = ref(false)
const selectedDepartment = ref('general')
const queueStatus = ref({
  is_open: false,
  department: 'general',
  total_patients: 0,
  estimated_wait_time: 0
})

interface QueueSchedule {
  id: number
  start_time: string
  end_time: string
  is_active: boolean
  department: string
}

const queueSchedules = ref<QueueSchedule[]>([])
const websocket = ref<WebSocket | null>(null)

interface QueueEntry {
  id: number
  name: string
  number: string
  department: string
  etaMins: number
  isCurrent?: boolean
  isMe?: boolean
}

const queueEntries = ref<QueueEntry[]>([])

// User information
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

// Queue management computed properties
const departmentOptions = computed(() => [
  { label: 'General Medicine', value: 'general' },
  { label: 'Emergency', value: 'emergency' },
  { label: 'Pediatrics', value: 'pediatrics' },
  { label: 'Cardiology', value: 'cardiology' },
  { label: 'Orthopedics', value: 'orthopedics' }
])

const isQueueAvailable = computed(() => {
  if (!queueStatus.value.is_open) return false
  
  const now = new Date()
  const currentTime = now.getHours() * 60 + now.getMinutes()
  
  // Check if current time is within any active schedule
  return queueSchedules.value.some(schedule => {
    if (!schedule.is_active) return false
    
    const startTimeParts = schedule.start_time?.split(':') || ['0', '0']
    const endTimeParts = schedule.end_time?.split(':') || ['0', '0']
    
    const startTime = parseInt(startTimeParts[0] || '0') * 60 + parseInt(startTimeParts[1] || '0')
    const endTime = parseInt(endTimeParts[0] || '0') * 60 + parseInt(endTimeParts[1] || '0')
    
    return currentTime >= startTime && currentTime <= endTime
  })
})

const queueScheduleText = computed(() => {
  const activeSchedules = queueSchedules.value.filter(s => s.is_active)
  if (activeSchedules.length === 0) return 'No schedule available'
  
  return activeSchedules
    .map(s => `${s.start_time} - ${s.end_time}`)
    .join(', ')
})



// Methods
const joinQueue = async () => {
  if (!selectedDepartment.value) return
  
  joiningQueue.value = true
  try {
    await api.post('/operations/queue/join/', {
      department: selectedDepartment.value
    })
    
    $q.notify({
      type: 'positive',
      message: 'Successfully joined the queue!',
      position: 'top'
    })
    
    // Refresh queue data
    await fetchQueueData()
  } catch (error: unknown) {
    const errorMessage = error instanceof Error && 'response' in error 
      ? (error as { response?: { data?: { error?: string } } }).response?.data?.error || 'Failed to join queue'
      : 'Failed to join queue'
    
    $q.notify({
      type: 'negative',
      message: errorMessage,
      position: 'top'
    })
  } finally {
    joiningQueue.value = false
  }
}

const fetchQueueData = async () => {
  try {
    // Fetch queue status
    const statusRes = await api.get(`/operations/queue/status/?department=${selectedDepartment.value || 'general'}`)
    queueStatus.value = statusRes.data || queueStatus.value

    // Fetch queue schedules
    const scheduleRes = await api.get(`/operations/queue/schedules/?department=${selectedDepartment.value || 'general'}`)
    queueSchedules.value = scheduleRes.data || []

    // Fetch queue summary
    const summaryRes = await api.get('/patient/queue/summary/')
    const data = summaryRes.data || {}
    nowServing.value = data.nowServing || ''
    currentPatient.value = data.currentPatient || ''
    myPosition.value = data.myPosition || ''
    estimatedWaitMins.value = data.estimatedWaitMins || 0
    progressValue.value = data.progressValue || 0

    // Fetch queue list
    const listRes = await api.get('/patient/queue/list/')
    queueEntries.value = (listRes.data || []) as QueueEntry[]
  } catch (e) {
    console.warn('Failed to fetch queue data', e)
  }
}

const setupWebSocket = () => {
  try {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const base = new URL(api.defaults.baseURL || `http://${window.location.hostname}:8000/api`)
    const backendHost = base.hostname
    const backendPort = base.port || (base.protocol === 'https:' ? '443' : '80')
    const wsUrl = `${protocol}//${backendHost}:${backendPort}/ws/queue/${selectedDepartment.value || 'general'}/`
    
    websocket.value = new WebSocket(wsUrl)
    
    websocket.value.onopen = () => {
      console.log('Queue WebSocket connected')
    }
    
    websocket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'queue_status_update') {
        queueStatus.value = data.status
      } else if (data.type === 'queue_position_update') {
        myPosition.value = data.position.position
        estimatedWaitMins.value = data.position.estimated_wait_time
      } else if (data.type === 'queue_notification') {
        $q.notify({
          type: 'info',
          message: data.notification.message,
          position: 'top'
        })
      }
    }
    
    websocket.value.onclose = () => {
      console.log('Queue WebSocket disconnected')
      // Attempt to reconnect after 5 seconds
      setTimeout(setupWebSocket, 5000)
    }
  } catch (e) {
    console.warn('Failed to setup WebSocket', e)
  }
}

onMounted(async () => {
  await fetchQueueData()
  setupWebSocket()
  
  try {
    // Declare window interface for lucide
    interface WindowWithLucide extends Window {
      lucide?: {
        createIcons(): void
      }
    }
    ;(window as WindowWithLucide).lucide?.createIcons()
  } catch (e) { console.warn('lucide icons init failed', e) }
})

onUnmounted(() => {
  if (websocket.value) {
    websocket.value.close()
  }
})

const navigateTo = (path: string) => {
  void router.push(path)
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  void router.push('/login')
}

const activateSMSAlert = async () => {
  try {
    await api.post('/patient/queue/alerts/sms/')
    smsAlertActive.value = true
    $q.notify({ type: 'positive', message: 'SMS alert activated', position: 'top' })
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to activate SMS alert', position: 'top' })
  }
}
</script>

<style scoped>
.status-card { border-radius: 12px; }
</style>