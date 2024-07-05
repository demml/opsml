import Highcharts from "highcharts";

import addExporting from "highcharts/modules/exporting";
import addExportData from "highcharts/modules/export-data";
import addBoost from "highcharts/modules/boost";
import addAccessibility from "highcharts/modules/accessibility";
import addSeriesLabel from "highcharts/modules/series-label";

import { type Graph } from "$lib/scripts/types";
import { type Metric } from "$lib/scripts/types";

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

function buildBarChart(graph: Graph, height: string | undefined) {
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
      renderTo: chartName,
      height: height,
      backgroundColor: "transparent",
      zooming: {
        type: "xy",
      },
    },
    title: {
      text: name,
      align: "left",
    },
    credits: {
      enabled: false,
    },

    xAxis: {
      type: "category",
      categories: metricNames,
      lineWidth: 1,
    },
    yAxis: {
      min: minyValue,
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
    plotOptions: {
      series: {
        shadow: false,
        borderWidth: 1,
        borderColor: "black",
        animation: false,
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
        showInLegend: false,
        colorByPoint: true,
        data: scores,
        colors: ["#04b78a", "#5e0fb7", "#bdbdbd", "#009adb"],
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

function buildLineChart(graph: Graph, height: string | undefined) {
  const chartName = graph.name;

  const y: Map<string, number[]> = graph.y as Map<string, number[]>;
  const x: Map<string, number[]> = graph.x as Map<string, number[]>;
  const metricNames = [...y.keys()];

  Highcharts.setOptions({
    colors: ["#04b78a", "#5e0fb7", "#bdbdbd", "#009adb"],
  });

  const data: GraphMetric[] = [];
  // iterate over metricsNames

  for (let i = 0; i < metricNames.length; i += 1) {
    const points: number[][] = [];

    const y_data = y.get(metricNames[i]) as number[];
    const x_data = x.get(metricNames[i]) as number[];

    for (let j = 0; j < y_data.length; j += 1) {
      points.push([x_data[j] || 1, y_data[j]]);
    }

    data.push({
      name: metricNames[i],
      data: points,
      marker: {
        enabled: false,
      },
      showInLegend: false,
    });
  }

  Highcharts.chart({
    chart: {
      type: "line",
      renderTo: chartName,
      height: height,
      backgroundColor: "transparent",
      zooming: {
        type: "x",
      },
    },
    credits: {
      enabled: false,
    },
    title: {
      text: chartName,
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
        animation: false,
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

function render_single_chart(
  metrics: Metric[],
  type: string,
  height: string | undefined
) {
  // get metric name from first in list
  const metricName: string = metrics[0].name;

  // create x and y maps for metricName
  const y: Map<string, number[]> = new Map();
  const x: Map<string, number[]> = new Map();

  y.set(metricName, []);
  x.set(metricName, []);

  for (let metric of metrics) {
    const metricName = metric.name;
    y.get(metricName).push(metric.value);
    x.get(metricName).push(metric.step);
  }

  const graph: Graph = {
    name: metricName,
    x_label: "Step",
    y_label: "Value",
    x,
    y,
    graph_style: type,
  };

  if (type === "bar") {
    buildBarChart(graph, height);
  } else if (type === "line") {
    buildLineChart(graph, height);
  }

  metricPlotSettings.set(metric, graph);
}

export {
  buildXyChart,
  buildMultiXyChart,
  buildBarChart,
  buildLineChart,
  render_single_chart,
};
