<template>
  <div class="otp-page safe-area-top safe-area-bottom">
    <div class="otp-container">
      <div class="otp-card">
        <div class="otp-header">
          <h2>Two-Factor Verification</h2>
          <p>Enter the verification code sent to your email</p>
        </div>

        <div class="otp-form">
          <form @submit.prevent="onVerify">
            <div class="form-group">
              <label>Email</label>
              <input :value="email" disabled />
            </div>
            <div class="form-group">
              <label for="otp">Verification Code</label>
              <input id="otp" v-model="otp" type="text" required placeholder="Enter code" />
            </div>
            <button type="submit" :disabled="loading" class="verify-btn">
              {{ loading ? 'Verifying...' : 'Verify' }}
            </button>
          </form>
        </div>

        <div class="otp-footer">
          <button class="link-btn" @click="backToLogin">Back to Login</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from '../boot/axios';

const router = useRouter();
const $q = useQuasar();

const email = ref('');
const otp = ref('');
const loading = ref(false);

onMounted(() => {
  const stored = localStorage.getItem('pending_otp_email');
  if (stored) {
    email.value = stored;
  }
});

const backToLogin = async () => {
  await router.push('/login');
};

const onVerify = async () => {
  if (!email.value) {
    $q.notify({ type: 'warning', message: 'Missing email for verification.', position: 'top' });
    return;
  }
  loading.value = true;
  try {
    const resp = await api.post('/users/2fa/login/verify/', { email: email.value, otp_code: otp.value }, { timeout: 10000 });

    if (!resp.data?.access || !resp.data?.refresh || !resp.data?.user) {
      throw new Error('Invalid response from server.');
    }

    // Store tokens and user
    try {
      localStorage.setItem('access_token', resp.data.access);
      localStorage.setItem('refresh_token', resp.data.refresh);
      localStorage.setItem('user', JSON.stringify(resp.data.user));
      localStorage.removeItem('pending_otp_email');
    } catch (e) {
      if (process.env.NODE_ENV === 'development') {
        console.warn('Token storage failed', e);
      }
    }

    $q.notify({ type: 'positive', message: 'Verification successful!', position: 'top', timeout: 2000 });

    const user = resp.data.user;
    if (user && !user.is_verified) {
      await router.push('/verification');
      return;
    }
    switch (user?.role) {
      case 'doctor':
        await router.push('/doctor-dashboard');
        break;
      case 'nurse':
        await router.push('/nurse-dashboard');
        break;
      case 'patient':
        await router.push('/patient-dashboard');
        break;
      default:
        await router.push('/');
    }
  } catch (err: unknown) {
    let msg = 'Verification failed.';
    if (typeof err === 'object' && err !== null) {
      const respData = (err as { response?: { data?: { error?: string; message?: string; detail?: string } } }).response?.data;
      const maybeMessage = (err as { message?: string }).message;
      msg = respData?.error || respData?.message || respData?.detail || maybeMessage || msg;
    }
    $q.notify({ type: 'negative', message: msg, position: 'top', timeout: 5000 });
  } finally {
    loading.value = false;
  }
};
</script>

<style>
.otp-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 20px;
}
.otp-container { width: 100%; max-width: 400px; }
.otp-card { background: #fff; border-radius: 12px; box-shadow: 0 10px 24px rgba(0,0,0,0.12); padding: 24px; }
.otp-header { text-align: center; margin-bottom: 20px; }
.otp-header h2 { margin: 0 0 8px; color: #333; font-size: 22px; }
.otp-header p { margin: 0; color: #666; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; color: #333; }
.form-group input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
.verify-btn { width: 100%; padding: 12px; background: #1e7668; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
.verify-btn:hover { background: #6ca299; }
.otp-footer { text-align: center; margin-top: 16px; }
.link-btn { background: none; border: none; color: #1e7668; text-decoration: underline; cursor: pointer; }
@media (max-width: 768px) {
  .otp-card { padding: 16px; }
  .verify-btn { padding: 10px; }
}
</style>