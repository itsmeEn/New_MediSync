<template>
  <q-layout view="hHh lpR fFf">
    <!-- Header -->
    <header class="bg-teal-800 p-4 md:p-6 shadow-lg">
      <div class="flex justify-between items-center max-w-7xl mx-auto">
        <!-- Logo + Title -->
        <div class="flex items-center space-x-3 text-white">
          <img :src="logoUrl" alt="Project Logo" class="h-10 w-10 rounded-full bg-white object-cover flex-shrink-0" />
          <div>
            <p class="text-lg font-semibold leading-none">Medical Request</p>
            <p class="text-sm font-light text-teal-300 leading-none">Request documents and records</p>
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
        <div class="max-w-7xl mx-auto">
          <h2 class="text-3xl font-bold text-gray-800 mb-6">Medical Records & General Requests</h2>

          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Request Form Panel -->
            <div class="lg:col-span-2 bg-white p-6 rounded-xl shadow-lg border border-gray-200">
              <h3 class="text-xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
                <i data-lucide="file-text" class="w-6 h-6 text-amber-600"></i>
                <span>Request Your Medical Records</span>
              </h3>
              <p class="text-gray-600 mb-6">Use this form to securely request your medical records. The records will be sent directly to your designated doctor or nurse for review and release.</p>
              
              <q-form ref="formRef" @submit="onSubmit" @reset="onReset" class="space-y-4">
                <!-- Request Type -->
                <div class="relative">
                  <label class="block text-sm font-semibold text-teal-600 mb-2">Type of Request</label>
                  <q-select
                    v-model="form.requestType"
                    :options="requestTypeOptions"
                    outlined
                    color="teal"
                    placeholder="Select request type"
                    :rules="[val => !!val || 'Please select a request type']"
                  >
                    <template #prepend>
                      <i data-lucide="file-text" class="w-5 h-5 text-teal-600"></i>
                    </template>
                  </q-select>
                </div>

                <!-- Recipient -->
                <div class="relative">
                  <label class="block text-sm font-semibold text-teal-600 mb-2">Recipient (Doctor/Nurse)</label>
                  <q-input
                    v-model="form.recipient"
                    outlined
                    color="teal"
                    placeholder="Dr. Amelia Chen"
                    :rules="[val => !!val || 'Please enter recipient']"
                  >
                    <template #prepend>
                      <i data-lucide="user" class="w-5 h-5 text-teal-600"></i>
                    </template>
                  </q-input>
                </div>

                <!-- Additional Details -->
                <div class="relative">
                  <label class="block text-sm font-semibold text-teal-600 mb-2">Additional Details (Optional)</label>
                  <q-input
                    v-model="form.details"
                    type="textarea"
                    outlined
                    color="teal"
                    placeholder="I need these records for my upcoming specialist consultation."
                    rows="3"
                  >
                    <template #prepend>
                      <i data-lucide="message-square" class="w-5 h-5 text-teal-600"></i>
                    </template>
                  </q-input>
                </div>

                <!-- Submit Button -->
                <q-btn
                  type="submit"
                  color="teal"
                  class="w-full"
                  label="Submit Record Request"
                  :loading="isSubmitting"
                />
              </q-form>
            </div>

            <!-- History/Status Panel -->
            <div class="lg:col-span-1 bg-white p-6 rounded-xl shadow-lg border border-gray-200">
              <h3 class="text-xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
                <i data-lucide="history" class="w-6 h-6 text-gray-600"></i>
                <span>Request History</span>
              </h3>
              
              <div v-if="recentRequests.length === 0" class="text-center py-8">
                <i data-lucide="file-text" class="w-12 h-12 text-gray-300 mx-auto mb-4"></i>
                <h4 class="text-lg font-semibold text-gray-600 mb-2">No recent requests</h4>
                <p class="text-gray-500 text-sm">Your submitted requests will appear here</p>
              </div>
              
              <div v-else class="space-y-3">
                <div 
                  v-for="request in recentRequests" 
                  :key="request.id"
                  :class="[
                    'p-3 rounded-lg border-l-4',
                    request.status === 'pending' ? 'bg-yellow-50 border-yellow-500' :
                    request.status === 'approved' ? 'bg-green-50 border-green-500' :
                    request.status === 'rejected' ? 'bg-red-50 border-red-500' :
                    'bg-gray-50 border-gray-500'
                  ]"
                >
                  <p class="font-medium text-gray-900">{{ request.type }}</p>
                  <p :class="[
                    'text-sm mt-1',
                    request.status === 'pending' ? 'text-yellow-600' :
                    request.status === 'approved' ? 'text-green-600' :
                    request.status === 'rejected' ? 'text-red-600' :
                    'text-gray-600'
                  ]">
                    Status: <span class="font-semibold">{{ request.status.charAt(0).toUpperCase() + request.status.slice(1) }}</span>
                  </p>
                  <p class="text-xs text-gray-500 mt-1">Date: {{ formatDate(request.createdAt) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
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
import logoUrl from 'src/assets/logo.png'

const router = useRouter()
const showUserMenu = ref(false)
const unreadCount = ref<number>(0)
const isSubmitting = ref(false)
const formRef = ref()

// Form data
const form = ref({
  requestType: '',
  recipient: 'Dr. Amelia Chen',
  details: ''
})

// Form options
const requestTypeOptions = [
  { label: 'Full Medical Records (Last 5 Years)', value: 'full_records' },
  { label: 'Specific Lab Results Only', value: 'lab_results' },
  { label: 'Immunization History', value: 'immunization' },
  { label: 'General Inquiry', value: 'general_inquiry' }
]

// Interface for medical request
interface MedicalRequest {
  id: number
  type: string
  recipient: string
  details: string
  status: string
  createdAt: string
  description?: string
  urgency?: string
  updatedAt?: string
}

// Recent requests
const recentRequests = ref<MedicalRequest[]>([])

// Form submission
const onSubmit = async () => {
  try {
    isSubmitting.value = true
    
    // Validate form
    if (!formRef.value) return
    const valid = await formRef.value.validate()
    if (!valid) return

    // Get patient information
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    
    // Create request object
    const request = {
      id: Date.now(),
      type: requestTypeOptions.find(opt => opt.value === form.value.requestType)?.label || form.value.requestType,
      recipient: form.value.recipient,
      details: form.value.details,
      status: 'pending',
      createdAt: new Date().toISOString(),
      patientName: user.full_name || user.email || 'Unknown Patient',
      patientEmail: user.email || 'No email provided'
    }

    // Save to localStorage
    const requests = JSON.parse(localStorage.getItem('medicalRequests') || '[]')
    requests.unshift(request)
    localStorage.setItem('medicalRequests', JSON.stringify(requests))
    
    // Update recent requests
    recentRequests.value = requests.slice(0, 5)
    
    // Reset form
    onReset()
    
    // Show success message
    alert('Request submitted successfully!')
    
  } catch (error) {
    console.error('Error submitting request:', error)
    alert('Error submitting request. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

const onReset = () => {
  form.value = {
    requestType: '',
    recipient: 'Dr. Amelia Chen',
    details: ''
  }
  if (formRef.value) {
    formRef.value.resetValidation()
  }
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
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

const toggleUserMenu = () => { showUserMenu.value = !showUserMenu.value }

const navigateTo = (path: string) => { void router.push(path) }

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  void router.push('/login')
}

onMounted(async () => {
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
  
  try {
    const res = await api.get('/patient/notifications/unread-count/')
    unreadCount.value = res.data?.count ?? 0
  } catch (e) { 
    console.warn('unread count fetch failed', e)
    unreadCount.value = 0 
  }
  
  // Load recent requests
  try {
    let requests: MedicalRequest[] = JSON.parse(localStorage.getItem('medicalRequests') || '[]')
    
    // Add sample data if no requests exist
    if (requests.length === 0) {
      const sampleRequests = [
        {
          id: 1,
          type: 'Records Request (Full)',
          recipient: 'Dr. Amelia Chen',
          details: 'Request for complete medical records',
          status: 'pending',
          createdAt: new Date('2024-09-01').toISOString(),
          patientName: 'John Smith',
          patientEmail: 'john.smith@email.com'
        },
        {
          id: 2,
          type: 'Lab Results (Specific)',
          recipient: 'Dr. Amelia Chen',
          details: 'Request for specific lab results',
          status: 'pending',
          createdAt: new Date('2024-08-15').toISOString(),
          patientName: 'Sarah Johnson',
          patientEmail: 'sarah.johnson@email.com'
        },
        {
          id: 3,
          type: 'Immunization History',
          recipient: 'Dr. Amelia Chen',
          details: 'Need immunization records for school enrollment',
          status: 'pending',
          createdAt: new Date().toISOString(),
          patientName: 'Michael Brown',
          patientEmail: 'michael.brown@email.com'
        }
      ]
      localStorage.setItem('medicalRequests', JSON.stringify(sampleRequests))
      requests = sampleRequests
    }
    
    recentRequests.value = requests.slice(0, 5) // Show only recent 5
  } catch (e) {
    console.warn('Failed to load recent requests', e)
    recentRequests.value = []
  }
})
</script>

<style scoped>
</style>