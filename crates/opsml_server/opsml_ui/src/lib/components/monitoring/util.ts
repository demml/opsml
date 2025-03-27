import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { ModelCard } from "../card/card_interfaces/modelcard";
import type { SpcDriftConfig, SpcDriftProfile } from "./spc";
import type { PsiDriftConfig, PsiDriftProfile } from "./psi";
import type { CustomDriftProfile, CustomMetricDriftConfig } from "./custom";
import {
  DriftType,
  TimeInterval,
  type BinnedDriftMap,
  type DriftRequest,
} from "./types";
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

export function getProfileFeatures(
  drift_type: DriftType,
  profile: DriftProfile
): string[] {
  const variables =
    drift_type === DriftType.Custom
      ? profile.Custom.metrics
      : drift_type === DriftType.Psi
      ? profile.Psi.features
      : profile.Spc.features;

  return Object.keys(variables).sort();
}

export function getProfileConfig(
  drift_type: DriftType,
  profile: DriftProfile
): DriftConfigType {
  const variables =
    drift_type === DriftType.Custom
      ? profile.Custom.config
      : drift_type === DriftType.Psi
      ? profile.Psi.config
      : profile.Spc.config;

  return variables;
}

export async function getLatestMetrics(
  profiles: DriftProfileResponse,
  time_interval: TimeInterval,
  max_data_points: number
): Promise<BinnedDriftMap> {
  const driftMap: BinnedDriftMap = {};

  // Create an array of promises
  const requests = Object.entries(profiles).map(
    async ([driftType, profile]) => {
      const config = getProfileConfig(driftType as DriftType, profile);

      const request: DriftRequest = {
        name: config.name,
        repository: config.repository,
        version: config.version,
        time_interval: time_interval,
        max_data_points: max_data_points,
        drift_type: driftType as DriftType,
      };

      // Determine route based on drift type
      const route = (() => {
        switch (driftType) {
          case DriftType.Custom:
            return RoutePaths.CUSTOM_DRIFT;
          case DriftType.Psi:
            return RoutePaths.PSI_DRIFT;
          case DriftType.Spc:
            return RoutePaths.SPC_DRIFT;
          default:
            throw new Error(`Unsupported drift type: ${driftType}`);
        }
      })();

      // Make the request and store result in driftMap
      const response = await opsmlClient.post(route, request);
      const data = await response.json();
      driftMap[driftType as DriftType] = data;
    }
  );

  // Wait for all requests to complete
  await Promise.all(requests);

  return driftMap;
}
