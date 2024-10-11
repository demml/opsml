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
import {
  type MonitoringVizData,
  type MonitoringLayoutPage,
  type MonitorData,
} from "$lib/scripts/monitoring/types";

/** @type {import('./$types').PageLoad} */
export async function load({ parent }) {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-call
  const parentData = (await parent()) as MonitoringLayoutPage;

  const profiles = parentData.driftProfiles;
  const profileType: ProfileType = parentData.type;
  const feature = parentData.feature;
  const timeWindow = parentData.timeWindow;
  const repository = parentData.repository;
  const name = parentData.name;
  const version = parentData.version;
  const max_data_points = parentData.max_data_points;

  let profile = profiles[profileType];
  let targetFeature: SpcFeatureDriftProfile = profile.features[feature];

  let featureValues = (await getFeatureDriftValues(
    repository,
    name,
    version,
    timeWindow,
    max_data_points,
    targetFeature.id
  )) as FeatureDriftValues;

  let driftVizData = createSpcDriftViz(
    featureValues.features[targetFeature.id],
    targetFeature
  );

  let featureDistVizData = (await createSpcFeatureDistributionViz(
    repository,
    name,
    version,
    targetFeature.id,
    timeWindow,
    max_data_points,
    targetFeature
  )) as ChartjsData;

  let vizData: MonitoringVizData = {
    driftVizData,
    featureDistVizData,
  };

  let monitorData: MonitorData = {
    vizData,
    feature: targetFeature,
  };

  let returnData = {
    ...parentData,
    driftProfiles: profiles,
    targetFeature,
    timeWindow: timeWindow,
    max_data_points: max_data_points,
    monitorData,
  };

  return returnData;
}
