import {
  getDriftProfile,
  getFeatureDriftValues,
  createDriftViz,
  createFeatureDistributionViz,
  getMonitorAlertData,
} from "$lib/scripts/monitoring/utils";
import {
  type DriftProfile,
  type FeatureDriftProfile,
  type FeatureDriftValues,
  TimeWindow,
  type ChartjsData,
  type MonitorAlerts,
} from "$lib/scripts/types";

/** @type {import('./$types').PageLoad} */
export async function load({ url }) {
  console.log("monitoring page load");
  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;

  const profile = (await getDriftProfile("ml-platform-1", "model-1", "0.1.0"))
    .profile as DriftProfile | undefined;

  // check if drift profile exists
  if (profile) {
    const features = Object.keys(profile.features);

    // get first feature as target feature
    let targetFeature: FeatureDriftProfile = profile.features[features[0]];

    // change target feature if targets are available
    if (profile.config.targets.length > 0) {
      targetFeature = profile.features[profile.config.targets[0]];
    }

    let featureValues = (await getFeatureDriftValues(
      "ml-platform-1",
      "model-1",
      "0.1.0",
      TimeWindow.TwentyFourHours,
      1000,
      targetFeature.id
    )) as FeatureDriftValues;

    let driftVizData = createDriftViz(
      featureValues.features[targetFeature.id],
      targetFeature
    );

    let featureDistVizData = (await createFeatureDistributionViz(
      "ml-platform-1",
      "model-1",
      "0.1.0",
      targetFeature.id,
      TimeWindow.TwentyFourHours,
      1000,
      targetFeature
    )) as ChartjsData;

    let alerts = (await getMonitorAlertData(
      "ml-platform-1",
      "model-1",
      "0.1.0"
    )) as MonitorAlerts;

    return {
      repository: "ml-platform-1",
      name: "model-1",
      version: "0.1.0",
      driftProfile: profile,
      targetFeature,
      features,
      featureValues,
      driftVizData,
      timeWindow: TimeWindow.TwentyFourHours,
      max_data_points: 1000,
      featureDistVizData,
      alerts,
      showProfile: false,
    };
  } else {
    return {
      repository,
      name,
      version,
      driftProfile: null,
    };
  }
}
