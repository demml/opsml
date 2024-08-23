import { type RunGraph } from "$lib/scripts/types";
import { it, expect } from "vitest";
import {
  createLineChart,
  createGroupedLineChart,
  createScatterChart,
  createMultiScatterChart,
} from "../lib/scripts/runGraphChart";

const lineGraph: RunGraph = {
  name: "line",
  x_label: "x",
  y_label: "y",
  x: [1, 2, 3, 4, 5],
  y: [1, 2, 3, 4, 5],
  graph_type: "single",
  graph_style: "line",
};

const groupedLineGraph: RunGraph = {
  name: "grouped line",
  x_label: "x",
  y_label: "y",
  x: [1, 2, 3, 4, 5],
  y: new Map([
    ["a", [1, 2, 3, 4, 5]],
    ["b", [5, 4, 3, 2, 1]],
    ["c", [1, 3, 1, 3, 1]],
  ]),
  graph_type: "grouped",
  graph_style: "line",
};

const groupedScatterGraph: RunGraph = {
  name: "grouped scatter",
  x_label: "x",
  y_label: "y",
  x: [1, 2, 3, 4, 5],
  y: new Map([
    ["a", [1, 2, 3, 4, 5]],
    ["b", [5, 4, 3, 2, 1]],
    ["c", [1, 3, 1, 3, 1]],
  ]),
  graph_type: "grouped",
  graph_style: "scatter",
};

const scatterGraph: RunGraph = {
  name: "scatter",
  x_label: "x",
  y_label: "y",
  x: [1, 2, 3, 4, 5],
  y: [1, 2, 3, 4, 5],
  graph_type: "single",
  graph_style: "scatter",
};

it("run line chart", () => {
  const graph = createLineChart(lineGraph);
  expect(graph.data.datasets[0].data).toEqual([1, 2, 3, 4, 5]);
});

it("run grouped line chart", () => {
  const graph = createGroupedLineChart(groupedLineGraph);
  expect(graph.data.datasets[0].data).toEqual([1, 2, 3, 4, 5]);
  expect(graph.data.datasets[1].data).toEqual([5, 4, 3, 2, 1]);
  expect(graph.data.datasets[2].data).toEqual([1, 3, 1, 3, 1]);
});

// test createScatterChart
it("run scatter chart", () => {
  const graph = createScatterChart(scatterGraph);
  expect(graph.data.datasets[0].data).toEqual([
    { x: 1, y: 1 },
    { x: 2, y: 2 },
    { x: 3, y: 3 },
    { x: 4, y: 4 },
    { x: 5, y: 5 },
  ]);
});

// test createMultiScatterChart
it("run grouped scatter chart", () => {
  const graph = createMultiScatterChart(groupedScatterGraph);
  expect(graph.data.datasets[0].data).toEqual([
    { x: 1, y: 1 },
    { x: 2, y: 2 },
    { x: 3, y: 3 },
    { x: 4, y: 4 },
    { x: 5, y: 5 },
  ]);
  expect(graph.data.datasets[1].data).toEqual([
    { x: 1, y: 5 },
    { x: 2, y: 4 },
    { x: 3, y: 3 },
    { x: 4, y: 2 },
    { x: 5, y: 1 },
  ]);
  expect(graph.data.datasets[2].data).toEqual([
    { x: 1, y: 1 },
    { x: 2, y: 3 },
    { x: 3, y: 1 },
    { x: 4, y: 3 },
    { x: 5, y: 1 },
  ]);
});
