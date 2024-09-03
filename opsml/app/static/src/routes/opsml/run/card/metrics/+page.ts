import { createMetricVizData } from "$lib/scripts/utils";
import { type RunPageReturn } from "$lib/scripts/types";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ parent }) {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-call
  const data = (await parent()) as RunPageReturn;

  const metricVizData = createMetricVizData(data.metrics, "bar");
  data["metricVizData"] = metricVizData;

  return data;
}
