import { apiHandler } from "$lib/scripts/apiHandler";
import {
  CommonPaths,
  type FileView,
  RegistryName,
  SaveName,
} from "$lib/scripts/types";
import { type DataProfile, type WordStats } from "$lib/scripts/data/types";
import { type ChartjsData } from "$lib/scripts/types";
import { zoomOptions, grace, legend, handleResize } from "$lib/scripts/chart";
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
  let content: string = view.content.content!;

  let profile: DataProfile = JSON.parse(content);

  return profile;
}

export function createCategoricalWordVizData(wordStats: WordStats): {
  x: string[];
  y: number[];
} {
  let words = wordStats.words;
  let entries = Object.entries(words).map(([key, stats]) => ({
    key,
    percent: stats.percent,
  }));

  // Sort entries by count
  entries.sort((a, b) => b.percent - a.percent);

  // Unpack sorted entries into x, y, and percentage
  let x = entries.map((entry) => entry.key);
  let y = entries.map((entry) => entry.percent);

  return { x, y };
}

export function createNumericWordViz(x: string[], y: number[]): ChartjsData {
  let datasets = [
    {
      backgroundColor: "rgba(4, 205, 155, 0.2)",
      data: y,
      datalabels: {
        align: "end",
        anchor: "start",
      },
    },
  ];

  let options = {
    plugins: {
      zoom: zoomOptions,
      legend,
      datalabels: {
        color: "white",
        font: {
          weight: "bold",
        },
        formatter: Math.round,
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
        title: { display: true, text: "Words" },
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
      padding: 10,
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
