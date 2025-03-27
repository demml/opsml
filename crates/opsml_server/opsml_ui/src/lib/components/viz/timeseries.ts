import type { ChartConfiguration } from "chart.js";
import "chartjs-plugin-zoom";

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
    `rgba(54, 162, 235, ${alpha})`, // blue
    `rgba(255, 99, 132, ${alpha})`, // red
    `rgba(75, 192, 192, ${alpha})`, // green
    `rgba(255, 206, 86, ${alpha})`, // yellow
    `rgba(153, 102, 255, ${alpha})`, // purple
    `rgba(255, 159, 64, ${alpha})`, // orange
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
              borderColor: "rgb(54, 162, 235)",
              borderWidth: 1,
              backgroundColor: "rgba(54, 162, 235, 0.3)",
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
          time: {
            displayFormats: {
              hour: "HH:mm",
              minute: "HH:mm",
              second: "HH:mm:ss",
            },
          },
          title: { display: true, text: x_label },
          ticks: {
            maxTicksLimit: 30,
          },
        },
        y: {
          title: { display: true, text: y_label },
          ticks: {
            maxTicksLimit: 30,
          },
          grace: "0%",
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
      pointRadius: 2,
      fill: true,
    },
  ];

  return buildTimeChart(x, datasets, "Time", y_label, false);
}
