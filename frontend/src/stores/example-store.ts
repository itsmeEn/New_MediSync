import { defineStore, acceptHMRUpdate } from 'pinia';

// Type declaration for HMR
interface ImportMetaHot {
  accept: (callback: (newModule: unknown) => void) => void;
}

declare global {
  interface ImportMeta {
    hot?: ImportMetaHot;
  }
}

export const useCounterStore = defineStore('counter', {
  state: () => ({
    counter: 0,
  }),

  getters: {
    doubleCount: (state) => state.counter * 2,
  },

  actions: {
    increment() {
      this.counter++;
    },
  },
});

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useCounterStore, import.meta.hot));
}
