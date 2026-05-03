import type { ChartConfiguration, ChartDataset } from "chart.js";
import { format } from "date-fns";
import { getChartTheme, getTooltip } from "$lib/components/viz/utils";
import type {
  AgentMetricBucket,
  GenAiOperationBreakdown,
  GenAiSpanRecord,
  ModelCostBreakdown,
  ToolTimeBucket,
} from "./types";

// Brutalist palette tied to opsml-theme tokens.
const PALETTE = {
  primary: "rgba(163, 135, 239, 1)",
  primarySoft: "rgba(163, 135, 239, 0.55)",
  secondary: "rgba(95, 214, 141, 1)",
  secondarySoft: "rgba(95, 214, 141, 0.55)",
  tertiary: "rgba(135, 170, 240, 1)",
  tertiarySoft: "rgba(135, 170, 240, 0.55)",
  warning: "rgba(249, 178, 94, 1)",
  warningSoft: "rgba(249, 178, 94, 0.55)",
  error: "rgba(254, 108, 107, 1)",
  errorSoft: "rgba(254, 108, 107, 0.55)",
  success: "rgba(253, 220, 90, 1)",
};

function timeAxis(theme: ReturnType<typeof getChartTheme>) {
  return {
    type: "time" as const,
    time: {
      displayFormats: {
        millisecond: "HH:mm",
        second: "HH:mm",
        minute: "HH:mm",
        hour: "HH:mm",
        day: "MM/dd",
      },
    },
    border: { display: true, width: 2, color: theme.axisColor },
    grid: { display: false, color: theme.gridColor },
    ticks: {
      maxTicksLimit: 8,
      color: theme.textColor,
      font: { size: 11 },
      callback: (v: number | string) => format(new Date(v), "HH:mm"),
    },
  };
}

function valueAxis(
  theme: ReturnType<typeof getChartTheme>,
  label: string,
  stacked = false,
) {
  return {
    stacked,
    border: { display: true, width: 2, color: theme.axisColor },
    grid: { display: true, color: theme.gridColor },
    ticks: {
      maxTicksLimit: 6,
      color: theme.textColor,
      font: { size: 11 },
    },
    title: {
      display: true,
      text: label,
      color: theme.textColor,
      font: { size: 11, weight: "bold" as const },
    },
  };
}

export function buildVolumeChart(
  buckets: AgentMetricBucket[],
): ChartConfiguration {
  const theme = getChartTheme();
  const labels = buckets.map((b) => new Date(b.bucket_start));
  return {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Success",
          data: buckets.map((b) => b.span_count - b.error_count),
          backgroundColor: PALETTE.primarySoft,
          borderColor: PALETTE.primary,
          borderWidth: 1,
          stack: "req",
        },
        {
          label: "Error",
          data: buckets.map((b) => b.error_count),
          backgroundColor: PALETTE.errorSoft,
          borderColor: PALETTE.error,
          borderWidth: 1,
          stack: "req",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: getTooltip(),
        legend: {
          display: true,
          position: "bottom",
          labels: { color: theme.textColor, font: { size: 11 } },
        },
      },
      scales: {
        x: { ...timeAxis(theme), stacked: true },
        y: valueAxis(theme, "requests", true),
      },
    },
  } as ChartConfiguration;
}

export function buildLatencyChart(
  buckets: AgentMetricBucket[],
): ChartConfiguration {
  const theme = getChartTheme();
  const labels = buckets.map((b) => new Date(b.bucket_start));
  return {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "p50",
          data: buckets.map((b) => b.p50_duration_ms ?? 0),
          borderColor: PALETTE.secondary,
          backgroundColor: "transparent",
          pointRadius: 0,
          borderWidth: 2,
          tension: 0.3,
        },
        {
          label: "p95",
          data: buckets.map((b) => b.p95_duration_ms ?? 0),
          borderColor: PALETTE.warning,
          backgroundColor: "transparent",
          pointRadius: 0,
          borderWidth: 2,
          tension: 0.3,
        },
        {
          label: "p99",
          data: buckets.map((b) => b.p99_duration_ms ?? 0),
          borderColor: PALETTE.error,
          backgroundColor: "transparent",
          pointRadius: 0,
          borderWidth: 2,
          tension: 0.3,
        },
      ] as ChartDataset[],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: getTooltip(),
        legend: {
          display: true,
          position: "bottom",
          labels: { color: theme.textColor, font: { size: 11 } },
        },
      },
      scales: {
        x: timeAxis(theme),
        y: valueAxis(theme, "ms"),
      },
    },
  } as ChartConfiguration;
}

export function buildTokenChart(
  buckets: AgentMetricBucket[],
): ChartConfiguration {
  const theme = getChartTheme();
  const labels = buckets.map((b) => new Date(b.bucket_start));
  return {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "input",
          data: buckets.map((b) => b.total_input_tokens),
          borderColor: PALETTE.primary,
          backgroundColor: PALETTE.primarySoft,
          fill: true,
          pointRadius: 0,
          borderWidth: 1.5,
          tension: 0.4,
        },
        {
          label: "output",
          data: buckets.map((b) => b.total_output_tokens),
          borderColor: PALETTE.secondary,
          backgroundColor: PALETTE.secondarySoft,
          fill: true,
          pointRadius: 0,
          borderWidth: 1.5,
          tension: 0.4,
        },
        {
          label: "cache_read",
          data: buckets.map((b) => b.total_cache_read_tokens),
          borderColor: PALETTE.tertiary,
          backgroundColor: PALETTE.tertiarySoft,
          fill: true,
          pointRadius: 0,
          borderWidth: 1.5,
          tension: 0.4,
        },
      ] as ChartDataset[],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: getTooltip(),
        legend: {
          display: true,
          position: "bottom",
          labels: { color: theme.textColor, font: { size: 11 } },
        },
      },
      scales: {
        x: timeAxis(theme),
        y: valueAxis(theme, "tokens", true),
      },
    },
  } as ChartConfiguration;
}

export function buildCostChart(buckets: AgentMetricBucket[]): ChartConfiguration {
  const theme = getChartTheme();
  const labels = buckets.map((b) => new Date(b.bucket_start));
  return {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "spend ($)",
          data: buckets.map((b) => b.total_cost ?? 0),
          backgroundColor: PALETTE.warningSoft,
          borderColor: PALETTE.warning,
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: getTooltip(),
        legend: { display: false },
      },
      scales: {
        x: timeAxis(theme),
        y: valueAxis(theme, "$ / bucket"),
      },
    },
  } as ChartConfiguration;
}

export function buildCostDonut(
  models: ModelCostBreakdown[],
): ChartConfiguration {
  const theme = getChartTheme();
  const colors = [
    PALETTE.primary,
    PALETTE.secondary,
    PALETTE.tertiary,
    PALETTE.warning,
    PALETTE.error,
  ];
  return {
    type: "doughnut",
    data: {
      labels: models.map((m) => m.model),
      datasets: [
        {
          data: models.map((m) => m.total_cost ?? 0),
          backgroundColor: colors.slice(0, models.length),
          borderColor: "rgb(0,0,0)",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "60%",
      plugins: {
        tooltip: getTooltip(),
        legend: {
          display: true,
          position: "right",
          labels: { color: theme.textColor, font: { size: 11 } },
        },
      },
    },
  } as ChartConfiguration;
}

export function buildErrorRateChart(
  buckets: AgentMetricBucket[],
): ChartConfiguration {
  const theme = getChartTheme();
  const labels = buckets.map((b) => new Date(b.bucket_start));
  return {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "error rate",
          data: buckets.map((b) => b.error_rate * 100),
          borderColor: PALETTE.error,
          backgroundColor: PALETTE.errorSoft,
          fill: true,
          pointRadius: 0,
          borderWidth: 2,
          tension: 0.3,
        },
      ] as ChartDataset[],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: getTooltip(),
        legend: { display: false },
      },
      scales: {
        x: timeAxis(theme),
        y: { ...valueAxis(theme, "% errors"), beginAtZero: true },
      },
    },
  } as ChartConfiguration;
}

export function buildTokenMixDonut(
  totalIn: number,
  totalOut: number,
  cacheCreate: number,
  cacheRead: number,
): ChartConfiguration {
  const theme = getChartTheme();
  return {
    type: "doughnut",
    data: {
      labels: ["input", "output", "cache_create", "cache_read"],
      datasets: [
        {
          data: [totalIn, totalOut, cacheCreate, cacheRead],
          backgroundColor: [
            PALETTE.primary,
            PALETTE.secondary,
            PALETTE.tertiary,
            PALETTE.warning,
          ],
          borderColor: "rgb(0,0,0)",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "55%",
      plugins: {
        tooltip: getTooltip(),
        legend: {
          display: true,
          position: "right",
          labels: { color: theme.textColor, font: { size: 10 } },
        },
      },
    },
  } as ChartConfiguration;
}

export function buildOperationBarChart(
  operations: GenAiOperationBreakdown[],
): ChartConfiguration {
  const theme = getChartTheme();
  const sorted = [...operations].sort((a, b) => b.span_count - a.span_count);
  return {
    type: "bar",
    data: {
      labels: sorted.map((o) => o.operation_name),
      datasets: [
        {
          label: "spans",
          data: sorted.map((o) => o.span_count),
          backgroundColor: PALETTE.primarySoft,
          borderColor: PALETTE.primary,
          borderWidth: 1,
        },
      ],
    },
    options: {
      indexAxis: "y" as const,
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: getTooltip(),
        legend: { display: false },
      },
      scales: {
        x: {
          border: { display: true, width: 2, color: theme.axisColor },
          grid: { display: true, color: theme.gridColor },
          ticks: {
            maxTicksLimit: 5,
            color: theme.textColor,
            font: { size: 10 },
          },
        },
        y: {
          border: { display: true, width: 2, color: theme.axisColor },
          grid: { display: false },
          ticks: { color: theme.textColor, font: { size: 10 } },
        },
      },
    },
  } as ChartConfiguration;
}

export function buildSpanDurationBar(
  spans: GenAiSpanRecord[],
): ChartConfiguration {
  const theme = getChartTheme();
  const sorted = [...spans].sort((a, b) => b.duration_ms - a.duration_ms);
  const labels = sorted.map(
    (s) => s.label ?? s.operation_name ?? s.span_id.slice(0, 8),
  );
  return {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "ms",
          data: sorted.map((s) => s.duration_ms),
          backgroundColor: sorted.map((s) =>
            s.error_type ? PALETTE.errorSoft : PALETTE.tertiarySoft,
          ),
          borderColor: sorted.map((s) =>
            s.error_type ? PALETTE.error : PALETTE.tertiary,
          ),
          borderWidth: 1,
        },
      ],
    },
    options: {
      indexAxis: "y" as const,
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: getTooltip(),
        legend: { display: false },
      },
      scales: {
        x: {
          border: { display: true, width: 2, color: theme.axisColor },
          grid: { display: true, color: theme.gridColor },
          ticks: {
            maxTicksLimit: 5,
            color: theme.textColor,
            font: { size: 10 },
          },
          title: {
            display: true,
            text: "ms",
            color: theme.textColor,
            font: { size: 10, weight: "bold" as const },
          },
        },
        y: {
          border: { display: true, width: 2, color: theme.axisColor },
          grid: { display: false },
          ticks: { color: theme.textColor, font: { size: 10 } },
        },
      },
    },
  } as ChartConfiguration;
}

export function buildToolStackChart(
  series: ToolTimeBucket[],
): ChartConfiguration {
  const theme = getChartTheme();
  const tools = Array.from(
    new Set(series.map((s) => s.tool_name ?? "unknown")),
  );
  const palette = [
    PALETTE.primarySoft,
    PALETTE.secondarySoft,
    PALETTE.tertiarySoft,
    PALETTE.warningSoft,
    PALETTE.errorSoft,
  ];
  const borders = [
    PALETTE.primary,
    PALETTE.secondary,
    PALETTE.tertiary,
    PALETTE.warning,
    PALETTE.error,
  ];
  // Pivot
  const byBucket = new Map<string, Map<string, number>>();
  for (const s of series) {
    const key = s.bucket_start;
    if (!byBucket.has(key)) byBucket.set(key, new Map());
    byBucket.get(key)!.set(s.tool_name ?? "unknown", s.call_count);
  }
  const sortedKeys = Array.from(byBucket.keys()).sort();
  const labels = sortedKeys.map((k) => new Date(k));
  const datasets = tools.map((tool, i) => ({
    label: tool,
    data: sortedKeys.map((k) => byBucket.get(k)?.get(tool) ?? 0),
    backgroundColor: palette[i % palette.length],
    borderColor: borders[i % borders.length],
    borderWidth: 1,
    stack: "tools",
  }));
  return {
    type: "bar",
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: getTooltip(),
        legend: {
          display: true,
          position: "bottom",
          labels: { color: theme.textColor, font: { size: 10 } },
        },
      },
      scales: {
        x: { ...timeAxis(theme), stacked: true },
        y: valueAxis(theme, "calls", true),
      },
    },
  } as ChartConfiguration;
}
