<template>
  <q-layout view="hHh lpR fFf">
    <!-- Header updated to Tailwind-based, consistent with other patient modules -->
    <header class="bg-teal-800 p-4 md:p-6 shadow-lg">
      <div class="flex justify-between items-center max-w-7xl mx-auto">
        <!-- Logo + Title -->
        <div class="flex items-center space-x-3 text-white">
          <img :src="logoUrl" alt="Project Logo" class="h-10 w-10 rounded-full bg-white object-cover flex-shrink-0" />
          <div>
            <p class="text-lg font-semibold leading-none">Notifications</p>
            <p class="text-sm font-light text-teal-300 leading-none">Patient updates</p>
          </div>
        </div>
          <!-- Right: Bell + User Dropdown -->
        <div class="flex items-center space-x-3">
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
        <div class="max-w-7xl mx-auto">
          <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <!-- Left Sidebar - Filter Navigation -->
            <div class="lg:col-span-1">
              <div class="bg-white rounded-xl shadow-lg p-4 sticky top-4">
                <!-- Search Function -->
                <div class="mb-6">
                  <h4 class="text-sm font-semibold text-gray-700 mb-3">Search Notifications</h4>
                  <div class="relative">
                    <input 
                      v-model="searchQuery"
                      type="text" 
                      placeholder="Search notifications..."
                      class="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition duration-200"
                    />
                    <i data-lucide="search" class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"></i>
                  </div>
                </div>

                <h3 class="text-lg font-semibold text-gray-800 mb-4">Filter Notifications</h3>
                
                <!-- Vertical Filter Navigation -->
                <div class="space-y-2">
                  <button 
                    v-for="filter in filterOptions" 
                    :key="filter.value"
                    @click="activeTab = filter.value"
                    :class="[
                      'w-full text-left px-4 py-3 rounded-lg transition-all duration-200 flex items-center justify-between',
                      activeTab === filter.value 
                        ? 'bg-teal-600 text-white shadow-md' 
                        : 'text-gray-700 hover:bg-teal-50 hover:text-teal-700'
                    ]"
                  >
                    <div class="flex items-center space-x-3">
                      <i :data-lucide="filter.icon" class="w-4 h-4"></i>
                      <span class="font-medium">{{ filter.label }}</span>
                    </div>
                    <span v-if="filter.count > 0" :class="[
                      'px-2 py-1 rounded-full text-xs font-semibold',
                      activeTab === filter.value ? 'bg-white text-teal-600' : 'bg-teal-100 text-teal-700'
                    ]">
                      {{ filter.count }}
                    </span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Right Content - Notifications List -->
            <div class="lg:col-span-3">
              <div class="bg-white rounded-xl shadow-lg">
                <div class="p-6 border-b border-gray-200">
                  <h2 class="text-xl font-bold text-gray-800">
                    {{ getFilterLabel() }} Notifications
                    <span class="text-sm font-normal text-gray-500">({{ filteredNotifications.length }})</span>
                  </h2>
                </div>

                <div class="p-6">
                  <div v-if="filteredNotifications.length === 0" class="text-center py-12">
                    <i data-lucide="bell-off" class="w-16 h-16 text-gray-300 mx-auto mb-4"></i>
                    <h3 class="text-lg font-semibold text-gray-600 mb-2">No notifications found</h3>
                    <p class="text-gray-500">Try adjusting your filters or search terms.</p>
                  </div>

                  <div v-else class="space-y-3">
                    <div 
                      v-for="n in filteredNotifications" 
                      :key="n.id"
                      @click="openNotification(n)"
                      @touchstart="startLongPress(n, $event)"
                      @touchend="endLongPress"
                      @mousedown="startLongPress(n, $event)"
                      @mouseup="endLongPress"
                      @mouseleave="endLongPress"
                      :class="[
                        'p-4 rounded-lg border cursor-pointer transition-all duration-200',
                        n.read ? 'bg-gray-50 border-gray-200' : 'bg-teal-50 border-teal-200',
                        'hover:shadow-md hover:scale-[1.02]'
                      ]"
                    >
                      <div class="flex items-start space-x-3">
                        <!-- Checkbox for marking as read -->
                        <div class="flex-shrink-0 mt-1">
                          <input 
                            type="checkbox" 
                            :checked="n.read"
                            @click.stop="toggleReadStatus(n)"
                            class="w-4 h-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
                          />
                        </div>

                        <!-- Notification Icon -->
                        <div class="flex-shrink-0">
                          <i :data-lucide="iconForType(n.type)" :class="[
                            'w-5 h-5',
                            n.read ? 'text-gray-400' : getIconColorClass(n.type)
                          ]"></i>
                        </div>

                        <!-- Notification Content -->
                        <div class="flex-1 min-w-0">
                          <div class="flex items-start justify-between">
                            <div class="flex-1">
                              <h4 :class="[
                                'text-sm font-semibold mb-1',
                                n.read ? 'text-gray-500' : 'text-gray-900'
                              ]">
                                {{ n.title }}
                              </h4>
                              <p :class="[
                                'text-sm mb-2 line-clamp-2',
                                n.read ? 'text-gray-400' : 'text-gray-600'
                              ]">
                                {{ n.message }}
                              </p>
                              <div class="flex items-center space-x-4 text-xs text-gray-500">
                                <span>{{ formatDate(n.createdAt) }}</span>
                                <span class="capitalize">{{ n.type }}</span>
                                <span v-if="n.archived" class="text-orange-600 font-medium">Archived</span>
                              </div>
                            </div>
                            
                            <!-- Status Indicators -->
                            <div class="flex items-center space-x-2">
                              <span v-if="!n.read" class="w-2 h-2 bg-teal-500 rounded-full"></span>
                              <span v-if="n.archived" class="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full">
                                Archived
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </q-page>
    </q-page-container>

    <!-- Long Press Action Menu -->
    <q-dialog v-model="showActionMenu" position="bottom">
      <q-card style="min-width: 400px; max-width: 500px">
        <q-card-section class="q-pa-lg">
          <div class="text-h5 text-teal-700 font-bold mb-4">Notification Actions</div>
          <div class="bg-teal-50 rounded-lg p-4 mb-4">
            <div class="text-sm font-semibold text-teal-800 mb-2">Notification Information:</div>
            <div class="text-sm text-gray-700">{{ selectedNotification?.title }}</div>
          </div>
          <div class="space-y-3">
            <q-btn 
              v-if="!selectedNotification?.read"
              color="teal" 
              class="w-full" 
              label="Mark as Read" 
              @click="markAsRead(selectedNotification)"
            />
            <q-btn 
              v-if="selectedNotification?.read"
              color="blue" 
              class="w-full" 
              label="Mark as Unread" 
              @click="markAsUnread(selectedNotification)"
            />
            <q-btn 
              v-if="!selectedNotification?.archived"
              color="orange" 
              class="w-full" 
              label="Archive" 
              @click="archiveNotification(selectedNotification)"
            />
            <q-btn 
              v-if="selectedNotification?.archived"
              color="green" 
              class="w-full" 
              label="Unarchive" 
              @click="unarchiveNotification(selectedNotification)"
            />
            <q-btn 
              color="red" 
              class="w-full" 
              label="Delete" 
              @click="deleteNotification(selectedNotification)"
            />
          </div>
        </q-card-section>
        <q-card-actions align="center" class="q-pa-lg">
          <q-btn color="teal" label="Close" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Notification Detail Modal -->
    <q-dialog v-model="showNotificationDetail">
      <q-card style="min-width: 400px; max-width: 600px">
        <q-card-section class="q-pa-lg">
          <div class="text-h5 text-teal-700 font-bold mb-4">Notification Details</div>
          <div class="bg-teal-50 rounded-lg p-4 mb-4">
            <div class="text-sm font-semibold text-teal-800 mb-3">Notification Information:</div>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Title:</span>
                <span class="text-gray-800 font-medium">{{ selectedNotification?.title }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Type:</span>
                <span class="text-gray-800 font-medium capitalize">{{ selectedNotification?.type }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Date:</span>
                <span class="text-gray-800 font-medium">{{ formatDate(selectedNotification?.createdAt) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Status:</span>
                <span :class="[
                  'px-2 py-1 rounded text-xs font-medium',
                  selectedNotification?.read ? 'bg-green-100 text-green-700' : 'bg-teal-100 text-teal-700'
                ]">
                  {{ selectedNotification?.read ? 'Read' : 'Unread' }}
                </span>
              </div>
              <div v-if="selectedNotification?.archived" class="flex justify-between">
                <span class="text-gray-600">Archive:</span>
                <span class="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs font-medium">Archived</span>
              </div>
            </div>
          </div>
          <div class="mb-4">
            <div class="text-sm font-semibold text-teal-800 mb-2">Message:</div>
            <p class="text-sm text-gray-700 leading-relaxed">{{ selectedNotification?.message }}</p>
          </div>
        </q-card-section>
        <q-card-actions align="center" class="q-pa-lg">
          <q-btn color="teal" label="Close" v-close-popup />
          <q-btn color="teal" label="Mark as Read" @click="markAsRead(selectedNotification); showNotificationDetail = false" v-if="!selectedNotification?.read" />
        </q-card-actions>
      </q-card>
    </q-dialog>

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

const router = useRouter()
const activeTab = ref<FilterValue>('all')
const searchQuery = ref('')
const showActionMenu = ref(false)
const showNotificationDetail = ref(false)
const selectedNotification = ref<Notification | null>(null)
const longPressTimer = ref<NodeJS.Timeout | null>(null)

interface Notification {
  id: number
  title: string
  message: string
  type: 'appointment' | 'queue' | 'medical' | 'info' | 'urgent'
  read: boolean
  archived?: boolean
  createdAt: string
}

// Filter value type to align template interactions
type FilterValue = 'all' | 'unread' | 'read' | 'appointments' | 'queue' | 'medical' | 'archived'

const notifications = ref<Notification[]>([])

const showUserMenu = ref(false)
const toggleUserMenu = () => { showUserMenu.value = !showUserMenu.value }

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

const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

// Filter options for the vertical sidebar
const filterOptions = computed((): { value: FilterValue; label: string; icon: string; count: number }[] => [
  { value: 'all', label: 'All', icon: 'bell', count: notifications.value.length },
  { value: 'unread', label: 'Unread', icon: 'mail', count: notifications.value.filter(n => !n.read).length },
  { value: 'read', label: 'Read', icon: 'mail-check', count: notifications.value.filter(n => n.read).length },
  { value: 'appointments', label: 'Appointments', icon: 'calendar', count: notifications.value.filter(n => n.type === 'appointment').length },
  { value: 'queue', label: 'Queue', icon: 'list-ordered', count: notifications.value.filter(n => n.type === 'queue').length },
  { value: 'medical', label: 'Medical', icon: 'heart', count: notifications.value.filter(n => n.type === 'medical').length },
  { value: 'archived', label: 'Archived', icon: 'archive', count: notifications.value.filter(n => n.archived).length }
])

const getFilterLabel = () => {
  const filter = filterOptions.value.find(f => f.value === activeTab.value)
  return filter ? filter.label : 'All'
}

// Declare window interface for lucide
interface WindowWithLucide extends Window {
  lucide?: {
    createIcons(): void
  }
}

onMounted(async () => {
  await fetchNotifications()
  try { (window as WindowWithLucide).lucide?.createIcons() } catch (e) { console.warn('lucide icons init failed', e) }
})

const fetchNotifications = async () => {
  try {
    const res = await api.get('/patient/notifications/')
    notifications.value = (res.data || []) as Notification[]
  } catch (e) {
    console.warn('Failed to fetch notifications', e)
    notifications.value = [
      { 
        id: 1, 
        title: 'Upcoming appointment', 
        message: 'You have an appointment tomorrow at 10:00 AM with Dr. Smith for your regular checkup.', 
        type: 'appointment', 
        read: false,
        archived: false,
        createdAt: new Date(Date.now() - 3600000).toISOString()
      },
      { 
        id: 2, 
        title: 'Queue update', 
        message: 'Your position in the queue has moved up to 3. Estimated wait time: 15 minutes.', 
        type: 'queue', 
        read: false,
        archived: false,
        createdAt: new Date(Date.now() - 1800000).toISOString()
      },
      { 
        id: 3, 
        title: 'Lab result ready', 
        message: 'Your blood test results are now available. Please check your medical records.', 
        type: 'medical', 
        read: true,
        archived: false,
        createdAt: new Date(Date.now() - 86400000).toISOString()
      },
      { 
        id: 4, 
        title: 'Appointment reminder', 
        message: 'Don\'t forget your appointment with Dr. Johnson tomorrow at 2:00 PM.', 
        type: 'appointment', 
        read: true,
        archived: true,
        createdAt: new Date(Date.now() - 172800000).toISOString()
      },
    ]
  }
}

const filteredNotifications = computed(() => {
  let filtered = notifications.value

  // Apply filter
  switch (activeTab.value) {
    case 'unread':
      filtered = filtered.filter(n => !n.read)
      break
    case 'read':
      filtered = filtered.filter(n => n.read)
      break
    case 'appointments':
      filtered = filtered.filter(n => n.type === 'appointment')
      break
    case 'queue':
      filtered = filtered.filter(n => n.type === 'queue')
      break
    case 'medical':
      filtered = filtered.filter(n => n.type === 'medical')
      break
    case 'archived':
      filtered = filtered.filter(n => n.archived)
      break
    // 'all' shows everything
  }

  // Apply search
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(n => 
      n.title.toLowerCase().includes(query) || 
      n.message.toLowerCase().includes(query)
    )
  }

  return filtered
})

const iconForType = (type: Notification['type']) => {
  switch (type) {
    case 'appointment': return 'calendar'
    case 'queue': return 'list-ordered'
    case 'medical': return 'heart'
    case 'urgent': return 'alert-triangle'
    case 'info': return 'info'
  }
}



const getIconColorClass = (type: Notification['type']) => {
  switch (type) {
    case 'appointment': return 'text-blue-600'
    case 'queue': return 'text-indigo-600'
    case 'medical': return 'text-red-600'
    case 'urgent': return 'text-orange-600'
    case 'info': return 'text-gray-600'
  }
}

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
  if (diffInHours < 1) {
    return 'Just now'
  } else if (diffInHours < 24) {
    return `${Math.floor(diffInHours)}h ago`
  } else if (diffInHours < 48) {
    return 'Yesterday'
  } else {
    return date.toLocaleDateString()
  }
}

// Long press functionality
const startLongPress = (notification: Notification, event: Event) => {
  event.preventDefault()
  selectedNotification.value = notification
  longPressTimer.value = setTimeout(() => {
    showActionMenu.value = true
  }, 500) // 500ms long press
}

const endLongPress = () => {
  if (longPressTimer.value) {
    clearTimeout(longPressTimer.value)
    longPressTimer.value = null
  }
}

// Notification actions
const openNotification = (notification: Notification) => {
  selectedNotification.value = notification
  showNotificationDetail.value = true
  // Auto-mark as read when opened
  if (!notification.read) {
    void markAsRead(notification)
  }
}

const toggleReadStatus = (notification: Notification) => {
  if (notification.read) {
    void markAsUnread(notification)
  } else {
    void markAsRead(notification)
  }
}

const markAsRead = async (n: Notification | null) => {
  if (!n) return
  try {
    await api.post(`/patient/notifications/${n.id}/read/`)
    n.read = true
  } catch (e) {
    console.warn('Failed to mark as read', e)
    n.read = true // Update locally anyway
  }
}

const markAsUnread = async (n: Notification | null) => {
  if (!n) return
  try {
    await api.post(`/patient/notifications/${n.id}/unread/`)
    n.read = false
  } catch (e) {
    console.warn('Failed to mark as unread', e)
    n.read = false // Update locally anyway
  }
}

const archiveNotification = async (n: Notification | null) => {
  if (!n) return
  try {
    await api.post(`/patient/notifications/${n.id}/archive/`)
    n.archived = true
  } catch (e) {
    console.warn('Failed to archive notification', e)
    n.archived = true // Update locally anyway
  }
  showActionMenu.value = false
}

const unarchiveNotification = async (n: Notification | null) => {
  if (!n) return
  try {
    await api.post(`/patient/notifications/${n.id}/unarchive/`)
    n.archived = false
  } catch (e) {
    console.warn('Failed to unarchive notification', e)
    n.archived = false // Update locally anyway
  }
  showActionMenu.value = false
}

const deleteNotification = async (n: Notification | null) => {
  if (!n) return
  try {
    await api.delete(`/patient/notifications/${n.id}/`)
    notifications.value = notifications.value.filter(x => x.id !== n.id)
  } catch (e) {
    console.warn('Failed to delete notification', e)
    notifications.value = notifications.value.filter(x => x.id !== n.id) // Remove locally anyway
  }
  showActionMenu.value = false
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
</script>

<style scoped>
.notification-card { border-left: 4px solid var(--q-color-primary); }
.unread { font-weight: 600; }
</style>