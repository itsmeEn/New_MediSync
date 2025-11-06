import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shouldSendQueueNotification } from '../../utils/queueNotificationService'

describe('PatientQueue notification scenarios', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('does not notify when not in queue', () => {
    const canNotify = shouldSendQueueNotification({ enabled: true, isOpen: true, inQueue: false })
    expect(canNotify).toBe(false)
  })

  it('does not notify when queue is closed', () => {
    const canNotify = shouldSendQueueNotification({ enabled: true, isOpen: false, inQueue: true })
    expect(canNotify).toBe(false)
  })

  it('notifies when enabled, in queue, and open', () => {
    const canNotify = shouldSendQueueNotification({ enabled: true, isOpen: true, inQueue: true })
    expect(canNotify).toBe(true)
  })
})