import type { DataProfile, WordStats } from "$lib/components/card/data/types";

export function loadDataProfile(jsonString: string): DataProfile {
  try {
    // Parse the JSON string
    const parsedData = JSON.parse(jsonString);

    // Cast the parsed data to the DataProfile type
    return parsedData as DataProfile;
  } catch (error) {
    throw new Error("Invalid JSON string");
  }
}

export function getSortedFeatureNames(dataProfile: DataProfile): string[] {
  return Object.keys(dataProfile.features).sort();
}

export function createCategoricalWordData(wordStats: WordStats): {
  x: string[];
  y: number[];
} {
  const entries = Object.entries(wordStats.words)
    .sort(([, a], [, b]) => b.percent - a.percent)
    .reduce(
      (acc, [key, stats]) => {
        acc.x.push(key);
        acc.y.push(stats.percent);
        return acc;
      },
      { x: [] as string[], y: [] as number[] }
    );

  // Limit to top 10 entries
  const limit = 10;
  if (entries.x.length > limit) {
    entries.x = entries.x.slice(0, limit);
    entries.y = entries.y.slice(0, limit);
  }

  return entries;
}
