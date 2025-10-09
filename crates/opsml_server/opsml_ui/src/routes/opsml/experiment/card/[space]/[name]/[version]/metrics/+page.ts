export const ssr = false;

import {
  getCardMetricNames,
  getRecentExperiments,
} from "$lib/components/card/experiment/util";
import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  const { metadata } = await parent();

  // get metric names, parameters
  let metricNames = await getCardMetricNames(metadata.uid);

  let recentExperiments = await getRecentExperiments(
    metadata.space,
    metadata.name,
    metadata.version
  );

  return { metadata, metricNames, recentExperiments };
};
