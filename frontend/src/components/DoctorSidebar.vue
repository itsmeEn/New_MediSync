<template>
  <q-drawer
    v-model="drawerOpen"
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
        <q-btn dense flat round icon="menu" @click="toggleDrawer" class="menu-btn" />
      </div>

      <!-- User Profile Section -->
      <div class="sidebar-user-profile">
        <div class="profile-picture-container">
          <q-avatar 
            size="80px" 
            class="profile-avatar clickable-avatar" 
            @click="navigateToProfile"
            v-ripple
          >
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
          <h6 class="user-name clickable-name" @click="navigateToProfile">{{ userProfile.full_name || 'Loading...' }}</h6>
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

      <!-- Navigation Menu -->
      <q-list class="navigation-menu">
        <q-item
          clickable
          v-ripple
          @click="navigateTo('doctor-dashboard')"
          :class="['nav-item', { active: activeRoute === 'doctor-dashboard' }]"
        >
          <q-item-section avatar>
            <q-icon name="dashboard" />
          </q-item-section>
          <q-item-section>Dashboard</q-item-section>
        </q-item>

        <q-item
          clickable
          v-ripple
          @click="navigateTo('appointments')"
          :class="['nav-item', { active: activeRoute === 'appointments' }]"
        >
          <q-item-section avatar>
            <q-icon name="event" />
          </q-item-section>
          <q-item-section>Appointments</q-item-section>
        </q-item>

        <q-item
          clickable
          v-ripple
          @click="navigateTo('messaging')"
          :class="['nav-item', { active: activeRoute === 'messaging' }]"
        >
          <q-item-section avatar>
            <q-icon name="message" />
          </q-item-section>
          <q-item-section>Messaging</q-item-section>
        </q-item>

        <q-item
          clickable
          v-ripple
          @click="navigateTo('patients')"
          :class="['nav-item', { active: activeRoute === 'patients' }]"
        >
          <q-item-section avatar>
            <q-icon name="people" />
          </q-item-section>
          <q-item-section>Patient Management</q-item-section>
        </q-item>

        <q-item
          clickable
          v-ripple
          @click="navigateTo('analytics')"
          :class="['nav-item', { active: activeRoute === 'analytics' }]"
        >
          <q-item-section avatar>
            <q-icon name="analytics" />
          </q-item-section>
          <q-item-section>Analytics</q-item-section>
        </q-item>

        <q-item
          clickable
          v-ripple
          @click="navigateTo('settings')"
          :class="['nav-item', { active: activeRoute === 'settings' }]"
        >
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
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineProps, defineEmits } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';

// Props
interface Props {
  modelValue: boolean;
  activeRoute?: string;
}

const props = withDefaults(defineProps<Props>(), {
  activeRoute: '',
});

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  profilePictureUpdated: [url: string];
}>();

// Types
interface UserProfile {
  id: number;
  full_name: string;
  specialization: string;
  verification_status: string;
  profile_picture?: string;
}

// Router and Quasar
const router = useRouter();
const $q = useQuasar();

// Reactive data
const fileInput = ref<HTMLInputElement | null>(null);
const userProfile = ref<UserProfile>({
  id: 0,
  full_name: '',
  specialization: '',
  verification_status: 'pending',
});

// Computed
const drawerOpen = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
});

const userInitials = computed(() => {
  if (!userProfile.value.full_name) return 'U';
  return userProfile.value.full_name
    .split(' ')
    .map((name) => name.charAt(0))
    .join('')
    .toUpperCase();
});

const profilePictureUrl = computed(() => {
  if (!userProfile.value.profile_picture) {
    return null;
  }

  // If it's already a full URL, return as is
  if (userProfile.value.profile_picture.startsWith('http')) {
    return userProfile.value.profile_picture;
  }

  // Get base URL without /api suffix for media files
  let baseURL = api.defaults.baseURL || 'http://localhost:8000';
  baseURL = baseURL.replace(/\/api\/?$/, '');

  // Check if it's a relative path starting with /
  if (userProfile.value.profile_picture.startsWith('/')) {
    return `${baseURL}${userProfile.value.profile_picture}`;
  }

  // If it's a relative path without leading slash, add it
  return `${baseURL}/${userProfile.value.profile_picture}`;
});

// Methods
const toggleDrawer = () => {
  drawerOpen.value = !drawerOpen.value;
};

const navigateTo = (route: string) => {
  drawerOpen.value = false;
  
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
  }
};

const logout = () => {
  $q.dialog({
    title: 'Confirm Logout',
    message: 'Are you sure you want to logout?',
    cancel: true,
    persistent: true,
  }).onOk(() => {
    // Clear all authentication data
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    
    // Close the drawer
    drawerOpen.value = false;
    
    // Show logout notification
    $q.notify({
      type: 'positive',
      message: 'Logged out successfully',
      position: 'top',
      timeout: 2000,
    });
    
    // Redirect to login page (void to ignore Promise)
    void router.push('/login');
  });
};

const navigateToProfile = () => {
  void router.push('/doctor-settings');
  emit('update:modelValue', false); // Close the sidebar on mobile
};

const triggerFileUpload = () => {
  fileInput.value?.click();
};

const handleProfilePictureUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  
  if (!file) return;

  // Validate file type
  if (!file.type.startsWith('image/')) {
    $q.notify({
      type: 'negative',
      message: 'Please select a valid image file',
    });
    return;
  }

  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    $q.notify({
      type: 'negative',
      message: 'File size must be less than 5MB',
    });
    return;
  }

  try {
    const formData = new FormData();
    formData.append('profile_picture', file);

    const response = await api.post('/users/profile/update/picture/', formData);

    userProfile.value.profile_picture = response.data.user.profile_picture;
    emit('profilePictureUpdated', response.data.user.profile_picture);

    // Store the updated profile picture in localStorage for cross-page sync
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    currentUser.profile_picture = response.data.user.profile_picture;
    localStorage.setItem('user', JSON.stringify(currentUser));

    $q.notify({
      type: 'positive',
      message: 'Profile picture updated successfully',
    });
  } catch (error) {
    console.error('Error uploading profile picture:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to update profile picture',
    });
  }
};

const loadUserProfile = async () => {
  try {
    const response = await api.get('/users/profile/');
    const userData = response.data.user || response.data;

    // Check if verification status has changed
    const previousStatus = userProfile.value.verification_status;
    const newStatus = userData.verification_status;

    userProfile.value = {
      id: userData.id,
      full_name: userData.full_name,
      specialization: userData.doctor_profile?.specialization || userData.specialization,
      verification_status: userData.verification_status,
      profile_picture: userData.profile_picture,
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
  } catch (error) {
    console.error('Error loading user profile:', error);
  }
};

// Lifecycle
onMounted(() => {
  void loadUserProfile();
  
  // Refresh user profile every 30 seconds to check for verification status updates
  setInterval(() => {
    void loadUserProfile();
  }, 30000);
});
</script>

<style scoped>
/* Sidebar Styles */
.prototype-sidebar {
  background: white;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-content {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Logo Section */
.logo-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-avatar {
  border: 2px solid #286660;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #286660;
}

.menu-btn {
  color: #666;
}

/* User Profile Section */
.sidebar-user-profile {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
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

.profile-avatar {
  border: 3px solid #1e7668 !important;
  border-radius: 50% !important;
  overflow: hidden !important;
}

.clickable-avatar {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.clickable-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(30, 118, 104, 0.3);
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
  background: #286660;
  color: white;
  font-weight: 600;
  font-size: 1.5rem;
  border-radius: 50%;
}

.user-info {
  text-align: center;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 4px 0;
}

.clickable-name {
  cursor: pointer;
  transition: color 0.2s ease;
}

.clickable-name:hover {
  color: #1e7668;
}

.user-role {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
}

/* Navigation Menu */
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

/* Logout Section */
.logout-section {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.logout-btn {
  width: 100%;
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar-content {
    padding: 16px;
  }

  .logo-section {
    margin-bottom: 20px;
    padding-bottom: 16px;
  }

  .sidebar-user-profile {
    margin-bottom: 20px;
    padding-bottom: 16px;
  }

  .profile-picture-container {
    margin-bottom: 12px;
  }

  .navigation-menu {
    padding: 12px 0;
  }

  .logout-section {
    padding: 16px;
  }
}
</style>