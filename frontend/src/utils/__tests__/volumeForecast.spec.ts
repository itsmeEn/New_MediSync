import { describe, it, expect } from 'vitest';
import { buildVolumeForecastChart } from '../../utils/volumeForecast';
import type { ForecastPoint } from '../../utils/volumeForecast';

describe('buildVolumeForecastChart', () => {
  it('returns two datasets over exactly three months', () => {
    const src: ForecastPoint[] = [
      { date: '2025-11-01', predicted_volume: 100, actual_volume: 90 },
      { date: '2025-12-01', predicted_volume: 120, actual_volume: 115 },
      { date: '2026-01-01', predicted_volume: 150 },
    ];

    const chart = buildVolumeForecastChart(src);
    expect(chart.labels.length).toBe(3);
    expect(chart.datasets.length).toBe(2);
    const labels = chart.datasets.map((d) => d.label);
    expect(labels).toContain('Predicted Volume');
    expect(labels).toContain('Actual Volume');
  });
});