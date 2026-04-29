export const ssr = false;

import { getRegistryPath, RegistryType } from "$lib/utils";
import { goto } from "$app/navigation";
import type { PageLoad } from "./$types";
import { ServerPaths } from "$lib/components/api/routes";
import { createInternalApiClient } from "$lib/api/internalClient";
import type { Experiment } from "$lib/components/card/experiment/types";
import { buildMockExperimentMetricsIndex } from "$lib/components/mock/opsmlMockData";

export const load: PageLoad = async ({ parent, fetch }) => {
  const { registryType, metadata, devMockEnabled } = await parent();
  const useMockFallback = Boolean(devMockEnabled);

  if (registryType !== RegistryType.Experiment) {
    throw goto(
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${
        metadata.name
      }/${metadata.version}`
    );
  }

  try {
    const [metricNamesResp, recentExperimentsResp] = await Promise.all([
      createInternalApiClient(fetch).post(ServerPaths.EXPERIMENT_METRIC_NAMES, {
        uid: metadata.uid,
      }),
      createInternalApiClient(fetch).post(ServerPaths.EXPERIMENT_RECENT, {
        space: metadata.space,
        name: metadata.name,
        version: metadata.version,
      }),
    ]);

    const [metricNames, recentExperiments] = await Promise.all([
      metricNamesResp.json() as Promise<string[]>,
      recentExperimentsResp.json() as Promise<Experiment[]>,
    ]);

    if (useMockFallback && metricNames.length === 0) {
      const mock = buildMockExperimentMetricsIndex(metadata.version);
      return { metadata, ...mock, mockMode: true };
    }

    return { metadata, metricNames, recentExperiments, mockMode: false };
  } catch (error) {
    if (!useMockFallback) {
      throw error;
    }

    return {
      metadata,
      ...buildMockExperimentMetricsIndex(metadata.version),
      mockMode: true,
    };
  }
};
