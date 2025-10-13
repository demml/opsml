import type { SpcDriftConfig, SpcDriftProfile } from "./spc/spc";
import type { PsiDriftConfig, PsiDriftProfile } from "./psi/psi";
import { createInternalApiClient } from "$lib/api/internalClient";
import type {
  CustomDriftProfile,
  CustomMetricDriftConfig,
} from "./custom/custom";
import {
  DriftType,
  TimeInterval,
  type BinnedDriftMap,
  type MetricData,
} from "./types";
import type { LLMDriftConfig, LLMDriftProfile } from "./llm/llm";
import {
  sampleSpcMetrics,
  sampleCustomMetrics,
  sampleLLMMetrics,
  samplePsiMetrics,
} from "./mocks";
import { ServerPaths } from "$lib/components/api/routes";

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

export async function getLatestMonitoringMetrics(
  profiles: DriftProfileResponse,
  time_interval: TimeInterval,
  max_data_points: number,
  fetch: typeof globalThis.fetch
): Promise<BinnedDriftMap> {
  // for dev, return example data
  if (import.meta.env.DEV) {
    return {
      [DriftType.Spc]: sampleSpcMetrics,
      [DriftType.Psi]: samplePsiMetrics,
      [DriftType.Custom]: sampleCustomMetrics,
      [DriftType.LLM]: sampleLLMMetrics,
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
