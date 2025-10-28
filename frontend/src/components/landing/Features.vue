<template>
  <section class="section" id="features">
    <h2 class="title">OUR FEATURES</h2>
    <p class="subtitle">Comprehensive tools designed to transform healthcare delivery and patient experience</p>
    <div class="features">
      <article class="feature"><div class="head"><svg width="26" height="26" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" stroke="#0ea5a6" stroke-width="2"/><path d="M12 7v5l4 2" stroke="#0ea5a6" stroke-width="2"/></svg><h4>Real-Time Queue Monitoring</h4></div><p>Track patient waiting times with live digital queue updates</p></article>
      <article class="feature"><div class="head"><svg width="26" height="26" viewBox="0 0 24 24"><path d="M12 3a6 6 0 016 6v3l2 2H4l2-2V9a6 6 0 016-6z" stroke="#0ea5a6" stroke-width="2"/><circle cx="12" cy="19" r="2" fill="#0ea5a6"/></svg><h4>Mobile Notifications</h4></div><p>Automated alerts keep patients informed about their appointments</p></article>
      <article class="feature"><div class="head"><svg width="26" height="26" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2" stroke="#0ea5a6" stroke-width="2"/><path d="M8 3v4M16 3v4M3 10h18" stroke="#0ea5a6" stroke-width="2"/></svg><h4>Automated Scheduling</h4></div><p>Intelligent appointment management optimizes patient flow and resources</p></article>
      <article class="feature"><div class="head"><svg width="26" height="26" viewBox="0 0 24 24"><path d="M8 7a4 4 0 118 0 4 4 0 11-8 0z" stroke="#0ea5a6" stroke-width="2"/><path d="M6 13c3 2 9 2 12 0" stroke="#0ea5a6" stroke-width="2"/></svg><h4>AI-Driven Insights</h4></div><p>Predictive analytics recommend actions to enhance decision-making</p></article>
      <article class="feature"><div class="head"><svg width="26" height="26" viewBox="0 0 24 24"><path d="M4 18h16" stroke="#0ea5a6" stroke-width="2"/><rect x="6" y="10" width="3" height="6" fill="#0ea5a6"/><rect x="11" y="8" width="3" height="8" fill="#0ea5a6"/><rect x="16" y="6" width="3" height="10" fill="#0ea5a6"/></svg><h4>Decision Support Tools</h4></div><p>Evidence-based guidance surfaces risks and recommended actions</p></article>
      <article class="feature"><div class="head"><svg width="26" height="26" viewBox="0 0 24 24"><circle cx="9" cy="9" r="3" stroke="#0ea5a6" stroke-width="2"/><circle cx="16" cy="11" r="2" stroke="#0ea5a6" stroke-width="2"/><path d="M3 19c0-3 3-5 6-5s6 2 6 5" stroke="#0ea5a6" stroke-width="2"/></svg><h4>Patient-Centered Care</h4></div><p>Tools designed around patient needs to improve satisfaction</p></article>
    </div>
  </section>
</template>
<script setup lang="ts">
defineOptions({ name: 'FeaturesSection' });
</script>
<style scoped>
.features{max-width:1040px;margin:0 auto;display:grid;gap:20px}
@media(min-width:860px){.features{grid-template-columns:1fr 1fr}}
.feature{background:#f7faf9;border-radius:14px;padding:22px;box-shadow:0 10px 30px rgba(13,84,80,.15)}
.feature .head{display:flex;align-items:center;gap:12px}
.feature h4{margin:0;font-size:21px}
.feature p{margin:10px 0 0;color:#3b4c5f}
.section{padding:48px 24px;background:#fff;scroll-margin-top:80px}
.title{text-align:center;font-size:clamp(26px,4vw,40px);font-weight:800;letter-spacing:.02em;margin:8px 0 16px;color:#0b2431}
.subtitle{text-align:center;color:#546579;max-width:900px;margin:0 auto 40px}
</style>