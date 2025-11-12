// Shared utilities for building monthly patient volume charts
// Refactored to a fixed 3‑month window with separate actual and predicted series

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

export function buildVolumeForecastChart(data: ForecastPoint[]) {
  const { labels, predValues, actualValues } = groupMonthly(data || []);

  // Limit to exactly 3 months, showing the latest 3 available
  const lastThreeLabels = labels.slice(-3);
  const startIndex = Math.max(labels.length - 3, 0);
  const pred3 = predValues.slice(startIndex);
  const actual3 = actualValues.slice(startIndex);

  // Colors to match reference (Predicted: blue with area fill, Actual: green)
  const COLOR_PRED_LINE = '#1976d2';
  const COLOR_PRED_FILL = 'rgba(33, 150, 243, 0.15)';
  const COLOR_ACTUAL_LINE = '#2e7d32';
  const COLOR_ACTUAL_FILL = 'rgba(76, 175, 80, 0.10)';

  return {
    labels: lastThreeLabels,
    datasets: [
      {
        label: 'Predicted Volume',
        data: pred3,
        borderColor: COLOR_PRED_LINE,
        backgroundColor: COLOR_PRED_FILL,
        tension: 0.25,
        fill: 'origin',
        pointRadius: 4,
        pointHoverRadius: 5,
        borderWidth: 2,
      },
      {
        label: 'Actual Volume',
        data: actual3,
        borderColor: COLOR_ACTUAL_LINE,
        backgroundColor: COLOR_ACTUAL_FILL,
        tension: 0.25,
        pointRadius: 4,
        pointHoverRadius: 5,
        borderWidth: 2,
        spanGaps: true,
      },
    ],
  };
}