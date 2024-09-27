import { server } from "./server";
import { render } from "@testing-library/svelte";
import { driftProfile, featureDriftValues, exampleAlerts } from "./constants";
import {
  type DriftValues,
  type FeatureDriftProfile,
  TimeWindow,
} from "$lib/scripts/types";
import MonitoringPage from "../routes/opsml/model/card/monitoring/+page.svelte";
import {
  createDriftViz,
  createFeatureDistributionViz,
} from "$lib/scripts/monitoring/utils";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it("render Scouter Monitoring Page", () => {
  let driftprofiles = new Map();
  driftprofiles["SPC"] = driftProfile;

  let driftValues: DriftValues = {
    created_at: featureDriftValues.features["col_1"].created_at,
    values: featureDriftValues.features["col_1"].values,
  };

  let featureProfile: FeatureDriftProfile = driftProfile.features["col1"];

  let driftVizData = createDriftViz(driftValues, featureProfile);
  let featureDistVizData = createFeatureDistributionViz(
    "repository",
    "model",
    "0.1.0",
    "col1",
    "24h",
    1000,
    featureProfile
  );

  const data = {
    driftprofiles: driftprofiles,
    targetFeature: driftProfile.features[Object.keys(driftProfile.features)[0]],
    features: Object.keys(driftProfile.features),
    driftVizData: driftVizData,
    featureDistVizData: featureDistVizData,
    timeWindow: TimeWindow.TwentyFourHours,
    max_data_points: 1000,
    name: "model-1",
    repository: "ml-platform-1",
    version: "0.1.0",
    alerts: exampleAlerts,
    showConfig: false,
    profileType: "SPC",
  };
  render(MonitoringPage, { data });
});
