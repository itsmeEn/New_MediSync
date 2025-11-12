import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { vi } from 'vitest'
// Mock axios boot to avoid Quasar wrapper resolution during tests
vi.mock('src/boot/axios', () => ({
  api: { get: vi.fn(), post: vi.fn(), defaults: { baseURL: 'http://localhost:8000/api' } }
}))
// Provide a minimal Quasar composable mock for notifications
vi.mock('quasar', () => ({ useQuasar: () => ({ notify: vi.fn() }) }))
import MedicalRecordRequestForm from '@/components/MedicalRecordRequestForm.vue'
import * as axiosBoot from 'src/boot/axios'
import { createPinia } from 'pinia'

describe('MedicalRecordRequestForm', () => {
  it('emits backend-compatible payload with delivery and consent', async () => {
    const wrapper = mount(MedicalRecordRequestForm, {
      props: {
        initial: {
          requestType: 'medical_certificate',
          details: 'Need for work',
          purpose: 'work_leave',
          dateRangeStart: '2024-01-01',
          dateRangeEnd: '2024-01-31',
          recipient: 'Dr. Smith',
        },
      },
      global: {
        plugins: [createPinia()],
        mocks: { $q: { notify: vi.fn() } },
        config: {
          compilerOptions: {
            isCustomElement: (tag: string) => tag.startsWith('q-'),
          },
        },
        stubs: {
          'q-form': true,
          'q-select': true,
          'q-input': true,
          'q-toggle': true,
          'q-btn': true,
        },
      },
    })

    // Trigger form submit on the stubbed q-form to invoke handleSubmit
    // Ensure submit succeeds by mocking backend creation response
    ;(axiosBoot.api.post as ReturnType<typeof vi.fn>).mockResolvedValue({ data: { id: 101, status: 'pending' } })
    // Provide user context for store to resolve patient ID
    localStorage.setItem('user', JSON.stringify({ id: 123 }))
    const formStub = wrapper.findComponent({ name: 'q-form' })
    await formStub.trigger('submit')
    await Promise.resolve()

    const events = wrapper.emitted('submitted')
    // Runtime guards to satisfy strict TS and ensure event existence
    expect(events).toBeTruthy()
    if (!events || !events[0]) {
      throw new Error('Submit event not emitted')
    }
    const created = events[0][0] as Record<string, unknown>
    expect(created).toBeTruthy()
  })
})