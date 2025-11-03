<template>
  <div class="chart-container">
    <slot />
  </div>
</template>

<script setup lang="ts">
// Simple wrapper to unify chart spacing and responsiveness
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  min-height: 240px;
}

@media (max-width: 768px) {
  .chart-container { min-height: 200px; }
}
</style>