export const ssr = false;

import { redirect } from "@sveltejs/kit";
import { getSortedFeatureNames } from "$lib/components/card/data/utils";
import { getRegistryPath, RegistryType } from "$lib/utils";
import type { PageLoad } from "./$types";
import { getDataProfile } from "$lib/components/card/data/getDataProfile";
import type { DataCard } from "$lib/components/card/card_interfaces/datacard";

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

  const dataCard = metadata as DataCard;

  let dataProfile = dataCard.metadata.interface_metadata.save_metadata
    ?.data_profile_uri
    ? await getDataProfile(fetch, dataCard)
    : undefined;

  // get sorted feature names from dataProfile.features
  let featureNames: string[] = [];

  if (dataProfile) {
    featureNames = getSortedFeatureNames(dataProfile);
  }

  return { dataProfile, featureNames };
};
