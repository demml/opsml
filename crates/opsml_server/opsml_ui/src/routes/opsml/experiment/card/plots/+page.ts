export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import {
  getCardMetricNames,
  getCardParameters,
  getCardVersions,
} from "$lib/components/card/experiment/util";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  await opsmlClient.validateAuth(true);

  const { metadata } = await parent();

  // get metric names, parameters and versions
  let metricNames = await getCardMetricNames(metadata.uid);
  let parameters = await getCardParameters(metadata.uid);
  let cardVersions = await getCardVersions(
    metadata.repository,
    metadata.name,
    metadata.version
  );

  return { metadata, metricNames, parameters, cardVersions };
};
