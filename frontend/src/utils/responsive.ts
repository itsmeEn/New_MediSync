// Shared responsive utilities for breakpoints and viewport handling
import { ref, onMounted, onUnmounted } from 'vue'

export const BREAKPOINTS = {
  xs: 320,
  sm: 480,
  md: 768,
  lg: 1024,
  xl: 1280,
} as const

// Sets a CSS variable that accounts for mobile browser chrome affecting 100vh
export function setViewportHeightVar() {
  const vh = window.innerHeight * 0.01
  document.documentElement.style.setProperty('--vh', `${vh}px`)
}

// Composable to expose responsive flags; keeps it minimal and framework-agnostic
export function useResponsive() {
  const width = ref(typeof window !== 'undefined' ? window.innerWidth : BREAKPOINTS.md)

  const updateWidth = () => {
    width.value = window.innerWidth
  }

  onMounted(() => {
    updateWidth()
    window.addEventListener('resize', updateWidth)
    window.addEventListener('orientationchange', updateWidth)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateWidth)
    window.removeEventListener('orientationchange', updateWidth)
  })

  const isXs = () => width.value <= BREAKPOINTS.sm
  const isSm = () => width.value <= BREAKPOINTS.md
  const isMdUp = () => width.value > BREAKPOINTS.md

  return { width, isXs, isSm, isMdUp }
}