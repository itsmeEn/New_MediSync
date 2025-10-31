/// <reference types="vitest" />

// Help the editor resolve '@vue/test-utils' in test files
declare module '@vue/test-utils' {
  export const mount: (...args: unknown[]) => unknown
}