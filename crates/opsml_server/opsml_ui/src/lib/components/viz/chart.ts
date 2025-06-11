import type { ChartConfiguration } from "chart.js";
import "chartjs-plugin-zoom";
import {
  generateColors,
  handleResize,
  type ChartjsLineDataset,
  type ChartjsBarDataset,
} from "$lib/components/viz/utils";
import type { GroupedMetrics } from "../card/experiment/types";
import { buildTimeChart } from "./timeseries";

export function buildChart(
  x: string[] | number[],
  datasets: (ChartjsLineDataset | ChartjsBarDataset)[],
  x_label: string,
  y_label: string,
  showLegend: boolean = false,
  chartType: "line" | "bar" = "line"
): ChartConfiguration {
  const baseConfig = {
    //@ts-ignore
    type: chartType,
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
            size: 14,
          },
          bodyColor: "rgb(0, 0, 0)",
          bodyFont: {
            size: 12,
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
              size: 12, // Increase legend font size (in pixels)
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
          type: chartType === "bar" ? "category" : "linear",
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
              size: 14,
            },
          },
          ticks: {
            maxTicksLimit: 10,
            color: "rgb(0,0,0)",
            font: {
              size: 12,
            },
          },
        },
        y: {
          title: {
            display: true,
            text: y_label,
            color: "rgb(0,0,0)",
            font: {
              size: 14,
            },
          },
          ticks: {
            maxTicksLimit: 10,
            color: "rgb(0,0,0)",
            font: {
              size: 12,
            },
          },
          border: {
            display: true,
            width: 2,
            color: "rgb(0, 0, 0)",
          },
          grace: "10%",
          padding: { top: 10 },
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

  return baseConfig as ChartConfiguration;
}

export function createLineChart(
  metricData: GroupedMetrics,
  y_label: string
): ChartConfiguration {
  const datasets: ChartjsLineDataset[] = [];

  const uniqueVersions = new Set(
    Object.values(metricData)
      .flat()
      .map((metric) => metric.version)
  );

  // Generate colors based on number of unique experiments
  const colors = generateColors(uniqueVersions.size, 1.0);

  // Create version to color index mapping
  const versionColorMap = new Map(
    Array.from(uniqueVersions).map((version, index) => [version, index])
  );

  // For each metric name
  Object.entries(metricData).forEach(([metricName, groupedMetrics]) => {
    // For each experiment's grouped metrics
    groupedMetrics.forEach((metric) => {
      const colorIndex = versionColorMap.get(metric.version) ?? 0;

      datasets.push({
        label: `${metricName} - ${metric.version}`,
        data: Array.from(metric.value),
        borderColor: colors[colorIndex],
        backgroundColor: "transparent",
        pointRadius: 2,
        fill: false,
        //@ts-ignore
        tension: 0.4,
      });
    });
  });

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
  return buildChart(xValues, datasets, effectiveXLabel, y_label, true);
}

export function createGroupedBarChart(
  metricData: GroupedMetrics,
  y_label: string
): ChartConfiguration {
  const datasets: ChartjsBarDataset[] = [];
  const metricNames = Object.keys(metricData);

  const uniqueVersions = new Set(
    Object.values(metricData)
      .flat()
      .map((metric) => metric.version)
  );

  const borderColors = generateColors(uniqueVersions.size, 1.0);
  const backgroundColors = generateColors(uniqueVersions.size, 0.5);

  const versionColorMap = new Map(
    Array.from(uniqueVersions).map((version, index) => [version, index])
  );

  // For each metric name
  Array.from(uniqueVersions).forEach((version) => {
    const values: number[] = [];

    // For each metric, find the value for this version
    metricNames.forEach((metricName) => {
      const metric = metricData[metricName].find((m) => m.version === version);
      const value = metric ? Array.from(metric.value).pop() ?? 0 : 0;
      values.push(value);
    });

    const colorIndex = versionColorMap.get(version) ?? 0;

    datasets.push({
      label: version,
      data: values,
      backgroundColor: backgroundColors[colorIndex],
      borderColor: borderColors[colorIndex],
      borderWidth: 2,
    });
  });

  return buildChart(metricNames, datasets, "Experiments", y_label, true, "bar");
}

export function createBarChart(
  x: string[] | number[],
  y: number[],
  label: string,
  x_label: string,
  y_label: string
): ChartConfiguration {
  const datasets: ChartjsBarDataset[] = [
    {
      label,
      data: y,
      borderColor: generateColors(1)[0],
      backgroundColor: generateColors(1, 0.2)[0],
      borderWidth: 2,
    },
  ];

  return buildChart(x, datasets, x_label, y_label, true, "bar");
}
