<template>
  <q-layout view="lHh Lpr lFf">
    <!-- Patient Portal Header -->
    <q-header class="bg-white text-teal-9">
      <q-toolbar>
        <q-avatar size="40px" class="q-mr-md">
          <img :src="logoUrl" alt="MediSync Logo" />
        </q-avatar>
        
        <div class="header-content"></div>

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
       <q-page class="patient-bg q-pa-md pb-safe">
         <div class="max-w-4xl mx-auto">
           <div class="text-h5 text-weight-bold q-mb-md">
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
                     <div class="text-caption">
                       Use this form to securely request your medical records
                     </div>
                   </div>
                 </div>
                 
                 <MedicalRecordRequestForm @submitted="onSubmitted" />
                 
                 
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
                 
                 <div v-if="store.recentRequests.length === 0" class="text-center q-py-xl">
                   <q-icon name="description" size="64px" color="grey-4" class="q-mb-md" />
                   <div class="text-h6 text-weight-medium q-mb-sm">
                     No recent requests
                   </div>
                   <div class="text-body2">
                     Your submitted requests will appear here
                   </div>
                 </div>
                 
                 <q-list v-else separator>
                   <q-item
                     v-for="request in store.recentRequests" 
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

    <!-- Success Confirmation Modal -->
    <q-dialog v-model="showSuccessModal" persistent>
      <q-card class="q-pa-md" style="min-width: 400px; max-width: 500px">
        <q-card-section class="text-center">
          <q-icon name="check_circle" size="64px" color="green" class="q-mb-md" />
          <div class="text-h6 text-weight-bold q-mb-sm">Request Submitted Successfully!</div>
          <div class="text-body2 text-grey-7 q-mb-md">
            Your medical certificate request has been submitted and your doctor has been notified.
          </div>
        </q-card-section>

        <q-card-section class="q-gutter-sm">
          <div class="row items-center q-pa-sm bg-grey-1 rounded-borders">
            <q-icon name="tag" size="20px" color="primary" class="q-mr-sm" />
            <div class="col">
              <div class="text-caption text-grey-7">Reference Number</div>
              <div class="text-body1 text-weight-bold">{{ requestReferenceNumber }}</div>
            </div>
          </div>
          
          <div class="row items-center q-pa-sm bg-grey-1 rounded-borders">
            <q-icon name="schedule" size="20px" color="orange" class="q-mr-sm" />
            <div class="col">
              <div class="text-caption text-grey-7">Expected Processing Time</div>
              <div class="text-body1">{{ expectedProcessingTime }}</div>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn 
            flat 
            label="View Request Status" 
            color="primary" 
            @click="viewRequestStatus"
          />
          <q-btn 
            unelevated 
            label="Close" 
            color="primary" 
            @click="showSuccessModal = false"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <PatientBottomNav />
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from 'src/boot/axios'
import logoUrl from 'src/assets/logo.png'
import PatientBottomNav from 'src/components/PatientBottomNav.vue'
import MedicalRecordRequestForm from 'src/components/MedicalRecordRequestForm.vue'
import { useMedicalRequestStore } from 'src/stores/medicalRequest'

const router = useRouter()
const route = useRoute()
const unreadCount = ref<number>(0)
// Submission and form are handled by shared store/component
const showUserMenu = ref(false)
const showSuccessModal = ref(false)
const requestReferenceNumber = ref<string>('')
const expectedProcessingTime = ref<string>('3-5 business days')
const store = useMedicalRequestStore()

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

// Local form state moved to shared store/component



// Removed legacy local form logic (now handled by store/component)

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

const viewRequestStatus = () => {
  showSuccessModal.value = false
  // Scroll to request history section
  setTimeout(() => {
    const historySection = document.querySelector('.text-h6:contains("Request History")')
    if (historySection) {
      historySection.scrollIntoView({ behavior: 'smooth' })
    }
  }, 100)
}

// Shared form submission callback
const onSubmitted = () => {
  requestReferenceNumber.value = store.requestReferenceNumber
  showSuccessModal.value = true
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
  
  // Pre-populate via shared store and load state
  store.prepopulateFromQuery(route.query as Record<string, unknown>)
  await store.loadRequests()
  if (!store.recipientOptions.length) {
    await store.loadRecipients()
  }
})
</script>

<style scoped>
</style>