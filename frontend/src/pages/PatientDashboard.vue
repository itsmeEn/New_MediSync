<template>
  <q-layout view="hHh lpR fFf">
    <!-- Header -->
    <q-header class="dashboard-header safe-area-top">
      <!-- Mobile Header Layout -->
      <div class="mobile-header-layout">
        <!-- Top Row: Profile, User Info, Logout -->
        <div class="header-top-row">
          <q-avatar size="40px" class="profile-avatar uploadable-avatar">
            <img v-if="profileImageUrl" :src="profileImageUrl" alt="Profile" />
            <q-icon v-else name="person" size="32px" />
            <!-- Avatar upload overlay -->
            <input
              type="file"
              accept="image/*"
              class="avatar-upload-input"
              @change="handleProfilePictureUpload"
              title="Upload profile picture"
            />
            <q-tooltip anchor="bottom middle" self="top middle" class="avatar-tooltip">
              Upload profile picture
            </q-tooltip>
          </q-avatar>

          <div class="user-info">
            <div class="user-name">{{ user?.full_name || 'Fetch Users Name Here' }}</div>
            <div class="user-age">Age: {{ age !== null ? age : '' }}</div>
          </div>

          <q-btn
            flat
            round
            dense
            icon="logout"
            @click="logout"
            class="logout-btn"
            aria-label="Logout"
          />
        </div>
      </div>
    </q-header>

    <!-- Main content area -->
    <q-page-container class="page-background">
      <div class="q-pa-md">
        <div v-if="activeTab === 0">
          <div class="text-subtitle1 q-mb-sm">Home</div>
          <div class="text-body2">Welcome back, {{ user?.full_name || 'Patient' }}.</div>
        </div>
        <div v-else-if="activeTab === 1">
          <div class="text-subtitle1 q-mb-sm">Appointments</div>
          <div class="text-body2">Your appointments will appear here.</div>
        </div>
        <div v-else-if="activeTab === 2">
          <div class="text-subtitle1 q-mb-sm">Medical Request</div>
          <div class="text-body2">Create and track your medical requests here.</div>
        </div>
        <div v-else-if="activeTab === 3">
          <div class="text-subtitle1 q-mb-sm">Notification History</div>
          <div class="text-body2">Past notifications will be listed here.</div>
        </div>
        <div v-else-if="activeTab === 4">
          <div class="text-subtitle1 q-mb-sm">Account Settings</div>
          <div class="text-body2">Manage your account preferences here.</div>
        </div>
      </div>
    </q-page-container>

    <!-- Footer with Quasar QTabs -->
    <q-footer class="custom-footer transparent-footer">
      <div class="footer-tabs-wrapper">
        <q-tabs
          v-model="activeTab"
          class="footer-tabs"
          align="justify"
          dense
          inverted
          indicator-color="transparent"
        >
          <q-tab
            v-for="(item, idx) in navItems"
            :key="item.name"
            :name="idx"
            class="footer-tab"
            :class="{ 'highlighted-tab': activeTab === idx }"
          >
            <div class="footer-tab-inner">
              <div class="footer-highlight-bg" v-if="activeTab === idx" />
              <q-icon
                :name="item.icon"
                class="footer-icon"
                :class="{ active: activeTab === idx }"
              />
              <div class="footer-tab-label" :class="{ active: activeTab === idx }">
                {{ capitalize(item.label) }}
              </div>
            </div>
          </q-tab>
        </q-tabs>
      </div>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from '../boot/axios';

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_verified: boolean;
  date_of_birth?: string | null;
  profile_picture?: string | null;
}

// Type definitions for API error handling
interface ApiErrorResponse {
  profile_picture?: string[];
  detail?: string;
}

interface ApiError {
  response?: {
    data?: ApiErrorResponse;
  };
}

const router = useRouter();
const $q = useQuasar();

const user = ref<User | null>(null);
const activeTab = ref(2);

const navItems = [
  { name: 'home', icon: 'home', label: 'dashboard' },
  { name: 'calendar', icon: 'event_note', label: 'appointment' },
  { name: 'appointments', icon: 'event_note', label: 'medical history' },
  { name: 'notifications', icon: 'notifications_none', label: 'notification' },
  { name: 'settings', icon: 'settings', label: 'account settings' },
];

// Profile Image URL (computed)
const profileImageUrl = computed(() => {
  const pic = user.value?.profile_picture || null;
  if (!pic) return null;
  if (/^https?:/i.test(pic)) return pic;
  try {
    const u = new URL(api.defaults.baseURL || '');
    return `${u.origin}${pic.startsWith('/') ? '' : '/'}${pic}`;
  } catch {
    return `${window.location.origin}${pic.startsWith('/') ? '' : '/'}${pic}`;
  }
});

// Avatar upload handler - all fixes applied
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

      const response = await api.post('/users/profile/update/picture/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Update user.value.profile_picture (not userProfile)
      if (user.value) {
        user.value.profile_picture = response.data.user.profile_picture;
      }

      $q.notify({
        type: 'positive',
        message: 'Profile picture updated successfully!',
        position: 'top',
        timeout: 3000,
      });

      target.value = '';
    } catch (error: unknown) {
      console.error('Profile picture upload failed:', error);

      let errorMessage = 'Failed to upload profile picture. Please try again.';
      // Defensive error extraction
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as ApiError;
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

function calcAge(dobStr?: string | null): number | null {
  if (!dobStr) return null;
  const dob = new Date(dobStr);
  if (isNaN(dob.getTime())) return null;
  const today = new Date();
  let age = today.getFullYear() - dob.getFullYear();
  const m = today.getMonth() - dob.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
    age--;
  }
  return age;
}

const age = computed(() => calcAge(user.value?.date_of_birth));

function capitalize(str: string) {
  return str.replace(/\b\w/g, (c) => c.toUpperCase());
}

const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  void router.push('/login');
};

async function loadUser() {
  try {
    const resp = await api.get('/users/profile/');
    user.value = resp.data.user;
    localStorage.setItem('user', JSON.stringify(user.value));
  } catch {
    const cached = localStorage.getItem('user');
    if (cached) {
      try {
        user.value = JSON.parse(cached);
        return;
      } catch {
        localStorage.removeItem('user');
        user.value = null;
      }
    }
    $q.notify({
      type: 'negative',
      message: 'Session expired. Please log in again.',
      position: 'top',
    });
    void router.push('/login');
  }
}

onMounted(loadUser);
</script>

<style scoped>
.page-background {
  background: url('/background.png') no-repeat center center;
  background-size: cover;
  min-height: 100vh;
  position: relative;
}

.page-background::before {
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

.page-background > * {
  position: relative;
  z-index: 1;
}

/* Safe Area Support */
.safe-area-top {
  padding-top: env(safe-area-inset-top);
}

.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}

/* Ensure mobile header is always visible on mobile devices */
@media (max-width: 768px) {
  .mobile-header-layout {
    display: flex !important;
  }

  .header-toolbar {
    display: none !important;
  }

  /* Force header visibility on iOS */
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

/* Modal Close Button Styles */
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

/* Mobile close button styling */
@media (max-width: 768px) {
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
}

@media (max-width: 480px) {
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
  min-height: 56px;
}

.dashboard-header {
  background: #286660;
  min-height: 70px;
  max-height: 70px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 12px 0 rgba(64, 110, 101, 0.08);
}
.header-content {
  display: flex;
  align-items: center;
  padding: 0 18px;
  height: 100%;
  width: 100%;
}
.profile-avatar {
  background: #b8d2ce;
  border-radius: 50%;
  margin-right: 14px;
  flex-shrink: 0;
  position: relative;
}
.uploadable-avatar:hover .avatar-upload-input {
  opacity: 1;
}
.avatar-upload-input {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
  opacity: 0;
  z-index: 10;
}
.avatar-tooltip {
  font-size: 0.9em;
}
.user-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.user-name {
  color: #fff;
  font-weight: 600;
  font-size: 1.12rem;
  line-height: 1.2;
  margin-bottom: 2px;
}
.user-age {
  color: #e0e0e0;
  font-size: 0.99rem;
  font-weight: 400;
}
.logout-btn {
  color: white;
  margin-left: 16px;
}

/* Footer (transparent background) */
.custom-footer {
  position: fixed;
  left: 0;
  bottom: 0;
  width: 100vw;
  background: transparent !important;
  box-shadow: none;
  border: none;
  z-index: 1000;
  padding: 0;
}
.transparent-footer {
  background: transparent !important;
}

.footer-tabs-wrapper {
  width: 100vw;
  background: transparent !important;
}
.footer-tabs {
  width: 100vw;
  background: transparent !important;
  min-height: 74px;
  border-bottom: none;
  box-shadow: none;
}
.footer-tab {
  flex: 1 1 0;
  min-width: 0;
  background: transparent !important;
  margin: 0 !important;
  padding: 0 !important;
  max-width: 20vw;
}
.footer-tab-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  min-width: 0;
  width: 100%;
  padding: 0;
  position: relative;
}

/* Highlighted tab background and border - now on top of icon */
.footer-highlight-bg {
  position: absolute;
  left: 50%;
  top: -9px;
  width: 44px;
  height: 24px;
  background: #eaf6f3;
  border-radius: 10px 10px 12px 12px;
  transform: translateX(-50%);
  z-index: 3;
  box-sizing: border-box;
  border-top: 5px solid #6ca299;
  border-bottom: none;
  border-left: none;
  border-right: none;
  pointer-events: none;
}
.footer-icon {
  color: #6ca299b3;
  font-size: 29px;
  min-width: 32px;
  min-height: 32px;
  transition: color 0.2s;
  margin-bottom: 2px;
  z-index: 2;
  position: relative;
}
.footer-icon.active {
  color: #6ca299 !important;
  z-index: 4;
}
.footer-tab-label {
  font-size: 0.82rem;
  color: #6ca299b3;
  font-weight: 500;
  letter-spacing: 0.01em;
  text-align: center;
  margin-bottom: 2px;
  margin-top: 2px;
  transition:
    color 0.2s,
    font-weight 0.2s;
  max-width: 95px;
  overflow: visible;
  white-space: normal;
  z-index: 2;
  text-transform: capitalize;
  line-height: 1.1;
}
.footer-tab-label.active {
  font-weight: 700;
  color: #6ca299;
}
.highlighted-tab .footer-icon,
.highlighted-tab .footer-tab-label {
  color: #6ca299 !important;
}
.highlighted-tab .footer-icon {
  font-weight: 700;
  z-index: 4;
}

/* Mobile responsiveness for main content */
@media (max-width: 768px) {
  .dashboard-header {
    padding-top: max(env(safe-area-inset-top), 8px);
    min-height: 64px;
  }

  .header-content {
    padding: 12px 0;
  }

  .header-top-row {
    padding: 4px 12px;
    min-height: 48px;
  }

  .profile-avatar {
    width: 36px;
    height: 36px;
  }

  .user-name {
    font-size: 14px;
    font-weight: 600;
  }

  .user-age {
    font-size: 11px;
    color: #666;
  }

  .logout-btn {
    margin-left: 12px;
    padding: 8px;
  }

  .q-page-container {
    padding-bottom: 80px;
  }

  .q-pa-md {
    padding: 16px;
  }

  .text-subtitle1 {
    font-size: 1.2rem;
    margin-bottom: 12px;
  }

  .text-body2 {
    font-size: 0.95rem;
    line-height: 1.5;
  }
}

@media (max-width: 480px) {
  .dashboard-header {
    padding-top: max(env(safe-area-inset-top), 12px);
    min-height: 56px;
  }

  .header-content {
    padding: 8px 0;
  }

  .header-top-row {
    padding: 2px 8px;
    min-height: 44px;
  }

  .profile-avatar {
    width: 32px;
    height: 36px;
  }

  .user-name {
    font-size: 0.95rem;
  }

  .user-age {
    font-size: 0.85rem;
  }

  .logout-btn {
    margin-left: 8px;
    padding: 6px;
  }

  .q-pa-md {
    padding: 12px;
  }

  .text-subtitle1 {
    font-size: 1.1rem;
    margin-bottom: 10px;
  }

  .text-body2 {
    font-size: 0.9rem;
  }
}

/* Responsive adjustments for mobile footer */
@media (max-width: 600px) {
  .footer-tabs,
  .footer-tabs-wrapper {
    min-height: 60px;
    height: 60px;
  }
  .footer-tab-label {
    font-size: 0.74rem;
    max-width: 80px;
    margin-bottom: 2px;
    margin-top: 1px;
    line-height: 1.1;
    overflow: visible;
    white-space: normal;
  }
  .footer-tab {
    max-width: 24vw;
  }
  .footer-icon {
    font-size: 20px;
    min-width: 20px;
    min-height: 20px;
    margin-bottom: 1px;
    margin-top: 1px;
  }
  .footer-tab-inner {
    min-width: 0;
    width: 100%;
    padding: 0 1px;
  }
  .footer-highlight-bg {
    border-radius: 8px 8px 10px 10px;
    border-top-width: 4px;
    width: 35px;
    height: 18px;
    top: -7px;
  }
}
</style>
