<template>
  <main class="landing-page">
    <Navbar />

    <header class="hero">
      <div class="container center">
        <h1>STREAMLINED HEALTHCARE MANAGEMENT</h1>
        <p>
          MediSync transforms clinical workflows with real-time queue monitoring, AI-driven insights, and automated scheduling.
          Experience healthcare that puts patients first while empowering healthcare providers with intelligent decision-support tools.
        </p>
        <a class="cta" href="#" aria-label="Download MediSync" @click.prevent="goto('download')">Download Now</a>
      </div>
    </header>

    <section class="section" id="about">
      <h2 class="title">ABOUT MEDISYNC</h2>
      <p class="subtitle">A comprehensive cross-platform solution designed to revolutionize outpatient department operations</p>
      <div class="text-block">
        <h3>Our Mission</h3>
        <p>
          MediSync addresses critical inefficiencies in traditional and QR-based queuing systems by introducing intelligent, real-time digital queue
          monitoring. We reduce patient waiting times and streamline service delivery through automated scheduling and mobile notifications.
        </p>
        <h3>Innovation in Healthcare</h3>
        <p>
          By integrating predictive analytics and AI-driven recommendations, MediSync empowers health centers with data-informed insights. Our system
          forecasts health trends, patient surges, and resource demands, enabling clinics to prepare for peak periods and deliver proactive healthcare.
        </p>
      </div>
    </section>

    <Features />
    <Download />
    <Contact />

    <footer class="footer">
      <div class="tagline">Transforming healthcare through intelligent technology</div>
      © {{ currentYear }} MediSync. All rights reserved.
    </footer>
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import Navbar from 'src/components/landing/Navbar.vue';
import Features from 'src/components/landing/Features.vue';
import Download from 'src/components/landing/Download.vue';
import Contact from 'src/components/landing/Contact.vue';

const currentYear = computed(() => new Date().getFullYear());
const goto = (id: string) => {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
};
</script>

<style>
:root { 
  --bg:#0f766e; 
  --bg2:#2dd4bf; 
  --teal:#0ea5a6; 
  --teal-dark:#0f766e; 
  --text:#0b1320; 
  --muted:#546579; 
  --card-bg:#f7faf9; 
  --white:#fff; 
  --shadow:0 10px 30px rgba(13,84,80,.15); 
  --curveH: clamp(40px, 8vw, 90px); 
}   
*{
  box-sizing:border-box
}
.landing-page{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial;
  color:var(--text); 
  background:#fbfcfd; 
  line-height:1.6; 
  padding-top:64px
}
.container{
  max-width:1100px;
  margin:0 auto
}
.center{
  text-align:center
}
.hero{
  background:linear-gradient(135deg,var(--bg),var(--bg2)); 
  color:var(--white); 
  padding:64px 24px 72px; 
  position: relative; 
  overflow: hidden
}
.hero h1{
  font-size:clamp(28px,4.5vw,40px); 
  margin:0 0 16px; 
  line-height:1.2; 
  font-weight:800; 
  letter-spacing:.02em
}
.hero p{
  max-width:900px;
  margin:0 auto 24px; 
  font-size:clamp(14px,2.2vw,18px); 
  opacity:.95
}
.cta{
  display:inline-block;
  background:var(--white);
  color:var(--teal-dark);
  border:none;
  border-radius:10px;
  padding:12px 18px;
  font-weight:600;
  text-decoration:none;
  box-shadow:var(--shadow);
  transition:transform .2s ease,box-shadow .2s ease
}
.cta:hover{
  transform:translateY(-2px); 
  box-shadow:0 14px 34px rgba(13,84,80,.18)
}
.section{
  padding:48px 24px;
  background:var(--white); 
  scroll-margin-top:80px
} 
.title{
  text-align:center; 
  font-size:clamp(26px,4vw,40px); 
  font-weight:800; 
  letter-spacing:.02em; 
  margin:8px 0 16px; 
  color:#0b2431
}
.subtitle{
  text-align:center;
  color:var(--muted);
  max-width:900px;
  margin:0 auto 40px
}
.text-block{
  max-width:1000px;
  margin:0 auto
}
.text-block h3{
  font-size:clamp(18px,3vw,26px);
  margin:24px 0 8px
}
.text-block p{
  color:#334155;
  margin:0 0 6px
}
.footer{
  text-align:center;
  color:#e2e8f0;
  padding:32px 24px;
  background:#0b2431
}
.footer .tagline{
  font-size:clamp(14px,2.2vw,18px);
  font-weight:700; letter-spacing:.02em; margin-bottom:4px
}
/* Inverted curvature: outward curve into content area */
.hero::after{
  content:""; 
  position:absolute; 
  left:-2%; right:-2%; 
  bottom:-1px; height:var(--curveH); 
  background:var(--white); 
  border-top-left-radius:100% 40%; 
  border-top-right-radius:100% 40%; 
  box-shadow:0 -8px 24px rgba(13,84,80,.10)
}
.hero .container{
  position:relative; 
  z-index:1
}

</style>