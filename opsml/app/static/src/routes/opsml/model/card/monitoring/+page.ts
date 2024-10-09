import {
  getDriftProfile,
  getFeatureDriftValues,
  createSpcDriftViz,
  createSpcFeatureDistributionViz,
  getMonitorAlerts,
  getAlertMetrics,
  createAlertMetricViz,
} from "$lib/scripts/monitoring/utils";
import {
  type SpcDriftProfile,
  type SpcFeatureDriftProfile,
  type FeatureDriftValues,
  TimeWindow,
  type ChartjsData,
  type MonitorAlerts,
  type AlertMetrics,
  ProfileType,
} from "$lib/scripts/types";

/** @type {import('./$types').PageLoad} */
export async function load({ url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;

  let profiles: Map<ProfileType, SpcDriftProfile> = new Map();

  profiles[ProfileType.SPC] = (
    await getDriftProfile(repository!, name!, version!)
  ).profile as SpcDriftProfile | undefined;

  console.log(profiles);

  // check if drift profile exists
  if (profiles) {
    let profile = profiles[ProfileType.SPC];
    const features = Object.keys(profile.features);

    // get first feature as target feature
    let targetFeature: SpcFeatureDriftProfile = profile.features[features[0]];

    // change target feature if targets are available
    if (profile.config.targets.length > 0) {
      targetFeature = profile.features[profile.config.targets[0]];
    }

    let featureValues = (await getFeatureDriftValues(
      repository!,
      name!,
      version!,
      TimeWindow.TwentyFourHours,
      1000,
      targetFeature.id
    )) as FeatureDriftValues;

    let driftVizData = createSpcDriftViz(
      featureValues.features[targetFeature.id],
      targetFeature
    );

    let featureDistVizData = (await createSpcFeatureDistributionViz(
      repository!,
      name!,
      version!,
      targetFeature.id,
      TimeWindow.TwentyFourHours,
      1000,
      targetFeature
    )) as ChartjsData;

    let alerts = (await getMonitorAlerts(
      repository!,
      name!,
      version!
    )) as MonitorAlerts;

    let alertMetrics = (await getAlertMetrics(
      repository!,
      name!,
      version!,
      TimeWindow.TwentyFourHours,
      1000
    )) as AlertMetrics;

    let alertMetricVizData = (await createAlertMetricViz(
      alertMetrics
    )) as ChartjsData;

    return {
      repository,
      name,
      version,
      driftProfiles: profiles,
      targetFeature,
      features,
      featureValues,
      driftVizData,
      timeWindow: TimeWindow.TwentyFourHours,
      max_data_points: 1000,
      featureDistVizData,
      alerts,
      showConfig: false,
      profileType: ProfileType.SPC,
      alertMetricVizData,
    };
  } else {
    return {
      repository,
      name,
      version,
      driftProfiles: null,
    };
  }
}
