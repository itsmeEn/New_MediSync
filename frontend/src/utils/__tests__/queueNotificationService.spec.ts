import { describe, it, expect, beforeEach } from 'vitest'
import { getQueuePreference, setQueuePreference, clearQueuePreference, shouldSendQueueNotification } from '../queueNotificationService'

const pid = 123

describe('queueNotificationService', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('returns disabled preference when none stored', () => {
    const pref = getQueuePreference(pid)
    expect(pref.enabled).toBe(false)
  })

  it('persists and reads enabled preference', () => {
    setQueuePreference(pid, { enabled: true, department: 'OPD' })
    const pref = getQueuePreference(pid)
    expect(pref.enabled).toBe(true)
    expect(pref.department).toBe('OPD')
  })

  it('clears preference', () => {
    setQueuePreference(pid, { enabled: true })
    clearQueuePreference(pid)
    const pref = getQueuePreference(pid)
    expect(pref.enabled).toBe(false)
  })

  it('guard allows notifications only when enabled, open and in queue', () => {
    expect(shouldSendQueueNotification({ enabled: true, isOpen: true, inQueue: true })).toBe(true)
    expect(shouldSendQueueNotification({ enabled: true, isOpen: false, inQueue: true })).toBe(false)
    expect(shouldSendQueueNotification({ enabled: true, isOpen: true, inQueue: false })).toBe(false)
    expect(shouldSendQueueNotification({ enabled: false, isOpen: true, inQueue: true })).toBe(false)
  })
})