export const ssr = false;

import {
  getCardMetricNames,
  getCardParameters,
  getRecentExperiments,
} from "$lib/components/card/experiment/util";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent }) => {
  const { metadata } = await parent();

  // get metric names, parameters
  let metricNames = await getCardMetricNames(metadata.uid);
  let parameters = await getCardParameters(metadata.uid);
  let recentExperiments = await getRecentExperiments(
    metadata.space,
    metadata.name,
    metadata.version
  );

  return { metadata, metricNames, parameters, recentExperiments };
};
