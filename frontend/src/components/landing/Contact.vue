<template>
  <section class="section contact" id="contact">
    <h2 class="title">GET IN TOUCH</h2>
    <p class="subtitle">We’re here to support your digital transformation</p>
    <div class="contact-card">
      <div class="items">
        <div class="item"><svg width="22" height="22" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2" stroke="#0ea5a6" stroke-width="2"/><path d="M3 7l9 6 9-6" stroke="#0ea5a6" stroke-width="2"/></svg><span>Email: support@medisync.com</span></div>
        <div class="item"><svg width="22" height="22" viewBox="0 0 24 24"><path d="M6 4l4 2-2 3c1 2 3 4 5 5l3-2 2 4-3 2c-5-2-9-6-11-11l2-3z" stroke="#0ea5a6" stroke-width="2"/></svg><span>Phone: +63 123 456 7890</span></div>
        <div class="item"><svg width="22" height="22" viewBox="0 0 24 24"><path d="M12 3c-3 0-6 3-6 6 0 5 6 12 6 12s6-7 6-12c0-3-3-6-6-6z" stroke="#0ea5a6" stroke-width="2"/><circle cx="12" cy="9" r="2" stroke="#0ea5a6" stroke-width="2"/></svg><span>Location: Manila, Philippines</span></div>
      </div>
    </div>
  </section>
</template>
<script setup lang="ts">
defineOptions({ name: 'ContactSection' });
</script>
<style scoped>
.contact{background:#fff}
.contact-card{max-width:900px;margin:0 auto;border:1px solid rgba(15,118,110,.08);border-radius:14px;padding:22px;box-shadow:0 10px 30px rgba(13,84,80,.15);text-align:center}
.items{display:grid;gap:12px}
@media(min-width:680px){.items{grid-template-columns:1fr 1fr 1fr}}
.item{display:flex;align-items:center;gap:10px;justify-content:center;color:#334155}
.item svg{flex:0 0 auto}
.section{padding:48px 24px;background:#fff;scroll-margin-top:80px}
.title{text-align:center;font-size:clamp(26px,4vw,40px);font-weight:800;letter-spacing:.02em;margin:8px 0 16px;color:#0b2431}
.subtitle{text-align:center;color:#546579;max-width:900px;margin:0 auto 40px}
</style>