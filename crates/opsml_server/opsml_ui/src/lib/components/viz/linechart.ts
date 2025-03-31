import type { ChartConfiguration } from "chart.js";
import "chartjs-plugin-zoom";
import {
  generateColors,
  handleResize,
  type ChartjsLineDataset,
} from "$lib/components/viz/utils";
// ...existing code...

export interface MetricData {
  [metricName: string]: {
    x: number[];
    y: { [experimentName: string]: number[] };
  };
}

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
  metricData: MetricData,
  x_label: string,
  y_label: string
): ChartConfiguration {
  const datasets: ChartjsLineDataset[] = [];

  // For each metric
  Object.entries(metricData).forEach(([metricName, data], metricIndex) => {
    // For each experiment in that metric
    Object.entries(data.y).forEach(([expName, yValues], expIndex) => {
      datasets.push({
        label: `${metricName} - ${expName}`,
        data: yValues,
        borderColor:
          generateColors(1)[
            metricIndex * Object.keys(data.y).length + expIndex
          ],
        backgroundColor: "transparent",
        pointRadius: 4,
        fill: false,
      });
    });
  });

  // Use x values from first metric (assuming all metrics share same x values)
  const xValues = Object.values(metricData)[0].x;

  return buildLineChart(xValues, datasets, x_label, y_label, true);
}
