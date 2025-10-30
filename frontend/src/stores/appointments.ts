import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from 'src/boot/axios'

export interface Appointment {
  id: number
  department: string
  type: string
  date: string
  time: string
  status: 'upcoming' | 'completed' | 'cancelled'
  archived?: boolean
  doctor?: string
  reason?: string
}

export const useAppointmentsStore = defineStore('appointments', () => {
  // State
  const appointments = ref<Appointment[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const nextAppointment = computed(() => {
    const upcoming = appointments.value
      .filter(a => a.status === 'upcoming' && !a.archived)
      .sort((a, b) => new Date(a.date + ' ' + a.time).getTime() - new Date(b.date + ' ' + b.time).getTime())
    return upcoming[0] || null
  })

  const lastAppointment = computed(() => {
    const completed = appointments.value
      .filter(a => a.status === 'completed')
      .sort((a, b) => new Date(b.date + ' ' + b.time).getTime() - new Date(a.date + ' ' + a.time).getTime())
    return completed[0] || null
  })

  // Actions
  const loadAppointments = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/operations/appointments/')
      type AppointmentDTO = {
        appointment_id?: number
        id?: number
        department?: string
        appointment_type?: string
        type?: string
        appointment_date?: string
        date?: string
        doctor_name?: string
        doctor?: string
        reason?: string
        status?: string
        time?: string
      }
      const raw = (response.data?.results ?? response.data ?? []) as AppointmentDTO[]
      appointments.value = raw.map((a) => {
        const dt = a.appointment_date ?? a.date
        const d = dt ? new Date(dt) : null
        const dateStr = d ? new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().split('T')[0] : (a.date ?? '')
        const timeStr = d ? d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }) : (a.time ?? '')
        const statusMap: Record<string, Appointment['status']> = {
          scheduled: 'upcoming',
          completed: 'completed',
          cancelled: 'cancelled',
          no_show: 'cancelled'
        }
        const statusVal: Appointment['status'] = statusMap[(a.status ?? '').toLowerCase()] ?? (a.status as Appointment['status']) ?? 'upcoming'
        return {
          id: a.appointment_id ?? a.id ?? 0,
          department: a.department ?? 'general',
          type: a.appointment_type ?? a.type ?? 'general',
          date: dateStr,
          time: timeStr,
          status: statusVal,
          doctor: a.doctor_name ?? a.doctor ?? undefined,
          reason: a.reason ?? undefined
        } as Appointment
      })
    } catch (err) {
      error.value = 'Failed to load appointments'
      console.error('Failed to load appointments:', err)
      // Set some mock data for development
      appointments.value = [
        {
          id: 1,
          department: 'general',
          type: 'general',
          date: '2024-01-15',
          time: '10:00',
          status: 'upcoming',
          doctor: 'Dr. Smith',
          reason: 'Regular checkup'
        },
        {
          id: 2,
          department: 'cardiology',
          type: 'specialist',
          date: '2024-01-10',
          time: '14:30',
          status: 'completed',
          doctor: 'Dr. Johnson',
          reason: 'Heart consultation'
        }
      ]
    } finally {
      loading.value = false
    }
  }

  const updateStatus = async (id: number, status: Appointment['status']) => {
    try {
      await api.patch(`/operations/appointments/${id}/`, { status })
      const appointment = appointments.value.find(a => a.id === id)
      if (appointment) {
        appointment.status = status
      }
      return true
    } catch (err) {
      console.warn('Failed to update appointment status via API, updating locally:', err)
      const appointment = appointments.value.find(a => a.id === id)
      if (appointment) {
        appointment.status = status
      }
      return false
    }
  }

  const archiveAppointment = (id: number) => {
    const appointment = appointments.value.find(a => a.id === id)
    if (appointment) {
      appointment.archived = true
    }
  }

  const rescheduleSameTime = async (id: number, newDate: string) => {
    try {
      await api.patch(`/operations/appointments/${id}/`, { date: newDate })
      const appointment = appointments.value.find(a => a.id === id)
      if (appointment) {
        appointment.date = newDate
      }
      return true
    } catch (err) {
      console.warn('Failed to reschedule appointment via API, updating locally:', err)
      const appointment = appointments.value.find(a => a.id === id)
      if (appointment) {
        appointment.date = newDate
      }
      return false
    }
  }

  const updateFields = async (id: number, fields: Partial<Appointment>) => {
    try {
      await api.patch(`/operations/appointments/${id}/`, fields)
      const appointment = appointments.value.find(a => a.id === id)
      if (appointment) {
        Object.assign(appointment, fields)
      }
      return true
    } catch (err) {
      console.warn('Failed to update appointment via API, updating locally:', err)
      const appointment = appointments.value.find(a => a.id === id)
      if (appointment) {
        Object.assign(appointment, fields)
      }
      return false
    }
  }

  return {
    // State
    appointments,
    loading,
    error,
    // Computed
    nextAppointment,
    lastAppointment,
    // Actions
    loadAppointments,
    updateStatus,
    archiveAppointment,
    rescheduleSameTime,
    updateFields
  }
})