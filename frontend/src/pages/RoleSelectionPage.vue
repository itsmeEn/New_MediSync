<template>
  <div class="role-selection-page">
    <div class="role-selection-container">
      <div class="role-selection-card">
        <div class="role-header">
          <h1>Which role best describes you?</h1>
        </div>

        <div class="role-options">
          <button
            class="role-btn"
            :class="{ selected: selectedRole === 'doctor' }"
            @click="selectRole('doctor')"
          >
            Doctor
          </button>

          <button
            class="role-btn"
            :class="{ selected: selectedRole === 'nurse' }"
            @click="selectRole('nurse')"
          >
            Nurse
          </button>

          <button
            class="role-btn"
            :class="{ selected: selectedRole === 'patient' }"
            @click="selectRole('patient')"
          >
            Patient
          </button>
        </div>

        <div class="role-actions" v-if="selectedRole">
          <button class="continue-btn" @click="continueToRegistration">Continue</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const selectedRole = ref('');

const selectRole = (role: string) => {
  selectedRole.value = role;
};

const continueToRegistration = () => {
  if (selectedRole.value) {
    void router.push(`/register/${selectedRole.value}`);
  }
};
</script>

<style scoped>
.role-selection-page {
  min-height: 100vh;
  background-color: white;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
}

.role-selection-page::before {
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

.role-selection-page > * {
  position: relative;
  z-index: 1;
}

.role-selection-container {
  width: 100%;
  max-width: 600px;
  text-align: center;
}

.role-selection-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.15),
    0 8px 16px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 40px;
  position: relative;
  overflow: hidden;
}

.role-selection-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #286660, #6ca299, #b8d2ce);
  border-radius: 20px 20px 0 0;
}

.role-header {
  margin-bottom: 40px;
}

.role-header h1 {
  margin: 0;
  color: #333;
  font-size: 28px;
  font-weight: 600;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.role-options {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin-bottom: 40px;
}

.role-btn {
  width: 200px;
  padding: 16px 24px;
  background: #286660;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.role-btn:hover {
  background: #1e5a52;
  transform: translateY(-2px);
}

.role-btn.selected {
  background: #1e5a52;
  box-shadow: 0 4px 12px rgba(40, 102, 96, 0.3);
}

.role-actions {
  margin-top: 40px;
}

.continue-btn {
  padding: 12px 30px;
  background: #286660;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.continue-btn:hover {
  background: #1e5a52;
}

@media (max-width: 768px) {
  .role-selection-page {
    padding: 8px;
    min-height: 100vh;
    padding-top: max(8px, var(--safe-area-inset-top));
    padding-bottom: max(8px, var(--safe-area-inset-bottom));
    padding-left: max(8px, var(--safe-area-inset-left));
    padding-right: max(8px, var(--safe-area-inset-right));
  }

  .role-selection-container {
    max-width: 100%;
  }

  .role-selection-card {
    padding: 16px;
    margin: 0;
    border-radius: 12px;
  }

  .role-header {
    margin-bottom: 20px;
  }

  .role-header h1 {
    font-size: 20px;
    margin-bottom: 8px;
  }

  .role-header p {
    font-size: 13px;
  }

  .role-options {
    gap: 12px;
  }

  .role-btn {
    width: 100%;
    padding: 16px;
    font-size: 14px;
    border-radius: 8px;
    min-height: 60px;
  }

  .role-icon {
    font-size: 24px;
    margin-bottom: 8px;
  }

  .role-name {
    font-size: 16px;
    margin-bottom: 4px;
  }

  .role-description {
    font-size: 12px;
  }

  .continue-btn {
    padding: 12px;
    font-size: 14px;
    border-radius: 8px;
    margin-top: 20px;
  }
}
</style>
