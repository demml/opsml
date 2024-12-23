import type {
  ParsedHardwareMetrics,
  Card,
  RunPageReturn,
} from "$lib/scripts/types";
import { getHardwareMetrics, parseHardwareMetrics } from "$lib/scripts/utils";
import { RunCardStore } from "$routes/store";
import { get } from "svelte/store";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ parent }) {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-call
  const data = (await parent()) as RunPageReturn;

  let parsedMetrics: ParsedHardwareMetrics | undefined = undefined;

  if (!get(RunCardStore).HardwareMetrics) {
    const runcard: Card = data.card;

    const hardwareVizData = await getHardwareMetrics(runcard.uid);
    // process hardware metrics
    if (hardwareVizData.metrics.length > 0) {
      parsedMetrics = parseHardwareMetrics(hardwareVizData.metrics);

      RunCardStore.update((store) => {
        store.HardwareMetrics = parsedMetrics;
        return store;
      });
    }
  }

  return data;
}
