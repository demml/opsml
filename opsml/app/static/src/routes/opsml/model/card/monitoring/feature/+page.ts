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
} from "$lib/scripts/monitoring/types";

/** @type {import('./$types').PageLoad} */
export async function load({ parent }) {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-call
  const data = (await parent()) as MonitoringLayoutPage;

  const profiles = data.driftProfiles;
  const profileType: ProfileType = data.type;
  const feature = data.feature!;
  const timeWindow = data.timeWindow;
  const repository = data.repository;
  const name = data.name;
  const version = data.version;
  const max_data_points = 1000;

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

  let alerts = (await getMonitorAlerts(
    repository,
    name,
    version
  )) as MonitorAlerts;

  let alertMetrics = (await getAlertMetrics(
    repository,
    name,
    version,
    timeWindow,
    max_data_points
  )) as AlertMetrics;

  let alertMetricVizData = (await createAlertMetricViz(
    alertMetrics
  )) as ChartjsData;

  let vizData: MonitoringVizData = {
    driftVizData,
    featureDistVizData,
    alertMetricVizData,
  };

  let returnData = {
    ...data,
    driftProfiles: profiles,
    targetFeature,
    timeWindow: timeWindow,
    max_data_points: max_data_points,
    alerts,
    monitorVizData: vizData,
  };

  return returnData;
}
