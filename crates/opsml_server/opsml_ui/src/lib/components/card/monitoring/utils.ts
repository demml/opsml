import type { SpcDriftConfig, SpcDriftProfile } from "./spc/spc";
import type { PsiDriftConfig, PsiDriftProfile } from "./psi/psi";
import { createInternalApiClient } from "$lib/api/internalClient";
import type {
  CustomDriftProfile,
  CustomMetricDriftConfig,
} from "./custom/custom";
import { mockPsiMetrics } from "./psi/mocks";
import { mockCustomMetrics } from "./custom/mocks";
import { mockSpcMetrics } from "./spc/mocks";
import { mockLLMMetrics } from "./llm/mocks";
import {
  DriftType,
  TimeInterval,
  type BinnedDriftMap,
  type MetricData,
} from "./types";
import type { LLMDriftConfig, LLMDriftProfile } from "./llm/llm";
import { mockAlerts } from "./mocks";
import { ServerPaths } from "$lib/components/api/routes";
import { mockDriftProfileResponse } from "./mocks";
import type { DriftProfileUri } from "../monitoring/types";
import { RegistryType } from "$lib/utils";
import { type Alert } from "./alert/types";

export type DriftProfile = {
  Spc: SpcDriftProfile;
  Psi: PsiDriftProfile;
  Custom: CustomDriftProfile;
  LLM: LLMDriftProfile;
};

export interface UiProfile {
  profile_uri: string;
  profile: DriftProfile;
}

export type DriftConfigType =
  | CustomMetricDriftConfig
  | PsiDriftConfig
  | SpcDriftConfig
  | LLMDriftConfig;

export type DriftProfileResponse = {
  [DriftType: string]: UiProfile;
};

export function getProfileFeatures(
  drift_type: DriftType,
  profile: DriftProfile
): string[] {
  const variables: string[] =
    drift_type === DriftType.Custom
      ? Object.keys(profile.Custom.metrics)
      : drift_type === DriftType.LLM
      ? profile.LLM.metric_names
      : drift_type === DriftType.Psi
      ? profile.Psi.config.alert_config.features_to_monitor
      : profile.Spc.config.alert_config.features_to_monitor;

  return variables.sort();
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
      : drift_type === DriftType.LLM
      ? profile.LLM.config
      : drift_type === DriftType.Psi
      ? profile.Psi.config
      : profile.Spc.config;

  return variables;
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
    case DriftType.LLM:
      return latestMetrics[DriftType.LLM]?.metrics[currentName] as MetricData;
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

export function isLlmConfig(config: DriftConfigType): config is LLMDriftConfig {
  return config.drift_type === DriftType.LLM;
}

export function isPsiConfig(config: DriftConfigType): config is PsiDriftConfig {
  return config.drift_type === DriftType.Psi;
}

export function isSpcConfig(config: DriftConfigType): config is SpcDriftConfig {
  return config.drift_type === DriftType.Spc;
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
  return past.toISOString();
}

/** Helper for getting latest monitoring metrics
 * @param profiles - drift profiles to get metrics for
 * @param time_interval - time interval for the metrics
 * @param max_data_points - maximum data points to retrieve
 * @param fetch - fetch function
 * @returns binned drift map with latest metrics
 */
export async function getLatestMonitoringMetrics(
  fetch: typeof globalThis.fetch,
  profiles: DriftProfileResponse,
  time_interval: TimeInterval,
  max_data_points: number
): Promise<BinnedDriftMap> {
  // for dev, return example data
  if (import.meta.env.DEV) {
    return {
      [DriftType.Spc]: mockSpcMetrics,
      [DriftType.Psi]: mockPsiMetrics,
      [DriftType.Custom]: mockCustomMetrics,
      [DriftType.LLM]: mockLLMMetrics,
    };
  }

  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.MONITORING_METRICS,
    {
      profiles,
      time_interval,
      max_data_points,
    }
  );

  let binnedMap = (await resp.json()) as BinnedDriftMap;
  return binnedMap;
}

/** Helper for getting monitoring drift profiles
 * @param fetch - fetch function
 * @param uid - unique identifier for the card
 * @param driftMap - map of drift profiles to fetch
 * @param registryType - type of registry (Model, Data, etc.)
 * @returns drift profiles
 */
export async function getMonitoringDriftProfiles(
  fetch: typeof globalThis.fetch,
  uid: string,
  driftMap: Record<string, DriftProfileUri>,
  registryType: RegistryType
): Promise<DriftProfileResponse> {
  if (import.meta.env.DEV) {
    return mockDriftProfileResponse;
  }

  let resp = createInternalApiClient(fetch).post(
    ServerPaths.MONITORING_PROFILES,
    {
      uid,
      driftMap,
      registryType,
    }
  );

  let profiles = (await (await resp).json()) as DriftProfileResponse;
  return profiles;
}

/** Helper for getting monitoring alerts
 * @param fetch - fetch function
 * @param space - space of the model card
 * @param name - name of the model card
 * @param version - version of the model card
 * @param timeInterval - time interval for the alerts
 * @param active - whether to fetch only active alerts
 * @returns list of alerts
 */
export async function getMonitoringAlerts(
  fetch: typeof globalThis.fetch,
  space: string,
  name: string,
  version: string,
  timeInterval: TimeInterval,
  active: boolean
): Promise<Alert[]> {
  if (import.meta.env.DEV) {
    return mockAlerts;
  }

  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.MONITORING_ALERTS,
    {
      space,
      name,
      version,
      timeInterval,
      active,
    }
  );

  let alerts = (await resp.json()) as Alert[];
  return alerts;
}
