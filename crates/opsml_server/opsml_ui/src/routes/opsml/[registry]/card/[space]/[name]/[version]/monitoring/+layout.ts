export const ssr = false;

import type { LayoutLoad } from "./$types";
import { getRegistryPath, RegistryType } from "$lib/utils";
import { redirect } from "@sveltejs/kit";
import {
  getProfilesFromMetadata,
  getSortedDriftTypes,
} from "$lib/components/scouter/dashboard/utils";
import { driftTypeFromString } from "$lib/components/scouter/types";

export const load: LayoutLoad = async ({ parent, fetch, url }) => {
  const parentData = await parent();
  const { registryType, metadata, settings } = parentData;

  if (registryType !== RegistryType.Model) {
    throw redirect(
      303,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}/card`,
    );
  }

  if (!settings?.scouter_enabled) {
    return {
      registryType,
      metadata,
      profiles: {},
      driftTypes: [],
    };
  }

  const profiles = await getProfilesFromMetadata(fetch, metadata, registryType);
  const driftTypes = getSortedDriftTypes(profiles);

  if (driftTypes.length === 0) {
    throw redirect(
      303,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}/card`,
    );
  }

  // split url to get current drift type
  const currentDriftType = driftTypeFromString(
    url.pathname.split("/").pop() || "",
  );

  if (!currentDriftType || !driftTypes.includes(currentDriftType)) {
    throw redirect(
      303,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}/monitoring/${driftTypes[0].toLowerCase()}`,
    );
  }

  return {
    registryType,
    metadata,
    profiles,
    driftTypes,
  };
};
