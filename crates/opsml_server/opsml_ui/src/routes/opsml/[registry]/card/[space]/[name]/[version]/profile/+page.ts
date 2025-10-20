export const ssr = false;

import { redirect } from "@sveltejs/kit";
import { getSortedFeatureNames } from "$lib/components/card/data/utils";
import { getRegistryPath, RegistryType } from "$lib/utils";
import type { PageLoad } from "./$types";
import { getDataProfile } from "$lib/components/card/data/getDataProfile";

export const load: PageLoad = async ({ parent, fetch }) => {
  const { registryType, metadata } = await parent();

  if (registryType !== RegistryType.Data) {
    throw redirect(
      302,
      `/opsml/${getRegistryPath(registryType)}/card/${metadata.space}/${
        metadata.name
      }/${metadata.version}`
    );
  }

  let dataProfile = metadata.metadata.interface_metadata.save_metadata
    ?.data_profile_uri
    ? await getDataProfile(fetch, metadata)
    : undefined;

  // get sorted feature names from dataProfile.features
  let featureNames: string[] = [];

  if (dataProfile) {
    featureNames = getSortedFeatureNames(dataProfile);
  }

  return { dataProfile, featureNames };
};
