import { getMaxDataPoints } from "$lib/utils";
import type { PageServerLoad } from "./$types";
import {
  getLatestMonitoringMetrics,
  getMonitoringAlerts,
  getMonitoringDriftProfiles,
  getProfileConfig,
  getProfileFeatures,
  type UiProfile,
} from "$lib/components/card/monitoring/utils";
import { DriftType, TimeInterval } from "$lib/components/card/monitoring/types";
import { getCurrentMetricData } from "$lib/components/card/monitoring/utils";

export const load: PageServerLoad = async ({ parent, fetch }) => {
  const { metadata, registryType } = await parent();

  let profiles = await getMonitoringDriftProfiles(
    fetch,
    metadata.uid,
    metadata.metadata.interface_metadata.save_metadata.drift_profile_uri_map ??
      {},
    registryType
  );

  // get all keys which should be of DriftType
  const keys: DriftType[] = Object.keys(profiles)
    .filter((key): key is DriftType => {
      return Object.values(DriftType).includes(key as DriftType);
    })
    .sort();

  let currentDriftType = keys[0];
  let currentProfile: UiProfile = profiles[currentDriftType];
  let currentNames: string[] = getProfileFeatures(
    currentDriftType,
    currentProfile.profile
  );
  let currentName: string = currentNames[0];
  let currentConfig = getProfileConfig(
    currentDriftType,
    currentProfile.profile
  );
  let maxDataPoints = getMaxDataPoints();

  // get latest metrics for all available drift profiles
  let latestMetrics = await getLatestMonitoringMetrics(
    fetch,
    profiles,
    TimeInterval.SixHours,
    maxDataPoints
  );

  // Filter latest metrics to the current drift type
  let currentMetricData = getCurrentMetricData(
    latestMetrics,
    currentDriftType,
    currentName
  );

  let currentAlerts = await getMonitoringAlerts(
    fetch,
    currentConfig.space,
    currentConfig.name,
    currentConfig.version,
    TimeInterval.SixHours,
    true
  );

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
  };
};
