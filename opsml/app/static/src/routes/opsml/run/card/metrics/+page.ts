import { createMetricVizData } from "$lib/scripts/utils";
import { type RunPageReturn } from "$lib/scripts/types";
import { RunCardStore } from "$routes/store";
import { get } from "svelte/store";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ parent }) {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-call
  const data = (await parent()) as RunPageReturn;

  if (!get(RunCardStore).MetricData) {
    const metricVizData = createMetricVizData(data.metrics, "bar");
    data["metricVizData"] = metricVizData;

    RunCardStore.update((store) => {
      store.MetricData = data.metricVizData;
      store.TableMetrics = data.tableMetrics;
      return store;
    });
  }

  return data;
}
