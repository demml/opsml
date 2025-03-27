export const ssr = false;

import { opsmlClient } from "$lib/components/api/client.svelte";
import { getMaxDataPoints } from "$lib/utils";
import type { PageLoad } from "./$types";
import {
  getDriftProfiles,
  getProfileConfig,
  getProfileFeatures,
} from "$lib/components/monitoring/util";
import { DriftType, TimeInterval } from "$lib/components/monitoring/types";
import {
  getLatestMetricsExample,
  getCurrentMetricData,
} from "$lib/components/monitoring/util";

export const load: PageLoad = async ({ parent }) => {
  await opsmlClient.validateAuth(true);

  const { metadata, registry, registryPath } = await parent();

  let profiles = await getDriftProfiles(metadata);

  // get all keys which should be of DriftType
  const keys: DriftType[] = Object.keys(profiles)
    .filter((key): key is DriftType => {
      return Object.values(DriftType).includes(key as DriftType);
    })
    .sort();

  let currentDriftType = keys[1];
  let currentProfile = profiles[currentDriftType];
  let currentNames: string[] = getProfileFeatures(
    currentDriftType,
    currentProfile
  );
  let currentName: string = currentNames[0];
  let currentConfig = getProfileConfig(currentDriftType, currentProfile);
  let maxDataPoints = getMaxDataPoints();

  // get latest metrics
  let latestMetrics = await getLatestMetricsExample(
    profiles,
    TimeInterval.SixHours,
    maxDataPoints
  );

  let currentMetricData = getCurrentMetricData(
    latestMetrics,
    currentDriftType,
    currentName
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
  };
};
