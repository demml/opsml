import { type ChartConfiguration } from "chart.js";
import { createBarChart } from "$lib/components/viz/chart";
import { type WordStats } from "$lib/components/card/data/types";
import { createCategoricalWordData } from "$lib/components/card/data/utils";

export function createWordBarChart(wordStats: WordStats): ChartConfiguration {
  let wordData = createCategoricalWordData(wordStats);

  return createBarChart(
    wordData.x,
    wordData.y,
    "Word Frequency",
    "Word Frequency",
    "Percent Occurrence"
  );
}
