export const ssr = false;

import type { PageLoad } from "./$types";
import { getRegistryPath, RegistryType } from "$lib/utils";
import { goto } from "$app/navigation";
import { ServerPaths } from "$lib/components/api/routes";
import { createInternalApiClient } from "$lib/api/internalClient";
import type { UiHardwareMetrics } from "$lib/components/card/experiment/types";
import { buildMockHardwareMetrics } from "$lib/components/mock/opsmlMockData";

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

  // get metric names, parameters
  try {
    let resp = await createInternalApiClient(fetch).post(
      ServerPaths.EXPERIMENT_HARDWARE,
      {
        uid: metadata.uid,
      }
    );
    const hardwareMetrics = (await resp.json()) as UiHardwareMetrics;

    return { hardwareMetrics, mockMode: false };
  } catch (error) {
    if (!useMockFallback) {
      throw error;
    }

    return { hardwareMetrics: buildMockHardwareMetrics(), mockMode: true };
  }
};
