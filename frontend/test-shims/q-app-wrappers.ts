// Minimal shim for Quasar app wrappers used during unit tests
// It allows modules importing "#q-app/wrappers" to be transformed without pulling Quasar runtime.
export const defineBoot = <T extends (...args: any[]) => any>(bootFn: T): T => {
  return bootFn
}

export default { defineBoot }