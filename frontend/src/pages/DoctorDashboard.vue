<template>
  <q-layout view="hHh Lpr fFf">
    <q-header elevated class="prototype-header safe-area-top">
      <q-toolbar class="header-toolbar">
        <q-btn dense flat round icon="menu" @click="toggleRightDrawer" class="menu-toggle-btn" />

        <div class="header-left">
          <div class="search-container">
            <q-input
              outlined
              dense
              v-model="text"
              placeholder="Search Patient, symptoms and Appointments"
              class="search-input"
              bg-color="white"
            >
              <template v-slot:prepend>
                <q-icon name="search" color="grey-6" />
              </template>
              <template v-slot:append v-if="text">
                <q-icon name="clear" class="cursor-pointer" @click="text = ''" />
              </template>
            </q-input>

            <div v-if="searchResults.length > 0" class="search-results">
              <q-list dense>
                <q-item
                  v-for="result in searchResults"
                  :key="`${result.type}-${result.data.id}`"
                  clickable
                >
                  <q-item-section avatar>
                    <q-icon :name="getSearchResultIcon(result.type)" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ getSearchResultTitle(result) }}</q-item-label>
                    <q-item-label caption>{{ getSearchResultSubtitle(result) }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </div>

        <div class="header-right">
          <q-btn
            flat
            round
            icon="notifications"
            class="notification-btn"
            @click="showNotifications = true"
          >
            <q-badge color="red" floating v-if="unreadNotificationsCount > 0">{{
              unreadNotificationsCount
            }}</q-badge>
          </q-btn>

          <div class="time-display">
            <q-icon name="schedule" size="md" />
            <span class="time-text">{{ currentTime }}</span>
          </div>

          <div class="weather-display" v-if="weatherData">
            <q-icon :name="getWeatherIcon(weatherData.condition)" size="sm" />
            <span class="weather-text">{{ weatherData.temperature }}°C</span>
            <span class="weather-location">{{ weatherData.location }}</span>
          </div>

          <div class="weather-loading" v-else-if="weatherLoading">
            <q-spinner size="sm" />
            <span class="weather-text">Loading weather...</span>
          </div>

          <div class="weather-error" v-else-if="weatherError">
            <q-icon name="error" size="sm" />
            <span class="weather-text">Weather Update and Place</span>
          </div>
        </div>
      </q-toolbar>

      <div class="mobile-header-layout">
        <div class="header-top-row">
          <q-btn dense flat round icon="menu" @click="toggleRightDrawer" class="menu-toggle-btn" />

          <div class="header-info">
            <div class="time-display">
              <q-icon name="schedule" size="sm" />
              <span class="time-text">{{ currentTime }}</span>
            </div>

            <div class="weather-display" v-if="weatherData">
              <q-icon :name="getWeatherIcon(weatherData.condition)" size="sm" />
              <span class="weather-text">{{ weatherData.temperature }}°C</span>
              <span class="weather-location">{{ weatherData.location }}</span>
            </div>

            <div class="weather-loading" v-else-if="weatherLoading">
              <q-spinner size="sm" />
              <span class="weather-text">Loading...</span>
            </div>

            <div class="weather-error" v-else-if="weatherError">
              <q-icon name="error" size="sm" />
              <span class="weather-text">Weather Update</span>
            </div>
          </div>

          <q-btn
            flat
            round
            icon="notifications"
            class="notification-btn"
            @click="showNotifications = true"
          >
            <q-badge color="red" floating v-if="unreadNotificationsCount > 0">{{
              unreadNotificationsCount
            }}</q-badge>
          </q-btn>
        </div>

        <div class="header-bottom-row">
          <div class="search-container">
            <q-input
              outlined
              dense
              v-model="text"
              placeholder="Search Patient, symptoms and Appointments"
              class="search-input"
              bg-color="white"
            >
              <template v-slot:prepend>
                <q-icon name="search" color="grey-6" />
              </template>
              <template v-slot:append v-if="text">
                <q-icon name="clear" class="cursor-pointer" @click="text = ''" />
              </template>
            </q-input>
          </div>
        </div>
      </div>
    </q-header>

    <q-drawer
      v-model="rightDrawerOpen"
      side="left"
      overlay
      bordered
      class="prototype-sidebar"
      :width="280"
    >
      <div class="sidebar-content">
        <div class="logo-section">
          <div class="logo-container">
            <q-avatar size="40px" class="logo-avatar">
              <img src="../assets/logo.png" alt="MediSync Logo" />
            </q-avatar>
            <span class="logo-text">MediSync</span>
          </div>
          <q-btn dense flat round icon="menu" @click="toggleRightDrawer" class="menu-btn" />
        </div>

        <div class="sidebar-user-profile">
          <div class="profile-picture-container">
            <q-avatar size="80px" class="profile-avatar">
              <img v-if="profilePictureUrl" :src="profilePictureUrl" alt="Profile Picture" />
              <div v-else class="profile-placeholder">
                {{ userInitials }}
              </div>
            </q-avatar>
            <q-btn
              round
              color="primary"
              icon="camera_alt"
              size="sm"
              class="upload-btn"
              @click="triggerFileUpload"
            />
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              style="display: none"
              @change="handleProfilePictureUpload"
            />
            <q-icon
              :name="userProfile.verification_status === 'approved' ? 'check_circle' : 'cancel'"
              :color="userProfile.verification_status === 'approved' ? 'positive' : 'negative'"
              class="verified-badge"
            />
          </div>

          <div class="user-info">
            <h6 class="user-name">{{ userProfile.full_name || 'Loading...' }}</h6>
            <p class="user-role">{{ userProfile.specialization || 'Loading specialization...' }}</p>
            <q-chip
              :color="userProfile.verification_status === 'approved' ? 'positive' : 'negative'"
              text-color="white"
              size="sm"
            >
              {{ userProfile.verification_status === 'approved' ? 'Verified' : 'Not Verified' }}
            </q-chip>
          </div>
        </div>

        <q-list class="navigation-menu">
          <q-item
            clickable
            v-ripple
            @click="navigateTo('doctor-dashboard')"
            class="nav-item active"
          >
            <q-item-section avatar>
              <q-icon name="dashboard" />
            </q-item-section>
            <q-item-section>Dashboard</q-item-section>
          </q-item>

          <q-item clickable v-ripple @click="navigateTo('appointments')" class="nav-item">
            <q-item-section avatar>
              <q-icon name="event" />
            </q-item-section>
            <q-item-section>Appointments</q-item-section>
          </q-item>

          <q-item clickable v-ripple @click="navigateTo('messaging')" class="nav-item">
            <q-item-section avatar>
              <q-icon name="message" />
            </q-item-section>
            <q-item-section>Messaging</q-item-section>
          </q-item>

          <q-item clickable v-ripple @click="navigateTo('patients')" class="nav-item">
            <q-item-section avatar>
              <q-icon name="people" />
            </q-item-section>
            <q-item-section>Patient Management</q-item-section>
          </q-item>

          <q-item clickable v-ripple @click="navigateTo('analytics')" class="nav-item">
            <q-item-section avatar>
              <q-icon name="analytics" />
            </q-item-section>
            <q-item-section>Analytics</q-item-section>
          </q-item>

          <q-item clickable v-ripple @click="navigateTo('settings')" class="nav-item">
            <q-item-section avatar>
              <q-icon name="settings" />
            </q-item-section>
            <q-item-section>Settings</q-item-section>
          </q-item>
        </q-list>

        <div class="logout-section">
          <q-btn color="negative" icon="logout" label="LOGOUT" class="logout-btn" @click="logout" />
        </div>
      </div>
    </q-drawer>

    <q-page-container class="page-container-with-fixed-header safe-area-bottom">
      <div class="greeting-section">
        <q-card class="greeting-card">
          <q-card-section class="greeting-content">
            <h2 class="greeting-text">
              Good {{ getTimeOfDay() }},
              {{ userProfile.role.charAt(0).toUpperCase() + userProfile.role.slice(1) }}
              {{ userProfile.full_name }}
            </h2>
            <p class="greeting-subtitle">See what's happening today - {{ currentDate }}</p>
          </q-card-section>
        </q-card>
      </div>

      <div class="dashboard-cards-section">
        <div class="dashboard-cards-grid">
          <q-card class="dashboard-card appointments-card" @click="showTodayAppointmentsModal">
            <q-card-section class="card-content">
              <div class="card-text">
                <div class="card-title">Today's Appointment</div>
                <div class="card-description">
                  {{ dashboardStats.todayAppointments }} appointments today
                </div>
                <div class="card-value">
                  <q-spinner v-if="statsLoading" size="md" />
                  <span v-else>{{ dashboardStats.todayAppointments }}</span>
                </div>
              </div>
              <div class="card-icon">
                <q-icon name="event" size="2.5rem" />
              </div>
            </q-card-section>
          </q-card>

          <q-card class="dashboard-card patients-card" @click="showTotalPatientsModal">
            <q-card-section class="card-content">
              <div class="card-text">
                <div class="card-title">Total Patient</div>
                <div class="card-description">Based on completed assessments</div>
                <div class="card-value">
                  <q-spinner v-if="statsLoading" size="md" />
                  <span v-else>{{ dashboardStats.totalPatients }}</span>
                </div>
              </div>
              <div class="card-icon">
                <q-icon name="people" size="2.5rem" />
              </div>
            </q-card-section>
          </q-card>

          <q-card class="dashboard-card completed-card" @click="showCompletedAppointmentsModal">
            <q-card-section class="card-content">
              <div class="card-text">
                <div class="card-title">Completed Appointment</div>
                <div class="card-description">All transaction history</div>
                <div class="card-value">
                  <q-spinner v-if="statsLoading" size="md" />
                  <span v-else>{{ dashboardStats.completedAppointments }}</span>
                </div>
              </div>
              <div class="card-icon">
                <q-icon name="check_circle" size="2.5rem" />
              </div>
            </q-card-section>
          </q-card>

          <q-card class="dashboard-card assessment-card" @click="showPendingAssessmentsModal">
            <q-card-section class="card-content">
              <div class="card-text">
                <div class="card-title">Pending Assessment</div>
                <div class="card-description">Currently being assessed by nurses</div>
                <div class="card-value">
                  <q-spinner v-if="statsLoading" size="md" />
                  <span v-else>{{ dashboardStats.pendingAssessments }}</span>
                </div>
              </div>
              <div class="card-icon">
                <q-icon name="assignment" size="2.5rem" />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <q-dialog v-model="todayAppointmentsModal" persistent>
        <q-card class="modal-card">
          <q-card-section class="modal-header">
            <div class="modal-title">Today's Appointments</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup class="modal-close-btn" />
          </q-card-section>

          <q-card-section>
            <q-list separator>
              <q-item
                v-for="appointment in todayAppointments"
                :key="appointment.id"
                class="q-pa-md"
              >
                <q-item-section avatar>
                  <q-avatar color="primary" text-color="white">
                    {{ appointment.patient?.name?.charAt(0) || 'P' }}
                  </q-avatar>
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ appointment.patient?.name || 'Unknown Patient' }}</q-item-label>
                  <q-item-label caption
                    >Appointment Time: {{ formatTime(appointment.appointment_time) }}</q-item-label
                  >
                  <q-item-label caption>Status: {{ appointment.status }}</q-item-label>
                </q-item-section>

                <q-item-section side>
                  <q-chip :color="getStatusColor(appointment.status)" text-color="white">
                    {{ appointment.status }}
                  </q-chip>
                </q-item-section>
              </q-item>
            </q-list>

            <div v-if="todayAppointments.length === 0" class="text-center q-pa-md text-grey-6">
              No appointments scheduled for today.
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>

      <q-dialog v-model="totalPatientsModal" persistent>
        <q-card class="modal-card">
          <q-card-section class="modal-header">
            <div class="modal-title">Total Patients (Completed Assessments)</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup class="modal-close-btn" />
          </q-card-section>

          <q-card-section>
            <q-list separator>
              <q-item v-for="patient in totalPatients" :key="patient.id" class="q-pa-md">
                <q-item-section avatar>
                  <q-avatar color="green" text-color="white">
                    {{ patient.patient?.name?.charAt(0) || 'P' }}
                  </q-avatar>
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ patient.patient?.name || 'Unknown Patient' }}</q-item-label>
                  <q-item-label caption
                    >Assessment Date: {{ formatDate(patient.assessment_date) }}</q-item-label
                  >
                  <q-item-label caption
                    >Completed by: {{ patient.nurse?.name || 'Unknown Nurse' }}</q-item-label
                  >
                </q-item-section>

                <q-item-section side>
                  <q-chip color="green" text-color="white"> Completed </q-chip>
                </q-item-section>
              </q-item>
            </q-list>

            <div v-if="totalPatients.length === 0" class="text-center q-pa-md text-grey-6">
              No completed assessments found.
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>

      <q-dialog v-model="completedAppointmentsModal" persistent>
        <q-card class="modal-card">
          <q-card-section class="modal-header">
            <div class="modal-title">Completed Appointments (Transaction History)</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup class="modal-close-btn" />
          </q-card-section>

          <q-card-section>
            <q-list separator>
              <q-item
                v-for="appointment in completedAppointments"
                :key="appointment.id"
                class="q-pa-md"
              >
                <q-item-section avatar>
                  <q-avatar color="orange" text-color="white">
                    {{ appointment.patient?.name?.charAt(0) || 'P' }}
                  </q-avatar>
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ appointment.patient?.name || 'Unknown Patient' }}</q-item-label>
                  <q-item-label caption
                    >Appointment Date: {{ formatDate(appointment.appointment_date) }}</q-item-label
                  >
                  <q-item-label caption
                    >Completed: {{ formatDateTime(appointment.completed_at) }}</q-item-label
                  >
                </q-item-section>

                <q-item-section side>
                  <q-chip color="orange" text-color="white"> Completed </q-chip>
                </q-item-section>
              </q-item>
            </q-list>

            <div v-if="completedAppointments.length === 0" class="text-center q-pa-md text-grey-6">
              No completed appointments found.
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>

      <q-dialog v-model="pendingAssessmentsModal" persistent>
        <q-card class="modal-card">
          <q-card-section class="modal-header">
            <div class="modal-title">Pending Assessments</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup class="modal-close-btn" />
          </q-card-section>

          <q-card-section>
            <q-list separator>
              <q-item v-for="assessment in pendingAssessments" :key="assessment.id" class="q-pa-md">
                <q-item-section avatar>
                  <q-avatar color="purple" text-color="white">
                    {{ assessment.patient?.name?.charAt(0) || 'P' }}
                  </q-avatar>
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ assessment.patient?.name || 'Unknown Patient' }}</q-item-label>
                  <q-item-label caption
                    >Assessment Started: {{ formatDateTime(assessment.created_at) }}</q-item-label
                  >
                  <q-item-label caption
                    >Assigned Nurse: {{ assessment.nurse?.name || 'Unknown Nurse' }}</q-item-label
                  >
                </q-item-section>

                <q-item-section side>
                  <q-chip color="purple" text-color="white"> In Progress </q-chip>
                </q-item-section>
              </q-item>
            </q-list>

            <div v-if="pendingAssessments.length === 0" class="text-center q-pa-md text-grey-6">
              No pending assessments found.
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>

      <q-dialog v-model="showNotifications" persistent>
        <q-card class="modal-card notification-modal">
          <q-card-section class="modal-header">
            <div class="modal-title">Notifications</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup class="modal-close-btn" />
          </q-card-section>

          <q-card-section>
            <div v-if="notifications.length === 0" class="text-center text-grey-6 q-py-lg">
              No notifications yet
            </div>
            <div v-else>
              <q-list>
                <q-item
                  v-for="notification in notifications"
                  :key="notification.id"
                  clickable
                  @click="handleNotificationClick(notification)"
                  :class="{ unread: !notification.is_read }"
                >
                  <q-item-section avatar>
                    <q-icon name="info" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ notification.message }}</q-item-label>
                    <q-item-label caption class="text-grey-5">{{
                      formatTime(notification.created_at)
                    }}</q-item-label>
                  </q-item-section>
                  <q-item-section side v-if="!notification.is_read">
                    <q-badge color="red" rounded />
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </q-card-section>

          <q-card-actions align="right" v-if="notifications.length > 0">
            <q-btn flat label="Mark All Read" @click="markAllNotificationsRead" />
            <q-btn flat label="Close" color="primary" v-close-popup />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from '../boot/axios';
import { useIntervalManager } from '../utils/intervalManager';

// Type definitions
interface Patient {
  id: number;
  name: string;
  [key: string]: unknown;
}

interface Nurse {
  id: number;
  name: string;
  [key: string]: unknown;
}

interface Appointment {
  id: number;
  patient?: Patient;
  appointment_time?: string;
  appointment_date?: string;
  status: string;
  completed_at?: string;
  [key: string]: unknown;
}

interface Assessment {
  id: number;
  patient?: Patient;
  nurse?: Nurse;
  assessment_date?: string;
  status: string;
  created_at?: string;
  [key: string]: unknown;
}

const router = useRouter();
const $q = useQuasar();

const rightDrawerOpen = ref(false);
const text = ref('');

// Carousel variables (removed but keeping for potential future use)
// const slide = ref(1)
// const autoplay = ref(true)

// Dashboard statistics
const dashboardStats = ref({
  todayAppointments: 0,
  totalPatients: 0,
  completedAppointments: 0,
  pendingAssessments: 0,
});

// Loading states for dashboard stats
const statsLoading = ref(true);

// Modal states
const todayAppointmentsModal = ref(false);
const totalPatientsModal = ref(false);
const completedAppointmentsModal = ref(false);
const pendingAssessmentsModal = ref(false);
const showNotifications = ref(false);

// Modal data
const todayAppointments = ref<Appointment[]>([]);
const totalPatients = ref<Assessment[]>([]);
const completedAppointments = ref<Appointment[]>([]);
const pendingAssessments = ref<Assessment[]>([]);

// Loading states for modals
const modalLoading = ref(false);

// Notification system
const notifications = ref<
  {
    id: number;
    message: string;
    is_read: boolean;
    created_at: string;
  }[]
>([]);

// Notification interface
interface Notification {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string;
}

// Search functionality
interface SearchResult {
  type: string;
  data: {
    id: number;
    name?: string;
    title?: string;
    description?: string;
    details?: string;
  };
}

const searchResults = ref<SearchResult[]>([]);

// Real-time features
const currentTime = ref('');
const weatherData = ref<{
  temperature: number;
  condition: string;
  location: string;
} | null>(null);
const weatherLoading = ref(false);
const weatherError = ref(false);

// Initialize interval manager
const { createTimeInterval, createNotificationInterval } = useIntervalManager();

// User profile data - fetched from API
const userProfile = ref<{
  id?: number;
  full_name: string;
  specialization?: string;
  role: string;
  profile_picture: string | null;
  verification_status: string;
}>({
  full_name: 'Loading...',
  specialization: 'Loading specialization...',
  role: 'doctor',
  profile_picture: null,
  verification_status: 'not_submitted',
});

// File input reference for profile picture upload
const fileInput = ref<HTMLInputElement | null>(null);

const userInitials = computed(() => {
  if (!userProfile.value.full_name) return 'U';
  return userProfile.value.full_name
    .split(' ')
    .map((name) => name.charAt(0))
    .join('')
    .toUpperCase();
});

// Get time of day for greeting
const getTimeOfDay = () => {
  const hour = new Date().getHours();
  if (hour < 12) return 'morning';
  if (hour < 18) return 'afternoon';
  return 'evening';
};

// Current date for greeting
const currentDate = computed(() => {
  const now = new Date();
  return now.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
});

// Format profile picture URL
const profilePictureUrl = computed(() => {
  if (!userProfile.value.profile_picture) {
    return null;
  }

  // If it's already a full URL, return as is
  if (userProfile.value.profile_picture.startsWith('http')) {
    return userProfile.value.profile_picture;
  }

  // Otherwise, construct the full URL
  return `http://localhost:8000${userProfile.value.profile_picture}`;
});

// Time is now updated via interval manager

// Weather icon mapping
const getWeatherIcon = (condition: string) => {
  const iconMap: { [key: string]: string } = {
    sunny: 'wb_sunny',
    cloudy: 'cloud',
    rainy: 'grain',
    stormy: 'thunderstorm',
    snowy: 'ac_unit',
    foggy: 'foggy',
  };
  return iconMap[condition.toLowerCase()] || 'wb_sunny';
};

// Search helper functions
const getSearchResultIcon = (type: string) => {
  const iconMap: { [key: string]: string } = {
    patient: 'person',
    symptom: 'local_hospital',
    appointment: 'event',
  };
  return iconMap[type.toLowerCase()] || 'search';
};

const getSearchResultTitle = (result: SearchResult) => {
  return result.data.name || result.data.title || 'Unknown';
};

const getSearchResultSubtitle = (result: SearchResult) => {
  return result.data.description || result.data.details || '';
};

// Fetch weather data
const fetchWeatherData = async () => {
  weatherLoading.value = true;
  weatherError.value = false;

  try {
    // Mock weather data - replace with actual API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    weatherData.value = {
      temperature: 28,
      condition: 'sunny',
      location: 'Mandaluyong City',
    };
  } catch (error) {
    console.error('Failed to fetch weather data:', error);
    weatherError.value = true;
  } finally {
    weatherLoading.value = false;
  }
};

const toggleRightDrawer = () => {
  rightDrawerOpen.value = !rightDrawerOpen.value;
};

// Profile picture upload functions
const triggerFileUpload = () => {
  fileInput.value?.click();
};

const handleProfilePictureUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
      $q.notify({
        type: 'negative',
        message: 'Please select a valid image file (JPG, PNG)',
        position: 'top',
        timeout: 3000,
      });
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      $q.notify({
        type: 'negative',
        message: 'File size must be less than 5MB',
        position: 'top',
        timeout: 3000,
      });
      return;
    }

    try {
      const formData = new FormData();
      formData.append('profile_picture', file);

      const response = await api.post('/users/profile/update/picture/', formData);

      userProfile.value.profile_picture = response.data.user.profile_picture;

      // Store the updated profile picture in localStorage for cross-page sync
      const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
      currentUser.profile_picture = response.data.user.profile_picture;
      localStorage.setItem('user', JSON.stringify(currentUser));

      // Show success toast
      $q.notify({
        type: 'positive',
        message: 'Profile picture updated successfully!',
        position: 'top',
        timeout: 3000,
      });

      // Clear the file input
      target.value = '';
    } catch (error: unknown) {
      console.error('Profile picture upload failed:', error);

      let errorMessage = 'Failed to upload profile picture. Please try again.';

      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as {
          response?: {
            data?: { profile_picture?: string[]; detail?: string; error?: string };
            status?: number;
          };
        };
        console.error('Upload error response:', axiosError.response?.data);

        if (axiosError.response?.data?.profile_picture?.[0]) {
          errorMessage = axiosError.response.data.profile_picture[0];
        } else if (axiosError.response?.data?.detail) {
          errorMessage = axiosError.response.data.detail;
        } else if (axiosError.response?.data?.error) {
          errorMessage = axiosError.response.data.error;
        } else if (axiosError.response?.status === 413) {
          errorMessage = 'File too large. Please select a smaller image.';
        } else if (axiosError.response?.status === 400) {
          errorMessage = 'Invalid file format. Please select a valid image file.';
        } else if (axiosError.response?.status === 500) {
          errorMessage = 'Server error. Please try again later.';
        }
      } else if (error && typeof error === 'object' && 'message' in error) {
        const errorMsg = (error as { message: string }).message;
        if (errorMsg.includes('Network Error')) {
          errorMessage = 'Network error. Please check your connection and try again.';
        }
      }

      $q.notify({
        type: 'negative',
        message: errorMessage,
        position: 'top',
        timeout: 5000,
      });
    }
  }
};

// Fetch user profile data
const fetchUserProfile = async () => {
  try {
    const response = await api.get('/users/profile/');
    const userData = response.data.user; // The API returns nested user data

    // Check localStorage for updated profile picture
    const storedUser = JSON.parse(localStorage.getItem('user') || '{}');

    userProfile.value = {
      id: userData.id,
      full_name: userData.full_name,
      specialization: userData.doctor_profile?.specialization,
      role: userData.role,
      profile_picture: storedUser.profile_picture || userData.profile_picture || null,
      verification_status: userData.verification_status,
    };

    console.log('User profile loaded:', userProfile.value);

    // Fetch dashboard stats after profile is loaded
    await fetchDashboardStats();
  } catch (error) {
    console.error('Failed to fetch user profile:', error);

    // Fallback to localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      const user = JSON.parse(userData);
      userProfile.value = {
        id: user.id,
        full_name: user.full_name,
        specialization: user.doctor_profile?.specialization,
        role: user.role,
        profile_picture: user.profile_picture || null,
        verification_status: user.verification_status || 'not_submitted',
      };

      // Still try to fetch dashboard stats
      await fetchDashboardStats();
    } else {
      $q.notify({
        type: 'negative',
        message: 'Failed to load user profile',
        position: 'top',
        timeout: 3000,
      });
    }
  }
};

const navigateTo = (route: string) => {
  // Close drawer first
  rightDrawerOpen.value = false;

  // Navigate to different sections
  switch (route) {
    case 'doctor-dashboard':
      void router.push('/doctor-dashboard');
      break;
    case 'appointments':
      void router.push('/doctor-appointments');
      break;
    case 'messaging':
      void router.push('/doctor-messaging');
      break;
    case 'patients':
      void router.push('/doctor-patient-management');
      break;
    case 'analytics':
      void router.push('/doctor-predictive-analytics');
      break;
    case 'settings':
      void router.push('/doctor-settings');
      break;
    default:
      console.log('Navigation to:', route);
  }
};

// Modal functions
const showTodayAppointmentsModal = async () => {
  modalLoading.value = true;
  todayAppointmentsModal.value = true;

  try {
    const response = await api.get('/operations/appointments/', {
      params: {
        doctor: userProfile.value.id,
        date: new Date().toISOString().split('T')[0],
        status: 'scheduled',
      },
    });
    todayAppointments.value = response.data.results || response.data || [];
  } catch (error) {
    console.error("Failed to fetch today's appointments:", error);
    todayAppointments.value = [];
  } finally {
    modalLoading.value = false;
  }
};

const showTotalPatientsModal = async () => {
  modalLoading.value = true;
  totalPatientsModal.value = true;

  try {
    const response = await api.get('/operations/patient-assessments/', {
      params: {
        status: 'completed',
      },
    });
    totalPatients.value = response.data.results || response.data || [];
  } catch (error) {
    console.error('Failed to fetch total patients:', error);
    totalPatients.value = [];
  } finally {
    modalLoading.value = false;
  }
};

const showCompletedAppointmentsModal = async () => {
  modalLoading.value = true;
  completedAppointmentsModal.value = true;

  try {
    const response = await api.get('/operations/appointments/', {
      params: {
        doctor: userProfile.value.id,
        status: 'completed',
      },
    });
    completedAppointments.value = response.data.results || response.data || [];
  } catch (error) {
    console.error('Failed to fetch completed appointments:', error);
    completedAppointments.value = [];
  } finally {
    modalLoading.value = false;
  }
};

const showPendingAssessmentsModal = async () => {
  modalLoading.value = true;
  pendingAssessmentsModal.value = true;

  try {
    const response = await api.get('/operations/patient-assessments/', {
      params: {
        status: 'in_progress',
      },
    });
    pendingAssessments.value = response.data.results || response.data || [];
  } catch (error) {
    console.error('Failed to fetch pending assessments:', error);
    pendingAssessments.value = [];
  } finally {
    modalLoading.value = false;
  }
};

// Utility functions for formatting
const formatTime = (timeString?: string) => {
  if (!timeString) return 'N/A';
  return new Date(timeString).toLocaleTimeString('en-US', {
    hour12: true,
    hour: 'numeric',
    minute: '2-digit',
  });
};

const formatDate = (dateString?: string) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

const formatDateTime = (dateString?: string) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};

const getStatusColor = (status?: string) => {
  switch (status?.toLowerCase()) {
    case 'scheduled':
      return 'blue';
    case 'completed':
      return 'green';
    case 'cancelled':
      return 'red';
    case 'in_progress':
      return 'orange';
    default:
      return 'grey';
  }
};

// Notification functions
const unreadNotificationsCount = computed(() => {
  return notifications.value.filter((n) => !n.is_read).length;
});

const loadNotifications = async (): Promise<void> => {
  try {
    console.log('📬 Loading doctor notifications...');

    const response = await api.get('/operations/notifications/');
    notifications.value = response.data || [];

    console.log('✅ Doctor notifications loaded:', notifications.value.length);
  } catch (error: unknown) {
    console.error('❌ Error loading doctor notifications:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to load notifications',
    });
  }
};

const handleNotificationClick = (notification: Notification): void => {
  // Mark as read
  notification.is_read = true;

  // Update on backend
  void markNotificationAsRead(notification.id);
};

const markNotificationAsRead = async (notificationId: number): Promise<void> => {
  try {
    await api.patch(`/operations/notifications/${notificationId}/mark-read/`);
  } catch (error) {
    console.error('Error marking notification as read:', error);
  }
};

const markAllNotificationsRead = async (): Promise<void> => {
  try {
    // Mark all notifications as read locally
    notifications.value.forEach((notification) => {
      notification.is_read = true;
    });

    // Mark all notifications as read on backend
    await api.post('/operations/notifications/mark-all-read/');

    $q.notify({
      type: 'positive',
      message: 'All notifications marked as read',
    });
  } catch (error) {
    console.error('Error marking notifications as read:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to mark notifications as read',
    });
  }
};

const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  void router.push('/login');
};

// Fetch dashboard statistics
const fetchDashboardStats = async () => {
  try {
    statsLoading.value = true;

    // Fetch all required data in parallel
    const [
      todayAppointmentsRes,
      totalPatientsRes,
      completedAppointmentsRes,
      pendingAssessmentsRes,
    ] = await Promise.all([
      // Today's appointments for doctor
      api
        .get('/operations/appointments/', {
          params: {
            doctor: userProfile.value.id,
            date: new Date().toISOString().split('T')[0],
            status: 'scheduled',
          },
        })
        .catch(() => ({ data: { count: 0 } })),

      // Total patients based on completed assessments
      api
        .get('/operations/patient-assessments/', {
          params: {
            status: 'completed',
          },
        })
        .catch(() => ({ data: { count: 0 } })),

      // Completed appointments (transaction history)
      api
        .get('/operations/appointments/', {
          params: {
            doctor: userProfile.value.id,
            status: 'completed',
          },
        })
        .catch(() => ({ data: { count: 0 } })),

      // Pending assessments (currently being assessed by nurses)
      api
        .get('/operations/patient-assessments/', {
          params: {
            status: 'in_progress',
          },
        })
        .catch(() => ({ data: { count: 0 } })),
    ]);

    dashboardStats.value = {
      todayAppointments:
        todayAppointmentsRes.data.count || todayAppointmentsRes.data.results?.length || 0,
      totalPatients: totalPatientsRes.data.count || totalPatientsRes.data.results?.length || 0,
      completedAppointments:
        completedAppointmentsRes.data.count || completedAppointmentsRes.data.results?.length || 0,
      pendingAssessments:
        pendingAssessmentsRes.data.count || pendingAssessmentsRes.data.results?.length || 0,
    };

    console.log('Dashboard stats loaded:', dashboardStats.value);
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error);

    // Set default values on error
    dashboardStats.value = {
      todayAppointments: 0,
      totalPatients: 0,
      completedAppointments: 0,
      pendingAssessments: 0,
    };
  } finally {
    statsLoading.value = false;
  }
};

// Daily refresh functionality
const setupDailyRefresh = () => {
  const now = new Date();
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(0, 0, 0, 0);

  const msUntilMidnight = tomorrow.getTime() - now.getTime();

  setTimeout(() => {
    // Refresh dashboard stats at midnight
    void fetchDashboardStats();

    // Set up daily refresh
    setInterval(
      () => {
        void fetchDashboardStats();
      },
      24 * 60 * 60 * 1000,
    ); // 24 hours
  }, msUntilMidnight);
};

onMounted(() => {
  // Load user profile data from API (this will also fetch dashboard stats)
  void fetchUserProfile();

  // Load notifications
  void loadNotifications();

  // Initialize real-time features with interval manager
  createTimeInterval('doctor-dashboard-time', (time) => {
    currentTime.value = time;
  });

  // Fetch weather data
  void fetchWeatherData();

  // Setup daily refresh
  setupDailyRefresh();

  // Setup notification polling with interval manager
  createNotificationInterval('doctor-dashboard-notifications', loadNotifications, 30000);
});

onUnmounted(() => {
  // Interval manager automatically cleans up intervals
  // No manual cleanup needed
});
</script>

<style scoped>
/* Prototype Header Styles */
.prototype-header {
  background: #286660;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Safe Area Support */
.safe-area-top {
  padding-top: env(safe-area-inset-top);
}

.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}

.safe-area-left {
  padding-left: env(safe-area-inset-left);
}

.safe-area-right {
  padding-right: env(safe-area-inset-right);
}

/* Tooltip Safe Area Support */
.q-tooltip {
  max-width: calc(100vw - env(safe-area-inset-left) - env(safe-area-inset-right) - 16px);
  margin-top: max(env(safe-area-inset-top), 8px);
}

@media (max-width: 768px) {
  .q-tooltip {
    margin-top: max(env(safe-area-inset-top), 12px);
    max-width: calc(100vw - env(safe-area-inset-left) - env(safe-area-inset-right) - 24px);
  }
}

@media (max-width: 480px) {
  .q-tooltip {
    margin-top: max(env(safe-area-inset-top), 16px);
    max-width: calc(100vw - env(safe-area-inset-left) - env(safe-area-inset-right) - 32px);
  }
}

.header-toolbar {
  padding: 0 24px;
  min-height: 64px;
}

/* Mobile Header Layout */
.mobile-header-layout {
  display: flex;
  flex-direction: column;
  padding: 8px 16px;
  min-height: 80px;
}

.header-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  min-height: 40px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  justify-content: center;
}

.header-bottom-row {
  display: flex;
  align-items: center;
  min-height: 40px;
}

/* Responsive Design - Mobile and Web Support */
@media (max-width: 768px) {
  .mobile-header-layout {
    display: flex !important;
  }

  .header-toolbar {
    display: none !important;
  }

  /* Mobile header positioning */
  .prototype-header {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 2000 !important;
    padding-top: max(env(safe-area-inset-top), 8px) !important;
  }

  /* Ensure main content doesn't overlap header */
  .q-page {
    padding-top: calc(env(safe-area-inset-top) + 120px) !important;
  }
}

/* Desktop Header Layout */
@media (min-width: 769px) {
  .mobile-header-layout {
    display: none;
  }

  .prototype-header .header-toolbar {
    display: flex;
  }
}

.menu-toggle-btn {
  color: white;
  margin-right: 16px;
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.search-container {
  width: 100%;
  max-width: 500px;
}

.search-input {
  background: white;
  border-radius: 8px;
}

.notification-btn {
  color: white;
}

.time-display,
.weather-display,
.weather-loading,
.weather-error {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-size: 14px;
}

/* Prototype Sidebar Styles */
.prototype-sidebar {
  background: white;
  border-right: 1px solid #e0e0e0;
}

.sidebar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Mobile Sidebar Styles */
@media (max-width: 768px) {
  .prototype-sidebar {
    width: 100vw !important;
    max-width: 100vw !important;
    z-index: 3000;
  }

  .q-drawer__backdrop {
    z-index: 2999;
  }

  .sidebar-content {
    padding-bottom: 60px;
  }

  .logo-section {
    padding: 16px;
  }

  .logo-text {
    font-size: 18px;
  }

  .sidebar-user-profile {
    padding: 16px;
  }

  .profile-avatar {
    width: 60px;
    height: 60px;
  }

  .user-name {
    font-size: 16px;
  }

  .user-role {
    font-size: 13px;
  }

  .navigation-menu {
    padding: 8px 0;
  }

  .nav-item {
    margin: 2px 12px;
    padding: 8px 12px;
    border-radius: 6px;
  }

  .logout-section {
    padding: 16px;
  }

  .logout-btn {
    padding: 8px 16px;
    font-size: 14px;
    border-radius: 6px;
  }
}

@media (max-width: 480px) {
  .prototype-sidebar {
    width: 100vw !important;
    max-width: 100vw !important;
  }

  .sidebar-content {
    padding-bottom: 50px;
  }

  .logo-section {
    padding: 12px;
  }

  .logo-text {
    font-size: 16px;
  }

  .sidebar-user-profile {
    padding: 12px;
  }

  .profile-avatar {
    width: 50px;
    height: 50px;
  }

  .user-name {
    font-size: 15px;
  }

  .user-role {
    font-size: 12px;
  }

  .navigation-menu {
    padding: 6px 0;
  }

  .nav-item {
    margin: 1px 8px;
    padding: 6px 10px;
    border-radius: 4px;
  }

  .logout-section {
    padding: 12px;
  }

  .logout-btn {
    padding: 6px 12px;
    font-size: 13px;
    border-radius: 4px;
  }
}

.logo-section {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #286660;
}

.menu-btn {
  color: #666;
}

.sidebar-user-profile {
  padding: 24px 20px;
  border-bottom: 1px solid #e0e0e0;
  text-align: center;
}

.profile-picture-container {
  position: relative;
  display: inline-block;
  margin-bottom: 16px;
}

.upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  transform: translate(25%, 25%);
}

.verified-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  background: white;
  border-radius: 50%;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 4px 0;
}

.user-role {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
}

.navigation-menu {
  flex: 1;
  padding: 16px 0;
}

.nav-item {
  margin: 4px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-item.active {
  background: #286660;
  color: white;
}

.nav-item.active .q-icon {
  color: white;
}

.nav-item:hover:not(.active) {
  background: #f5f5f5;
}

.logout-section {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.logout-btn {
  width: 100%;
  border-radius: 8px;
  font-weight: 600;
  text-transform: uppercase;
}

/* Page Container with Background */
.page-container-with-fixed-header {
  background: #f8f9fa;
  background-size: cover;
  min-height: 100vh;
  position: relative;
}

.page-container-with-fixed-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.25) 0%,
    rgba(248, 249, 250, 0.15) 50%,
    rgba(240, 242, 245, 0.08) 100%
  );
  z-index: 0;
  pointer-events: none;
}

.page-container-with-fixed-header > * {
  position: relative;
  z-index: 1;
}

/* Greeting Section */
.greeting-section {
  padding: 24px;
  background: transparent;
}

.greeting-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
}

.greeting-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #286660, #6ca299, #b8d2ce);
  border-radius: 16px 16px 0 0;
}

.greeting-content {
  padding: 24px;
}

.greeting-text {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px 0;
}

.greeting-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

/* Dashboard Cards Section */
.dashboard-cards-section {
  padding: 24px;
}

.dashboard-cards-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Glassmorphism Dashboard Cards */
.dashboard-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  overflow: hidden;
  position: relative;
  min-height: 140px;
}

.dashboard-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #286660, #6ca299, #b8d2ce);
  border-radius: 16px 16px 0 0;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.dashboard-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 0.35);
}

.dashboard-card:hover::before {
  opacity: 1;
}

.card-content {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.card-text {
  flex: 1;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.3;
}

.card-description {
  font-size: 14px;
  color: #666;
  line-height: 1.4;
  margin-bottom: 8px;
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: #286660;
  line-height: 1;
  margin-top: 8px;
}

.card-icon {
  margin-left: 16px;
  color: #286660;
  opacity: 0.8;
  transition: all 0.3s ease;
}

.dashboard-card:hover .card-icon {
  opacity: 1;
  transform: scale(1.1);
}

/* Card-specific colors */
.appointments-card .card-icon {
  color: #2196f3;
}
.appointments-card .card-value {
  color: #2196f3;
}

.patients-card .card-icon {
  color: #4caf50;
}
.patients-card .card-value {
  color: #4caf50;
}

.completed-card .card-icon {
  color: #ff9800;
}
.completed-card .card-value {
  color: #ff9800;
}

.assessment-card .card-icon {
  color: #9c27b0;
}
.assessment-card .card-value {
  color: #9c27b0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .prototype-header {
    padding-top: max(env(safe-area-inset-top), 8px);
  }

  .header-toolbar {
    display: none;
  }

  .mobile-header-layout {
    padding: 8px 12px;
    padding-top: max(env(safe-area-inset-top), 8px);
    min-height: auto;
  }

  .header-top-row {
    margin-bottom: 6px;
    min-height: 36px;
  }

  .header-info {
    gap: 8px;
  }

  .header-bottom-row {
    min-height: 36px;
  }

  .search-container {
    width: 100%;
  }

  .search-input {
    font-size: 14px;
  }

  .search-input .q-field__control {
    min-height: 36px;
  }

  .time-display {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .time-text {
    font-size: 12px;
    font-weight: 500;
  }

  .weather-display {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .weather-text {
    font-size: 11px;
  }

  .weather-location {
    font-size: 10px;
  }

  .notification-btn {
    padding: 4px;
    min-width: 32px;
    min-height: 32px;
  }

  .menu-toggle-btn {
    padding: 4px;
    min-width: 32px;
    min-height: 32px;
  }

  .greeting-section {
    padding: 16px;
  }

  .greeting-content {
    padding: 20px;
  }

  .dashboard-cards-section {
    padding: 16px;
  }

  .dashboard-cards-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .greeting-text {
    font-size: 24px;
  }

  .greeting-subtitle {
    font-size: 14px;
  }

  .card-content {
    padding: 20px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .card-title {
    font-size: 16px;
  }

  .card-description {
    font-size: 13px;
  }

  .card-value {
    font-size: 28px;
    align-self: flex-end;
  }

  .card-icon {
    margin-left: 0;
    align-self: flex-end;
  }
}

@media (max-width: 480px) {
  .prototype-header {
    padding-top: max(env(safe-area-inset-top), 12px);
  }

  .mobile-header-layout {
    padding: 6px 8px;
    padding-top: max(env(safe-area-inset-top), 12px);
  }

  .header-top-row {
    margin-bottom: 4px;
    min-height: 32px;
  }

  .header-info {
    gap: 6px;
  }

  .header-bottom-row {
    min-height: 32px;
  }

  .header-left {
    flex: 1;
    min-width: 0;
  }

  .header-right {
    gap: 6px;
    flex-shrink: 0;
  }

  .search-container {
    max-width: 100%;
    width: 100%;
  }

  .search-input {
    font-size: 12px;
  }

  .search-input .q-field__control {
    min-height: 32px;
  }

  .time-display {
    display: none;
  }

  .weather-display {
    flex-direction: column;
    align-items: center;
    gap: 1px;
  }

  .weather-text {
    font-size: 10px;
  }

  .weather-location {
    font-size: 9px;
  }

  .time-pill,
  .weather-pill,
  .location-pill {
    font-size: 9px;
    padding: 1px 3px;
  }

  .notification-btn {
    padding: 2px;
    min-width: 32px;
    min-height: 32px;
  }

  .menu-toggle-btn {
    padding: 2px;
    min-width: 32px;
    min-height: 32px;
  }

  .greeting-section {
    padding: 12px;
  }

  .greeting-content {
    padding: 16px;
  }

  .dashboard-cards-section {
    padding: 12px;
  }

  .dashboard-cards-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .greeting-text {
    font-size: 20px;
  }

  .greeting-subtitle {
    font-size: 13px;
  }

  .card-content {
    padding: 16px;
  }

  .card-title {
    font-size: 15px;
  }

  .card-description {
    font-size: 12px;
  }

  .card-value {
    font-size: 24px;
  }

  .notification-btn {
    padding: 8px;
  }

  .menu-toggle-btn {
    padding: 8px;
  }
}

/* Profile Avatar Styles - Circular Design */
.profile-avatar {
  border: 3px solid #1e7668 !important;
  border-radius: 50% !important;
  overflow: hidden !important;
}

.profile-avatar img {
  border-radius: 50% !important;
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
}

.profile-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1e7668;
  color: white;
  font-size: 24px;
  font-weight: bold;
  border-radius: 50%;
}

.upload-btn {
  position: absolute;
  bottom: -5px;
  right: -5px;
  background: #1e7668 !important;
  border-radius: 50% !important;
  width: 24px !important;
  height: 24px !important;
  min-height: 24px !important;
  padding: 0 !important;
}

.verified-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

/* Modal Styles */
.modal-card {
  min-width: 800px;
  max-width: 90vw;
  border-radius: 12px;
}

.modal-header {
  display: flex;
  align-items: center;
  padding-bottom: 0;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.modal-close-btn {
  padding: 4px;
  transition: all 0.2s ease;
}

/* Desktop close button styling */
@media (min-width: 769px) {
  .modal-close-btn {
    padding: 6px;
    min-width: 36px;
    min-height: 36px;
    font-size: 18px;
  }

  .modal-close-btn:hover {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 50%;
  }
}

.notification-modal {
  width: 400px;
  max-width: 90vw;
}

/* Global Modal Safe Area Support */
@media (max-width: 768px) {
  :deep(.q-dialog) {
    padding: 0 !important;
    margin: 0 !important;
  }

  :deep(.q-dialog__inner) {
    padding: max(env(safe-area-inset-top), 20px) max(env(safe-area-inset-right), 8px)
      max(env(safe-area-inset-bottom), 8px) max(env(safe-area-inset-left), 8px) !important;
    margin: 0 !important;
    min-height: 100vh !important;
    display: flex !important;
    align-items: flex-start !important;
    justify-content: center !important;
    padding-top: max(env(safe-area-inset-top), 20px) !important;
  }

  :deep(.q-dialog__inner > div) {
    max-height: calc(
      100vh - max(env(safe-area-inset-top), 20px) - max(env(safe-area-inset-bottom), 8px)
    ) !important;
    width: 100% !important;
    max-width: calc(
      100vw - max(env(safe-area-inset-left), 8px) - max(env(safe-area-inset-right), 8px)
    ) !important;
    margin: 0 !important;
  }
}

@media (max-width: 480px) {
  :deep(.q-dialog__inner) {
    padding: max(env(safe-area-inset-top), 24px) max(env(safe-area-inset-right), 4px)
      max(env(safe-area-inset-bottom), 4px) max(env(safe-area-inset-left), 4px) !important;
  }

  :deep(.q-dialog__inner > div) {
    max-height: calc(
      100vh - max(env(safe-area-inset-top), 24px) - max(env(safe-area-inset-bottom), 4px)
    ) !important;
    max-width: calc(
      100vw - max(env(safe-area-inset-left), 4px) - max(env(safe-area-inset-right), 4px)
    ) !important;
  }
}

/* Mobile Modal Styles */
@media (max-width: 768px) {
  .modal-card {
    min-width: unset;
    width: 100%;
    max-width: 100%;
    margin: 0;
    border-radius: 12px;
    max-height: calc(
      100vh - max(env(safe-area-inset-top), 20px) - max(env(safe-area-inset-bottom), 8px)
    );
    overflow-y: auto;
  }

  .modal-header {
    padding: 16px;
    padding-bottom: 0;
  }

  .modal-title {
    font-size: 16px;
  }

  .modal-close-btn {
    padding: 8px !important;
    min-width: 44px !important;
    min-height: 44px !important;
    font-size: 20px !important;
    background: rgba(0, 0, 0, 0.1) !important;
    border-radius: 50% !important;
  }

  .modal-close-btn:hover {
    background: rgba(0, 0, 0, 0.2) !important;
  }

  .notification-modal {
    width: 100%;
    max-width: 100%;
  }

  .q-card__section {
    padding: 16px;
  }

  .q-item {
    padding: 12px 8px;
  }

  .q-item__section--avatar {
    min-width: 40px;
  }

  .q-avatar {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }

  .q-item__label {
    font-size: 14px;
  }

  .q-item__label--caption {
    font-size: 12px;
  }

  .q-chip {
    font-size: 11px;
    padding: 4px 8px;
  }
}

@media (max-width: 480px) {
  .modal-card {
    width: 100%;
    max-width: 100%;
    margin: 0;
    border-radius: 8px;
    max-height: calc(
      100vh - max(env(safe-area-inset-top), 24px) - max(env(safe-area-inset-bottom), 4px)
    );
    overflow-y: auto;
  }

  .modal-header {
    padding: 12px;
    padding-bottom: 0;
  }

  .modal-title {
    font-size: 15px;
  }

  .modal-close-btn {
    padding: 10px !important;
    min-width: 48px !important;
    min-height: 48px !important;
    font-size: 22px !important;
    background: rgba(0, 0, 0, 0.1) !important;
    border-radius: 50% !important;
  }

  .modal-close-btn:hover {
    background: rgba(0, 0, 0, 0.2) !important;
  }

  .notification-modal {
    width: 100%;
    max-width: 100%;
  }

  .q-card__section {
    padding: 12px;
  }

  .q-item {
    padding: 8px 4px;
  }

  .q-avatar {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }

  .q-item__label {
    font-size: 13px;
  }

  .q-item__label--caption {
    font-size: 11px;
  }

  .q-chip {
    font-size: 10px;
    padding: 2px 6px;
  }
}

/* Notification styles */
.unread {
  background-color: rgba(25, 118, 210, 0.05);
  border-left: 3px solid #1976d2;
}

.unread .q-item-label {
  font-weight: 600;
}
</style>
