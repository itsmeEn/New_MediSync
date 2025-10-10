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
           <div class="text-h5 text-weight-bold q-mb-md text-grey-8">
             Medical Records & General Requests
           </div>

           <div class="q-gutter-md">
             <!-- Request Form Panel -->
             <q-card>
               <q-card-section>
                 <div class="row items-center q-mb-md">
                   <q-avatar color="amber-1" text-color="amber" icon="description" size="48px" class="q-mr-md" />
                   <div>
                     <div class="text-h6 text-weight-bold">
                       Request Your Medical Records
                     </div>
                     <div class="text-caption text-grey-6">
                       Use this form to securely request your medical records
                     </div>
                   </div>
                 </div>
                 
                 <q-form ref="formRef" @submit="onSubmit" @reset="onReset" class="q-gutter-md">
                   <!-- Request Type -->
                   <q-select
                     v-model="form.requestType"
                     :options="requestTypeOptions"
                     outlined
                     label="Type of Request"
                     color="teal"
                     placeholder="Select request type"
                     :rules="[val => !!val || 'Please select a request type']"
                     behavior="menu"
                   >
                     <template #prepend>
                       <q-icon name="description" color="teal" />
                     </template>
                   </q-select>

                   <!-- Recipient -->
                   <q-input
                     v-model="form.recipient"
                     outlined
                     label="Recipient (Doctor/Nurse)"
                     color="teal"
                     placeholder="Dr. Amelia Chen"
                     :rules="[val => !!val || 'Please enter recipient']"
                   >
                     <template #prepend>
                       <q-icon name="person" color="teal" />
                     </template>
                   </q-input>

                   <!-- Additional Details -->
                   <q-input
                     v-model="form.details"
                     type="textarea"
                     outlined
                     label="Additional Details (Optional)"
                     color="teal"
                     placeholder="I need these records for my upcoming specialist consultation."
                     rows="3"
                     autogrow
                   >
                     <template #prepend>
                       <q-icon name="message" color="teal" />
                     </template>
                   </q-input>

                   <!-- Submit Button -->
                   <q-btn
                     type="submit"
                     color="teal"
                     class="full-width"
                     label="Submit Record Request"
                     :loading="isSubmitting"
                     unelevated
                     size="lg"
                   />
                 </q-form>
               </q-card-section>
             </q-card>

             <!-- History/Status Panel -->
             <q-card>
               <q-card-section>
                 <div class="row items-center q-mb-md">
                   <q-avatar color="grey-3" text-color="grey-7" icon="history" size="48px" class="q-mr-md" />
                   <div>
                     <div class="text-h6 text-weight-bold">
                       Request History
                     </div>
                   </div>
                 </div>
                 
                 <div v-if="recentRequests.length === 0" class="text-center q-py-xl">
                   <q-icon name="description" size="64px" color="grey-4" class="q-mb-md" />
                   <div class="text-h6 text-weight-medium text-grey-6 q-mb-sm">
                     No recent requests
                   </div>
                   <div class="text-body2 text-grey-5">
                     Your submitted requests will appear here
                   </div>
                 </div>
                 
                 <q-list v-else separator>
                   <q-item
                     v-for="request in recentRequests" 
                     :key="request.id"
                     class="q-pa-md"
                   >
                     <q-item-section side>
                       <q-icon 
                         :name="request.status === 'pending' ? 'schedule' : 
                                request.status === 'approved' ? 'check_circle' : 
                                request.status === 'rejected' ? 'cancel' : 'help'"
                         :color="request.status === 'pending' ? 'orange' : 
                                request.status === 'approved' ? 'green' : 
                                request.status === 'rejected' ? 'red' : 'grey'"
                         size="md"
                       />
                     </q-item-section>
                     
                     <q-item-section>
                       <q-item-label class="text-weight-medium">
                         {{ request.type }}
                       </q-item-label>
                       <q-item-label caption>
                         Status: {{ request.status.charAt(0).toUpperCase() + request.status.slice(1) }}
                       </q-item-label>
                       <q-item-label caption>
                         Date: {{ formatDate(request.createdAt) }}
                       </q-item-label>
                     </q-item-section>
                     
                     <q-item-section side>
                       <q-badge 
                         :color="request.status === 'pending' ? 'orange' : 
                                request.status === 'approved' ? 'green' : 
                                request.status === 'rejected' ? 'red' : 'grey'"
                         :label="request.status"
                       />
                     </q-item-section>
                   </q-item>
                 </q-list>
               </q-card-section>
             </q-card>
           </div>
         </div>
       </q-page>
     </q-page-container>

    <!-- Bottom Navigation -->
    <q-footer class="bg-white text-grey-8 border-t">
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
          name="records" 
          icon="description" 
          label="Records"
          @click="navigateTo('/patient-medical-request')"
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
            :label="unreadCount"
            floating
          />
        </q-tab>
        <q-tab 
          name="queue" 
          icon="people" 
          label="Queue"
          @click="navigateTo('/patient-queue')"
        />
      </q-tabs>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'src/boot/axios'
import logoUrl from 'src/assets/logo.svg'

const router = useRouter()
const unreadCount = ref<number>(0)
const isSubmitting = ref(false)
const formRef = ref()
const currentTab = ref('records')
const showUserMenu = ref(false)

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