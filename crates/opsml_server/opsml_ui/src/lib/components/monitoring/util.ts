import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { ModelCard } from "../card/card_interfaces/modelcard";
import type { SpcDriftConfig, SpcDriftProfile } from "./spc";
import type { PsiDriftConfig, PsiDriftProfile } from "./psi";
import type { CustomDriftProfile, CustomMetricDriftConfig } from "./custom";
import { DriftType } from "./types";
import { RegistryType } from "$lib/utils";

export type DriftProfile = {
  Spc: SpcDriftProfile;
  Psi: PsiDriftProfile;
  Custom: CustomDriftProfile;
};

export type DriftConfigType =
  | CustomMetricDriftConfig
  | PsiDriftConfig
  | SpcDriftConfig;

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

export async function getProfileFeatures(
  drift_type: DriftType,
  profile: DriftProfile
): Promise<string[]> {
  const variables =
    drift_type === DriftType.Custom
      ? profile.Custom.metrics
      : drift_type === DriftType.Psi
      ? profile.Psi.features
      : profile.Spc.features;

  return Object.keys(variables).sort();
}

export async function getProfileConfig(
  drift_type: DriftType,
  profile: DriftProfile
): Promise<DriftConfigType> {
  const variables =
    drift_type === DriftType.Custom
      ? profile.Custom.config
      : drift_type === DriftType.Psi
      ? profile.Psi.config
      : profile.Spc.config;

  return variables;
}
