<template>
  <div class="forgot-password-page">
    <div class="forgot-password-container">
      <div class="forgot-password-card">
        <div class="forgot-password-header">
          <h2>Forgot Password</h2>
          <p>Enter your email to reset your password</p>
        </div>

        <div v-if="!resetEmailSent" class="forgot-password-form">
          <form @submit.prevent="onRequestReset">
            <div class="form-group">
              <label for="email">Email Address</label>
              <input
                id="email"
                v-model="email"
                type="email"
                required
                placeholder="Enter your registered email"
              />
            </div>

            <button type="submit" :disabled="loading" class="reset-btn">
              {{ loading ? 'Sending...' : 'Send Reset Link' }}
            </button>
          </form>
        </div>

        <div v-else class="reset-sent">
          <div class="success-icon">✓</div>
          <h3>Reset Link Sent!</h3>
          <p>
            We've sent a password reset link to <strong>{{ email }}</strong>
          </p>
          <p>Please check your email and follow the instructions to reset your password.</p>
        </div>

        <div class="forgot-password-footer">
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
import { ref } from 'vue';
import { useQuasar } from 'quasar';
import { api } from '../boot/axios';

const $q = useQuasar();
const email = ref('');
const loading = ref(false);
const resetEmailSent = ref(false);

const onRequestReset = async () => {
  loading.value = true;

  try {
    const response = await api.post('/users/forgot-password/', {
      email: email.value,
    });

    resetEmailSent.value = true;

    // In development, show the reset URL in console
    if (response.data.reset_url) {
      console.log('Password reset URL:', response.data.reset_url);
      $q.notify({
        type: 'positive',
        message:
          'Password reset link sent! Check the browser console for the reset URL (development mode).',
        position: 'top',
        timeout: 4000,
      });
    }
  } catch (error: unknown) {
    console.error('Password reset error:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to send reset link. Please check your email address and try again.',
      position: 'top',
      timeout: 4000,
    });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.forgot-password-page {
  min-height: 100vh;
  background-color: white;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.forgot-password-container {
  width: 100%;
  max-width: 400px;
}

.forgot-password-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.forgot-password-header {
  text-align: center;
  margin-bottom: 30px;
}

.forgot-password-header h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 24px;
}

.forgot-password-header p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.forgot-password-form {
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

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #1e7668;
  box-shadow: 0 0 0 2px rgba(30, 118, 104, 0.2);
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

.reset-sent {
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

.reset-sent h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 20px;
}

.reset-sent p {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.forgot-password-footer {
  text-align: center;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.forgot-password-footer p {
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
