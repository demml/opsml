export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import type { PageLoad } from "./$types";
import {
  getDriftProfiles,
  getProfileFeatures,
} from "$lib/components/monitoring/util";
import { DriftType } from "$lib/components/monitoring/types";

export const load: PageLoad = async ({ parent }) => {
  await opsmlClient.validateAuth(true);

  const { metadata, registry, registryPath } = await parent();

  let profiles = await getDriftProfiles(metadata);

  // get all keys which should be of DriftType
  const keys: DriftType[] = Object.keys(profiles)
    .filter((key): key is DriftType => {
      return Object.values(DriftType).includes(key as DriftType);
    })
    .sort();

  let currentDriftType = keys[0];
  let currentProfile = profiles[currentDriftType];
  let currentNames: string[] = getProfileFeatures(
    currentDriftType,
    currentProfile
  );
  let currentName: string = currentNames[0];

  return {
    profiles,
    keys,
    currentName,
    currentNames,
    currentDriftType,
    currentProfile,
  };
};
