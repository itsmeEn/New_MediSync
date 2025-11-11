// Shared utilities for building monthly patient volume charts with 3-month forecasts
// Consistent data model across DoctorPredictiveAnalytics.vue and NurseAnalytics.vue

export interface ForecastPoint {
  date: string; // ISO date string (YYYY-MM-DD)
  predicted_volume: number;
  actual_volume?: number;
}

function formatMonthLabel(dateStr: string): string {
  const d = new Date(dateStr);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}`;
}

function addMonths(base: Date, months: number): Date {
  const d = new Date(base);
  d.setMonth(d.getMonth() + months);
  return d;
}

function nextMonthLabel(lastLabel: string): string {
  const parts = lastLabel.split('-');
  const yPart = Number(parts[0]);
  const mPart = Number(parts[1]);
  const y = Number.isFinite(yPart) ? yPart : new Date().getFullYear();
  const m = Number.isFinite(mPart) ? mPart : new Date().getMonth() + 1;
  const base = new Date(y, m - 1, 1);
  const next = addMonths(base, 1);
  const ny = next.getFullYear();
  const nm = String(next.getMonth() + 1).padStart(2, '0');
  return `${ny}-${nm}`;
}

// Group daily entries into monthly totals
export function groupMonthly(
  data: ForecastPoint[],
): { labels: string[]; predValues: number[]; actualValues: Array<number | null> } {
  const monthlyPred: Record<string, number> = {};
  const monthlyActual: Record<string, number> = {};

  for (const item of data || []) {
    if (!item || !item.date) continue;
    const label = formatMonthLabel(item.date);
    const pv = Number(item.predicted_volume || 0) || 0;
    const av = typeof item.actual_volume === 'number' ? Number(item.actual_volume) || 0 : null;
    monthlyPred[label] = (monthlyPred[label] || 0) + pv;
    if (av != null) monthlyActual[label] = (monthlyActual[label] || 0) + av;
  }

  const labels = Object.keys(monthlyPred).sort();
  const predValues = labels.map((l) => monthlyPred[l] || 0);
  const actualValues = labels.map((l) => (l in monthlyActual ? monthlyActual[l] || 0 : null));

  return { labels, predValues, actualValues };
}

// Simple linear regression y = a + b*x for forecasting
function linearRegressionForecast(values: number[], periods: number): number[] {
  const n = values.length;
  if (n === 0) return Array(periods).fill(0);
  if (n === 1) return Array(periods).fill(values[0]);

  // x indices: 0..n-1
  const xs = Array.from({ length: n }, (_, i) => i);
  const sumX = xs.reduce((s, x) => s + x, 0);
  const sumY = values.reduce((s, y) => s + y, 0);
  // Guard against mismatched lengths or undefined indexes
  const sumXY = xs.reduce((s, x, i) => s + x * (values[i] ?? 0), 0);
  const sumXX = xs.reduce((s, x) => s + x * x, 0);
  const denom = n * sumXX - sumX * sumX;
  const b = denom !== 0 ? (n * sumXY - sumX * sumY) / denom : 0;
  const a = (sumY - b * sumX) / n;

  const forecasts: number[] = [];
  for (let k = 1; k <= periods; k++) {
    const x = n - 1 + k; // next indices
    const y = a + b * x;
    forecasts.push(Math.max(0, Math.round(y)));
  }
  return forecasts;
}

export function buildVolumeForecastChart(data: ForecastPoint[]) {
  const { labels, predValues, actualValues } = groupMonthly(data || []);

  // Forecast next 3 months based on predicted monthly totals
  const forecastNext3 = linearRegressionForecast(predValues, 3);
  const forecastLabels: string[] = [];
  const lastSeed = labels.length ? labels[labels.length - 1] : undefined;
  let last: string =
    typeof lastSeed === 'string' ? lastSeed : formatMonthLabel(new Date().toISOString());
  for (let i = 0; i < 3; i++) {
    last = nextMonthLabel(last);
    forecastLabels.push(last);
  }

  const combinedLabels = [...labels, ...forecastLabels];
  const predCombined = [...predValues, ...forecastNext3];
  const actualCombined = [...actualValues, ...Array(3).fill(null)];

  // Colors (consistent across components)
  const COLOR_PRED = '#9c27b0';
  const COLOR_PRED_BORDER = '#7b1fa2';
  const COLOR_ACTUAL = '#2196f3';
  const COLOR_ACTUAL_BORDER = '#1976d2';

  // Split datasets: historical predicted, forecasted predicted, and actual
  const historicalLength = labels.length;
  const predictedHistorical = predCombined.map((v, idx) => (idx < historicalLength ? v : null));
  const predictedForecast = predCombined.map((v, idx) => (idx >= historicalLength ? v : null));

  return {
    labels: combinedLabels,
    datasets: [
      {
        label: 'Actual Volume',
        data: actualCombined,
        borderColor: COLOR_ACTUAL_BORDER,
        backgroundColor: COLOR_ACTUAL,
        tension: 0.25,
        spanGaps: true,
        pointRadius: 3,
      },
      {
        label: 'Predicted Volume',
        data: predictedHistorical,
        borderColor: COLOR_PRED_BORDER,
        backgroundColor: COLOR_PRED,
        tension: 0.25,
        spanGaps: true,
        pointRadius: 3,
      },
      {
        label: 'Forecast (Next 3 Months)',
        data: predictedForecast,
        borderColor: COLOR_PRED_BORDER,
        backgroundColor: COLOR_PRED,
        tension: 0.25,
        spanGaps: true,
        pointRadius: 3,
        borderDash: [6, 4],
      },
    ],
  };
}