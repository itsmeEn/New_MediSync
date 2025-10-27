<template>
  <section class="section download" id="download">
    <h2 class="title">DOWNLOAD MEDISYNC</h2>
    <p class="subtitle">Cross-platform apps for patients and providers</p>
    <div class="platforms">
      <article class="platform-card android">
        <div class="head"><svg width="24" height="24" viewBox="0 0 24 24"><path d="M12 3v10" stroke="white" stroke-width="2"/><path d="M8 9l4 4 4-4" stroke="white" stroke-width="2"/></svg><h4>Android</h4></div>
        <p>Optimized APK for quick installation on Android devices</p>
        <a class="download-btn" href="/medisync-landing/downloads/medisync-1.0.0-apk.txt" download>Download APK</a>
        <div class="version">Version 1.0.0 — 25MB</div>
      </article>
      <article class="platform-card ios">
        <div class="head"><svg width="24" height="24" viewBox="0 0 24 24"><path d="M12 3v10" stroke="white" stroke-width="2"/><path d="M8 9l4 4 4-4" stroke="white" stroke-width="2"/></svg><h4>iOS</h4></div>
        <p>TestFlight-ready IPA for iPhone and iPad devices</p>
        <a class="download-btn" href="/medisync-landing/downloads/medisync-1.0.0-ipa.txt" download>Download IPA</a>
        <div class="version">Version 1.0.0 — 28MB</div>
      </article>
    </div>
  </section>
</template>
<script setup lang="ts">
defineOptions({ name: 'DownloadSection' });
</script>
<style scoped>
.download{background:#f4f7f8}
.platforms{display:grid;gap:20px;max-width:1040px;margin:0 auto}
@media(min-width:860px){.platforms{grid-template-columns:1fr 1fr}}
.platform-card{border-radius:16px;padding:24px;box-shadow:0 10px 30px rgba(13,84,80,.15);color:#fff;display:flex;flex-direction:column;gap:14px}
.platform-card .head{display:flex;align-items:center;gap:10px}
.platform-card h4{margin:0;font-size:22px}
.platform-card p{margin:4px 0 0;opacity:.9}
.download-btn{display:inline-block;background:#fff;color:#0f766e;text-decoration:none;border-radius:12px;padding:12px 16px;font-weight:700;text-align:center;box-shadow:0 10px 30px rgba(13,84,80,.15)}
.android{background:linear-gradient(135deg,#0fb3a1,#0d8d80)}
.ios{background:#10212f}
.version{font-size:13px;opacity:.9}
.section{padding:48px 24px;background:#fff;scroll-margin-top:80px}
.title{text-align:center;font-size:clamp(26px,4vw,40px);font-weight:800;letter-spacing:.02em;margin:8px 0 16px;color:#0b2431}
.subtitle{text-align:center;color:#546579;max-width:900px;margin:0 auto 40px}
</style>