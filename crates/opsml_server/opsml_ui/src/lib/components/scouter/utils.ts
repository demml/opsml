import type { AlertDispatchConfig } from "./types";
// Add these type guard functions
export function hasConsoleConfig(config: AlertDispatchConfig): boolean {
  return !!config.Console;
}

export function hasSlackConfig(config: AlertDispatchConfig): boolean {
  return !!config.Slack;
}

export function hasOpsGenieConfig(config: AlertDispatchConfig): boolean {
  return !!config.OpsGenie;
}

import type { SpcDriftConfig, SpcDriftProfile } from "./spc/types";
import type { PsiDriftConfig, PsiDriftProfile } from "./psi/types";
import { createInternalApiClient } from "$lib/api/internalClient";
import type {
  CustomDriftProfile,
  CustomMetricDriftConfig,
} from "./custom/types";
import { DriftType, type BinnedDriftMap, type MetricData } from "./types";
import type {
  GenAIEvalConfig,
  GenAIEvalProfile,
} from "$lib/components/scouter/genai/types";

import { ServerPaths } from "$lib/components/api/routes";
import type { DriftProfileUri } from "./types";
import { RegistryType } from "$lib/utils";
import {
  type Alert,
  type DriftAlertPaginationRequest,
  type DriftAlertPaginationResponse,
} from "./alert/types";
import type { TimeRange } from "$lib/components/trace/types";

export type DriftProfile = {
  Spc: SpcDriftProfile;
  Psi: PsiDriftProfile;
  Custom: CustomDriftProfile;
  GenAI: GenAIEvalProfile;
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

// Add this new helper function
export function getProfileDataWithConfig(
  profiles: DriftProfileResponse,
  driftType: DriftType
): { profile: UiProfile; config: DriftConfigType } {
  console.log("profiles:", profiles);
  const uiProfile = profiles[driftType];
  console.log("uiProfile:", uiProfile);

  const config = getProfileConfig(driftType, uiProfile.profile);
  return { profile: uiProfile, config };
}

export function extractProfile(
  profile: DriftProfile,
  drift_type: DriftType
): SpcDriftProfile | PsiDriftProfile | CustomDriftProfile | GenAIEvalProfile {
  return drift_type === DriftType.Custom
    ? profile.Custom
    : drift_type === DriftType.GenAI
    ? profile.GenAI
    : drift_type === DriftType.Psi
    ? profile.Psi
    : profile.Spc;
}

/**
 * Specifies which GenAI metric category to retrieve
 */
export enum GenAIMetricType {
  Task = "task",
  Workflow = "workflow",
}

/**
 * Retrieves metric data for a specific drift type and name
 * @param latestMetrics - The binned drift map containing all metrics
 * @param currentDriftType - The drift type to query
 * @param currentName - The feature/metric name to retrieve
 * @param genAIMetricType - Optional: For GenAI, specify 'task' or 'workflow' (defaults to 'task')
 * @returns The metric data or null if not found
 */
export function getCurrentMetricData(
  latestMetrics: BinnedDriftMap,
  currentDriftType: DriftType,
  currentName: string,
  genAIMetricType: GenAIMetricType = GenAIMetricType.Task
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
    case DriftType.GenAI:
      return latestMetrics[DriftType.GenAI]?.[genAIMetricType]?.metrics[
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

/** Helper for getting latest monitoring metrics
 * @param profiles - drift profiles to get metrics for
 * @param time_interval - time interval for the metrics
 * @param max_data_points - maximum data points to retrieve
 * @param fetch - fetch function
 * @returns binned drift map with latest metrics
 */
async function getLatestMonitoringMetrics(
  fetch: typeof globalThis.fetch,
  profiles: DriftProfileResponse,
  time_range: TimeRange,
  max_data_points: number,
  server_path: ServerPaths
): Promise<BinnedDriftMap> {
  let resp = await createInternalApiClient(fetch).post(server_path, {
    profiles,
    time_range,
    max_data_points,
  });

  let binnedMap = (await resp.json()) as BinnedDriftMap;
  return binnedMap;
}

export async function getSpcDriftMetrics(
  fetch: typeof globalThis.fetch,
  profiles: DriftProfileResponse,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedDriftMap> {
  return getLatestMonitoringMetrics(
    fetch,
    profiles,
    time_range,
    max_data_points,
    ServerPaths.SPC_DRIFT
  );
}

export async function getPsiDriftMetrics(
  fetch: typeof globalThis.fetch,
  profiles: DriftProfileResponse,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedDriftMap> {
  return getLatestMonitoringMetrics(
    fetch,
    profiles,
    time_range,
    max_data_points,
    ServerPaths.PSI_DRIFT
  );
}

export async function getCustomDriftMetrics(
  fetch: typeof globalThis.fetch,
  profiles: DriftProfileResponse,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedDriftMap> {
  return getLatestMonitoringMetrics(
    fetch,
    profiles,
    time_range,
    max_data_points,
    ServerPaths.CUSTOM_DRIFT
  );
}

export async function getGenAIEvalTaskMetrics(
  fetch: typeof globalThis.fetch,
  profiles: DriftProfileResponse,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedDriftMap> {
  return getLatestMonitoringMetrics(
    fetch,
    profiles,
    time_range,
    max_data_points,
    ServerPaths.GENAI_TASK_DRIFT
  );
}

export async function getGenAIEvalWorkflowMetrics(
  fetch: typeof globalThis.fetch,
  profiles: DriftProfileResponse,
  time_range: TimeRange,
  max_data_points: number
): Promise<BinnedDriftMap> {
  return getLatestMonitoringMetrics(
    fetch,
    profiles,
    time_range,
    max_data_points,
    ServerPaths.GENAI_WORKFLOW_DRIFT
  );
}

/**
 * Maps drift types to their corresponding metric loader functions
 */
const METRIC_LOADERS = {
  [DriftType.Spc]: getSpcDriftMetrics,
  [DriftType.Psi]: getPsiDriftMetrics,
  [DriftType.Custom]: getCustomDriftMetrics,
  [DriftType.GenAI]: getGenAIEvalTaskMetrics, // Default to task metrics
} as const;

/**
 * Loads metrics for a specific drift type
 */
export async function loadMetricsForDriftType(
  fetch: typeof globalThis.fetch,
  driftType: DriftType,
  profiles: DriftProfileResponse,
  timeRange: TimeRange,
  maxDataPoints: number
): Promise<BinnedDriftMap> {
  const loader = METRIC_LOADERS[driftType];
  if (!loader) {
    throw new Error(`No metric loader found for drift type: ${driftType}`);
  }

  return loader(fetch, profiles, timeRange, maxDataPoints);
}

/**
 * Loads both task and workflow metrics for GenAI profiles
 */
export async function loadGenAIMetrics(
  fetch: typeof globalThis.fetch,
  profiles: DriftProfileResponse,
  timeRange: TimeRange,
  maxDataPoints: number
): Promise<{ task: BinnedDriftMap; workflow: BinnedDriftMap }> {
  const [task, workflow] = await Promise.all([
    getGenAIEvalTaskMetrics(fetch, profiles, timeRange, maxDataPoints),
    getGenAIEvalWorkflowMetrics(fetch, profiles, timeRange, maxDataPoints),
  ]);

  return { task, workflow };
}

/**
 * Type guard to check if metrics are available for a drift type
 */
export function hasMetricsForDriftType(
  driftType: DriftType,
  metrics: BinnedDriftMap | null
): boolean {
  if (!metrics) return false;
  return driftType in metrics && metrics[driftType] !== null;
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

/**
 * Helper to get label from time range value
 * Maps the value back to a human-readable label
 */
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

export async function loadAllMetrics(
  fetch: typeof globalThis.fetch,
  profiles: DriftProfileResponse,
  timeRange: TimeRange,
  maxDataPoints: number
): Promise<BinnedDriftMap> {
  // Explicitly type the accumulator to prevent improper inference
  const driftMap: BinnedDriftMap = {};

  const requests = Object.entries(profiles).map(
    async ([driftTypeKey, profile]) => {
      const driftType = driftTypeKey as DriftType;
      try {
        if (driftType === DriftType.GenAI) {
          const { task, workflow } = await loadGenAIMetrics(
            fetch,
            { [DriftType.GenAI]: profile },
            timeRange,
            maxDataPoints
          );

          // Narrow the results from the BinnedDriftMap returned by loaders
          const taskData = task[DriftType.GenAI];
          const workflowData = workflow[DriftType.GenAI];

          if (taskData && workflowData) {
            (driftMap as any)[DriftType.GenAI] = {
              task: taskData,
              workflow: workflowData,
            };
          }
        } else {
          const metrics = await loadMetricsForDriftType(
            fetch,
            driftType,
            { [driftType]: profile },
            timeRange,
            maxDataPoints
          );

          const metricData = metrics[driftType];
          if (metricData) {
            (driftMap as any)[driftType] = metricData;
          }
        }
      } catch (err) {
        console.error(`[Drift Architect] Failed loading ${driftType}:`, err);
      }
    }
  );

  await Promise.all(requests);
  return driftMap;
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
