import { server } from "./server";
import { render } from "@testing-library/svelte";
import {
  SpcDriftProfile,
  featureDriftValues,
  exampleAlerts,
} from "./constants";
import {
  type DriftValues,
  type SpcFeatureDriftProfile,
  TimeWindow,
} from "$lib/scripts/types";
import MonitoringPage from "../routes/opsml/model/card/monitoring/+page.svelte";
import {
  createSpcDriftViz,
  createSpcFeatureDistributionViz,
} from "$lib/scripts/monitoring/utils";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it("render Scouter Monitoring Page", () => {
  let driftprofiles = new Map();
  driftprofiles["SPC"] = SpcDriftProfile;

  let driftValues: DriftValues = {
    created_at: featureDriftValues.features["col_1"].created_at,
    values: featureDriftValues.features["col_1"].values,
  };

  let featureProfile: SpcFeatureDriftProfile = SpcDriftProfile.features["col1"];

  let driftVizData = createSpcDriftViz(driftValues, featureProfile);
  let featureDistVizData = createSpcFeatureDistributionViz(
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
    targetFeature:
      SpcDriftProfile.features[Object.keys(SpcDriftProfile.features)[0]],
    features: Object.keys(SpcDriftProfile.features),
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
