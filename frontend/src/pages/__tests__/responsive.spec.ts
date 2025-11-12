import { describe, it, expect, beforeEach } from 'vitest'
import fs from 'fs'
import path from 'path'
import { setViewportHeightVar, useResponsive, BREAKPOINTS } from '../../utils/responsive'
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'

describe('Responsive utilities and meta tags', () => {
  it('index.html has accessible viewport meta with viewport-fit=cover', () => {
    const htmlPath = path.resolve(__dirname, '../../../index.html')
    const html = fs.readFileSync(htmlPath, 'utf-8')
    expect(html).toMatch(/name="viewport"/)
    expect(html).toMatch(/width=device-width, initial-scale=1, viewport-fit=cover/)
    expect(html).not.toMatch(/user-scalable=no/)
  })

  it('setViewportHeightVar sets --vh CSS variable', () => {
    const original = window.innerHeight
    // Simulate a mobile-like viewport height
    Object.defineProperty(window, 'innerHeight', { value: 900, configurable: true })
    setViewportHeightVar()
    const val = getComputedStyle(document.documentElement).getPropertyValue('--vh').trim()
    expect(val).toBe(`${900 * 0.01}px`)
    // restore
    Object.defineProperty(window, 'innerHeight', { value: original, configurable: true })
  })

  describe('useResponsive()', () => {
    beforeEach(() => {
      // default to desktop size
      Object.defineProperty(window, 'innerWidth', { value: 1024, configurable: true })
    })

    it('reports mobile flags correctly at xs/sm/md breakpoints', async () => {
      const Comp = defineComponent({
        setup() {
          const r = useResponsive()
          return { r }
        },
        template: '<div />',
      })
      const wrapper = mount(Comp)
      // Start desktop
      expect(wrapper.vm.r.isXs()).toBe(false)
      expect(wrapper.vm.r.isSm()).toBe(false)

      // Set to small width and trigger update
      Object.defineProperty(window, 'innerWidth', { value: BREAKPOINTS.sm, configurable: true })
      window.dispatchEvent(new Event('resize'))
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.r.isXs()).toBe(true)
      expect(wrapper.vm.r.isSm()).toBe(true)

      // Set to md and verify
      Object.defineProperty(window, 'innerWidth', { value: BREAKPOINTS.md, configurable: true })
      window.dispatchEvent(new Event('resize'))
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.r.isXs()).toBe(false)
      expect(wrapper.vm.r.isSm()).toBe(true)
    })
  })
})