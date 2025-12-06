import { getMaxDataPoints, RegistryType } from "$lib/utils";
import {
  getLatestMonitoringMetrics,
  getLLMMonitoringRecordPage,
  getMonitoringAlerts,
  getMonitoringDriftProfiles,
  getProfileConfig,
  getProfileFeatures,
  getCurrentMetricData,
  type UiProfile,
  type DriftProfileResponse,
} from "$lib/components/card/monitoring/utils";
import {
  DriftType,
  TimeInterval,
  type ServiceInfo,
  type BinnedDriftMap,
  type MetricData,
  type DriftProfileUri,
} from "$lib/components/card/monitoring/types";
import type { Alert } from "$lib/components/card/monitoring/alert/types";

/**
 * Parent data interface expected from SvelteKit page hierarchy
 * Supports different metadata structures for different registry types
 */
export interface MonitoringParentData {
  metadata: {
    uid: string;
    metadata: {
      // For Prompt registries - direct drift profile URI map
      drift_profile_uri_map?: Record<string, DriftProfileUri>;
      // For Model/Data/Experiment registries - nested structure
      interface_metadata?: {
        save_metadata?: {
          drift_profile_uri_map?: Record<string, DriftProfileUri>;
        };
      };
    };
  };
  registryType: RegistryType;
}

/**
 * Extracts the drift profile URI map from metadata based on registry type
 *
 * Different registry types store drift profile URI maps in different locations:
 * - Prompt registries: metadata.metadata.drift_profile_uri_map
 * - Model/Data/Experiment registries: metadata.metadata.interface_metadata.save_metadata.drift_profile_uri_map
 *
 * @param metadata - The metadata object containing drift profile information
 * @param registryType - The type of registry (Prompt, Model, Data, or Experiment)
 * @returns Record of drift profile URI mappings, empty object if none found
 */
function getDriftProfileUriMap(
  metadata: MonitoringParentData["metadata"],
  registryType: RegistryType
): Record<string, DriftProfileUri> {
  if (registryType === RegistryType.Prompt) {
    return metadata.metadata.drift_profile_uri_map ?? {};
  }

  // Model, Data, Experiment registries
  return (
    metadata.metadata.interface_metadata?.save_metadata
      ?.drift_profile_uri_map ?? {}
  );
}

/**
 * Configuration options for monitoring dashboard data loading
 */
export interface MonitoringDashboardLoadOptions {
  /** Initial time interval for metrics, defaults to 6 hours */
  initialTimeInterval?: TimeInterval;
  /** Whether to load LLM records for prompt registries, defaults to true */
  loadLLMRecords?: boolean;
  /** Whether to load alerts, defaults to true */
  loadAlerts?: boolean;
}

/**
 * Return type for monitoring dashboard data
 */
export interface MonitoringDashboardData {
  profiles: DriftProfileResponse;
  keys: DriftType[];
  currentName: string;
  currentNames: string[];
  currentDriftType: DriftType;
  currentProfile: UiProfile;
  currentConfig: ReturnType<typeof getProfileConfig>;
  latestMetrics: BinnedDriftMap;
  currentMetricData: MetricData;
  maxDataPoints: number;
  currentAlerts: Alert[];
  currentLLMRecords?: any; // Type this more specifically based on your LLM record structure
}

/**
 * Loads monitoring dashboard data for SvelteKit pages
 *
 * This function encapsulates the common data loading logic for monitoring
 * dashboards, providing consistent initialization across different routes.
 *
 * @param fetch - SvelteKit fetch function for server-side requests
 * @param parentData - Data from parent layout loaders
 * @param options - Configuration options for data loading
 * @returns Promise resolving to monitoring dashboard data
 *
 * @example
 * ```typescript
 * // In your +page.ts file
 * export const load: PageLoad = async ({ parent, fetch }) => {
 *   const parentData = await parent();
 *   return await loadMonitoringDashboardData(fetch, parentData);
 * };
 * ```
 */
export async function loadMonitoringDashboardData(
  fetch: typeof globalThis.fetch,
  parentData: MonitoringParentData,
  options: MonitoringDashboardLoadOptions = {}
): Promise<MonitoringDashboardData> {
  const {
    initialTimeInterval = TimeInterval.SixHours,
    loadLLMRecords = true,
    loadAlerts = true,
  } = options;

  const { metadata, registryType } = parentData;

  // Extract drift profile URI map based on registry type
  const profileMap = getDriftProfileUriMap(metadata, registryType);

  // Load drift profiles
  const profiles = await getMonitoringDriftProfiles(
    fetch,
    metadata.uid,
    profileMap,
    registryType
  );

  // Extract and sort available drift types
  const keys: DriftType[] = Object.keys(profiles)
    .filter((key): key is DriftType =>
      Object.values(DriftType).includes(key as DriftType)
    )
    .sort();

  // Validate that we have at least one drift type
  if (keys.length === 0) {
    throw new Error("No valid drift types found in profiles");
  }

  // Initialize current selections with first available drift type
  const currentDriftType = keys[0];
  const currentProfile: UiProfile = profiles[currentDriftType];
  const currentNames: string[] = getProfileFeatures(
    currentDriftType,
    currentProfile.profile
  );

  // Validate that we have at least one feature name
  if (currentNames.length === 0) {
    throw new Error(
      `No feature names found for drift type: ${currentDriftType}`
    );
  }

  const currentName: string = currentNames[0];
  const currentConfig = getProfileConfig(
    currentDriftType,
    currentProfile.profile
  );
  const maxDataPoints = getMaxDataPoints();

  // Load metrics data
  const latestMetrics = await getLatestMonitoringMetrics(
    fetch,
    profiles,
    initialTimeInterval,
    maxDataPoints
  );

  // Get current metric data for selected drift type and name
  const currentMetricData = getCurrentMetricData(
    latestMetrics,
    currentDriftType,
    currentName
  );

  // Load alerts if enabled
  const currentAlerts = loadAlerts
    ? await getMonitoringAlerts(
        fetch,
        currentConfig.uid,
        initialTimeInterval,
        true
      )
    : [];

  // Load LLM records for prompt registries if enabled
  let currentLLMRecords;
  if (loadLLMRecords && registryType === RegistryType.Prompt) {
    const serviceInfo: ServiceInfo = {
      space: currentConfig.space,
      uid: currentConfig.uid,
    };

    currentLLMRecords = await getLLMMonitoringRecordPage(
      fetch,
      serviceInfo,
      undefined,
      undefined
    );
  }

  return {
    profiles,
    keys,
    currentName,
    currentNames,
    currentDriftType,
    currentProfile,
    currentConfig,
    latestMetrics,
    currentMetricData,
    maxDataPoints,
    currentAlerts,
    currentLLMRecords,
  };
}
