<template>
  <q-page class="q-pa-md">
    <div class="queue-management-page">
      <div class="page-header">
        <h2 class="page-title">Nurse Queue Management</h2>
        <p class="page-subtitle">Manage patient queues and call next patients.</p>
      </div>

      <div class="content-placeholder">
        <q-banner class="bg-blue-1 text-blue-8" rounded>
          <template v-slot:avatar>
            <q-icon name="schedule" color="blue" />
          </template>
          This is a temporary placeholder page to restore the application build.
        </q-banner>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
// Placeholder component for Nurse Queue Management route
</script>

<style scoped>
.queue-management-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
}

.page-subtitle {
  font-size: 1rem;
  color: #607d8b;
}

.content-placeholder {
  margin-top: 8px;
}
</style>