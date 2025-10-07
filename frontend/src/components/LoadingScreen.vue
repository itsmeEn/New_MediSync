<template>
  <div class="loading-screen" v-if="isLoading">
    <div class="loading-content">
      <div class="logo-container">
        <div class="logo">
          <img src="../assets/logo.png" alt="MediSync Logo" class="logo-image" />
        </div>
        <h1 class="app-name">MediSync</h1>
      </div>
      <div class="loading-spinner">
        <div class="spinner"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const isLoading = ref(true);

onMounted(() => {
  // Simulate loading time (you can adjust this or make it dynamic)
  setTimeout(() => {
    isLoading.value = false;
  }, 3000); // 3 seconds loading time
});
</script>

<style scoped>
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  transition: opacity 0.5s ease-out;
}

.loading-content {
  text-align: center;
  animation: fadeIn 0.5s ease-in;
}

.logo-container {
  margin-bottom: 40px;
}

.logo {
  margin-bottom: 20px;
  animation: pulse 2s infinite;
}

.logo-image {
  width: 200px;
  height: 200px;
  object-fit: contain;
}

.app-name {
  color: #286660;
  font-size: 36px;
  font-weight: 700;
  margin: 0;
  letter-spacing: 2px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  animation: slideInUp 0.8s ease-out;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(40, 102, 96, 0.3);
  border-top: 4px solid #1e7668;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .app-name {
    font-size: 28px;
  }

  .logo-image {
    width: 150px;
    height: 150px;
  }
}
</style>
