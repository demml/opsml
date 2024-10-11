import {
  getDriftProfile,
  getAlertMetrics,
  createAlertMetricViz,
  getMonitorAlerts,
} from "$lib/scripts/monitoring/utils";
import {
  type SpcDriftProfile,
  ProfileType,
  TimeWindow,
  type AlertMetrics,
  type ChartjsData,
  type MonitorAlerts,
} from "$lib/scripts/types";

export const ssr = false;

/** @type {import('./$types').LayoutLoad} */
export async function load({ url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;
  let feature = (url as URL).searchParams.get("feature") as string | undefined;
  let type = (url as URL).searchParams.get("type") as string | undefined;
  let timeWindow = (url as URL).searchParams.get("time") as string | undefined;
  let max_data_points = 1000;

  timeWindow = timeWindow || TimeWindow.TwentyFourHours;
  let profiles: Map<ProfileType, SpcDriftProfile> = new Map();

  profiles[ProfileType.SPC] = (
    await getDriftProfile(repository!, name!, version!)
  ).profile as SpcDriftProfile | undefined;

  if (profiles) {
    let profile = profiles[ProfileType.SPC];

    const features = Object.keys(profile.features);

    // assign target feature if feature is provided

    if (!feature) {
      if (profile.config.targets.length > 0) {
        feature = profile.config.targets[0];
      } else {
        feature = features[0];
      }
    }

    if (!type) {
      type = ProfileType.SPC;
    }

    return {
      repository: repository,
      name: name,
      version: version,
      feature: feature,
      features: features,
      type: type,
      driftProfiles: profiles,
      showConfig: false,
      timeWindow: timeWindow,
    };
  }
  return {
    repository,
    name,
    version,
    feature: null,
    type: ProfileType.SPC,
    driftProfiles: profiles,
    showConfig: false,
    timeWindow: timeWindow,
  };
}
