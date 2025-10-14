import { defineBoot } from '#q-app/wrappers'

// Parse tokens from URL query and stash into localStorage for dev
export default defineBoot(() => {
  try {
    const url = new URL(window.location.href)
    const access = url.searchParams.get('access_token')
    const refresh = url.searchParams.get('refresh_token')
    const apiBase = url.searchParams.get('api_base')

    let changed = false

    if (access) {
      localStorage.setItem('access_token', access)
      changed = true
    }
    if (refresh) {
      localStorage.setItem('refresh_token', refresh)
      changed = true
    }
    if (apiBase) {
      // allow overriding API base used by axios boot
      localStorage.setItem('API_BASE_URL', apiBase.replace(/\/$/, ''))
      changed = true
    }

    if (changed) {
      // Clean tokens from URL for aesthetics and to avoid reprocessing
      url.searchParams.delete('access_token')
      url.searchParams.delete('refresh_token')
      url.searchParams.delete('api_base')
      const newUrl = `${url.origin}${url.pathname}${url.search}${url.hash}`
      window.history.replaceState({}, document.title, newUrl)
    }
  } catch (e) {
    // no-op if URL parsing fails
    console.warn('devTokenFromUrl failed:', e)
  }
})