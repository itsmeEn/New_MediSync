<template>
  <section class="section download" id="download">
    <h2 class="title">DOWNLOAD MEDISYNC</h2>
    <p class="subtitle">Cross-platform apps for patients and providers</p>
    <div class="platforms">
      <article class="platform-card android">
        <div class="head">
          <svg width="24" height="24" viewBox="0 0 24 24"><path d="M12 3v10" stroke="white" stroke-width="2"/><path d="M8 9l4 4 4-4" stroke="white" stroke-width="2"/></svg>
          <h4>Android</h4>
        </div>
        <p>Install the PWA or download the APK for direct install.</p>
        <div class="btn-row">
          <button class="download-btn" @click="installPwaAndroid" :disabled="!canPromptInstall">
            {{ canPromptInstall ? 'Install App' : 'Install via browser menu' }}
          </button>
          <a class="download-btn" href="/medisync-landing/downloads/medisync-1.0.0.apk" download rel="noopener">
            Download APK
          </a>
        </div>
        <div class="version">Version 1.0.0 — ~25MB • SHA-256: <a href="/medisync-landing/downloads/medisync-1.0.0.apk.sha256" target="_blank" rel="noopener">view</a></div>
        <ul class="install-notes">
          <li>To Add to Home Screen: open menu • Add to Home screen.</li>
          <li>APK requires enabling installs from your browser in Android settings.</li>
        </ul>
      </article>
      <article class="platform-card ios">
        <div class="head">
          <svg width="24" height="24" viewBox="0 0 24 24"><path d="M12 3v10" stroke="white" stroke-width="2"/><path d="M8 9l4 4 4-4" stroke="white" stroke-width="2"/></svg>
          <h4>iOS</h4>
        </div>
        <p>Add to Home Screen or download the enterprise IPA.</p>
        <div class="btn-row">
          <button class="download-btn" @click="showIosA2hs" title="Use Share • Add to Home Screen">
            Add to Home Screen
          </button>
          <a class="download-btn" href="/medisync-landing/downloads/medisync-1.0.0.ipa" download rel="noopener">
            Download IPA
          </a>
        </div>
        <div class="version">Version 1.0.0 — ~28MB • SHA-256: <a href="/medisync-landing/downloads/medisync-1.0.0.ipa.sha256" target="_blank" rel="noopener">view</a></div>
        <ul class="install-notes">
          <li>On Safari: Share • Add to Home Screen to install the PWA.</li>
          <li>IPA requires enterprise signing and trust in Settings • General • VPN & Device Management.</li>
        </ul>
      </article>
    </div>
  </section>
</template>
<script setup lang="ts">
defineOptions({ name: 'DownloadSection' });

import { onMounted, onUnmounted, ref } from 'vue'

// Android PWA install prompt handling
const canPromptInstall = ref(false)
interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>
}
declare global {
  interface WindowEventMap {
    beforeinstallprompt: BeforeInstallPromptEvent
  }
}
let deferredPrompt: BeforeInstallPromptEvent | null = null

const beforeInstallHandler = (e: BeforeInstallPromptEvent) => {
  e.preventDefault()
  deferredPrompt = e
  canPromptInstall.value = true
}

const installPwaAndroid = async () => {
  try {
    if (!deferredPrompt) {
      alert('Use your browser menu • Add to Home screen to install the PWA.')
      return
    }
    await deferredPrompt.prompt()
    const choice = await deferredPrompt.userChoice
    // Reset prompt reference after user interaction
    deferredPrompt = null
    canPromptInstall.value = false
    console.log('PWA install outcome:', choice)
  } catch (err) {
    console.warn('PWA install prompt failed', err)
  }
}

const showIosA2hs = () => {
  alert('On Safari: tap Share • Add to Home Screen to install MediSync.')
}

onMounted(() => {
  window.addEventListener('beforeinstallprompt', beforeInstallHandler)
})

onUnmounted(() => {
  window.removeEventListener('beforeinstallprompt', beforeInstallHandler)
})
</script>
<style scoped>
.download{background:#f4f7f8}
.platforms{display:grid;gap:20px;max-width:1040px;margin:0 auto}
@media(min-width:860px){.platforms{grid-template-columns:1fr 1fr}}
.platform-card{border-radius:16px;padding:24px;box-shadow:0 10px 30px rgba(13,84,80,.15);color:#fff;display:flex;flex-direction:column;gap:14px}
.platform-card .head{display:flex;align-items:center;gap:10px}
.platform-card h4{margin:0;font-size:22px}
.platform-card p{margin:4px 0 0;opacity:.9}
.btn-row{display:flex;gap:12px;flex-wrap:wrap}
.download-btn{display:inline-block;background:#fff;color:#0f766e;text-decoration:none;border-radius:12px;padding:12px 16px;font-weight:700;text-align:center;box-shadow:0 10px 30px rgba(13,84,80,.15);cursor:pointer}
.android{background:linear-gradient(135deg,#0fb3a1,#0d8d80)}
.ios{background:#10212f}
.version{font-size:13px;opacity:.9}
.install-notes{margin:6px 0 0;padding-left:18px;font-size:13px;opacity:.95}
.section{padding:48px 24px;background:#fff;scroll-margin-top:80px}
.title{text-align:center;font-size:clamp(26px,4vw,40px);font-weight:800;letter-spacing:.02em;margin:8px 0 16px;color:#0b2431}
.subtitle{text-align:center;color:#546579;max-width:900px;margin:0 auto 40px}
</style>