export const ssr = false;

import type { PageLoad } from "./$types";
import { getRegistryPath, RegistryType } from "$lib/utils";
import { goto } from "$app/navigation";
import { ServerPaths } from "$lib/components/api/routes";
import { createInternalApiClient } from "$lib/api/internalClient";
import type { HardwareMetrics } from "$lib/components/card/experiment/types";

export const load: PageLoad = async ({ parent, fetch }) => {
  const { registryType, metadata } = await parent();

  if (registryType !== RegistryType.Experiment) {
    throw goto(
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${
        metadata.name
      }/${metadata.version}`
    );
  }

  // get metric names, parameters
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.EXPERIMENT_HARDWARE,
    {
      uid: metadata.uid,
    }
  );
  const hardwareMetrics = (await resp.json()) as HardwareMetrics;

  return { hardwareMetrics };
};
