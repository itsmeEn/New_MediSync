<template>
  <div class="sections-pager">
    <q-card flat class="pager-card">
      <q-card-section class="pager-controls">
        <q-pagination
          v-model="page"
          :max="3"
          :max-pages="3"
          boundary-numbers
          direction-links
          color="primary"
          size="md"
          @update:model-value="onPageChange"
        />
        <div class="pager-labels">
          <div :class="['pager-label', { active: page === 1 }]">Doctor</div>
          <div :class="['pager-label', { active: page === 2 }]">Messaging</div>
          <div :class="['pager-label', { active: page === 3 }]">Nurse</div>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const page = ref(1);

const setPageFromRoute = () => {
  const name = route.name as string | undefined;
  if (name === 'DoctorMessaging') page.value = 1;
  else if (name === 'MessagingCenter') page.value = 2;
  else if (route.path === '/nurse-messaging') page.value = 3;
  else page.value = 2; // default to center
};
setPageFromRoute();
watch(() => route.fullPath, setPageFromRoute);

const onPageChange = (val: number) => {
  const target =
    val === 1 ? { name: 'DoctorMessaging' } :
    val === 2 ? { name: 'MessagingCenter' } :
    { path: '/nurse-messaging' };
  void router.push(target);
};
</script>

<style scoped>
.sections-pager {
  display: flex;
  justify-content: center;
  margin: 8px 0 16px;
}
.pager-card {
  width: 100%;
  max-width: 640px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  border-radius: 14px;
  border: 1px solid rgba(40, 102, 96, 0.12);
  box-shadow: 0 8px 20px rgba(40, 102, 96, 0.08);
}
.pager-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.pager-labels {
  display: flex;
  gap: 16px;
  font-size: 0.85rem;
  color: #587672;
}
.pager-label.active {
  color: #286660;
  font-weight: 600;
}
@media (max-width: 600px) {
  .pager-card {
    max-width: 100%;
  }
}
</style>