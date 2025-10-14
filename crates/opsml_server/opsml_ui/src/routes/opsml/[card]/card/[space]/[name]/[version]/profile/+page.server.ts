import { redirect } from "@sveltejs/kit";
import {
  getDataProfile,
  getSortedFeatureNames,
} from "$lib/components/card/data/utils";
import { getRegistryPath, RegistryType } from "$lib/utils";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ parent }) => {
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
    ? await getDataProfile(metadata)
    : undefined;

  // get sorted feature names from dataProfile.features
  let featureNames: string[] = [];

  if (dataProfile) {
    featureNames = getSortedFeatureNames(dataProfile);
  }

  return { dataProfile, featureNames };
};
