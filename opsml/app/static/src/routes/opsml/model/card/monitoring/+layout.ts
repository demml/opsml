import {
  getDriftProfile,
  getAlertMetrics,
  createAlertMetricViz,
  getMonitorAlerts,
  getObservabilityMetrics,
  createObservabilityViz,
  type RouteVizData,
} from "$lib/scripts/monitoring/utils";
import { getScreenSize } from "$lib/scripts/utils";
import {
  type SpcDriftProfile,
  ProfileType,
  TimeWindow,
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
  const max_data_points = getScreenSize();

  timeWindow = timeWindow || TimeWindow.TwentyFourHours;
  const profiles: Map<ProfileType, SpcDriftProfile> = new Map();

  profiles[ProfileType.SPC] = (
    await getDriftProfile(repository!, name!, version!)
  ).profile;

  if (profiles) {
    const profile = profiles[ProfileType.SPC] as SpcDriftProfile;

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

    const alerts = await getMonitorAlerts(repository!, name!, version!);

    const alertMetrics = await getAlertMetrics(
      repository!,
      name!,
      version!,
      timeWindow,
      max_data_points
    );

    const alertMetricVizData = createAlertMetricViz(alertMetrics);

    const observabilityMetrics = await getObservabilityMetrics(
      repository!,
      name!,
      version!,
      timeWindow,
      max_data_points
    );

    let routeViz: RouteVizData[] = [];
    if (observabilityMetrics.metrics.length > 0) {
      routeViz = createObservabilityViz(observabilityMetrics);
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
      alerts: alerts,
      alertMetricVizData: alertMetricVizData,
      max_data_points: max_data_points,
      routeViz,
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
    max_data_points: max_data_points,
  };
}
