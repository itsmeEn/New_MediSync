<template>
  <q-layout view="hHh lpR fFf">
    <!-- Header -->
    <header class="bg-teal-800 p-4 md:p-6 shadow-lg">
      <div class="flex justify-between items-center max-w-7xl mx-auto">
        <!-- Logo + Title -->
        <div class="flex items-center space-x-3 text-white">
          <img :src="logoUrl" alt="Project Logo" class="h-10 w-10 rounded-full bg-white object-cover flex-shrink-0" />
          <div>
            <p class="text-lg font-semibold leading-none">Settings</p>
            <p class="text-sm font-light text-teal-300 leading-none">Manage your account</p>
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
              <a href="#" @click.prevent="toggleUserMenu()" class="flex items-center space-x-3 px-4 py-3 text-sm text-gray-700 hover:bg-teal-50 transition-colors duration-200">
                <i data-lucide="user" class="w-4 h-4 text-teal-600"></i>
                <span>Profile</span>
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
        <!-- Existing settings content -->
        <slot />
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
import { api } from 'src/boot/axios'
// removed: import { useQuasar } from 'quasar'
import logoUrl from 'src/assets/logo.png'

const router = useRouter()
// removed: const $q = useQuasar()
// removed: const bottomTab = ref('home')
const showUserMenu = ref(false)
const unreadCount = ref<number>(0)

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

const navigateTo = (path: string) => { void router.push(path) }

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  void router.push('/login')
}

// Declare window interface for lucide
interface WindowWithLucide extends Window {
  lucide?: {
    createIcons(): void
  }
}

onMounted(async () => {
  try { (window as WindowWithLucide).lucide?.createIcons() } catch (e) { console.warn('lucide icons init failed', e) }
  try {
    const res = await api.get('/patient/notifications/unread-count/')
    unreadCount.value = res.data?.count ?? 0
  } catch (e) { console.warn('unread count fetch failed', e); unreadCount.value = 0 }
})
</script>

<style scoped>
</style>