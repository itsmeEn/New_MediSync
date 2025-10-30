<template>
  <nav class="navbar" :class="{ open: navOpen }" role="navigation" aria-label="Primary">
    <div class="nav-inner">
      <div class="nav-brand">MEDISYNC</div>
      <button class="menu-toggle" aria-label="Toggle navigation" @click="toggleNav" :aria-expanded="navOpen">
        <span></span><span></span><span></span>
      </button>
      <div class="nav-links" role="menu" @click="closeOnLink">
        <a class="nav-link" href="#" role="menuitem" @click.prevent="scrollTo('about')">About</a>
        <a class="nav-link" href="#" role="menuitem" @click.prevent="scrollTo('features')">Features</a>
        <a class="nav-link" href="#" role="menuitem" @click.prevent="scrollTo('download')">Download</a>
        <a class="nav-link" href="#" role="menuitem" @click.prevent="scrollTo('contact')">Contact</a>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue';
defineOptions({ name: 'LandingNavbar' });
const navOpen = ref(false);
const toggleNav = () => (navOpen.value = !navOpen.value);
const closeOnLink = (e: Event) => {
  const target = e.target as HTMLElement | null;
  if (target && target.tagName === 'A') navOpen.value = false;
};
const scrollTo = (id: string) => {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    navOpen.value = false;
  }
};
</script>

<style scoped>
.navbar{position:fixed;top:0;left:0;right:0;height:60px;background:#fff;border-bottom:1px solid rgba(15,118,110,.08);z-index:1000}
.nav-inner{max-width:1100px;margin:0 auto;height:60px;display:flex;align-items:center;justify-content:space-between;padding:0 16px}
.nav-brand{font-weight:800;letter-spacing:.04em;color:#0f766e}
.nav-links{display:flex;gap:18px}
.nav-link{color:#0f766e;text-decoration:none;font-weight:600;padding:8px 10px;border-radius:8px}
.nav-link:hover{background:rgba(15,118,110,.08)}
.menu-toggle{display:none;background:none;border:none;cursor:pointer;padding:8px}
.menu-toggle span{display:block;width:22px;height:2px;background:#0f766e;margin:4px 0}
@media (max-width:720px){
  .menu-toggle{display:block}
  .nav-links{position:fixed;top:60px;left:0;right:0;background:#fff;border-bottom:1px solid rgba(15,118,110,.08);display:none;flex-direction:column;padding:12px 16px}
  .navbar.open .nav-links{display:flex}
}
</style>