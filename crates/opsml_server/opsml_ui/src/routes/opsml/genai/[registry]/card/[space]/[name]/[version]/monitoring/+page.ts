export const ssr = false;

import type { PageLoad } from "./$types";
import { getMonitoringPageData } from "$lib/components/scouter/dashboard/utils";
import { getRegistryPath, RegistryType } from "$lib/utils";
import { redirect } from "@sveltejs/kit";

export const load: PageLoad = async ({ parent, fetch }) => {
  const parentData = await parent();
  const { registryType, metadata } = parentData;

  if (registryType !== RegistryType.Prompt) {
    throw redirect(
      303,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${
        metadata.name
      }/${metadata.version}/card`
    );
  }

  const data = await getMonitoringPageData(fetch, metadata, registryType);

  return { monitoringData: data, registryType, metadata };
};
