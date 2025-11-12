import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { nextTick } from 'vue'
import { useMedicalRequestStore } from 'src/stores/medicalRequest'

// Provide a mocked axios boot module to avoid loading Quasar wrappers in tests
vi.mock('src/boot/axios', () => ({
  api: { get: vi.fn(), post: vi.fn(), defaults: { baseURL: 'http://localhost:8000/api' } }
}))

import PatientMedicalRequest from 'src/pages/PatientMedicalRequest.vue'
import * as axiosBoot from 'src/boot/axios'

// Convenience aliases bound to mocked api functions
type MockedFn = ReturnType<typeof vi.fn>
const getMock: MockedFn = vi.fn()
const postMock: MockedFn = vi.fn()
// Forward the axios mock implementation to our local mocks without invoking them directly
;(axiosBoot.api.get as MockedFn).mockImplementation(getMock as unknown as (...args: unknown[]) => unknown)
;(axiosBoot.api.post as MockedFn).mockImplementation(postMock as unknown as (...args: unknown[]) => unknown)

beforeEach(() => {
  setActivePinia(createPinia())
  getMock.mockReset()
  postMock.mockReset()
  // Reset stub implementations
  // Mock localStorage user
  vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key: string) => {
    if (key === 'user') {
      return JSON.stringify({ id: 123, full_name: 'Test User' })
    }
    return null
  })
})

describe('PatientMedicalRequest.vue', () => {
  it('prefills type and recipient from query params', async () => {
    // Mock recipients
    getMock.mockImplementation((url: string) => {
      if (url.includes('/operations/availability/doctors/free/')) {
        return { data: { doctors: [{ id: 77, full_name: 'Dr Alice' }] } }
      }
      if (url.includes('/operations/patient/appointments/')) {
        return { data: { results: [] } }
      }
      if (url.includes('/operations/medical-requests/')) {
        return { data: [] }
      }
      return { data: {} }
    })

    const router = createRouter({
      history: createWebHistory(),
      routes: [{ path: '/', name: 'root', component: { template: '<div />' } }]
    })
    await router.push({ path: '/', query: { type: 'medical_certificate', doctor_id: '77', doctor_name: 'Dr Alice' } })
    await router.isReady()

    const pinia = createPinia()
    setActivePinia(pinia)
    mount(PatientMedicalRequest, {
      global: {
        plugins: [pinia, router],
        stubs: { PatientBottomNav: true },
        mocks: { $q: { notify: vi.fn() } }
      }
    })
    const store = useMedicalRequestStore()
    await nextTick()
    expect(store.form.requestType).toBe('medical_certificate')
    expect(store.form.recipient).toBe('Dr Alice')
  })

  it('builds payload with attending_doctor_id and certificate fields', async () => {
    // Mock endpoints
    getMock.mockImplementation((url: string) => {
      if (url.includes('/operations/availability/doctors/free/')) {
        return { data: { doctors: [{ id: 77, full_name: 'Dr Alice' }] } }
      }
      if (url.includes('/operations/patient/appointments/')) {
        return { data: { results: [] } }
      }
      if (url.includes('/operations/medical-requests/')) {
        return { data: [] }
      }
      return { data: {} }
    })
    postMock.mockImplementation(() => ({ data: { id: 999, status: 'pending', request_reference_number: 'MC-999' } }))

    const router = createRouter({
      history: createWebHistory(),
      routes: [{ path: '/', name: 'root', component: { template: '<div />' } }]
    })
    await router.push({ path: '/' })
    await router.isReady()

    const pinia = createPinia()
    setActivePinia(pinia)
    mount(PatientMedicalRequest, {
      global: {
        plugins: [pinia, router],
        stubs: { PatientBottomNav: true },
        mocks: { $q: { notify: vi.fn() } }
      }
    })
    const store = useMedicalRequestStore()
    await store.loadRecipients()
    store.form.requestType = 'medical_certificate'
    store.form.recipient = '77'
    store.form.purpose = 'work_leave'
    store.form.dateRangeStart = '2025-01-01'
    store.form.dateRangeEnd = '2025-01-10'
    store.form.details = 'Need certificate for leave'

    await store.submit()
    expect(postMock).toHaveBeenCalled()
    const call = postMock.mock.calls[0]
    expect(call).toBeTruthy()
    const [url, payload] = call as [string, unknown]
    expect(url).toContain('/operations/medical-requests/')
    type CreatedPayload = {
      attending_doctor_id?: number
      purpose?: string
      requested_date_range_start?: string
      requested_date_range_end?: string
    }
    const p = payload as CreatedPayload
    expect(p.attending_doctor_id).toBe(77)
    expect(p.purpose).toBe('work_leave')
    expect(p.requested_date_range_start).toBe('2025-01-01')
    expect(p.requested_date_range_end).toBe('2025-01-10')
  })
})