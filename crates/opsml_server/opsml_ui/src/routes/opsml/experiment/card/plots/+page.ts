export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import {
  getCardMetricNames,
  getCardParameters,
  getRecentExperiments,
} from "$lib/components/card/experiment/util";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  await opsmlClient.validateAuth(true);

  const { metadata } = await parent();

  // get metric names, parameters
  let metricNames = await getCardMetricNames(metadata.uid);
  let parameters = await getCardParameters(metadata.uid);
  let recentExperiments = await getRecentExperiments(
    metadata.repository,
    metadata.name,
    metadata.version
  );

  return { metadata, metricNames, parameters, recentExperiments };
};
