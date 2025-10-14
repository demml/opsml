import { getHardwareMetrics } from "$lib/server/experiment/utils";
import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getRegistryPath, RegistryType } from "$lib/utils";

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
  let hardwareMetrics = await getHardwareMetrics(fetch, metadata.uid);

  return { hardwareMetrics };
};
