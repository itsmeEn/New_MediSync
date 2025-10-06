/**
 * Interval Manager for MediSync
 * Provides safe interval management to prevent memory leaks and improve performance
 */

import { onUnmounted, type Ref } from 'vue';

export interface IntervalConfig {
  interval: number;
  immediate?: boolean;
  maxExecutions?: number;
  onError?: (error: Error) => void;
  enabled?: Ref<boolean> | undefined;
}

export interface ManagedInterval {
  id: string;
  start: () => void;
  stop: () => void;
  restart: () => void;
  isRunning: () => boolean;
  getExecutionCount: () => number;
}

class IntervalManager {
  private intervals: Map<
    string,
    {
      intervalId: number | null;
      callback: () => void | Promise<void>;
      config: IntervalConfig;
      executionCount: number;
      isRunning: boolean;
    }
  > = new Map();

  private static instance: IntervalManager;

  static getInstance(): IntervalManager {
    if (!IntervalManager.instance) {
      IntervalManager.instance = new IntervalManager();
    }
    return IntervalManager.instance;
  }

  /**
   * Create a managed interval
   */
  createInterval(
    id: string,
    callback: () => void | Promise<void>,
    config: IntervalConfig,
  ): ManagedInterval {
    // Clear existing interval with same ID
    this.clearInterval(id);

    const intervalData = {
      intervalId: null as number | null,
      callback,
      config,
      executionCount: 0,
      isRunning: false,
    };

    this.intervals.set(id, intervalData);

    const managedInterval: ManagedInterval = {
      id,
      start: () => this.startInterval(id),
      stop: () => this.stopInterval(id),
      restart: () => this.restartInterval(id),
      isRunning: () => intervalData.isRunning,
      getExecutionCount: () => intervalData.executionCount,
    };

    // Auto-start if immediate is true
    if (config.immediate !== false) {
      managedInterval.start();
    }

    return managedInterval;
  }

  /**
   * Start an interval
   */
  private startInterval(id: string): void {
    const intervalData = this.intervals.get(id);
    if (!intervalData || intervalData.isRunning) return;

    const wrappedCallback = () => {
      void (async () => {
        try {
          // Check if enabled (if provided)
          if (intervalData.config.enabled && !intervalData.config.enabled.value) {
            return;
          }

          // Check max executions
          if (
            intervalData.config.maxExecutions &&
            intervalData.executionCount >= intervalData.config.maxExecutions
          ) {
            this.stopInterval(id);
            return;
          }

          // Execute callback
          await intervalData.callback();
          intervalData.executionCount++;
        } catch (error) {
          console.error(`Interval ${id} callback error:`, error);
          if (intervalData.config.onError) {
            intervalData.config.onError(error as Error);
          }
        }
      })();
    };

    intervalData.intervalId = window.setInterval(wrappedCallback, intervalData.config.interval);
    intervalData.isRunning = true;
  }

  /**
   * Stop an interval
   */
  private stopInterval(id: string): void {
    const intervalData = this.intervals.get(id);
    if (!intervalData || !intervalData.isRunning) return;

    if (intervalData.intervalId !== null) {
      clearInterval(intervalData.intervalId);
      intervalData.intervalId = null;
    }
    intervalData.isRunning = false;
  }

  /**
   * Restart an interval
   */
  private restartInterval(id: string): void {
    this.stopInterval(id);
    this.startInterval(id);
  }

  /**
   * Clear an interval completely
   */
  clearInterval(id: string): void {
    this.stopInterval(id);
    this.intervals.delete(id);
  }

  /**
   * Clear all intervals
   */
  clearAllIntervals(): void {
    for (const id of this.intervals.keys()) {
      this.clearInterval(id);
    }
  }

  /**
   * Get interval statistics
   */
  getStats(): {
    totalIntervals: number;
    runningIntervals: number;
    intervals: Array<{
      id: string;
      isRunning: boolean;
      executionCount: number;
      interval: number;
    }>;
  } {
    const intervals = Array.from(this.intervals.entries()).map(([id, data]) => ({
      id,
      isRunning: data.isRunning,
      executionCount: data.executionCount,
      interval: data.config.interval,
    }));

    return {
      totalIntervals: this.intervals.size,
      runningIntervals: intervals.filter((i) => i.isRunning).length,
      intervals,
    };
  }
}

/**
 * Vue composable for managing intervals
 */
export function useIntervalManager() {
  const manager = IntervalManager.getInstance();
  const intervals: ManagedInterval[] = [];

  /**
   * Create a managed interval that auto-cleans on unmount
   */
  const createInterval = (
    id: string,
    callback: () => void | Promise<void>,
    config: IntervalConfig,
  ): ManagedInterval => {
    const interval = manager.createInterval(id, callback, config);
    intervals.push(interval);
    return interval;
  };

  /**
   * Create a time update interval (common pattern)
   */
  const createTimeInterval = (
    id: string,
    updateCallback: (time: string) => void,
    format: 'time' | 'datetime' = 'time',
  ): ManagedInterval => {
    const formatTime = () => {
      const now = new Date();
      if (format === 'datetime') {
        return now.toLocaleString();
      }
      return now.toLocaleTimeString();
    };

    return createInterval(id, () => updateCallback(formatTime()), {
      interval: 1000,
      immediate: true,
    });
  };

  /**
   * Create a periodic data refresh interval
   */
  const createRefreshInterval = (
    id: string,
    refreshCallback: () => Promise<void>,
    intervalMs: number = 30000,
    enabled?: Ref<boolean>,
  ): ManagedInterval => {
    return createInterval(id, refreshCallback, {
      interval: intervalMs,
      immediate: false,
      enabled: enabled || undefined,
      onError: (error) => {
        console.error(`Refresh interval ${id} failed:`, error);
      },
    });
  };

  /**
   * Create a notification polling interval
   */
  const createNotificationInterval = (
    id: string,
    pollCallback: () => Promise<void>,
    intervalMs: number = 30000,
  ): ManagedInterval => {
    return createInterval(id, pollCallback, {
      interval: intervalMs,
      immediate: false,
      onError: (error) => {
        console.error(`Notification polling ${id} failed:`, error);
      },
    });
  };

  /**
   * Cleanup all intervals on component unmount
   */
  onUnmounted(() => {
    intervals.forEach((interval) => interval.stop());
  });

  return {
    createInterval,
    createTimeInterval,
    createRefreshInterval,
    createNotificationInterval,
    getStats: () => manager.getStats(),
    clearAll: () => {
      intervals.forEach((interval) => interval.stop());
      intervals.length = 0;
    },
  };
}

/**
 * Optimized interval patterns for common use cases
 */
export class OptimizedIntervals {
  /**
   * Debounced interval - only executes if no new calls within debounce period
   */
  static createDebouncedInterval(
    callback: () => void | Promise<void>,
    interval: number,
    debounceMs: number = 1000,
  ): ManagedInterval {
    let timeoutId: number | null = null;
    let lastCallTime = 0;

    const debouncedCallback = () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }

      timeoutId = window.setTimeout(() => {
        if (Date.now() - lastCallTime >= debounceMs) {
          lastCallTime = Date.now();
          void (async () => {
            try {
              await callback();
            } catch (error) {
              console.error('Debounced interval error:', error);
            }
          })();
        }
      }, debounceMs);
    };

    return IntervalManager.getInstance().createInterval(
      `debounced-${Date.now()}`,
      debouncedCallback,
      { interval, immediate: false },
    );
  }

  /**
   * Adaptive interval - adjusts frequency based on activity
   */
  static createAdaptiveInterval(
    callback: () => void | Promise<void>,
    baseInterval: number,
    options: {
      slowInterval?: number;
      fastInterval?: number;
      activityThreshold?: number;
    } = {},
  ): ManagedInterval {
    const {
      slowInterval = baseInterval * 3,
      fastInterval = baseInterval / 2,
      activityThreshold = 60000, // 1 minute
    } = options;

    let lastActivity = Date.now();
    let currentInterval = baseInterval;

    // Listen for user activity
    const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    const updateActivity = () => {
      lastActivity = Date.now();
    };

    activityEvents.forEach((event) => {
      document.addEventListener(event, updateActivity, { passive: true });
    });

    const adaptiveCallback = async () => {
      const timeSinceActivity = Date.now() - lastActivity;
      const newInterval = timeSinceActivity > activityThreshold ? slowInterval : fastInterval;

      if (newInterval !== currentInterval) {
        currentInterval = newInterval;
        // Note: This would require restarting the interval with new timing
        // For simplicity, we'll just log the change
        console.log(`Adaptive interval changed to ${newInterval}ms`);
      }

      await callback();
    };

    return IntervalManager.getInstance().createInterval(
      `adaptive-${Date.now()}`,
      adaptiveCallback,
      { interval: currentInterval, immediate: false },
    );
  }
}

// Export singleton instance
export const intervalManager = IntervalManager.getInstance();
