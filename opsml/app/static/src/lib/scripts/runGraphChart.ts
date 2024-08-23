import {
  type RunGraph,
  type ChartjsLineDataset,
  type ChartjsData,
  type ChartjsScatterDataset,
  type ScatterData,
} from "$lib/scripts/types";
import { generateColors, buildDataforChart } from "$lib/scripts/utils";

export function createLineChart(graph: RunGraph): ChartjsData {
  const colors = generateColors(2);
  const datasets: ChartjsLineDataset[] = [];

  datasets.push({
    label: graph.name,
    data: graph.y as number[],
    borderColor: colors[0],
    backgroundColor: colors[0],
    pointRadius: 1,
  });

  return buildDataforChart(
    graph.x,
    datasets,
    graph.x_label,
    graph.y_label,
    graph.graph_style
  );
}

export function createGroupedLineChart(graph: RunGraph): ChartjsData {
  const datasets: ChartjsLineDataset[] = [];

  const y = graph.y as Map<string, number[]>;
  const borders = generateColors(y.size + 1);

  Array.from(y).forEach(([key, value], index) => {
    const borderColor = borders[index + 1];

    datasets.push({
      label: key,
      data: value,
      borderColor,
      backgroundColor: borderColor,
      pointRadius: 1,
    });
  });

  return buildDataforChart(
    graph.x,
    datasets,
    graph.x_label,
    graph.y_label,
    graph.graph_style,
    true
  );
}

export function createMultiScatterChart(graph: RunGraph): ChartjsData {
  const datasets: ChartjsScatterDataset[] = [];
  const y = graph.y as Map<string, number[]>;
  const colors = generateColors(y.size + 1);

  Array.from(y).forEach(([key, value], index) => {
    const borderColor = colors[index + 1];

    // iterate over x and y values
    const data: ScatterData[] = [];

    for (let i = 0; i < graph.x.length; i++) {
      data.push({ x: graph.x[i], y: value[i] });
    }

    datasets.push({
      label: key,
      data: data,
      borderColor,
      backgroundColor: borderColor,
      pointRadius: 1,
    });
  });

  return buildDataforChart(
    graph.x,
    datasets,
    graph.x_label,
    graph.y_label,
    graph.graph_style,
    true
  );
}

export function createScatterChart(graph: RunGraph): ChartjsData {
  const datasets: ChartjsScatterDataset[] = [];
  const colors = generateColors(2);
  const data: ScatterData[] = [];
  const y = graph.y as number[];

  for (let i = 0; i < graph.x.length; i++) {
    data.push({ x: graph.x[i], y: y[i] });
  }

  datasets.push({
    label: graph.name,
    data: data,
    borderColor: colors[0],
    backgroundColor: colors[0],
    pointRadius: 1,
  });

  return buildDataforChart(
    graph.x,
    datasets,
    graph.x_label,
    graph.y_label,
    graph.graph_style
  );
}

export function createRunGraphChart(graph: RunGraph): ChartjsData {
  if (graph.graph_style === "line") {
    if (graph.graph_type === "multi" || graph.graph_type === "grouped") {
      return createGroupedLineChart(graph);
    }
    return createLineChart(graph);
  }

  if (graph.graph_type === "multi" || graph.graph_type === "grouped") {
    return createMultiScatterChart(graph);
  }
  return createScatterChart(graph);
}
