export const ssr = false;

import type { LayoutLoad } from "./$types";
import { getRegistryPath, RegistryType } from "$lib/utils";
import { redirect } from "@sveltejs/kit";
import {
  getProfilesFromMetadata,
  getSortedDriftTypes,
} from "$lib/components/scouter/dashboard/utils";

export const load: LayoutLoad = async ({ parent, fetch }) => {
  const parentData = await parent();
  const { registryType, metadata } = parentData;

  if (registryType !== RegistryType.Prompt) {
    throw redirect(
      303,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}/card`
    );
  }

  const profiles = await getProfilesFromMetadata(fetch, metadata, registryType);
  const driftTypes = getSortedDriftTypes(profiles);

  if (driftTypes.length === 0) {
    throw redirect(
      303,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${metadata.name}/${metadata.version}/card`
    );
  }

  return {
    registryType,
    metadata,
    profiles,
    driftTypes,
  };
};
