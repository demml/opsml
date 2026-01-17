import type { AlertDispatchConfig } from "./types";
import type { SpcDriftConfig, SpcDriftProfile } from "./spc/types";
import type { PsiDriftConfig, PsiDriftProfile } from "./psi/types";
import { createInternalApiClient } from "$lib/api/internalClient";
import type {
  BinnedMetrics,
  CustomDriftProfile,
  CustomMetricDriftConfig,
} from "./custom/types";
import { DriftType, type MetricData } from "./types";
import type {
  GenAIEvalConfig,
  GenAIEvalProfile,
} from "$lib/components/scouter/genai/types";
import { ServerPaths } from "$lib/components/api/routes";
import type { DriftProfileUri } from "./types";
import { RegistryType } from "$lib/utils";
import {
  type DriftAlertPaginationRequest,
  type DriftAlertPaginationResponse,
} from "./alert/types";
import type { TimeRange } from "$lib/components/trace/types";

// ============================================================================
// TYPE GUARDS - ALERT DISPATCH CONFIGS
// ============================================================================

export function hasConsoleConfig(config: AlertDispatchConfig): boolean {
  return !!config.Console;
}

export function hasSlackConfig(config: AlertDispatchConfig): boolean {
  return !!config.Slack;
}

export function hasOpsGenieConfig(config: AlertDispatchConfig): boolean {
  return !!config.OpsGenie;
}

// ============================================================================
// DRIFT PROFILE TYPES AND HELPERS
// ============================================================================

export type DriftProfile = {
  [DriftType.Spc]: SpcDriftProfile;
  [DriftType.Psi]: PsiDriftProfile;
  [DriftType.Custom]: CustomDriftProfile;
  [DriftType.GenAI]: GenAIEvalProfile;
};

export interface UiProfile {
  profile_uri: string;
  profile: DriftProfile;
}

export type DriftConfigType =
  | CustomMetricDriftConfig
  | PsiDriftConfig
  | SpcDriftConfig
  | GenAIEvalConfig;

export type DriftProfileResponse = Record<DriftType, UiProfile>;

export function getProfileFeatures(
  drift_type: DriftType,
  profile: DriftProfile
): string[] {
  const variables: string[] =
    drift_type === DriftType.Custom
      ? Object.keys(profile.Custom.metrics)
      : drift_type === DriftType.GenAI
      ? profile.GenAI.task_ids
      : drift_type === DriftType.Psi
      ? profile.Psi.config.alert_config.features_to_monitor
      : profile.Spc.config.alert_config.features_to_monitor;

  return variables.sort();
}

export function getProfileConfig(
  drift_type: DriftType,
  profile: DriftProfile
): DriftConfigType {
  const variables =
    drift_type === DriftType.Custom
      ? profile.Custom.config
      : drift_type === DriftType.GenAI
      ? profile.GenAI.config
      : drift_type === DriftType.Psi
      ? profile.Psi.config
      : profile.Spc.config;

  return variables;
}

export function getProfileDataWithConfig(
  profiles: DriftProfileResponse,
  driftType: DriftType
): { profile: UiProfile; config: DriftConfigType } {
  const uiProfile = profiles[driftType];
  const config = getProfileConfig(driftType, uiProfile.profile);
  return { profile: uiProfile, config };
}

/**
 * Mapping object to replace conditional logic.
 * This ensures that adding a new DriftType requires a corresponding
 * entry here, preventing runtime regressions.
 */
const PROFILE_EXTRACTOR: {
  [K in DriftType]: (profile: DriftProfile) => DriftProfile[K];
} = {
  [DriftType.Spc]: (p) => p[DriftType.Spc],
  [DriftType.Psi]: (p) => p[DriftType.Psi],
  [DriftType.Custom]: (p) => p[DriftType.Custom],
  [DriftType.GenAI]: (p) => p[DriftType.GenAI],
};

/**
 * Extracts the specific profile variant from the response.
 * Utilizing generics <T> ensures the return type matches the input driftType exactly.
 */
export function getProfileFromResponse<T extends DriftType>(
  driftType: T,
  profiles: DriftProfileResponse
): DriftProfile[T] {
  const uiProfile = profiles[driftType];

  if (!uiProfile) {
    throw new Error(
      `Profile for drift type ${driftType} not found in response.`
    );
  }

  // We invoke the mapper to extract the specific variant from the DriftProfile union/object
  return PROFILE_EXTRACTOR[driftType](uiProfile.profile) as DriftProfile[T];
}

/**
 * Standalone extractor for raw DriftProfile objects.
 */
export function extractProfile<T extends DriftType>(
  profile: DriftProfile,
  driftType: T
): DriftProfile[T] {
  return PROFILE_EXTRACTOR[driftType](profile) as DriftProfile[T];
}

// ============================================================================
// TYPE GUARDS - DRIFT CONFIG TYPES
// ============================================================================

export function isCustomConfig(
  config: DriftConfigType
): config is CustomMetricDriftConfig {
  return config.drift_type === DriftType.Custom;
}

export function isGenAIConfig(
  config: DriftConfigType
): config is GenAIEvalConfig {
  return config.drift_type === DriftType.GenAI;
}

export function isPsiConfig(config: DriftConfigType): config is PsiDriftConfig {
  return config.drift_type === DriftType.Psi;
}

export function isSpcConfig(config: DriftConfigType): config is SpcDriftConfig {
  return config.drift_type === DriftType.Spc;
}
//====================================================
// SERVER API HELPERS
// ============================================================================

export async function getMonitoringDriftProfiles(
  fetch: typeof globalThis.fetch,
  uid: string,
  driftMap: Record<string, DriftProfileUri>,
  registryType: RegistryType
): Promise<DriftProfileResponse> {
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

export async function getServerDriftAlerts(
  fetch: typeof globalThis.fetch,
  request: DriftAlertPaginationRequest
): Promise<DriftAlertPaginationResponse> {
  let resp = await createInternalApiClient(fetch).post(
    ServerPaths.MONITORING_ALERTS,
    request
  );

  let alerts = (await resp.json()) as DriftAlertPaginationResponse;
  return alerts;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export function getLabelFromValue(value: string): string {
  const labelMap: Record<string, string> = {
    "15min-live": "Live (15min)",
    "15min": "Past 15 Minutes",
    "30min": "Past 30 Minutes",
    "1hour": "Past 1 Hour",
    "4hours": "Past 4 Hours",
    "12hours": "Past 12 Hours",
    "24hours": "Past 24 Hours",
    "7days": "Past 7 Days",
    "30days": "Past 30 Days",
  };
  return labelMap[value] || "Custom Range";
}

export function getDriftProfileUriMap(
  metadata: any,
  registryType: RegistryType
) {
  if (registryType === RegistryType.Prompt) {
    return metadata.metadata.drift_profile_uri_map ?? {};
  }
  return (
    metadata.metadata.interface_metadata?.save_metadata
      ?.drift_profile_uri_map ?? {}
  );
}
