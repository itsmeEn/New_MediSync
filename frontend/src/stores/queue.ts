import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface QueueDepartmentStatus {
  department: string
  isOpen: boolean
  updatedAt: number
}

export interface QueueNotification {
  type: 'queue_opened' | 'queue_closed' | 'queue_status_update'
  department: string
  message?: string
  payload?: unknown
  ts: number
}

export const useQueueStore = defineStore('queue', () => {
  const statusByDepartment = ref<Record<string, QueueDepartmentStatus>>({})
  const lastNotification = ref<QueueNotification | null>(null)

  const setStatus = (department: string, isOpen: boolean) => {
    const ts = Date.now()
    statusByDepartment.value[department] = { department, isOpen, updatedAt: ts }
    lastNotification.value = {
      type: isOpen ? 'queue_opened' : 'queue_closed',
      department,
      ts,
    }
  }

  const broadcastOpen = (department: string, message?: string) => {
    try {
      setStatus(department, true)
      const event = new CustomEvent('queue:open', {
        detail: {
          department,
          message: message || `Queue opened for ${department}`,
          ts: Date.now(),
        },
      })
      window.dispatchEvent(event)
    } catch (e) {
      // Swallow errors but expose a notification record
      lastNotification.value = {
        type: 'queue_status_update',
        department,
        message: `Failed to broadcast open: ${e instanceof Error ? e.message : String(e)}`,
        payload: e,
        ts: Date.now(),
      }
    }
  }

  const broadcastClose = (department: string, message?: string) => {
    try {
      setStatus(department, false)
      const event = new CustomEvent('queue:close', {
        detail: {
          department,
          message: message || `Queue closed for ${department}`,
          ts: Date.now(),
        },
      })
      window.dispatchEvent(event)
    } catch (e) {
      lastNotification.value = {
        type: 'queue_status_update',
        department,
        message: `Failed to broadcast close: ${e instanceof Error ? e.message : String(e)}`,
        payload: e,
        ts: Date.now(),
      }
    }
  }

  const receiveServerNotification = (notif: QueueNotification) => {
    lastNotification.value = notif

    // Safely read is_open from payload when present
    const isOpenFromPayload = (() => {
      const p = notif.payload
      if (typeof p === 'object' && p !== null) {
        const val = (p as Record<string, unknown>)['is_open']
        if (typeof val === 'boolean') return val
      }
      return null
    })()

    if (notif.type === 'queue_opened' || (notif.type === 'queue_status_update' && isOpenFromPayload === true)) {
      setStatus(notif.department, true)
      window.dispatchEvent(
        new CustomEvent('queue:open', { detail: { department: notif.department, message: notif.message, ts: notif.ts } }),
      )
    } else if (notif.type === 'queue_closed' || (notif.type === 'queue_status_update' && isOpenFromPayload === false)) {
      setStatus(notif.department, false)
      window.dispatchEvent(
        new CustomEvent('queue:close', { detail: { department: notif.department, message: notif.message, ts: notif.ts } }),
      )
    }
  }

  const isDepartmentOpen = (department: string) => {
    return !!statusByDepartment.value[department]?.isOpen
  }

  return {
    statusByDepartment,
    lastNotification,
    setStatus,
    broadcastOpen,
    broadcastClose,
    receiveServerNotification,
    isDepartmentOpen,
  }
})