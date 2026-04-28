import type { ChartConfiguration } from "chart.js";
import { format } from "date-fns";
import { getChartTheme, getCssVar, getTooltip } from "$lib/components/viz/utils";
import type { TraceMetricBucket } from "./types";

export function createStackedTraceCountChart(
  buckets: TraceMetricBucket[],
  startTime?: string,
  endTime?: string,
): ChartConfiguration {
  const labels = buckets.map((bucket) => new Date(bucket.bucket_start));
  const errorCounts = buckets.map((bucket) =>
    Math.round(bucket.trace_count * bucket.error_rate),
  );
  const successCounts = buckets.map((bucket, index) =>
    Math.max(0, bucket.trace_count - errorCounts[index]),
  );

  const theme = getChartTheme();
  const successColor = getCssVar("--chart-trace-success", "rgba(95, 214, 141, 0.85)");
  const errorColor = getCssVar("--chart-trace-error", "rgba(254, 108, 107, 0.9)");

  const isMultiDay = (() => {
    if (labels.length < 2) return false;
    const span = Math.abs(labels[labels.length - 1].getTime() - labels[0].getTime());
    return span > 24 * 60 * 60 * 1000;
  })();

  return {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Success",
          data: successCounts,
          backgroundColor: successColor,
          borderColor: successColor,
          borderWidth: 1,
          stack: "traces",
        },
        {
          label: "Error",
          data: errorCounts,
          backgroundColor: errorColor,
          borderColor: errorColor,
          borderWidth: 1,
          stack: "traces",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: getTooltip(),
        legend: { display: true, position: "bottom" },
      },
      scales: {
        x: {
          stacked: true,
          type: "time",
          min: startTime ? new Date(startTime).getTime() : undefined,
          max: endTime ? new Date(endTime).getTime() : undefined,
          time: {
            displayFormats: {
              minute: "HH:mm",
              hour: "HH:mm",
              day: "MM/dd HH:mm",
            },
          },
          ticks: {
            color: theme.textColor,
            maxTicksLimit: isMultiDay ? 12 : 25,
            callback: (value) => {
              const tickDate = new Date(value as number);
              return isMultiDay
                ? format(tickDate, "MM/dd HH:mm")
                : format(tickDate, "HH:mm");
            },
          },
          grid: { color: theme.gridColor, display: true },
          border: { display: true, width: 2, color: theme.axisColor },
        },
        y: {
          stacked: true,
          beginAtZero: true,
          ticks: { color: theme.textColor, maxTicksLimit: 8 },
          grid: { color: theme.gridColor, display: true },
          border: { display: true, width: 2, color: theme.axisColor },
        },
      },
      layout: { padding: 10 },
    },
  };
}
