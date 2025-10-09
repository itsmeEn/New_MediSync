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
      const response = await api.get('/patient/appointments/')
      appointments.value = response.data.results || response.data || []
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
      await api.patch(`/patient/appointments/${id}/`, { status })
      const appointment = appointments.value.find(a => a.id === id)
      if (appointment) {
        appointment.status = status
      }
    } catch (err) {
      console.error('Failed to update appointment status:', err)
      throw err
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
      await api.patch(`/patient/appointments/${id}/`, { date: newDate })
      const appointment = appointments.value.find(a => a.id === id)
      if (appointment) {
        appointment.date = newDate
      }
    } catch (err) {
      console.error('Failed to reschedule appointment:', err)
      throw err
    }
  }

  const updateFields = async (id: number, fields: Partial<Appointment>) => {
    try {
      await api.patch(`/patient/appointments/${id}/`, fields)
      const appointment = appointments.value.find(a => a.id === id)
      if (appointment) {
        Object.assign(appointment, fields)
      }
    } catch (err) {
      console.error('Failed to update appointment:', err)
      throw err
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