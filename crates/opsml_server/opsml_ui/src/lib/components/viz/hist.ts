import type { Histogram } from "../card/data/types";
import type { ChartConfiguration } from "chart.js";
import { generateColors } from "./utils";
import { getPlugins } from "./utils";
import { handleResize } from "./utils";

export function createHistogramViz(data: Histogram): ChartConfiguration {
  const datasets = [
    {
      backgroundColor: generateColors(1, 0.2)[0],
      borderColor: generateColors(1)[0],
      borderWidth: 2,
      data: Array.from(data.bin_counts),
    },
  ];

  const labels = Array.from(data.bins).map((bin) => bin.toFixed(2));

  const baseConfig = {
    type: "bar",
    data: {
      labels,
      datasets,
    },
    options: {
      plugins: getPlugins(false),
      responsive: true,
      //onresize: handleResize,
      maintainAspectRatio: false,
      scales: {
        x: {
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
            text: "Bins",
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
            text: "Count",
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
    },
    layout: {
      padding: 10,
    },
  };

  return baseConfig as ChartConfiguration;
}
