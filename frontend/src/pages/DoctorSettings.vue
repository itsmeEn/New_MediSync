<template>
  <q-layout view="hHh Lpr fFf">
    <q-header elevated class="prototype-header safe-area-top">
      <!-- Mobile Header Layout -->
      <div class="mobile-header-layout">
        <!-- Top Row: Menu, Time, Weather, Notifications -->
        <div class="header-top-row">
          <q-btn dense flat round icon="menu" @click="toggleRightDrawer" class="menu-toggle-btn" />

          <div class="header-info">
            <!-- Time Display -->
            <div class="time-display">
              <q-icon name="schedule" size="sm" />
              <span class="time-text">{{ currentTime }}</span>
            </div>

            <!-- Weather Display -->
            <div class="weather-display" v-if="weatherData">
              <q-icon :name="getWeatherIcon(weatherData.condition)" size="sm" />
              <span class="weather-text">{{ weatherData.temperature }}°C</span>
              <span class="weather-location">{{ weatherData.location }}</span>
            </div>

            <!-- Loading Weather -->
            <div class="weather-loading" v-else-if="weatherLoading">
              <q-spinner size="sm" />
              <span class="weather-text">Loading...</span>
            </div>

            <!-- Weather Error -->
            <div class="weather-error" v-else-if="weatherError">
              <q-icon name="error" size="sm" />
              <span class="weather-text">Weather Update</span>
            </div>
          </div>

          <!-- Notifications -->
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

        <!-- Bottom Row: Search Bar -->
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
        <!-- Logo Section -->
        <div class="logo-section">
          <div class="logo-container">
            <q-avatar size="40px" class="logo-avatar">
              <img src="../assets/logo.png" alt="MediSync Logo" />
            </q-avatar>
            <span class="logo-text">MediSync</span>
          </div>
          <q-btn dense flat round icon="menu" @click="toggleRightDrawer" class="menu-btn" />
        </div>

        <!-- User Profile Section -->
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
              :name="userProfile?.verification_status === 'approved' ? 'check_circle' : 'cancel'"
              :color="userProfile?.verification_status === 'approved' ? 'positive' : 'negative'"
              class="verified-badge"
            />
          </div>

          <div class="user-info">
            <h6 class="user-name">{{ userProfile?.full_name || 'Loading...' }}</h6>
            <p class="user-role">
              {{ userProfile?.specialization || 'Loading specialization...' }}
            </p>
            <q-chip
              :color="userProfile?.verification_status === 'approved' ? 'positive' : 'negative'"
              text-color="white"
              size="sm"
            >
              {{ userProfile?.verification_status === 'approved' ? 'Verified' : 'Not Verified' }}
            </q-chip>
          </div>
        </div>

        <!-- Navigation Menu -->
        <q-list class="navigation-menu">
          <q-item clickable v-ripple @click="navigateTo('doctor-dashboard')" class="nav-item">
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

          <q-item clickable v-ripple @click="navigateTo('settings')" class="nav-item active">
            <q-item-section avatar>
              <q-icon name="settings" />
            </q-item-section>
            <q-item-section>Settings</q-item-section>
          </q-item>
        </q-list>

        <!-- Logout Section -->
        <div class="logout-section">
          <q-btn color="negative" icon="logout" label="Logout" class="logout-btn" @click="logout" />
        </div>
      </div>
    </q-drawer>

    <!-- Main Content -->
    <q-page-container class="page-container-with-fixed-header">
      <!-- Account Settings Section -->
      <div class="greeting-section">
        <q-card class="greeting-card">
          <q-card-section class="greeting-content">
            <h2 class="greeting-text">Account Settings</h2>
            <p class="greeting-subtitle">Customize your MediSync experience</p>
          </q-card-section>
        </q-card>
      </div>

      <div class="settings-page">
        <div class="settings-container">
          <div class="settings-content">
            <!-- All Settings in One Card -->
            <q-card class="settings-card">
              <q-card-section>
                <h6 class="text-h6 q-mb-lg text-center">Settings</h6>

                <!-- Profile Information Section -->
                <div class="settings-section">
                  <h6 class="text-subtitle1 q-mb-md">Profile Information</h6>

                  <div class="profile-section">
                    <div class="profile-picture-container">
                      <q-avatar size="120px" class="profile-avatar">
                        <img
                          v-if="profilePictureUrl"
                          :src="profilePictureUrl"
                          alt="Profile Picture"
                        />
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
                    </div>

                    <div class="profile-form">
                      <div class="row q-gutter-md">
                        <div class="col-12">
                          <q-input
                            v-model="profileForm.fullName"
                            label="Full Name"
                            outlined
                            readonly
                            class="large-input"
                          />
                        </div>
                        <div class="col-12">
                          <q-input
                            v-model="profileForm.email"
                            label="Email Address"
                            type="email"
                            outlined
                            readonly
                            class="large-input"
                          />
                        </div>
                        <div class="col-12">
                          <q-input
                            v-model="profileForm.phone"
                            label="Phone Number"
                            outlined
                            mask="(###) ### - ####"
                            class="large-input"
                          />
                        </div>
                        <div class="col-12">
                          <q-select
                            v-model="profileForm.specialization"
                            :options="specializationOptions"
                            label="Specialization"
                            outlined
                            emit-value
                            map-options
                            class="large-input"
                          />
                        </div>
                        <div class="col-12">
                          <q-input
                            v-model="profileForm.licenseNumber"
                            label="Medical License Number"
                            outlined
                            readonly
                            class="large-input"
                          />
                        </div>
                        <div class="col-12">
                          <q-input
                            v-model="profileForm.bio"
                            label="Bio"
                            type="textarea"
                            outlined
                            rows="4"
                            placeholder="Tell us about yourself..."
                            class="large-input"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <q-separator class="q-my-lg" />

                <!-- Security Settings Section -->
                <div class="settings-section">
                  <h6 class="text-subtitle1 q-mb-md">Security Settings</h6>

                  <div class="row q-gutter-md">
                    <div class="col-12">
                      <q-input
                        v-model="securityForm.currentPassword"
                        label="Current Password"
                        type="password"
                        outlined
                        :rules="[(val) => !!val || 'Current password is required']"
                        class="large-input"
                      />
                    </div>
                    <div class="col-12">
                      <q-input
                        v-model="securityForm.newPassword"
                        label="New Password"
                        type="password"
                        outlined
                        :rules="[
                          (val) => !!val || 'New password is required',
                          (val) => val.length >= 8 || 'Password must be at least 8 characters',
                        ]"
                        class="large-input"
                      />
                    </div>
                    <div class="col-12">
                      <q-input
                        v-model="securityForm.confirmPassword"
                        label="Confirm New Password"
                        type="password"
                        outlined
                        :rules="[
                          (val) => !!val || 'Please confirm your password',
                          (val) => val === securityForm.newPassword || 'Passwords do not match',
                        ]"
                        class="large-input"
                      />
                    </div>
                    <div class="col-12">
                      <q-toggle
                        v-model="securityForm.twoFactorAuth"
                        label="Enable Two-Factor Authentication"
                        color="primary"
                        class="large-toggle"
                      />
                    </div>
                  </div>
                </div>

                <q-separator class="q-my-lg" />

                <!-- Notification Preferences Section -->
                <div class="settings-section">
                  <h6 class="text-subtitle1 q-mb-md">Notification Preferences</h6>

                  <div class="notification-settings">
                    <div class="notification-item">
                      <div class="notification-info">
                        <div class="notification-title">Patient Alerts</div>
                        <div class="notification-description">
                          Receive notifications for patient emergencies and urgent care needs
                        </div>
                      </div>
                      <q-toggle v-model="notificationSettings.patientAlerts" color="primary" />
                    </div>

                    <div class="notification-item">
                      <div class="notification-info">
                        <div class="notification-title">Appointment Reminders</div>
                        <div class="notification-description">
                          Get reminded about upcoming appointments and schedule changes
                        </div>
                      </div>
                      <q-toggle
                        v-model="notificationSettings.appointmentReminders"
                        color="primary"
                      />
                    </div>

                    <div class="notification-item">
                      <div class="notification-info">
                        <div class="notification-title">Message Notifications</div>
                        <div class="notification-description">
                          Notifications for new messages from patients and colleagues
                        </div>
                      </div>
                      <q-toggle
                        v-model="notificationSettings.messageNotifications"
                        color="primary"
                      />
                    </div>

                    <div class="notification-item">
                      <div class="notification-info">
                        <div class="notification-title">Analytics Updates</div>
                        <div class="notification-description">
                          Weekly analytics reports and predictive insights
                        </div>
                      </div>
                      <q-toggle v-model="notificationSettings.analyticsUpdates" color="primary" />
                    </div>
                  </div>
                </div>

                <q-separator class="q-my-lg" />

                <!-- Account Status Section -->
                <div class="settings-section">
                  <h6 class="text-subtitle1 q-mb-md">Account Status</h6>

                  <div class="row q-gutter-md">
                    <div class="col-12 col-md-6">
                      <div class="status-item">
                        <div class="status-label">Account Type</div>
                        <div class="status-value-right">Doctor</div>
                      </div>
                    </div>
                    <div class="col-12 col-md-6">
                      <div class="status-item">
                        <div class="status-label">Verification Status</div>
                        <div class="status-value-right">
                          <q-chip
                            :color="getVerificationColor(userProfile.verification_status)"
                            text-color="white"
                            :label="getVerificationLabel(userProfile.verification_status)"
                            size="sm"
                          />
                        </div>
                      </div>
                    </div>
                    <div class="col-12 col-md-6">
                      <div class="status-item">
                        <div class="status-label">Last Login</div>
                        <div class="status-value-right">{{ accountStatus.lastLogin }}</div>
                      </div>
                    </div>
                    <div class="col-12 col-md-6">
                      <div class="status-item">
                        <div class="status-label">Member Since</div>
                        <div class="status-value-right">{{ accountStatus.memberSince }}</div>
                      </div>
                    </div>
                  </div>
                </div>

                <q-separator class="q-my-lg" />

                <!-- Quick Actions Section -->
                <div class="settings-section">
                  <h6 class="text-subtitle1 q-mb-md">Quick Actions</h6>

                  <div class="quick-actions-container">
                    <q-btn
                      color="primary"
                      label="Save Changes"
                      icon="save"
                      class="large-button"
                      @click="saveSettings"
                      :loading="saving"
                    />
                    <q-btn
                      color="secondary"
                      label="Export Data"
                      icon="download"
                      class="large-button"
                      @click="exportData"
                    />
                    <q-btn
                      color="accent"
                      label="Backup Settings"
                      icon="backup"
                      class="large-button"
                      @click="backupSettings"
                    />
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </q-page-container>

    <!-- Notifications Modal -->
    <q-dialog v-model="showNotifications" persistent>
      <q-card style="width: 400px; max-width: 90vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Notifications</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
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
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from '../boot/axios';
// import { AxiosError } from 'axios' // Unused import

// Reactive data
const rightDrawerOpen = ref(false);
const text = ref('');
const showNotifications = ref(false);
// const loading = ref(false) // Unused variable

// Header functions
const toggleRightDrawer = () => {
  console.log('Toggle drawer called, current state:', rightDrawerOpen.value);
  rightDrawerOpen.value = !rightDrawerOpen.value;
  console.log('New state:', rightDrawerOpen.value);
};

// User profile data
const userProfile = ref({
  first_name: '',
  last_name: '',
  full_name: '',
  email: '',
  specialization: '',
  role: '',
  profile_picture: '',
  verification_status: 'approved',
});

// Real-time data
const currentTime = ref('');
const weatherData = ref<{
  temperature: number;
  condition: string;
  location: string;
} | null>(null);
const weatherLoading = ref(false);
const weatherError = ref(false);
const timeInterval = ref<ReturnType<typeof setInterval> | null>(null);

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

// Loading states
const saving = ref(false);

// Form data
const profileForm = ref({
  fullName: '',
  email: '',
  phone: '',
  specialization: '',
  licenseNumber: '',
  bio: '',
});

const securityForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
  twoFactorAuth: false,
});

const notificationSettings = ref({
  patientAlerts: true,
  appointmentReminders: true,
  messageNotifications: true,
  analyticsUpdates: true,
});

// Account status
const accountStatus = ref({
  verified: true,
  lastLogin: '2024-01-15 10:30 AM',
  memberSince: '2023-06-15',
});

// Options
const specializationOptions = [
  { label: 'Internal Medicine', value: 'internal_medicine' },
  { label: 'Cardiology', value: 'cardiology' },
  { label: 'Dermatology', value: 'dermatology' },
  { label: 'Emergency Medicine', value: 'emergency_medicine' },
  { label: 'Family Medicine', value: 'family_medicine' },
  { label: 'Neurology', value: 'neurology' },
  { label: 'Orthopedics', value: 'orthopedics' },
  { label: 'Pediatrics', value: 'pediatrics' },
  { label: 'Psychiatry', value: 'psychiatry' },
  { label: 'Radiology', value: 'radiology' },
  { label: 'Surgery', value: 'surgery' },
  { label: 'Other', value: 'other' },
];

// File input reference for profile picture upload
const fileInput = ref<HTMLInputElement | null>(null);

// Computed properties
const userInitials = computed(() => {
  if (!userProfile.value.first_name || !userProfile.value.last_name) {
    return 'DR';
  }
  return `${userProfile.value.first_name.charAt(0)}${userProfile.value.last_name.charAt(0)}`.toUpperCase();
});

const profilePictureUrl = computed(() => {
  if (!userProfile.value.profile_picture) {
    return null;
  }

  if (userProfile.value.profile_picture.startsWith('http')) {
    return userProfile.value.profile_picture;
  }

  return `http://localhost:8000${userProfile.value.profile_picture}`;
});

// Router and Quasar
const router = useRouter();
// const route = useRoute() // Unused variable
const $q = useQuasar();

// Methods

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
      // Already on settings page
      break;
    default:
      void router.push(`/${route}`);
  }
};

const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  void router.push('/login');
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
          response?: { data?: { profile_picture?: string[]; detail?: string } };
        };
        if (axiosError.response?.data?.profile_picture?.[0]) {
          errorMessage = axiosError.response.data.profile_picture[0];
        } else if (axiosError.response?.data?.detail) {
          errorMessage = axiosError.response.data.detail;
        }
      }

      $q.notify({
        type: 'negative',
        message: errorMessage,
        position: 'top',
        timeout: 4000,
      });
    }
  }
};

// Real-time functions
const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString('en-US', {
    hour12: true,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

const fetchWeather = async () => {
  if (!navigator.geolocation) {
    weatherError.value = true;
    return;
  }

  weatherLoading.value = true;
  weatherError.value = false;

  try {
    const position = await new Promise<GeolocationPosition>((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject);
    });

    const { latitude, longitude } = position.coords;
    const apiKey = 'YOUR_OPENWEATHER_API_KEY'; // Replace with actual API key
    const response = await fetch(
      `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${apiKey}&units=metric`,
    );

    if (!response.ok) throw new Error('Weather API request failed');

    const data = await response.json();
    weatherData.value = {
      temperature: Math.round(data.main.temp),
      condition: data.weather[0].main.toLowerCase(),
      location: data.name,
    };
  } catch (error) {
    console.error('Weather fetch error:', error);
    weatherError.value = true;
  } finally {
    weatherLoading.value = false;
  }
};

const getWeatherIcon = (condition: string): string => {
  const iconMap: Record<string, string> = {
    clear: 'wb_sunny',
    clouds: 'cloud',
    rain: 'opacity',
    snow: 'ac_unit',
    thunderstorm: 'flash_on',
    drizzle: 'grain',
    mist: 'cloud',
    smoke: 'cloud',
    haze: 'cloud',
    dust: 'cloud',
    fog: 'cloud',
    sand: 'cloud',
    ash: 'cloud',
    squall: 'air',
    tornado: 'air',
  };
  return iconMap[condition] || 'wb_sunny';
};

const saveSettings = async () => {
  saving.value = true;

  try {
    // Save profile information
    await api.put('/users/profile/update/', {
      email: profileForm.value.email,
      phone: profileForm.value.phone,
      bio: profileForm.value.bio,
      doctor_profile: {
        specialization: profileForm.value.specialization,
      },
    });

    // Save notification preferences
    await api.put('/users/notification-preferences/', {
      patient_alerts: notificationSettings.value.patientAlerts,
      appointment_reminders: notificationSettings.value.appointmentReminders,
      message_notifications: notificationSettings.value.messageNotifications,
      analytics_updates: notificationSettings.value.analyticsUpdates,
    });

    // Save security settings if password is being changed
    if (securityForm.value.newPassword) {
      if (securityForm.value.newPassword !== securityForm.value.confirmPassword) {
        $q.notify({
          type: 'negative',
          message: 'New passwords do not match',
          position: 'top',
        });
        return;
      }

      await api.put('/users/change-password/', {
        current_password: securityForm.value.currentPassword,
        new_password: securityForm.value.newPassword,
      });

      // Reset password fields
      securityForm.value.currentPassword = '';
      securityForm.value.newPassword = '';
      securityForm.value.confirmPassword = '';
    }

    $q.notify({
      type: 'positive',
      message: 'Settings saved successfully!',
      position: 'top',
    });
  } catch (error) {
    console.error('Error saving settings:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to save settings. Please try again.',
      position: 'top',
    });
  } finally {
    saving.value = false;
  }
};

const exportData = async () => {
  try {
    $q.loading.show({
      message: 'Exporting profile data...',
      spinnerColor: 'primary',
    });

    // Fetch complete profile data
    const profileResponse = await api.get('/users/profile/');
    const profileData = profileResponse.data.user;

    // Create export data object
    const exportData = {
      profileInformation: {
        fullName: profileData.full_name,
        email: profileData.email,
        phone: profileData.phone || 'Not provided',
        specialization: profileData.doctor_profile?.specialization || 'Not specified',
        licenseNumber: profileData.doctor_profile?.license_number || 'Not provided',
        bio: profileData.bio || 'Not provided',
        verificationStatus: profileData.verification_status,
        memberSince: accountStatus.value.memberSince,
        lastLogin: accountStatus.value.lastLogin,
      },
      exportDate: new Date().toISOString(),
      exportType: 'Doctor Profile Information',
      exportedBy: profileData.full_name,
    };

    // Create and download JSON file
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `doctor-profile-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    $q.notify({
      type: 'positive',
      message: 'Profile data exported successfully!',
      position: 'top',
      timeout: 3000,
    });
  } catch (error) {
    console.error('Export failed:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to export data. Please try again.',
      position: 'top',
      timeout: 4000,
    });
  } finally {
    $q.loading.hide();
  }
};

const backupSettings = async () => {
  try {
    $q.loading.show({
      message: 'Backing up patient management data...',
      spinnerColor: 'primary',
    });

    // Fetch patient management data
    const patientsResponse = await api.get('/operations/patients/');
    const appointmentsResponse = await api.get('/operations/appointments/');

    // Create backup data object
    const backupData = {
      patientManagement: {
        patients: patientsResponse.data.results || patientsResponse.data,
        appointments: appointmentsResponse.data.results || appointmentsResponse.data,
        totalPatients: patientsResponse.data.count || 0,
        totalAppointments: appointmentsResponse.data.count || 0,
      },
      backupDate: new Date().toISOString(),
      backupType: 'Patient Management Data',
      backedUpBy: userProfile.value.full_name,
    };

    // Create and download JSON file
    const dataStr = JSON.stringify(backupData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `doctor-patient-management-backup-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    $q.notify({
      type: 'positive',
      message: 'Patient management data backed up successfully!',
      position: 'top',
      timeout: 3000,
    });
  } catch (error) {
    console.error('Backup failed:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to backup data. Please try again.',
      position: 'top',
      timeout: 4000,
    });
  } finally {
    $q.loading.hide();
  }
};

// Verification status helpers
const getVerificationColor = (status: string | undefined) => {
  switch (status) {
    case 'approved':
    case 'verified':
      return 'positive';
    case 'pending':
    case 'for_review':
      return 'warning';
    case 'declined':
    case 'rejected':
      return 'negative';
    default:
      return 'warning';
  }
};

const getVerificationLabel = (status: string | undefined) => {
  switch (status) {
    case 'approved':
    case 'verified':
      return 'Verified';
    case 'pending':
      return 'Pending';
    case 'for_review':
      return 'For Review';
    case 'declined':
    case 'rejected':
      return 'Declined';
    default:
      return 'Unverified';
  }
};

const fetchUserProfile = async () => {
  try {
    const response = await api.get('/users/profile/');
    const userData = response.data.user || response.data;

    // Check localStorage for updated profile picture
    const storedUser = JSON.parse(localStorage.getItem('user') || '{}');

    // Check if verification status has changed
    const previousStatus = userProfile.value.verification_status;
    const newStatus = userData.verification_status;

    userProfile.value = {
      first_name: userData.first_name,
      last_name: userData.last_name,
      full_name: userData.full_name,
      email: userData.email,
      specialization: userData.doctor_profile?.specialization || userData.specialization,
      role: userData.role,
      profile_picture: storedUser.profile_picture || userData.profile_picture || null,
      verification_status: userData.verification_status,
    };

    // Show notification if verification status changed to approved
    if (previousStatus !== newStatus && newStatus === 'approved') {
      $q.notify({
        type: 'positive',
        message: '🎉 Your account has been verified!',
        position: 'top',
        timeout: 5000,
        actions: [{ label: 'Dismiss', color: 'white' }],
      });
    }

    // Update localStorage with new verification status
    if (storedUser) {
      storedUser.verification_status = newStatus;
      localStorage.setItem('user', JSON.stringify(storedUser));
    }
  } catch (error) {
    console.error('Failed to fetch user profile:', error);
  }
};

// Load user profile data
const loadUserProfile = async () => {
  try {
    const response = await api.get('/users/profile/');
    const userData = response.data.user;

    profileForm.value = {
      fullName: userData.full_name || '',
      email: userData.email || '',
      phone: userData.phone || '',
      specialization: userData.doctor_profile?.specialization || '',
      licenseNumber: userData.doctor_profile?.license_number || '',
      bio: userData.bio || '',
    };
  } catch (error) {
    console.error('Failed to load user profile:', error);

    // Fallback to localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      const user = JSON.parse(userData);
      profileForm.value = {
        fullName: user.full_name || '',
        email: user.email || '',
        phone: user.phone || '',
        specialization: user.doctor_profile?.specialization || '',
        licenseNumber: user.doctor_profile?.license_number || '',
        bio: user.bio || '',
      };
    }
  }
};

// Lifecycle hooks
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

const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};

onMounted(() => {
  void loadUserProfile();
  void fetchUserProfile();

  // Load notifications
  void loadNotifications();

  // Initialize real-time features
  updateTime();
  timeInterval.value = setInterval(updateTime, 1000);
  void fetchWeather();

  // Refresh notifications every 30 seconds
  setInterval(() => void loadNotifications(), 30000);

  // Refresh user profile every 10 seconds to check for verification status updates
  setInterval(() => void fetchUserProfile(), 10000);
});

onUnmounted(() => {
  if (timeInterval.value) {
    clearInterval(timeInterval.value);
  }
});
</script>

<style scoped>
.page-background {
  background: #f8f9fa;
  background-size: cover;
  min-height: 100vh;
}

.settings-page {
  /* background-color: #f5f5f5; */
  min-height: 100vh;
  padding: 20px;
}

.settings-container {
  max-width: 800px;
  margin: 0 auto;
}

.settings-header {
  text-align: center;
  margin-bottom: 30px;
}

.settings-header h2 {
  color: #286660;
  margin-bottom: 10px;
}

.settings-header p {
  color: #666;
  font-size: 16px;
}

.settings-card {
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #eee;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  display: flex;
  align-items: center;
  font-weight: 500;
  color: #333;
}

.settings-actions {
  display: flex;
  justify-content: center;
  margin-top: 30px;
  padding: 20px;
}

/* Real-time info styles */
.real-time-info {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-left: auto;
}

.time-display,
.weather-display,
.weather-loading,
.weather-error {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 12px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.time-text,
.weather-text,
.weather-location {
  font-size: 14px;
  font-weight: 500;
  color: white;
}

.weather-location {
  font-size: 12px;
  opacity: 0.8;
}

/* Drawer styles */
.drawer-content {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.user-profile-section {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.profile-picture-container {
  position: relative;
  display: inline-block;
  margin-bottom: 15px;
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

.profile-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #286660;
  color: white;
  font-weight: bold;
  font-size: 24px;
}

.user-name {
  margin: 0 0 5px 0;
  color: #333;
  font-weight: 600;
}

.user-specialization {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
}

.navigation-menu {
  flex: 1;
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
}

/* Search container */
.search-container {
  flex: 1;
  max-width: 400px;
  margin-right: 20px;
}

.search-input {
  width: 100%;
}

/* Safe Area Support */
.safe-area-top {
  padding-top: env(safe-area-inset-top);
}

.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}

/* Mobile Header Layout */
.mobile-header-layout {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.header-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  min-height: 48px;
}

.header-bottom-row {
  padding: 0 16px 8px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  justify-content: center;
}

/* Time and Weather Display Styles */
.time-display {
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  font-size: 12px;
}

.weather-display {
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  font-size: 12px;
}

.weather-loading,
.weather-error {
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  font-size: 12px;
}

.time-text,
.weather-text {
  font-weight: 500;
}

.weather-location {
  font-size: 10px;
  opacity: 0.8;
}

/* Prototype Header Styles */
.prototype-header {
  background: #286660;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-toolbar {
  padding: 0 24px;
  min-height: 64px;
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
  z-index: 2000;
}

.sidebar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding-bottom: 80px; /* Space for footer */
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

/* Duplicate CSS removed - using standardized styles above */

.logout-btn {
  width: 100%;
  border-radius: 8px;
  font-weight: 600;
  text-transform: uppercase;
}

/* Page Container with Off-White Background */
.page-container-with-fixed-header {
  background: #f8f9fa;
  min-height: 100vh;
  position: relative;
}

/* Prototype Header Styles */

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

/* Settings Section Styles */
.settings-section {
  margin-bottom: 24px;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.settings-section h6 {
  color: #286660;
  font-weight: 600;
  border-bottom: 2px solid #e8f5e8;
  padding-bottom: 8px;
}

/* Profile Section Styles */
.profile-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.profile-picture-container {
  position: relative;
  display: flex;
  justify-content: center;
}

.profile-avatar {
  border: 3px solid #1e7668 !important;
  border-radius: 50% !important;
  overflow: hidden !important;
  box-shadow: 0 4px 12px rgba(40, 102, 96, 0.2);
}

.profile-avatar img {
  border-radius: 50% !important;
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
}

.profile-placeholder {
  background: #286660;
  color: white;
  font-size: 2rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: white;
  border: 2px solid #286660;
}

.profile-form {
  width: 100%;
  max-width: 600px;
}

/* Notification Settings Styles */
.notification-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.notification-info {
  flex: 1;
  margin-right: 16px;
}

.notification-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.notification-description {
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

/* Status Item Styles */
.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e0e0e0;
  width: 100%;
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  font-weight: 500;
  color: #666;
  flex: 1;
}

.status-value {
  font-weight: 600;
  color: #333;
}

.status-value-right {
  font-weight: 600;
  color: #333;
  text-align: right;
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

/* Large Input Styles */
.large-input {
  font-size: 16px;
}

.large-input .q-field__control {
  min-height: 56px;
  font-size: 16px;
}

.large-input .q-field__label {
  font-size: 16px;
  font-weight: 500;
}

.large-input .q-field__native {
  font-size: 16px;
  padding: 12px 16px;
}

.large-toggle {
  font-size: 16px;
}

.large-toggle .q-toggle__label {
  font-size: 16px;
  font-weight: 500;
}

/* Quick Actions Container */
.quick-actions-container {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Large Button Styles */
.large-button {
  min-height: 48px;
  font-size: 16px;
  font-weight: 600;
  padding: 12px 24px;
  min-width: 200px;
  max-width: 200px;
  flex: 1;
}

/* Responsive Design */
@media (max-width: 768px) {
  .prototype-header {
    padding-top: max(env(safe-area-inset-top), 8px);
  }

  .header-toolbar {
    padding: 0 16px;
    min-height: 56px;
    padding-top: max(env(safe-area-inset-top), 4px);
  }

  /* Mobile Header Layout */
  .header-top-row {
    padding: 4px 12px;
    min-height: 44px;
  }

  .header-bottom-row {
    padding: 0 12px 6px;
  }

  .header-info {
    gap: 8px;
  }

  .time-display,
  .weather-display,
  .weather-loading,
  .weather-error {
    font-size: 11px;
  }

  .time-text,
  .weather-text {
    font-size: 11px;
  }

  .weather-location {
    font-size: 9px;
  }

  /* Hide time display on mobile to save space */
  .time-display {
    display: none;
  }

  /* Make weather display more compact */
  .weather-display {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }

  .weather-location {
    display: none;
  }

  .q-page-container {
    padding: 8px;
  }

  .q-card {
    margin: 8px 0;
    border-radius: 12px;
  }

  .q-card__section {
    padding: 16px;
  }

  .profile-section {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }

  .profile-avatar {
    width: 80px;
    height: 80px;
  }

  .profile-info h6 {
    font-size: 18px;
    margin-bottom: 4px;
  }

  .profile-info .text-caption {
    font-size: 13px;
  }

  .form-section {
    margin-bottom: 16px;
  }

  .form-section h6 {
    font-size: 16px;
    margin-bottom: 12px;
  }

  .q-field {
    margin-bottom: 12px;
  }

  .q-field__label {
    font-size: 14px;
  }

  .q-field__control {
    font-size: 14px;
  }

  .notification-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px;
  }

  .notification-info {
    margin-right: 0;
  }

  .notification-info .q-item-label {
    font-size: 14px;
  }

  .notification-info .q-item-label--caption {
    font-size: 12px;
  }

  .status-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
    padding: 12px;
  }

  .q-btn {
    padding: 10px 16px;
    font-size: 14px;
    border-radius: 6px;
  }

  .q-tab {
    padding: 8px 12px;
    font-size: 14px;
  }

  .q-tab-panel {
    padding: 16px 0;
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

@media (max-width: 480px) {
  .prototype-header {
    padding-top: max(env(safe-area-inset-top), 12px);
  }

  .header-toolbar {
    padding: 0 12px;
    min-height: 52px;
    padding-top: max(env(safe-area-inset-top), 6px);
  }

  /* Mobile Header Layout - Extra Small */
  .header-top-row {
    padding: 2px 8px;
    min-height: 40px;
  }

  .header-bottom-row {
    padding: 0 8px 4px;
  }

  .header-info {
    gap: 6px;
  }

  .time-display,
  .weather-display,
  .weather-loading,
  .weather-error {
    font-size: 10px;
  }

  .time-text,
  .weather-text {
    font-size: 10px;
  }

  /* Make weather even more compact */
  .weather-display {
    flex-direction: row;
    align-items: center;
    gap: 2px;
  }

  .weather-location {
    display: none;
  }
}
</style>
