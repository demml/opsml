import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { ModelCard } from "../card/card_interfaces/modelcard";
import type { SpcDriftProfile } from "./spc";
import type { PsiDriftProfile } from "./psi";
import type { CustomDriftProfile } from "./custom";
import type { DriftType } from "./types";
import { RegistryType } from "$lib/utils";

export type DriftProfile = {
  Spc: SpcDriftProfile;
  Psi: PsiDriftProfile;
  Custom: CustomDriftProfile;
};

export type DriftProfileResponse = {
  [DriftType: string]: DriftProfile;
};

export async function getDriftProfiles(
  metadata: ModelCard
): Promise<DriftProfileResponse> {
  let driftUri =
    metadata.metadata.interface_metadata.save_metadata.drift_profile_uri;

  const body = {
    path: driftUri,
    uid: metadata.uid,
    registry_type: RegistryType.Model,
  };

  const response = await opsmlClient.post(RoutePaths.DRIFT_PROFILE_UI, body);
  return (await response.json()) as DriftProfileResponse;
}
