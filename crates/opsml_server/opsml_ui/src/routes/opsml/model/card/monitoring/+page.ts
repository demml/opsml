export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import type { PageLoad } from "./$types";
import { getDriftProfiles } from "$lib/components/monitoring/util";
import { DriftType } from "$lib/components/monitoring/types";

export const load: PageLoad = async ({ parent }) => {
  await opsmlClient.validateAuth(true);

  const { metadata, registry, registryPath } = await parent();

  let profiles = await getDriftProfiles(metadata);

  const psiProfile = profiles[DriftType.Psi];
  const customProfile = profiles[DriftType.Custom];
  const spcProfile = profiles[DriftType.Spc];

  console.log(psiProfile);
  console.log(customProfile);
  console.log(spcProfile);

  return { profiles };
};
