import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AssessmentDataView from '../AssessmentDataView.vue'

const mountWith = (data: Record<string, unknown> | null) => {
  return mount(AssessmentDataView, {
    props: { data },
    global: {
      // Stub Quasar components used inside the SFC
      stubs: {
        'q-markup-table': {
          template: '<table><slot /><slot name="thead" /><slot name="tbody" /></table>'
        }
      }
    }
  })
}

describe('AssessmentDataView', () => {
  it('renders score keys title-cased and supports numeric keys', () => {
    const wrapper = mountWith({ scores: { systolic_bp: 120, 1: 'ok' } })
    const text = wrapper.text()
    expect(text).toContain('Scores')
    expect(text).toContain('Systolic Bp')
    expect(text).toContain('1')
    expect(text).toContain('120')
    expect(text).toContain('ok')
  })

  it('renders participants table with normalized rows', () => {
    const wrapper = mountWith({ participants: [{ name: 'Alice', role: 'Nurse' }, 'Bob'] })
    const html = wrapper.html()
    expect(html).toContain('Participants')
    // Column headers are title-cased
    expect(html).toMatch(/<th[^>]*>Name<\/th>/)
    expect(html).toMatch(/<th[^>]*>Role<\/th>/)
  })

  it('handles circular objects without crashing', () => {
    const circ: any = {}
    circ.self = circ
    const wrapper = mountWith({ details: { circ } })
    const text = wrapper.text()
    // Fallback string from safeStringify
    expect(text).toContain('[object Object]')
  })

  it('escapes HTML in comments to prevent injection', () => {
    const wrapper = mountWith({ comments: '<script>alert(1)</script>' })
    const html = wrapper.html()
    // Vue escapes by default; raw tags become entities
    expect(html).toContain('&lt;script&gt;alert(1)&lt;/script&gt;')
  })

  it('shows empty state when no renderable content', () => {
    const wrapper = mountWith(null)
    expect(wrapper.text()).toContain('No structured assessment data available.')
  })

  it('mounts within a reasonable time for large datasets (performance sanity)', () => {
    const rows = Array.from({ length: 500 }, (_, i) => ({ id: i + 1, value: `v_${i}` }))
    const big = { items_table: rows }
    const start = performance.now()
    const wrapper = mountWith(big)
    const duration = performance.now() - start
    expect(wrapper.exists()).toBe(true)
    // Generous threshold to avoid flakiness in CI
    expect(duration).toBeLessThan(1500)
  })
})