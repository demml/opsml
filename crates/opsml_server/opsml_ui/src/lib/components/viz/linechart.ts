import type { ChartConfiguration } from "chart.js";
import "chartjs-plugin-zoom";
import {
  generateColors,
  handleResize,
  type ChartjsLineDataset,
} from "$lib/components/viz/utils";
import type { GroupedMetrics } from "../card/experiment/types";
import { buildTimeChart } from "./timeseries";

export function buildLineChart(
  x: number[],
  datasets: ChartjsLineDataset[],
  x_label: string,
  y_label: string,
  showLegend: boolean = false
): ChartConfiguration {
  return {
    type: "line",
    data: {
      labels: x,
      datasets,
    },
    options: {
      plugins: {
        tooltip: {
          cornerRadius: 1,
          backgroundColor: "rgba(255, 255, 255, 1)",
          borderColor: "rgb(0, 0, 0)",
          borderWidth: 1,
          enabled: true,
          titleColor: "rgb(0, 0, 0)",
          titleFont: {
            size: 16,
          },
          bodyColor: "rgb(0, 0, 0)",
          bodyFont: {
            size: 16,
          },
        },
        //@ts-ignore
        zoom: {
          pan: {
            enabled: true,
            mode: "xy",
            modifierKey: "ctrl",
          },
          zoom: {
            mode: "xy",
            drag: {
              enabled: true,
              borderColor: "rgb(163, 135, 239)",
              borderWidth: 1,
              backgroundColor: "rgba(163, 135, 239, 0.3)",
            },
          },
        },
        legend: {
          display: showLegend,
          position: "bottom",
          labels: {
            font: {
              size: 16, // Increase legend font size (in pixels)
            },
            color: "rgb(0, 0, 0)",
          },
        },
      },

      responsive: true,
      onResize: handleResize,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: "linear",
          border: {
            display: true,
            width: 2,
            color: "rgb(0, 0, 0)",
          },
          grid: {
            display: true,
            color: "rgba(0, 0, 0, 0.1)",
            tickLength: 8,
            drawTicks: true,
          },
          title: {
            display: true,
            text: x_label,
            color: "rgb(0,0,0)",
            font: {
              size: 16,
            },
          },
          ticks: {
            maxTicksLimit: 10,
            color: "rgb(0,0,0)",
            font: {
              size: 14,
            },
          },
        },
        y: {
          title: {
            display: true,
            text: y_label,
            color: "rgb(0,0,0)",
            font: {
              size: 16,
            },
          },
          ticks: {
            maxTicksLimit: 10,
            color: "rgb(0,0,0)",
            font: {
              size: 14,
            },
          },
          border: {
            display: true,
            width: 2,
            color: "rgb(0, 0, 0)",
          },
          grace: "0%",
          grid: {
            display: true,
            color: "rgba(0, 0, 0, 0.1)",
            tickLength: 8,
            drawTicks: true,
          },
        },
      },
      layout: {
        padding: 10,
      },
    },
  };
}

export function createLineChart(
  metricData: GroupedMetrics,
  y_label: string
): ChartConfiguration {
  const datasets: ChartjsLineDataset[] = [];
  let totalExperiments = 0;

  // For each metric name
  Object.entries(metricData).forEach(
    ([metricName, groupedMetrics], metricIndex) => {
      // For each experiment's grouped metrics
      groupedMetrics.forEach((metric, experimentIndex) => {
        const colorIndex = totalExperiments + experimentIndex;
        const color = generateColors(1)[colorIndex];

        datasets.push({
          label: `${metricName} - ${metric.version}`,
          data: Array.from(metric.value),
          borderColor: color,
          backgroundColor: "transparent",
          pointRadius: 2,
          fill: false,

          //@ts-ignore
          tension: 0.4,
        });
      });

      totalExperiments += groupedMetrics.length;
    }
  );

  // Get first non-empty metric data for x-axis values
  const firstMetric = Object.values(metricData)[0]?.[0];

  // Try steps first, then timestamp, then fallback to array indices
  const xValues = Array.from(
    firstMetric?.step ??
      firstMetric?.timestamp ??
      Array.from({ length: firstMetric?.value.length ?? 0 }, (_, i) => i)
  );

  // Adjust x-axis label based on what we're using
  const effectiveXLabel = firstMetric?.step
    ? "Step"
    : firstMetric?.timestamp
    ? "Time"
    : "Index";

  // Build the line chart configuration if effectiveXLabel is Time
  if (effectiveXLabel === "Time") {
    const xAsDate = xValues.map((x) => new Date(x));
    return buildTimeChart(xAsDate, datasets, effectiveXLabel, y_label, true);
  }
  return buildLineChart(xValues, datasets, effectiveXLabel, y_label, true);
}
