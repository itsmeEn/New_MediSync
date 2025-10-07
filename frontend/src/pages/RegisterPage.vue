<template>
  <div class="register-page safe-area-top safe-area-bottom">
    <div class="register-container">
      <div class="register-card">
        <div class="register-header">
          <h2>Create Account</h2>
          <p>{{ roleTitle }} Registration</p>
        </div>

        <div class="register-form">
          <form @submit.prevent="onRegister">
            <!-- Common Fields -->
            <div class="form-row">
              <div class="form-group">
                <label for="full_name">Full Name *</label>
                <input
                  id="full_name"
                  v-model="formData.full_name"
                  type="text"
                  required
                  placeholder="Enter your full name"
                />
              </div>
              <div class="form-group">
                <label for="email">Email Address *</label>
                <input
                  id="email"
                  v-model="formData.email"
                  type="email"
                  required
                  placeholder="Enter your email"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="date_of_birth">Date of Birth</label>
                <input id="date_of_birth" v-model="formData.date_of_birth" type="date" />
              </div>
              <div class="form-group">
                <label for="gender">Gender</label>
                <select id="gender" v-model="formData.gender">
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="password">Password *</label>
                <input
                  id="password"
                  v-model="formData.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  placeholder="Enter password (min 8 chars, alphanumeric)"
                />
                <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                  {{ showPassword ? 'Hide' : 'Show' }}
                </button>
                <div class="password-strength" :class="passwordStrengthClass">
                  {{ passwordStrengthText }}
                </div>
              </div>
              <div class="form-group">
                <label for="password2">Confirm Password *</label>
                <input
                  id="password2"
                  v-model="formData.password2"
                  :type="showPassword2 ? 'text' : 'password'"
                  required
                  placeholder="Confirm your password"
                />
                <button
                  type="button"
                  class="toggle-password"
                  @click="showPassword2 = !showPassword2"
                >
                  {{ showPassword2 ? 'Hide' : 'Show' }}
                </button>
              </div>
            </div>

            <!-- Role-specific Fields -->
            <div v-if="role === 'doctor'" class="role-specific-fields">
              <div class="form-row">
                <div class="form-group">
                  <label for="license_number">Medical License Number *</label>
                  <input
                    id="license_number"
                    v-model="formData.license_number"
                    type="text"
                    required
                    placeholder="Enter your medical license number"
                  />
                </div>
                <div class="form-group">
                  <label for="specialization">Specialization *</label>
                  <input
                    id="specialization"
                    v-model="formData.specialization"
                    type="text"
                    required
                    placeholder="e.g., Cardiology, Pediatrics"
                  />
                </div>
              </div>
            </div>

            <div v-if="role === 'nurse'" class="role-specific-fields">
              <div class="form-row">
                <div class="form-group">
                  <label for="nurse_license">Nursing License Number *</label>
                  <input
                    id="nurse_license"
                    v-model="formData.license_number"
                    type="text"
                    required
                    placeholder="Enter your nursing license number"
                  />
                </div>
                <div class="form-group">
                  <label for="department">Department *</label>
                  <input
                    id="department"
                    v-model="formData.department"
                    type="text"
                    required
                    placeholder="e.g., Emergency, ICU, Pediatrics"
                  />
                </div>
              </div>
            </div>

            <div v-if="role === 'patient'" class="role-specific-fields">
              <!-- Patient registration - no additional fields required -->
            </div>

            <button type="submit" :disabled="loading" class="register-btn">
              {{ loading ? 'Creating Account...' : 'Create Account' }}
            </button>
          </form>
        </div>

        <div class="register-footer">
          <p>
            Already have an account?
            <button @click="$router.push('/login')" class="link-btn">Sign In</button>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from '../boot/axios';
import { AxiosError } from 'axios';

interface RegistrationFormData {
  full_name: string;
  email: string;
  date_of_birth: string;
  gender: string;
  password: string;
  password2: string;
  license_number: string;
  specialization: string;
  department: string;
}

const router = useRouter();
const route = useRoute();
const $q = useQuasar();

const role = ref('');
const loading = ref(false);
const showPassword = ref(false);
const showPassword2 = ref(false);

// Password strength
const passwordStrengthClass = ref('');
const passwordStrengthText = ref('');

const formData = ref<RegistrationFormData>({
  full_name: '',
  email: '',
  date_of_birth: '',
  gender: '',
  password: '',
  password2: '',
  license_number: '',
  specialization: '',
  department: '',
});

const roleTitle = computed(() => {
  switch (role.value) {
    case 'doctor':
      return 'Doctor';
    case 'nurse':
      return 'Nurse';
    case 'patient':
      return 'Patient';
    default:
      return '';
  }
});

// Password strength calculation
const calculatePasswordStrength = (password: string) => {
  if (!password) {
    passwordStrengthText.value = '';
    passwordStrengthClass.value = '';
    return;
  }

  let score = 0;
  const feedback = [];

  // Length check
  if (password.length >= 8) score += 1;
  else feedback.push('at least 8 characters');

  // Lowercase check
  if (/[a-z]/.test(password)) score += 1;
  else feedback.push('lowercase letters');

  // Uppercase check
  if (/[A-Z]/.test(password)) score += 1;
  else feedback.push('uppercase letters');

  // Number check
  if (/\d/.test(password)) score += 1;
  else feedback.push('numbers');

  // Special character check
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 1;
  else feedback.push('special characters');

  // Determine strength
  if (score <= 2) {
    passwordStrengthText.value = 'Weak password';
    passwordStrengthClass.value = 'weak';
  } else if (score <= 3) {
    passwordStrengthText.value = 'Medium password';
    passwordStrengthClass.value = 'medium';
  } else {
    passwordStrengthText.value = 'Strong password';
    passwordStrengthClass.value = 'strong';
  }

  // Add feedback for weak passwords
  if (score <= 2 && feedback.length > 0) {
    passwordStrengthText.value += ` - needs ${feedback.slice(0, 2).join(', ')}`;
  }
};

onMounted(() => {
  role.value = route.params.role as string;
  if (!['doctor', 'nurse', 'patient'].includes(role.value)) {
    void router.push('/role-selection');
  }
});

// Watch password changes to update strength indicator
watch(
  () => formData.value.password,
  (newPassword) => {
    calculatePasswordStrength(newPassword);
  },
);

const onRegister = async () => {
  // Validate required fields based on role
  if (role.value === 'doctor') {
    if (!formData.value.license_number || !formData.value.specialization) {
      $q.notify({
        type: 'negative',
        message: 'License number and specialization are required for doctors.',
        position: 'top',
        timeout: 4000,
      });
      return;
    }
  } else if (role.value === 'nurse') {
    if (!formData.value.license_number || !formData.value.department) {
      $q.notify({
        type: 'negative',
        message: 'License number and department are required for nurses.',
        position: 'top',
        timeout: 4000,
      });
      return;
    }
  }

  // A boolean flag is set to true to indicate that the registration process has started.
  loading.value = true;

  try {
    // A FormData object is instantiated to handle the data submission.
    // This is necessary for including file uploads, such as images and documents.
    const registrationData = new FormData();

    // The function retrieves the file input elements for the profile picture and verification document.
    const profilePictureInput = document.getElementById('profile_picture') as HTMLInputElement;
    const verificationDocumentInput = document.getElementById(
      'verification_document',
    ) as HTMLInputElement;

    // It is checked if a profile picture file has been selected, and if so, it is appended to the FormData object.
    if (profilePictureInput?.files?.[0]) {
      registrationData.append('profile_picture', profilePictureInput.files[0]);
    }
    // It is checked if a verification document file has been selected, and if so, it is appended to the FormData object.
    if (verificationDocumentInput?.files?.[0]) {
      registrationData.append('verification_document', verificationDocumentInput.files[0]);
    }

    // The function iterates through the common form fields and appends them to the FormData object.
    Object.entries(formData.value).forEach(([key, value]) => {
      registrationData.append(key, value);
    });
    // The user's role is appended to the FormData object.
    registrationData.append('role', role.value);

    // The FormData object, ready for submission, is logged to the console for debugging.
    console.log('Sending registration data (FormData):', registrationData);

    // Debug: Log the actual form data being sent
    for (const [key, value] of registrationData.entries()) {
      console.log(`${key}:`, value);
    }

    // An HTTP POST request is sent to the registration endpoint.
    // Axios automatically configures the correct 'Content-Type' header for FormData.
    const response = await api.post('/users/register/', registrationData);

    // Upon successful registration, the access and refresh tokens are stored in local storage.
    localStorage.setItem('access_token', response.data.tokens.access);
    localStorage.setItem('refresh_token', response.data.tokens.refresh);

    // The user's data from the response is stored in local storage.
    localStorage.setItem('user', JSON.stringify(response.data.user));

    // A success message is displayed to the user.
    $q.notify({
      type: 'positive',
      message: 'Account created successfully!',
      position: 'top',
      timeout: 3000,
    });

    // The user is redirected to the verification page after successful registration.
    void router.push('/verification');
  } catch (error: unknown) {
    // If the registration request fails, the error is logged to the console.
    console.error('Registration error:', error);

    // A default error message is set.
    let errorMessage = 'Registration failed. Please try again.';

    // It is checked if the error is an AxiosError to handle specific HTTP response details.
    if (error instanceof AxiosError) {
      console.error('Axios error response:', error.response?.data);
      console.error('Axios error status:', error.response?.status);

      // If the server provided a response body with the error details, it is processed.
      if (error.response?.data) {
        // More robust error handling for validation errors from Django is applied here.
        if (typeof error.response.data === 'object' && error.response.data !== null) {
          // The error data object is converted to a readable JSON string.
          errorMessage = JSON.stringify(error.response.data, null, 2);
        } else if (typeof error.response.data === 'string') {
          // If the error data is a string, it is used directly as the error message.
          errorMessage = error.response.data;
        }
      }
    }

    // The final error message is displayed to the user.
    $q.notify({
      type: 'negative',
      message: `Registration failed: ${errorMessage}`,
      position: 'top',
      timeout: 4000,
    });
  } finally {
    // The loading flag is set to false, indicating that the registration process has completed.
    loading.value = false;
  }
};
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: url('/background.png') no-repeat center center;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
}

.register-page::before {
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

.register-page > * {
  position: relative;
  z-index: 1;
}

.register-container {
  width: 100%;
  max-width: 600px;
}

.register-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 28px;
  font-weight: 600;
}

.register-header p {
  margin: 0;
  color: #666;
  font-size: 18px;
}

.register-form {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
  font-family: inherit;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1e7668;
  box-shadow: 0 0 0 2px rgba(30, 118, 104, 0.2);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.toggle-password {
  margin-top: 8px;
  background: none;
  border: none;
  color: #1e7668;
  cursor: pointer;
  font-size: 14px;
}

.password-strength {
  margin-top: 8px;
  font-size: 12px;
  font-weight: 500;
  transition: color 0.3s ease;
}

.password-strength.weak {
  color: #e74c3c;
}

.password-strength.medium {
  color: #f39c12;
}

.password-strength.strong {
  color: #27ae60;
}

.role-specific-fields {
  border-top: 1px solid #eee;
  padding-top: 20px;
  margin-top: 20px;
}

.register-btn {
  width: 100%;
  padding: 12px;
  background: #1e7668;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.register-btn:hover:not(:disabled) {
  background: #6ca299;
}

.register-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.register-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.register-footer p {
  margin: 0;
  color: #666;
}

.link-btn {
  background: none;
  border: none;
  color: #1e7668;
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
}

.link-btn:hover {
  color: #6ca299;
}

@media (max-width: 768px) {
  .register-page {
    padding: 8px;
    min-height: 100vh;
    /* Ensure content doesn't overlap with safe areas and navigation */
    padding-top: max(80px, calc(var(--safe-area-inset-top) + 60px));
    padding-bottom: max(8px, var(--safe-area-inset-bottom));
    padding-left: max(8px, var(--safe-area-inset-left));
    padding-right: max(8px, var(--safe-area-inset-right));
    /* Adjust alignment for mobile to start from top */
    align-items: flex-start;
  }

  .register-container {
    max-width: 100%;
  }

  .register-card {
    padding: 16px;
    margin: 0;
    border-radius: 12px;
  }

  .register-header {
    margin-bottom: 20px;
  }

  .register-header h2 {
    font-size: 20px;
    margin-bottom: 6px;
  }

  .register-header p {
    font-size: 14px;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 12px;
    margin-bottom: 12px;
  }

  .form-group {
    margin-bottom: 12px;
  }

  .form-group label {
    margin-bottom: 4px;
    font-size: 14px;
  }

  .form-group input,
  .form-group select,
  .form-group textarea {
    padding: 10px;
    font-size: 14px;
    border-radius: 6px;
  }

  .register-btn {
    padding: 10px;
    font-size: 14px;
    border-radius: 6px;
  }

  .register-footer {
    padding-top: 16px;
  }

  .register-footer p {
    font-size: 13px;
  }

  .link-btn {
    font-size: 13px;
  }

  .toggle-password {
    font-size: 12px;
  }

  .password-strength {
    font-size: 11px;
  }
}
</style>
