import type { ChartConfiguration } from "chart.js";
import "chartjs-plugin-zoom";
import { format } from "date-fns";
import {
  generateColors,
  handleResize,
  tooltip,
  type ChartjsLineDataset,
} from "$lib/components/viz/utils";

export function buildTimeChart(
  x: Date[],
  datasets: ChartjsLineDataset[],
  x_label: string,
  y_label: string,
  showLegend: boolean = false
): ChartConfiguration {
  const timeRange =
    x.length > 1 ? Math.abs(x[x.length - 1].getTime() - x[0].getTime()) : 0;
  const dayInMs = 24 * 60 * 60 * 1000;
  const isMultiDay = timeRange > dayInMs;

  const maxY = Math.max(
    ...datasets.flatMap((dataset) =>
      Array.isArray(dataset.data) ? (dataset.data as number[]) : []
    )
  );

  return {
    type: "line",
    data: {
      labels: x,
      datasets,
    },
    options: {
      plugins: {
        tooltip: tooltip,
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
              borderColor: "rgb(	163, 135, 239)",
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
          type: "time",
          border: {
            display: true,
            width: 2,
            color: "rgb(0, 0, 0)", // You can adjust color as needed
          },
          time: {
            displayFormats: {
              millisecond: "HH:mm",
              second: "HH:mm",
              minute: "HH:mm",
              hour: "HH:mm",
              day: "MM/dd HH:mm",
              week: "MM/dd HH:mm",
              month: "MM/dd HH:mm",
              quarter: "MM/dd HH:mm",
              year: "MM/dd HH:mm",
            },
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
            color: "rgb(0,0,0)", // gray-600
            font: {
              size: 14,
            },
          },
          ticks: {
            maxTicksLimit: isMultiDay ? 12 : 25,
            color: "rgb(0,0,0)", // gray-600
            font: {
              size: 12,
            },
            callback: function (value) {
              const date = new Date(value);
              if (isMultiDay) {
                return format(date, "MM/dd HH:mm");
              }
              return format(date, "HH:mm");
            },
          },
        },
        y: {
          suggestedMax: maxY * 1.1,
          title: {
            display: true,
            text: y_label,
            color: "rgb(0,0,0)", // gray-600
            font: {
              size: 14,
            },
          },
          ticks: {
            maxTicksLimit: 10,
            color: "rgb(0,0,0)", // gray-600
            font: {
              size: 12,
            },
          },
          border: {
            display: true,
            width: 2,
            color: "rgb(0, 0, 0)", // You can adjust color as needed
          },
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

export function createTimeSeriesChart(
  x: Date[],
  y: number[],
  label: string,
  y_label: string
): ChartConfiguration {
  const datasets: ChartjsLineDataset[] = [
    {
      label,
      data: y,
      borderColor: generateColors(1)[0],
      backgroundColor: generateColors(1, 0.2)[0],
      pointRadius: 4,
      fill: true,
    },
  ];

  return buildTimeChart(x, datasets, "Time", y_label, false);
}
