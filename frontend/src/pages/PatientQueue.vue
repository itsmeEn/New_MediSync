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
            <div class="mb-6">
              <h1 class="text-xl font-bold text-gray-700">Live Queue &amp; Wait Time</h1>
            </div>

          <!-- Current Status Cards -->
          <section class="grid grid-cols-2 gap-4 mb-8">
            <div class="status-card bg-teal-600 text-white p-4 shadow-xl rounded-xl">
              <p class="text-xs font-medium uppercase tracking-wider opacity-90 mb-1">Now Serving</p>
              <p class="status-number text-white">{{ nowServing || '—' }}</p>
              <p class="text-sm font-semibold mt-1">{{ currentPatient || '—' }}</p>
            </div>
            <div class="status-card bg-teal-700 text-white p-4 shadow-xl rounded-xl">
              <p class="text-xs font-medium uppercase tracking-wider opacity-90 mb-1">Your Queue Status</p>
              <p class="status-number text-white">{{ myPosition || '—' }}</p>
              <p class="text-sm font-semibold mt-1">Estimated Wait: ~{{ estimatedWaitMins }} mins</p>
            </div>
          </section>

          <div class="grid grid-cols-7 gap-6">
            <!-- Current Queue -->
            <section class="col-span-7 md:col-span-4">
              <div class="bg-white rounded-xl shadow-md p-4">
                <div class="flex items-center mb-4">
                  <i data-lucide="list-ordered" class="w-5 h-5 text-teal-600 mr-2"></i>
                  <h2 class="text-lg font-semibold text-gray-800">Current Queue</h2>
                  <div class="ml-auto inline-flex items-center px-2 py-1 rounded-full bg-teal-100 text-teal-700 text-xs">
                    Position: {{ myPosition || '—' }}
                  </div>
                </div>

                <ul class="divide-y divide-gray-100">
                  <li v-for="entry in queueEntries" :key="entry.id" class="py-3 flex items-center">
                    <i data-lucide="user" :class="['w-5 h-5 mr-3', entry.isCurrent ? 'text-teal-600' : 'text-gray-400']"></i>
                    <div class="flex-1">
                      <p class="text-sm font-medium text-gray-800">{{ entry.name }} ({{ entry.number }})</p>
                      <p class="text-xs text-gray-500">{{ entry.isMe ? 'You' : entry.department }}</p>
                    </div>
                    <div class="text-right">
                      <div class="text-xs text-gray-500">~{{ entry.etaMins }} mins</div>
                      <span v-if="entry.isCurrent" class="inline-block mt-1 px-2 py-0.5 text-xs rounded bg-orange-500 text-white">Next</span>
                      <span v-else-if="entry.isMe" class="inline-block mt-1 px-2 py-0.5 text-xs rounded bg-gray-600 text-white">You</span>
                    </div>
                  </li>
                  <li v-if="queueEntries.length === 0" class="py-6 text-center text-gray-500">No queue data available.</li>
                </ul>
              </div>
            </section>

            <!-- Queue Alerts & Info -->
            <section class="col-span-7 md:col-span-3">
              <div class="bg-white rounded-xl shadow-md p-4">
                <div class="flex items-center mb-4">
                  <i data-lucide="info" class="w-5 h-5 text-gray-500 mr-2"></i>
                  <h2 class="text-lg font-semibold text-gray-800">Queue Alerts &amp; Info</h2>
                </div>

                <p class="text-sm text-gray-600 mb-4">
                  Request a text message alert when you are the <b>next patient</b> in line.
                </p>

                <div class="rounded-lg bg-orange-50 border border-orange-200 p-3 mb-4">
                  <p class="text-orange-700 text-sm font-medium">Current estimated total wait time: ~{{ estimatedWaitMins }} minutes.</p>
                </div>

                <button 
                  class="w-full inline-flex items-center justify-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition"
                  @click="activateSMSAlert"
                  :disabled="smsAlertActive"
                >
                  <i data-lucide="sms" class="w-4 h-4 mr-2"></i>
                  Activate SMS Alert
                </button>

                <div v-if="smsAlertActive" class="text-center mt-3">
                  <span class="inline-flex items-center px-3 py-1 rounded-full bg-green-600 text-white text-sm">
                    <i data-lucide="check-circle" class="w-4 h-4 mr-1"></i>
                    SMS Alert Active
                  </span>
                </div>
              </div>
            </section>
          </div>
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
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { api } from 'src/boot/axios'
import logoUrl from 'src/assets/logo.png'

const router = useRouter()
const $q = useQuasar()
// removed: const activeTab = ref('queue')
const smsAlertActive = ref(false)

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

const userName = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    return u.full_name || u.email || 'User'
  } catch {
    return 'User'
  }
})

const showUserMenu = ref(false)
const toggleUserMenu = () => { showUserMenu.value = !showUserMenu.value }
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