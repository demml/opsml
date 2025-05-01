import { opsmlClient } from "$lib/components/api/client.svelte";
import { RoutePaths } from "$lib/components/api/routes";
import type { ModelCard } from "$lib/components/card/card_interfaces/modelcard";
import type { SpcDriftConfig, SpcDriftProfile } from "./spc/spc";
import type { PsiDriftConfig, PsiDriftProfile } from "./psi/psi";
import type {
  CustomDriftProfile,
  CustomMetricDriftConfig,
} from "./custom/custom";
import {
  DriftType,
  TimeInterval,
  type BinnedDriftMap,
  type DriftRequest,
  type MetricData,
  type UpdateProfileRequest,
  type UpdateResponse,
} from "./types";
import { RegistryType } from "$lib/utils";
import {
  samplePsiMetrics,
  sampleSpcMetrics,
  sampleCustomMetrics,
} from "./example";

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

export function extractProfile(
  profile: DriftProfile,
  drift_type: DriftType
): SpcDriftProfile | PsiDriftProfile | CustomDriftProfile {
  return drift_type === DriftType.Custom
    ? profile.Custom
    : drift_type === DriftType.Psi
    ? profile.Psi
    : profile.Spc;
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
        space: config.space,
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

export async function getLatestMetricsExample(
  profiles: DriftProfileResponse,
  time_interval: TimeInterval,
  max_data_points: number
): Promise<BinnedDriftMap> {
  return {
    [DriftType.Spc]: sampleSpcMetrics,
    [DriftType.Psi]: samplePsiMetrics,
    [DriftType.Custom]: sampleCustomMetrics,
  };
}

// Funcs
// Helper function to get current metric data
export function getCurrentMetricData(
  latestMetrics: BinnedDriftMap,
  currentDriftType: DriftType,
  currentName: string
): MetricData {
  if (!latestMetrics || !currentDriftType || !currentName) return null;

  switch (currentDriftType) {
    case DriftType.Spc:
      return latestMetrics[DriftType.Spc]?.features[currentName] as MetricData;
    case DriftType.Psi:
      return latestMetrics[DriftType.Psi]?.features[currentName] as MetricData;
    case DriftType.Custom:
      return latestMetrics[DriftType.Custom]?.metrics[
        currentName
      ] as MetricData;
    default:
      return null;
  }
}

// Type guard functions to determine config type
export function isCustomConfig(
  config: DriftConfigType
): config is CustomMetricDriftConfig {
  return config.drift_type === DriftType.Custom;
}

export function isPsiConfig(config: DriftConfigType): config is PsiDriftConfig {
  return config.drift_type === DriftType.Psi;
}

export function isSpcConfig(config: DriftConfigType): config is SpcDriftConfig {
  return config.drift_type === DriftType.Spc;
}

export async function updateDriftProfile(
  updateRequest: UpdateProfileRequest
): Promise<UpdateResponse> {
  const response = await opsmlClient.put(
    RoutePaths.DRIFT_PROFILE,
    updateRequest
  );
  return (await response.json()) as UpdateResponse;
}

export function timeIntervalToDateTime(interval: TimeInterval): string {
  const now = new Date();
  const minutesMap: Record<TimeInterval, number> = {
    [TimeInterval.FiveMinutes]: 5,
    [TimeInterval.FifteenMinutes]: 15,
    [TimeInterval.ThirtyMinutes]: 30,
    [TimeInterval.OneHour]: 60,
    [TimeInterval.ThreeHours]: 180,
    [TimeInterval.SixHours]: 360,
    [TimeInterval.TwelveHours]: 720,
    [TimeInterval.TwentyFourHours]: 1440,
    [TimeInterval.TwoDays]: 2880,
    [TimeInterval.FiveDays]: 7200,
  };

  const minutes = minutesMap[interval];
  const past = new Date(now.getTime() - minutes * 60000);

  // Format to YYYY-MM-DD HH:MM:SS
  return past.toISOString().replace("T", " ").slice(0, 19);
}
