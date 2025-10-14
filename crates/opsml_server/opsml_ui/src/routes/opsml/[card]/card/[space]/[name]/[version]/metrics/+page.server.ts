import {
  getCardMetricNames,
  getRecentExperiments,
} from "$lib/server/experiment/utils";
import { getRegistryPath, RegistryType } from "$lib/utils";
import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ parent, fetch }) => {
  const { registryType, metadata } = await parent();

  if (registryType !== RegistryType.Experiment) {
    throw redirect(
      302,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${
        metadata.name
      }/${metadata.version}`
    );
  }

  // get metric names, parameters
  let metricNames = await getCardMetricNames(fetch, metadata.uid);

  let recentExperiments = await getRecentExperiments(
    fetch,
    metadata.space,
    metadata.name,
    metadata.version
  );

  return { metadata, metricNames, recentExperiments };
};
