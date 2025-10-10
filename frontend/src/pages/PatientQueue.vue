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
        <div class="q-pa-md">
          <!-- Page Title -->
          <div class="q-mb-md">
            <div class="text-h5 text-weight-bold text-grey-8">Live Queue & Wait Time</div>
          </div>

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
              <q-card class="bg-teal-7 text-white">
                <q-card-section class="q-pa-md">
                  <div class="text-caption text-weight-medium text-uppercase q-mb-xs">Your Queue Status</div>
                  <div class="text-h4 text-weight-bold">{{ myPosition || '—' }}</div>
                  <div class="text-body2 text-weight-medium q-mt-xs">Estimated Wait: ~{{ estimatedWaitMins }} mins</div>
                </q-card-section>
              </q-card>
            </div>
          </div>

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
        <q-tab name="appointments" icon="event" label="Appointments" @click="navigateTo('/patient-appointments')" />
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
import { ref, computed, onMounted } from 'vue'
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
const unreadCount = ref(3)

// Queue data
const nowServing = ref<string | number>('')
const currentPatient = ref<string>('')
const myPosition = ref<string | number>('')
const estimatedWaitMins = ref<number>(15)
const progressValue = ref<number>(75)

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



onMounted(async () => {
  try {
    const res = await api.get('/patient/queue/summary/')
    const data = res.data || {}
    nowServing.value = data.nowServing
    currentPatient.value = data.currentPatient
    myPosition.value = data.myPosition
    estimatedWaitMins.value = data.estimatedWaitMins || 15
    progressValue.value = data.progressValue || 75
  } catch (e) {
    console.warn('Failed to fetch queue summary', e)
    nowServing.value = '001'
    currentPatient.value = 'Current Patient'
    myPosition.value = '005'
    estimatedWaitMins.value = 15
    progressValue.value = 75
  }

  try {
    const res = await api.get('/patient/queue/list/')
    queueEntries.value = (res.data || []) as QueueEntry[]
  } catch (e) {
    console.warn('Failed to fetch queue list', e)
    queueEntries.value = [
      { id: 1, name: userName.value, number: '001', department: 'general', etaMins: 15, isCurrent: true },
      { id: 2, name: 'Jane Doe', number: '002', department: 'dermatology', etaMins: 25, isMe: true }
    ]
  }
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