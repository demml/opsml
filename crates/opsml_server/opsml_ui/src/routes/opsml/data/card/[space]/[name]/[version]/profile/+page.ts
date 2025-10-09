export const ssr = false;

import {
  getDataProfile,
  getSortedFeatureNames,
} from "$lib/components/card/data/utils";
import type { PageLoad } from "./$types";
import { validateUserOrRedirect } from "$lib/components/user/user.svelte";

export const load: PageLoad = async ({ parent }) => {
  const { metadata } = await parent();

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
