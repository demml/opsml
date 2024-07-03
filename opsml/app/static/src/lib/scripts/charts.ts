import Highcharts from "highcharts";

import addExporting from "highcharts/modules/exporting";
import addExportData from "highcharts/modules/export-data";
import addBoost from "highcharts/modules/boost";
import addAccessibility from "highcharts/modules/accessibility";
import addSeriesLabel from "highcharts/modules/series-label";

import { type Graph } from "$lib/scripts/types";

addExporting(Highcharts);
addExportData(Highcharts);
addBoost(Highcharts);
addAccessibility(Highcharts);
addSeriesLabel(Highcharts);

Highcharts.setOptions({
  colors: [
    "#04b78a",
    "#5e0fb7",
    "#bdbdbd",
    "#009adb",
    "#e74c3c",
    "#e73c3c",
    "#f2cc35",
  ],
});

function getToolTip(graphStyle: string) {
  let tooltip;
  if (graphStyle === "line") {
    tooltip = {
      valueDecimals: 2,
      shared: true,
      split: true,
      crosshairs: true,
    };
  } else if (graphStyle === "scatter") {
    tooltip = {
      pointFormat: "{point.y}",
      shared: true,
      split: true,
      valueDecimals: 2,
      crosshairs: true,
    };
  }
  return tooltip;
}

function getPlotOptions(graphStyle: string) {
  let PlotOptions;

  if (graphStyle === "line") {
    PlotOptions = {
      series: {
        states: {
          inactive: {
            opacity: 1,
          },
        },
        lineWidth: 3,
        animation: false,
        marker: {
          enabled: false,
        },
      },
    };
  } else if (graphStyle === "scatter") {
    PlotOptions = {
      series: {
        states: {
          inactive: {
            opacity: 1,
          },
        },
        marker: {
          enabled: true,
          radius: 3,
        },
        animation: false,
      },
    };
  }

  return PlotOptions;
}

function buildXyChart(graph: Graph) {
  const { name } = graph;
  const xLabel = graph.x_label;
  const yLabel = graph.y_label;
  const { x } = graph;
  const { y } = graph;
  const chartName = `graph_${name}`;
  const graphStyle = graph.graph_style;
  const plotOptions = getPlotOptions(graphStyle);
  const toolTip = getToolTip(graphStyle);

  Highcharts.chart({
    chart: {
      type: graphStyle,
      borderColor: "#390772",
      borderWidth: 2,
      shadow: true,
      renderTo: chartName,
      zooming: {
        type: "xy",
      },
    },
    title: {
      text: name,
      align: "left",
    },

    xAxis: {
      labels: {
        format: "{value:.1f}",
        // @ts-expect-error: skipping
        tickInterval: 5,
      },
      categories: x,
      allowDecimals: false,
      title: {
        text: xLabel,
      },
      lineWidth: 1,
    },

    yAxis: {
      labels: {
        format: "{value:.1f}",
        step: 1,
      },
      title: {
        text: yLabel,
      },
      lineWidth: 1,
      tickLength: 10,
      tickWidth: 1,
    },

    // @ts-expect-error: skipping
    series: [{ data: y }],
    plotOptions,
    tooltip: toolTip,
    credits: {
      enabled: false,
    },
  });
}

function getYSeries(yKeys, y) {
  const ySeries: { name: string; data: number[] }[] = [];
  for (let i = 0; i < yKeys.length; i += 1) {
    ySeries.push({
      name: yKeys[i],
      data: y[yKeys[i]],
    });
  }
  return ySeries;
}

function buildMultiXyChart(graph: Graph) {
  const { name } = graph;
  const xLabel = graph.x_label;
  const yLabel = graph.y_label;
  const { x } = graph;
  const { y } = graph;
  const yKeys = Object.keys(y);
  const chartName = `graph_${name}`;
  const ySeries = getYSeries(yKeys, y) as Highcharts.SeriesOptionsType[];
  const graphStyle = graph.graph_style;
  const plotOptions = getPlotOptions(graphStyle);
  const toolTip = getToolTip(graphStyle);

  Highcharts.chart({
    chart: {
      type: graphStyle,
      borderColor: "#390772",
      borderWidth: 2,
      shadow: true,
      renderTo: chartName,
      zooming: {
        type: "xy",
      },
    },
    title: {
      text: name,
      align: "left",
    },

    xAxis: {
      labels: {
        format: "{value:.1f}",

        // @ts-expect-error: skipping
        tickInterval: 5,
      },

      categories: x,
      allowDecimals: true,
      title: {
        text: xLabel,
      },
      lineWidth: 1,
    },

    yAxis: {
      labels: {
        format: "{value:.1f}",
        step: 1,
      },
      title: {
        text: yLabel,
      },
      lineWidth: 1,
      tickLength: 10,
      tickWidth: 1,
    },

    series: ySeries,
    plotOptions,
    tooltip: toolTip,
    credits: {
      enabled: false,
    },

    legend: {
      align: "left",
      verticalAlign: "top",
      borderWidth: 0,
    },
  });
}

function buildBarChart(graph: Graph) {
  const { name } = graph;
  const y: Map<string, number[]> = graph.y as Map<string, number[]>;
  const metricNames = [...y.keys()];
  const chartName = name;

  Highcharts.setOptions({
    colors: ["#04b78a", "#5e0fb7", "#bdbdbd", "#009adb"],
  });

  const scores: number[] = [];

  metricNames.forEach((metricName) => {
    const data = y.get(metricName) as number[];
    scores.push(data[data.length - 1]);
  });

  // get min and max values for y axis across all metrics
  // if min is greater than 0 set to 0
  // add padding to max
  const minyValue = Math.min(Math.min(...scores), 0);

  Highcharts.chart({
    chart: {
      type: "column",
      borderColor: "#390772",
      borderWidth: 2,
      shadow: true,
      renderTo: chartName,
      zooming: {
        type: "xy",
      },
    },
    title: {
      text: `Metrics for ${name}`,
      align: "left",
    },

    xAxis: {
      type: "category",
      categories: metricNames,
      lineWidth: 1,
    },
    yAxis: {
      min: minyValue,
      title: {
        text: "Metric Value)",
      },
      lineWidth: 1,
      tickLength: 10,
      tickWidth: 1,
    },
    legend: {
      enabled: true,
    },
    plotOptions: {
      series: {
        borderWidth: 1,
        borderColor: "black",
        states: {
          inactive: {
            opacity: 1,
          },
        },
        lineWidth: 3,
      },
    },
    series: [
      {
        name: "Metrics",
        colorByPoint: true,
        data: scores,
        colors: ["#04b78a", "#5e0fb7", "#bdbdbd", "#009adb"],
        pointPadding: 0,
        type: "column",
      },
    ],
  });
}

interface GraphMetric {
  name: string;
  data: number[][];
  marker: {
    enabled: boolean;
  };
}

function buildLineChart(name, metrics) {
  Highcharts.setOptions({
    colors: ["#04b78a", "#5e0fb7", "#bdbdbd", "#009adb"],
  });

  const metricNames = Object.keys(metrics);

  const data: GraphMetric[] = [];
  // iterate over metricsNames
  for (let i = 0; i < metricNames.length; i += 1) {
    const points: number[][] = [];
    const { y } = metrics[metricNames[i]];
    const { x } = metrics[metricNames[i]];

    for (let j = 0; j < x.length; j += 1) {
      points.push([x[j] || 1, y[j]]);
    }

    data.push({
      name: metricNames[i],
      data: points,
      marker: {
        enabled: false,
      },
    });
  }

  Highcharts.chart({
    chart: {
      type: "line",
      height: `${(9 / 16) * 90}%`,
      renderTo: "MetricChart",
      zooming: {
        type: "x",
      },
    },
    title: {
      text: `Metrics for ${name}`,
      align: "left",
    },

    xAxis: {
      type: "category",
      title: {
        text: "Step",
      },
      lineWidth: 1,
    },
    yAxis: {
      title: {
        text: "Value",
      },
      lineWidth: 1,
      tickLength: 10,
      tickWidth: 1,
    },
    legend: {
      enabled: true,
    },

    series: data as Highcharts.SeriesOptionsType[],
    plotOptions: {
      series: {
        states: {
          inactive: {
            opacity: 1,
          },
        },
        lineWidth: 3,
      },
    },
  });
}

export { buildXyChart, buildMultiXyChart, buildBarChart, buildLineChart };
