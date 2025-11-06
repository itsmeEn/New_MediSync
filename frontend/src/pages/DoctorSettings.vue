<template>
  <q-layout view="hHh Lpr fFf">
    <DoctorHeader @toggle-drawer="rightDrawerOpen = !rightDrawerOpen" />

    <DoctorSidebar 
      v-model="rightDrawerOpen"
      active-route="settings"
    />

    <!-- Main Content -->
    <q-page-container class="page-container-with-fixed-header role-body-bg">
      

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
                        <div class="profile-placeholder">
                          {{ userInitials }}
                        </div>
                      </q-avatar>
                      <!-- Upload controls removed: initials-only avatar -->
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
                            readonly
                            emit-value
                            map-options
                            class="large-input"
                          />
                        </div>
                        <div class="col-12">
                          <q-input
                            v-model="profileForm.hospitalName"
                            label="Hospital Name"
                            outlined
                            placeholder="Enter your hospital or clinic name"
                            class="large-input"
                          />
                        </div>
                        <div class="col-12">
                          <q-input
                            v-model="profileForm.hospitalAddress"
                            label="Hospital Address"
                            outlined
                            placeholder="Enter hospital address"
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

                      </div>
                    </div>
                  </div>
                </div>

                <q-separator class="q-my-lg" />

                <!-- Security Settings Section -->
                <div class="settings-section">
                  <h6 class="text-subtitle1 q-mb-md">Security Settings</h6>

                  <div class="security-form-container">
                    <div class="security-field">
                      <q-input
                        v-model="securityForm.currentPassword"
                        label="Current Password"
                        type="password"
                        outlined
                        :rules="[(val) => !!val || 'Current password is required']"
                        class="large-input"
                      />
                    </div>
                    <div class="security-field">
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
                    <div class="security-field">
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
                    <div class="security-field">
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

                  <div class="account-status-grid">
                    <div class="status-item">
                      <div class="status-label">Account Type</div>
                      <div class="status-value">Doctor</div>
                    </div>

                    <div class="status-item">
                      <div class="status-label">Verification Status</div>
                      <div class="status-value">
                        <q-chip
                          :color="getVerificationColor(userProfile.verification_status)"
                          text-color="white"
                          :label="getVerificationLabel(userProfile.verification_status)"
                          size="sm"
                        />
                      </div>
                    </div>

                    <div class="status-item">
                      <div class="status-label">Last Login</div>
                      <div class="status-value">{{ accountStatus.lastLogin }}</div>
                    </div>

                    <div class="status-item">
                      <div class="status-label">Member Since</div>
                      <div class="status-value">{{ accountStatus.memberSince }}</div>
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
import { useQuasar } from 'quasar';
import { api } from '../boot/axios';
import DoctorHeader from '../components/DoctorHeader.vue';
import DoctorSidebar from '../components/DoctorSidebar.vue';

import { showVerificationToastOnce } from 'src/utils/verificationToast';
// import { AxiosError } from 'axios' // Unused import

// Reactive data
const rightDrawerOpen = ref(false);
const showNotifications = ref(false);
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

// Real-time data functionality removed - now handled by DoctorHeader component

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
  hospitalName: '',
  hospitalAddress: '',
  licenseNumber: '',
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
  memberSince: '',
});

// Options: reuse patient appointment departments for specialization to keep consistency
import { departmentOptions as sharedDepartmentOptions } from '../utils/departments'
const specializationOptions = sharedDepartmentOptions


// Computed properties
const userInitials = computed(() => {
  const fn = (userProfile.value.first_name || '').trim();
  const ln = (userProfile.value.last_name || '').trim();
  if (fn && ln) {
    return `${fn[0]}${ln[0]}`.toUpperCase();
  }

  const full = (userProfile.value.full_name || profileForm.value.fullName || '').trim();
  if (full) {
    const parts = full.split(/\s+/);
    const initials = parts.slice(0, 2).map((p) => p[0]?.toUpperCase() ?? '').join('');
    return initials || (full[0]?.toUpperCase() ?? 'D');
  }

  const email = (userProfile.value.email || '').trim();
  if (email) {
    return (email[0]?.toUpperCase() ?? 'D');
  }

  return 'DR';
});



const $q = useQuasar();






// Real-time functions removed - now handled by DoctorHeader component

const saveSettings = async () => {
  saving.value = true;

  try {
    // Save profile information (fields supported by ProfileUpdateSerializer)
    const { status } = await api.put('/users/profile/update/', {
      full_name: profileForm.value.fullName,
      hospital_name: profileForm.value.hospitalName,
      hospital_address: profileForm.value.hospitalAddress,
      specialization: profileForm.value.specialization,
      license_number: profileForm.value.licenseNumber,
    });

    // Check if profile update was successful
    if (status === 200) {
      // Update localStorage with the new profile data
      const userData = JSON.parse(localStorage.getItem('userData') || '{}');
      userData.full_name = profileForm.value.fullName;
      userData.hospital_name = profileForm.value.hospitalName;
      userData.hospital_address = profileForm.value.hospitalAddress;
      userData.doctor_profile = userData.doctor_profile || {};
      userData.doctor_profile.specialization = profileForm.value.specialization;
      userData.doctor_profile.license_number = profileForm.value.licenseNumber;
      localStorage.setItem('userData', JSON.stringify(userData));
    }

    // Note: phone field is not supported by the current backend
    // ProfileUpdateSerializer and would need backend changes to be saved

    // Save notification preferences (if endpoint exists)
    try {
      await api.put('/users/notification-preferences/', {
        patient_alerts: notificationSettings.value.patientAlerts,
        appointment_reminders: notificationSettings.value.appointmentReminders,
        message_notifications: notificationSettings.value.messageNotifications,
        analytics_updates: notificationSettings.value.analyticsUpdates,
      });
    } catch (notificationError) {
      console.log('Notification preferences endpoint not available:', notificationError);
      // Continue without failing the entire save operation
    }

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

      try {
        await api.put('/users/change-password/', {
          current_password: securityForm.value.currentPassword,
          new_password: securityForm.value.newPassword,
        });

        // Reset password fields
        securityForm.value.currentPassword = '';
        securityForm.value.newPassword = '';
        securityForm.value.confirmPassword = '';
      } catch (passwordError) {
        console.log('Password change endpoint not available:', passwordError);
        // Continue without failing the entire save operation
      }
    }

    $q.notify({
      type: 'positive',
      message: 'Profile settings saved successfully!',
      position: 'top',
    });
  } catch (error) {
    console.error('Error saving settings:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to save profile settings. Please try again.',
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

    // Update memberSince with formatted date_joined
    if (userData.date_joined) {
      accountStatus.value.memberSince = formatDate(userData.date_joined);
    }

    // Show notification if verification status changed to approved
    if (previousStatus !== newStatus && newStatus === 'approved') {
      showVerificationToastOnce(newStatus, '🎉 Your account has been verified!');
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
      // Read hospital fields from top-level user fields
      hospitalName: userData.hospital_name || '',
      hospitalAddress: userData.hospital_address || '',
      licenseNumber: userData.doctor_profile?.license_number || '',
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
        // Read hospital fields from top-level user fields in localStorage
        hospitalName: user.hospital_name || '',
        hospitalAddress: user.hospital_address || '',
        licenseNumber: user.doctor_profile?.license_number || '',
      };
    }
  }
};

// Notification functions
// unreadNotificationsCount removed - now handled by DoctorHeader component

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

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

onMounted(() => {
  void loadUserProfile();
  void fetchUserProfile();

  // Load notifications
  void loadNotifications();

  // Real-time features removed - now handled by DoctorHeader component
  
  // Refresh notifications every 30 seconds
  setInterval(() => void loadNotifications(), 30000);

  // Refresh user profile every 10 seconds to check for verification status updates
  setInterval(() => void fetchUserProfile(), 10000);
});

onUnmounted(() => {
  // Time interval cleanup removed - now handled by DoctorHeader component
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
  width: 100%;
  max-width: 100%;
  overflow: hidden;
}

.settings-card .q-card-section {
  padding: 24px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
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
  background: #286660;
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
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.large-input .q-field__control {
  min-height: 56px;
  font-size: 16px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.large-input .q-field__label {
  font-size: 16px;
  font-weight: 500;
}

.large-input .q-field__native {
  font-size: 16px;
  padding: 12px 16px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.large-toggle {
  font-size: 16px;
}

.large-toggle .q-toggle__label {
  font-size: 16px;
  font-weight: 500;
}

/* Security Settings Form Container */
.security-form-container {
  width: 100%;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-sizing: border-box;
}

.security-form-container > div {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.security-field {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
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

  .account-status-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  /* On mobile, all items stack vertically */
  .account-status-grid .status-item:nth-child(1),
  .account-status-grid .status-item:nth-child(2),
  .account-status-grid .status-item:nth-child(3),
  .account-status-grid .status-item:nth-child(4) {
    grid-column: span 1;
  }

  .account-status-grid .status-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px;
  }
}

/* Account Status Grid */
.account-status-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

/* First row: Account Type and Verification Status */
.account-status-grid .status-item:nth-child(1),
.account-status-grid .status-item:nth-child(2) {
  grid-column: span 1;
}

/* Second row: Last Login and Member Since side by side */
.account-status-grid .status-item:nth-child(3),
.account-status-grid .status-item:nth-child(4) {
  grid-column: span 1;
}

.account-status-grid .status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.account-status-grid .status-label {
  font-weight: 500;
  color: #666;
  font-size: 14px;
}

.account-status-grid .status-value {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}
</style>
