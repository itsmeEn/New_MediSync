<template>
  <LoadingScreen />
  <router-view />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import LoadingScreen from './components/LoadingScreen.vue'
import { setViewportHeightVar } from 'src/utils/responsive'

const handleResize = () => setViewportHeightVar()

onMounted(() => {
  // Initialize CSS variable for mobile viewport height and listen for changes
  setViewportHeightVar()
  window.addEventListener('resize', handleResize)
  window.addEventListener('orientationchange', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('orientationchange', handleResize)
})
</script>

<style src="./css/responsive.css"></style>
<style src="./css/cards.css"></style>
