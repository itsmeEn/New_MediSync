<template>
  <div class="reset-password-page">
    <div class="reset-password-container">
      <div class="reset-password-card">
        <div class="reset-password-header">
          <h2>Reset Password</h2>
          <p>Enter your new password</p>
        </div>

        <div v-if="!passwordReset" class="reset-password-form">
          <form @submit.prevent="onResetPassword">
            <div class="form-group">
              <label for="new_password">New Password</label>
              <input
                id="new_password"
                v-model="newPassword"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="Enter new password (min 8 chars, alphanumeric)"
              />
              <button type="button" @click="showPassword = !showPassword">
                {{ showPassword ? 'Hide' : 'Show' }}
              </button>
            </div>

            <div class="form-group">
              <label for="confirm_password">Confirm New Password</label>
              <input
                id="confirm_password"
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                placeholder="Confirm your new password"
              />
              <button type="button" @click="showConfirmPassword = !showConfirmPassword">
                {{ showConfirmPassword ? 'Hide' : 'Show' }}
              </button>
            </div>

            <div v-if="passwordError" class="error-message">
              {{ passwordError }}
            </div>

            <button type="submit" :disabled="loading" class="reset-btn">
              {{ loading ? 'Resetting...' : 'Reset Password' }}
            </button>
          </form>
        </div>

        <div v-else class="reset-success">
          <div class="success-icon">✓</div>
          <h3>Password Reset Successful!</h3>
          <p>
            Your password has been reset successfully. You can now log in with your new password.
          </p>
          <button @click="$router.push('/login')" class="login-btn">Go to Login</button>
        </div>

        <div class="reset-password-footer">
          <p>
            Remember your password?
            <button @click="$router.push('/login')" class="link-btn">Back to Login</button>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from '../boot/axios';

const router = useRouter();
const route = useRoute();
const $q = useQuasar();

const newPassword = ref('');
const confirmPassword = ref('');
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const loading = ref(false);
const passwordReset = ref(false);
const passwordError = ref('');

const uidb64 = ref('');
const token = ref('');

onMounted(() => {
  // Get uidb64 and token from route params
  uidb64.value = route.params.uidb64 as string;
  token.value = route.params.token as string;

  if (!uidb64.value || !token.value) {
    $q.notify({
      type: 'negative',
      message: 'Invalid reset link. Please request a new password reset.',
      position: 'top',
      timeout: 4000,
    });
    void router.push('/forgot-password');
  }
});

const validatePassword = (password: string): string => {
  if (password.length < 8) {
    return 'Password must be at least 8 characters long.';
  }

  if (!/[a-zA-Z]/.test(password) || !/\d/.test(password)) {
    return 'Password must contain both letters and numbers.';
  }

  return '';
};

const onResetPassword = async () => {
  passwordError.value = '';

  // Validate passwords
  const passwordValidation = validatePassword(newPassword.value);
  if (passwordValidation) {
    passwordError.value = passwordValidation;
    return;
  }

  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = 'Passwords do not match.';
    return;
  }

  loading.value = true;

  try {
    await api.post(`/users/reset-password/${uidb64.value}/${token.value}/`, {
      new_password: newPassword.value,
    });

    passwordReset.value = true;
  } catch (error: unknown) {
    console.error('Password reset error:', error);
    if (error instanceof Error) {
      passwordError.value = error.message;
    } else {
      passwordError.value = 'Failed to reset password. Please try again.';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.reset-password-page {
  min-height: 100vh;
  background: url('/background.png') no-repeat center center;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.reset-password-container {
  width: 100%;
  max-width: 400px;
}

.reset-password-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.reset-password-header {
  text-align: center;
  margin-bottom: 30px;
}

.reset-password-header h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 24px;
}

.reset-password-header p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.reset-password-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
  position: relative;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
  padding-right: 60px;
}

.form-group input:focus {
  outline: none;
  border-color: #1e7668;
  box-shadow: 0 0 0 2px rgba(30, 118, 104, 0.2);
}

.form-group button {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #667eea;
  font-size: 14px;
  cursor: pointer;
  padding: 4px 8px;
}

.form-group button:hover {
  color: #5a6fd8;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 14px;
}

.reset-btn {
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

.reset-btn:hover:not(:disabled) {
  background: #6ca299;
}

.reset-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.reset-success {
  text-align: center;
  margin-bottom: 20px;
}

.success-icon {
  width: 60px;
  height: 60px;
  background: #4caf50;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin: 0 auto 20px;
}

.reset-success h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 20px;
}

.reset-success p {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.login-btn {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background: #5a6fd8;
}

.reset-password-footer {
  text-align: center;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.reset-password-footer p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.link-btn {
  background: none;
  border: none;
  color: #667eea;
  font-size: 14px;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
}

.link-btn:hover {
  color: #5a6fd8;
}
</style>
