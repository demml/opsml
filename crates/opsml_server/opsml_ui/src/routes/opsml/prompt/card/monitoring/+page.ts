export const ssr = false;

import { getMaxDataPoints } from "$lib/utils";
import type { PageLoad } from "./$types";
import {
  getDriftProfiles,
  getProfileConfig,
  getProfileFeatures,
  type UiProfile,
} from "$lib/components/card/monitoring/util";
import { DriftType, TimeInterval } from "$lib/components/card/monitoring/types";
import {
  getLatestMetricsExample,
  getLatestMetrics,
  getCurrentMetricData,
} from "$lib/components/card/monitoring/util";
import { getDriftAlerts } from "$lib/components/card/monitoring/alert/utils";
import { getLLMRecordPage } from "$lib/components/card/monitoring/util";
import type { ServiceInfo } from "$lib/components/card/monitoring/types";
import { mockLLMDriftPageResponse } from "$lib/components/card/monitoring/example";
import { RegistryType } from "$lib/utils";

export const load: PageLoad = async ({ parent }) => {
  const { metadata, registry, registryPath } = await parent();

  let profiles = await getDriftProfiles(
    metadata.uid,
    metadata.metadata.drift_profile_uri_map ?? {},
    registry
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
  //let latestMetrics = await getLatestMetricsExample(
  //  profiles,
  //  TimeInterval.SixHours,
  //  maxDataPoints
  //);

  let latestMetrics = await getLatestMetrics(
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

  let currentAlerts = await getDriftAlerts(
    currentConfig.space,
    currentConfig.name,
    currentConfig.version,
    TimeInterval.SixHours,
    true
  );

  let service_info: ServiceInfo = {
    space: currentConfig.space,
    name: currentConfig.name,
    version: currentConfig.version,
  };

  let currentLLMRecords = await getLLMRecordPage(
    service_info,
    undefined,
    undefined
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
    currentLLMRecords,
  };
};
