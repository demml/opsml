import { server } from "./server";
import { render } from "@testing-library/svelte";
import {
  SpcDriftProfile,
  featureDriftValues,
  exampleAlerts,
} from "./constants";
import {
  type DriftValues,
  ProfileType,
  type SpcFeatureDriftProfile,
  TimeWindow,
  type AlertMetrics,
} from "$lib/scripts/types";
import MonitoringPage from "../routes/opsml/model/card/monitoring/feature/+page.svelte";
import {
  createAlertMetricViz,
  createSpcDriftViz,
  createSpcFeatureDistributionViz,
} from "$lib/scripts/monitoring/utils";
import type { MonitorData } from "$lib/scripts/monitoring/types";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it("render Scouter Monitoring Page", async () => {
  let driftprofiles = new Map();
  driftprofiles["SPC"] = SpcDriftProfile;

  let driftValues: DriftValues = {
    created_at: featureDriftValues.features["col_1"].created_at,
    values: featureDriftValues.features["col_1"].values,
  };

  let featureProfile: SpcFeatureDriftProfile = SpcDriftProfile.features["col1"];

  let driftVizData = createSpcDriftViz(driftValues, featureProfile);
  let featureDistVizData = await createSpcFeatureDistributionViz(
    "repository",
    "model",
    "0.1.0",
    "col1",
    "24h",
    1000,
    featureProfile
  );

  let alertMetrics: AlertMetrics = {
    created_at: ["2021-08-10T00:00:00Z"],
    acknowledged: [0],
    active: [0],
    alert_count: [0],
  };

  let alertMetricVizData = createAlertMetricViz(alertMetrics);

  let vizData = {
    driftVizData: driftVizData,
    featureDistVizData: featureDistVizData,
  };

  let monitorData: MonitorData = {
    vizData,
    feature: SpcDriftProfile.features["col1"],
  };

  const data = {
    name: "model-1",
    repository: "ml-platform-1",
    version: "0.1.0",
    feature: "col1",
    type: ProfileType.SPC,
    driftprofiles,
    showConfig: false,
    timeWindow: "24h",
    alerts: exampleAlerts,
    alertMetricVizData,
    max_data_points: 1000,
    targetFeature: SpcDriftProfile.features["col1"],
    monitorData,
  };
  render(MonitoringPage, { data });
});
