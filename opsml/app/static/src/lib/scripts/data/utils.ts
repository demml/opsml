import { apiHandler } from "$lib/scripts/apiHandler";
import {
  CommonPaths,
  type FileView,
  RegistryName,
  SaveName,
} from "$lib/scripts/types";
import {
  type DataProfile,
  type WordStats,
  type Histogram,
} from "$lib/scripts/data/types";
import { type ChartjsData } from "$lib/scripts/types";
import { grace, legend, handleResize } from "$lib/scripts/chart";
export async function getDataProfile(
  repository,
  name,
  version
): Promise<DataProfile> {
  const filePath: string = `opsml-root:/${RegistryName.Data}/${repository}/${name}/v${version}/${SaveName.DataProfile}`;

  const viewData = await apiHandler.get(
    `${CommonPaths.FILES_VIEW}?${new URLSearchParams({
      path: filePath,
    }).toString()}`
  );

  const view = (await viewData.json()) as FileView;
  const content: string = view.content.content!;

  const profile = JSON.parse(content) as DataProfile;

  return profile;
}

export function createCategoricalWordVizData(wordStats: WordStats): {
  x: string[];
  y: number[];
} {
  const words = wordStats.words;
  const entries = Object.entries(words).map(([key, stats]) => ({
    key,
    percent: stats.percent,
  }));

  // Sort entries by count
  entries.sort((a, b) => b.percent - a.percent);

  // Unpack sorted entries into x, y, and percentage
  const x = entries.map((entry) => entry.key);
  const y = entries.map((entry) => entry.percent);

  return { x, y };
}

export function createBarViz(
  x: string[],
  y: number[],
  xTitle: string
): ChartjsData {
  const datasets = [
    {
      backgroundColor: "rgba(75, 57, 120, 0.5)",
      borderColor: "rgba(75, 57, 120, 1)",
      borderWidth: 2,
      data: y,
      datalabels: {
        align: "start",
        anchor: "end",
      },
    },
  ];

  const options = {
    plugins: {
      legend,
      datalabels: {
        color: "white",
        font: {
          weight: "bold",
        },
        formatter: function (value: number, _context): string {
          return value.toFixed(3);
        },
      },
    },
    responsive: true,
    onresize: handleResize,
    maintainAspectRatio: false,
    scales: {
      x: {
        border: {
          width: 2,
          color: "rgba(0, 0, 0, 1)",
        },
        grid: {
          display: false,
        },
        title: { display: true, text: xTitle },
        ticks: {
          maxTicksLimit: 30,
        },
      },
      y: {
        grace: grace,
        border: {
          width: 2,
          color: "rgba(0, 0, 0, 1)",
        },
        grid: {
          display: false,
        },
        title: { display: true, text: "Distribution" },
        ticks: {
          maxTicksLimit: 30,
        },
      },
    },
    layout: {
      padding: 5,
    },
  };

  const graphData = {
    labels: x,
    datasets: datasets,
  };

  return {
    type: "bar",
    data: graphData,
    options: options,
  };
}

export function createHistViz(data: Histogram): ChartjsData {
  const datasets = [
    {
      backgroundColor: "rgba(75, 57, 120, 0.5)",
      borderColor: "rgba(75, 57, 120, 1)",
      borderWidth: 2,
      data: data.bin_counts,
    },
  ];

  const options = {
    plugins: {
      legend,
    },
    responsive: true,
    onresize: handleResize,
    maintainAspectRatio: false,
    scales: {
      x: {
        border: {
          width: 2,
          color: "rgba(0, 0, 0, 1)",
        },
        grid: {
          display: false,
        },
        title: { display: true, text: "Bins" },
        ticks: {
          maxTicksLimit: 30,
          callback: function (value: number): string {
            return value.toFixed(2);
          },
        },
      },
      y: {
        grace: grace,
        border: {
          width: 2,
          color: "rgba(0, 0, 0, 1)",
        },
        grid: {
          display: false,
        },
        title: { display: true, text: "Distribution" },
        ticks: {
          maxTicksLimit: 30,
        },
      },
    },
    layout: {
      padding: 5,
    },
  };

  const graphData = {
    labels: data.bins,
    datasets: datasets,
  };

  return {
    type: "bar",
    data: graphData,
    options: options,
  };
}
