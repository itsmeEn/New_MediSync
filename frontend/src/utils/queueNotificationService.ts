// Simple persistent storage for queue notification preferences keyed by patient
// Provides guards to verify when notifications should be active

export type QueuePreference = {
  enabled: boolean
  updatedAt: number
  department?: string | null
}

const keyFor = (patientId: number | string): string => `queue_notifications_enabled:${patientId}`

export function getQueuePreference(patientId?: number | string | null): QueuePreference {
  try {
    if (!patientId) return { enabled: false, updatedAt: Date.now(), department: null }
    const raw = localStorage.getItem(keyFor(patientId))
    if (!raw) return { enabled: false, updatedAt: Date.now(), department: null }
    const parsed = JSON.parse(raw)
    return {
      enabled: !!parsed.enabled,
      updatedAt: Number(parsed.updatedAt) || Date.now(),
      department: parsed.department ?? null
    }
  } catch {
    return { enabled: false, updatedAt: Date.now(), department: null }
  }
}

export function setQueuePreference(patientId?: number | string | null, pref?: Partial<QueuePreference>): QueuePreference {
  if (!patientId) return { enabled: false, updatedAt: Date.now(), department: null }
  const existing = getQueuePreference(patientId)
  const merged: QueuePreference = {
    enabled: pref?.enabled ?? existing.enabled,
    updatedAt: Date.now(),
    department: pref?.department ?? existing.department ?? null
  }
  try {
    localStorage.setItem(keyFor(patientId), JSON.stringify(merged))
    // Trigger listeners in other pages/tabs
    try {
      window.dispatchEvent(new CustomEvent('queue-preferences-updated', { detail: { patientId, pref: merged } }))
    } catch { /* ignore */ }
  } catch { /* ignore */ }
  return merged
}

export function clearQueuePreference(patientId?: number | string | null): void {
  try {
    if (!patientId) return
    localStorage.removeItem(keyFor(patientId))
    try {
      window.dispatchEvent(new CustomEvent('queue-preferences-updated', { detail: { patientId, pref: { enabled: false } } }))
    } catch { /* ignore */ }
  } catch { /* ignore */ }
}

export function shouldSendQueueNotification(opts: {
  enabled: boolean
  isOpen: boolean
  inQueue: boolean
}): boolean {
  return !!(opts.enabled && opts.isOpen && opts.inQueue)
}

export function getCurrentPatientId(): number | null {
  try {
    const raw = localStorage.getItem('user') || '{}'
    const u = JSON.parse(raw)
    const pid = u?.patient_profile?.id ?? u?.id
    return typeof pid === 'number' ? pid : null
  } catch {
    return null
  }
}