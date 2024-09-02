import {
  type CardRequest,
  type CardResponse,
  type CompareMetricPage,
  CardRegistries,
  type Card,
  type RunMetrics,
  type RunCard,
  type ChartjsData,
} from "$lib/scripts/types";
import { listCards, createMetricVizData } from "$lib/scripts/utils";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ parent }) {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
  const data = await parent();

  let metricVizData = createMetricVizData(data.metrics, "bar");
  data["metricVizData"] = metricVizData;

  return data;
}
