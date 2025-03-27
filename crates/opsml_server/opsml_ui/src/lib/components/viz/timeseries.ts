import type { ChartConfiguration } from "chart.js";
import "chartjs-plugin-zoom";
import { format } from "date-fns";

interface ChartjsLineDataset {
  label: string;
  data: number[];
  borderColor: string;
  backgroundColor: string;
  pointRadius: number;
  fill: boolean;
}

// Generate an array of colors with optional alpha
function generateColors(count: number, alpha: number = 1): string[] {
  const colors = [
    `rgba(163, 135, 239, ${alpha})`, // primary-500
    `rgba(95, 214, 141, ${alpha})`, // secondary-500
    `rgba(135, 170, 240, ${alpha})`, // tertiary-500
    `rgba(253, 220, 90, ${alpha})`, // success-500
    `rgba(249, 178, 94, ${alpha})`, // warning-500
    `rgba(254, 108, 107, ${alpha})`, // error-500
  ];

  return Array(count)
    .fill(null)
    .map((_, i) => colors[i % colors.length]);
}

function handleResize(chart: any) {
  if (chart.canvas) {
    chart.resize();
  }
}

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
              size: 16,
            },
          },
          ticks: {
            maxTicksLimit: isMultiDay ? 12 : 25,
            color: "rgb(0,0,0)", // gray-600
            font: {
              size: 14,
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
          title: {
            display: true,
            text: y_label,
            color: "rgb(0,0,0)", // gray-600
            font: {
              size: 16,
            },
          },
          ticks: {
            maxTicksLimit: 10,
            color: "rgb(0,0,0)", // gray-600
            font: {
              size: 14,
            },
          },
          border: {
            display: true,
            width: 2,
            color: "rgb(0, 0, 0)", // You can adjust color as needed
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
