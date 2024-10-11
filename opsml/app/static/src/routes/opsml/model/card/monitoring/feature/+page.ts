import {
  getFeatureDriftValues,
  createSpcDriftViz,
  createSpcFeatureDistributionViz,
} from "$lib/scripts/monitoring/utils";
import {
  type SpcFeatureDriftProfile,
  ProfileType,
  type SpcDriftProfile,
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
  const feature = parentData.feature as string;
  const timeWindow = parentData.timeWindow;
  const repository = parentData.repository;
  const name = parentData.name;
  const version = parentData.version;
  const max_data_points = parentData.max_data_points;

  const profile = profiles[profileType] as SpcDriftProfile;
  const targetFeature: SpcFeatureDriftProfile = profile.features[feature];

  const featureValues = await getFeatureDriftValues(
    repository,
    name,
    version,
    timeWindow,
    max_data_points,
    targetFeature.id
  );

  const driftVizData = createSpcDriftViz(
    featureValues.features[targetFeature.id],
    targetFeature
  );

  const featureDistVizData = await createSpcFeatureDistributionViz(
    repository,
    name,
    version,
    targetFeature.id,
    timeWindow,
    max_data_points,
    targetFeature
  );

  const vizData: MonitoringVizData = {
    driftVizData,
    featureDistVizData,
  };

  const monitorData: MonitorData = {
    vizData,
    feature: targetFeature,
  };

  const returnData = {
    ...parentData,
    driftProfiles: profiles,
    targetFeature,
    timeWindow: timeWindow,
    max_data_points: max_data_points,
    monitorData,
  };

  return returnData;
}
