/**
 * Mock data for SPC, PSI, and Custom monitoring drift dashboards.
 * Used in dev mode so dashboards render without a running Scouter instance.
 *
 * Style: follows the builder pattern in src/lib/server/trace/mockData.ts.
 */

import { DriftType, AlertThreshold } from "$lib/components/scouter/types";
import type { FeatureMap } from "$lib/components/scouter/types";
import type {
  SpcDriftProfile,
  SpcFeatureDriftProfile,
  SpcDriftConfig,
  BinnedSpcFeatureMetrics,
  SpcDriftFeature,
} from "$lib/components/scouter/spc/types";
import { AlertZone as SpcAlertZone } from "$lib/components/scouter/spc/types";
import type {
  PsiDriftProfile,
  PsiFeatureDriftProfile,
  PsiDriftConfig,
  BinnedPsiFeatureMetrics,
  BinnedPsiMetric,
  Bin,
} from "$lib/components/scouter/psi/types";
import { BinType } from "$lib/components/scouter/psi/types";
import type {
  CustomDriftProfile,
  CustomMetricDriftConfig,
  BinnedMetrics,
  BinnedMetric,
  BinnedMetricStats,
} from "$lib/components/scouter/custom/types";
import type {
  DriftAlertPaginationResponse,
  Alert,
} from "$lib/components/scouter/alert/types";
import type {
  DriftProfileResponse,
  UiProfile,
  DriftProfile,
} from "$lib/components/scouter/utils";
import type {
  MonitoringPageData,
  SelectedData,
} from "$lib/components/scouter/dashboard/utils";
import type { TimeRange } from "$lib/components/trace/types";
import { RegistryType } from "$lib/utils";

// ── Helpers ───────────────────────────────────────────────────────────────────

const MOCK_UID = "mock-uid-00000000-0000-0000-0000-000000000000";
const MOCK_SPACE = "mock-space";
const MOCK_NAME = "mock-model";
const MOCK_VERSION = "1.0.0";
const DATA_POINTS = 30;

/** Generates an array of ISO timestamps at 1-minute intervals ending at `endMs`. */
function buildTimestamps(endMs: number, count: number, intervalMs = 60_000): string[] {
  const ts: string[] = [];
  for (let i = count - 1; i >= 0; i--) {
    ts.push(new Date(endMs - i * intervalMs).toISOString());
  }
  return ts;
}

/** Generates a sinusoidal series with optional noise. */
function buildSineSeries(
  count: number,
  center: number,
  amplitude: number,
  noiseScale = 0,
): number[] {
  return Array.from({ length: count }, (_, i) => {
    const phase = (i / count) * 2 * Math.PI;
    const noise = noiseScale * (Math.random() * 2 - 1);
    return center + amplitude * Math.sin(phase) + noise;
  });
}

const NOW = Date.now();

// ── SPC ───────────────────────────────────────────────────────────────────────

const SPC_FEATURE_NAMES = ["feature_0", "feature_1", "feature_2", "feature_3", "feature_4"];

function buildSpcFeatureProfile(name: string, idx: number): SpcFeatureDriftProfile {
  const center = 10 + idx * 5;
  const sigma = 1.5 + idx * 0.3;
  return {
    id: `spc-feat-${idx}`,
    center,
    one_ucl: center + sigma,
    one_lcl: center - sigma,
    two_ucl: center + 2 * sigma,
    two_lcl: center - 2 * sigma,
    three_ucl: center + 3 * sigma,
    three_lcl: center - 3 * sigma,
    timestamp: new Date(NOW - 86_400_000).toISOString(),
  };
}

function buildSpcFeatureMap(): FeatureMap {
  const features: Record<string, Record<string, number>> = {};
  SPC_FEATURE_NAMES.forEach((name, i) => {
    features[name] = { mean: 10 + i * 5, std: 1.5 + i * 0.3 };
  });
  return { features };
}

function buildSpcDriftConfig(): SpcDriftConfig {
  return {
    sample_size: 100,
    sample: true,
    space: MOCK_SPACE,
    name: MOCK_NAME,
    version: MOCK_VERSION,
    uid: MOCK_UID,
    alert_config: {
      rule: {
        rule: "8 16 4 8 2 4 1 1",
        zones_to_monitor: [
          SpcAlertZone.Zone1,
          SpcAlertZone.Zone2,
          SpcAlertZone.Zone3,
          SpcAlertZone.Zone4,
        ],
      },
      dispatch_config: { Console: { enabled: true } },
      schedule: "0 * * * *",
      features_to_monitor: SPC_FEATURE_NAMES,
    },
    feature_map: buildSpcFeatureMap(),
    targets: [],
    drift_type: DriftType.Spc,
  };
}

function buildSpcDriftProfile(): SpcDriftProfile {
  const features: Record<string, SpcFeatureDriftProfile> = {};
  SPC_FEATURE_NAMES.forEach((name, i) => {
    features[name] = buildSpcFeatureProfile(name, i);
  });
  return {
    features,
    config: buildSpcDriftConfig(),
    scouter_version: "0.6.0",
  };
}

function buildBinnedSpcMetrics(endMs: number): BinnedSpcFeatureMetrics {
  const timestamps = buildTimestamps(endMs, DATA_POINTS);
  const features: Record<string, SpcDriftFeature> = {};
  SPC_FEATURE_NAMES.forEach((name, i) => {
    const center = 10 + i * 5;
    const amplitude = 0.8 + i * 0.1;
    features[name] = {
      created_at: timestamps,
      values: buildSineSeries(DATA_POINTS, center, amplitude, 0.2),
    };
  });
  return { features };
}

function buildSpcAlerts(): DriftAlertPaginationResponse {
  const items: Alert[] = [
    {
      id: 1,
      created_at: new Date(NOW - 5 * 60_000).toISOString(),
      entity_name: "feature_2",
      active: true,
      // Partial AlertMap — only Spc key is populated; cast is intentional.
      alert: {
        Spc: { feature: "feature_2", kind: "OutOfBounds", zone: "Zone3" },
      } as any,
    },
    {
      id: 2,
      created_at: new Date(NOW - 12 * 60_000).toISOString(),
      entity_name: "feature_4",
      active: true,
      alert: {
        Spc: { feature: "feature_4", kind: "Consecutive", zone: "Zone2" },
      } as any,
    },
  ];
  return { items, has_next: false, has_previous: false };
}

// ── PSI ───────────────────────────────────────────────────────────────────────

const PSI_FEATURE_NAMES = ["age", "income", "credit_score", "loan_amount"];

function buildBins(count: number): Bin[] {
  const binWidth = 1 / count;
  return Array.from({ length: count }, (_, i) => ({
    id: i,
    lower_limit: i === 0 ? null : i * binWidth,
    upper_limit: i === count - 1 ? null : (i + 1) * binWidth,
    proportion: binWidth + (Math.random() * 0.02 - 0.01),
  }));
}

function buildPsiFeatureProfile(name: string, idx: number): PsiFeatureDriftProfile {
  return {
    id: `psi-feat-${idx}`,
    bins: buildBins(10),
    timestamp: new Date(NOW - 86_400_000).toISOString(),
    bin_type: BinType.Numeric,
  };
}

function buildPsiFeatureMap(): FeatureMap {
  const features: Record<string, Record<string, number>> = {};
  PSI_FEATURE_NAMES.forEach((name, i) => {
    features[name] = { bin_count: 10 };
  });
  return { features };
}

function buildPsiDriftConfig(): PsiDriftConfig {
  return {
    space: MOCK_SPACE,
    name: MOCK_NAME,
    version: MOCK_VERSION,
    uid: MOCK_UID,
    feature_map: buildPsiFeatureMap(),
    alert_config: {
      dispatch_config: { Console: { enabled: true } },
      schedule: "0 * * * *",
      features_to_monitor: PSI_FEATURE_NAMES,
      threshold: { Fixed: { threshold: 0.2 } },
    },
    targets: [],
    drift_type: DriftType.Psi,
  };
}

function buildPsiDriftProfile(): PsiDriftProfile {
  const features: Record<string, PsiFeatureDriftProfile> = {};
  PSI_FEATURE_NAMES.forEach((name, i) => {
    features[name] = buildPsiFeatureProfile(name, i);
  });
  return {
    features,
    config: buildPsiDriftConfig(),
    scouter_version: "0.6.0",
  };
}

function buildBinnedPsiMetrics(endMs: number): BinnedPsiFeatureMetrics {
  const timestamps = buildTimestamps(endMs, DATA_POINTS);
  const features: Record<string, BinnedPsiMetric> = {};

  PSI_FEATURE_NAMES.forEach((name, i) => {
    const basePsi = 0.05 + i * 0.03;
    const psiValues = buildSineSeries(DATA_POINTS, basePsi, basePsi * 0.5, 0.005);
    const bins: Record<number, number> = {};
    for (let b = 0; b < 10; b++) {
      bins[b] = 0.1 + Math.random() * 0.02 - 0.01;
    }
    features[name] = {
      created_at: timestamps,
      psi: psiValues,
      overall_psi: basePsi,
      bins,
    };
  });
  return { features };
}

function buildPsiAlerts(): DriftAlertPaginationResponse {
  const items: Alert[] = [
    {
      id: 3,
      created_at: new Date(NOW - 8 * 60_000).toISOString(),
      entity_name: "credit_score",
      active: true,
      // Partial AlertMap — only Psi key is populated; cast is intentional.
      alert: {
        Psi: { feature: "credit_score", drift: 0.28, threshold: 0.2 },
      } as any,
    },
  ];
  return { items, has_next: false, has_previous: false };
}

// ── Custom ────────────────────────────────────────────────────────────────────

const CUSTOM_METRIC_NAMES = [
  "accuracy",
  "precision",
  "recall",
  "f1_score",
  "latency_p99",
];

const CUSTOM_METRIC_BASELINES: Record<string, number> = {
  accuracy: 0.95,
  precision: 0.93,
  recall: 0.91,
  f1_score: 0.92,
  latency_p99: 120,
};

function buildCustomDriftConfig(): CustomMetricDriftConfig {
  const alertConditions: Record<string, any> = {};
  CUSTOM_METRIC_NAMES.forEach((name) => {
    if (name === "latency_p99") {
      alertConditions[name] = {
        alert_threshold: AlertThreshold.Above,
        baseline_value: CUSTOM_METRIC_BASELINES[name],
        delta: 50,
      };
    } else {
      alertConditions[name] = {
        alert_threshold: AlertThreshold.Below,
        baseline_value: CUSTOM_METRIC_BASELINES[name],
        delta: 0.05,
      };
    }
  });

  return {
    sample_size: 100,
    sample: false,
    space: MOCK_SPACE,
    name: MOCK_NAME,
    version: MOCK_VERSION,
    uid: MOCK_UID,
    alert_config: {
      dispatch_config: { Console: { enabled: true } },
      schedule: "0 * * * *",
      alert_conditions: alertConditions,
    },
    drift_type: DriftType.Custom,
  };
}

function buildCustomDriftProfile(): CustomDriftProfile {
  const metrics: Record<string, number> = {};
  CUSTOM_METRIC_NAMES.forEach((name) => {
    metrics[name] = CUSTOM_METRIC_BASELINES[name];
  });
  return {
    config: buildCustomDriftConfig(),
    metrics,
    scouter_version: "0.6.0",
  };
}

function buildBinnedCustomMetrics(endMs: number): BinnedMetrics {
  const timestamps = buildTimestamps(endMs, DATA_POINTS);
  const metricsMap: Record<string, BinnedMetric> = {};

  CUSTOM_METRIC_NAMES.forEach((name) => {
    const baseline = CUSTOM_METRIC_BASELINES[name];
    const isLatency = name === "latency_p99";
    const amplitude = isLatency ? 20 : 0.03;
    const noiseScale = isLatency ? 5 : 0.005;
    const avgValues = buildSineSeries(DATA_POINTS, baseline, amplitude, noiseScale);

    const stats: BinnedMetricStats[] = avgValues.map((avg) => {
      const spread = isLatency ? 15 : 0.02;
      return {
        avg,
        lower_bound: avg - spread,
        upper_bound: avg + spread,
      };
    });

    metricsMap[name] = {
      metric: name,
      created_at: timestamps,
      stats,
    };
  });

  return { metrics: metricsMap };
}

function buildCustomAlerts(): DriftAlertPaginationResponse {
  const items: Alert[] = [
    {
      id: 4,
      created_at: new Date(NOW - 3 * 60_000).toISOString(),
      entity_name: "accuracy",
      active: true,
      // Partial AlertMap — only Custom key is populated; cast is intentional.
      alert: {
        Custom: {
          metric_name: "accuracy",
          baseline_value: 0.95,
          observed_value: 0.87,
          delta: null,
          alert_threshold: AlertThreshold.Below,
        },
      } as any,
    },
    {
      id: 5,
      created_at: new Date(NOW - 7 * 60_000).toISOString(),
      entity_name: "latency_p99",
      active: true,
      alert: {
        Custom: {
          metric_name: "latency_p99",
          baseline_value: 120,
          observed_value: 185,
          delta: null,
          alert_threshold: AlertThreshold.Above,
        },
      } as any,
    },
  ];
  return { items, has_next: false, has_previous: false };
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Returns a mock DriftProfileResponse containing SPC, PSI, and Custom profiles.
 *
 * Each UiProfile.profile only populates the key matching its drift type.
 * The full DriftProfile union requires all keys; we cast to satisfy TypeScript
 * while keeping the partial shape intentional for mock usage.
 */
export function getMockMonitoringProfiles(): DriftProfileResponse {
  const spcProfile = buildSpcDriftProfile();
  const psiProfile = buildPsiDriftProfile();
  const customProfile = buildCustomDriftProfile();

  const spcUiProfile: UiProfile = {
    profile_uri: "mock://spc/profile.json",
    // Partial DriftProfile — only Spc key populated; cast is intentional.
    profile: { Spc: spcProfile } as unknown as DriftProfile,
  };

  const psiUiProfile: UiProfile = {
    profile_uri: "mock://psi/profile.json",
    // Partial DriftProfile — only Psi key populated; cast is intentional.
    profile: { Psi: psiProfile } as unknown as DriftProfile,
  };

  const customUiProfile: UiProfile = {
    profile_uri: "mock://custom/profile.json",
    // Partial DriftProfile — only Custom key populated; cast is intentional.
    profile: { Custom: customProfile } as unknown as DriftProfile,
  };

  return {
    [DriftType.Spc]: spcUiProfile,
    [DriftType.Psi]: psiUiProfile,
    [DriftType.Custom]: customUiProfile,
    // Agent is not included in standard monitoring mock — cast satisfies the Record type.
  } as unknown as DriftProfileResponse;
}

/** Returns sorted drift types present in the mock profiles. */
export function getMockDriftTypes(): DriftType[] {
  return [DriftType.Custom, DriftType.Psi, DriftType.Spc];
}

/**
 * Returns a mock MonitoringPageData (success variant) for the given drift type.
 * Timestamps in metrics are derived from the provided timeRange.endTime.
 */
export function getMockMonitoringPageData(
  driftType: DriftType,
  uid: string,
  registryType: RegistryType,
  timeRange: TimeRange,
): Extract<MonitoringPageData, { status: "success" }> {
  const profiles = getMockMonitoringProfiles();
  const driftTypes = getMockDriftTypes();
  const endMs = new Date(timeRange.endTime).getTime();

  let metrics: any;
  let driftAlerts: DriftAlertPaginationResponse;
  let profile: DriftProfile[DriftType];
  let profileUri: string;

  switch (driftType) {
    case DriftType.Spc: {
      metrics = buildBinnedSpcMetrics(endMs);
      driftAlerts = buildSpcAlerts();
      profile = buildSpcDriftProfile() as unknown as DriftProfile[DriftType];
      profileUri = "mock://spc/profile.json";
      break;
    }
    case DriftType.Psi: {
      metrics = buildBinnedPsiMetrics(endMs);
      driftAlerts = buildPsiAlerts();
      profile = buildPsiDriftProfile() as unknown as DriftProfile[DriftType];
      profileUri = "mock://psi/profile.json";
      break;
    }
    case DriftType.Custom:
    default: {
      metrics = buildBinnedCustomMetrics(endMs);
      driftAlerts = buildCustomAlerts();
      profile = buildCustomDriftProfile() as unknown as DriftProfile[DriftType];
      profileUri = "mock://custom/profile.json";
      break;
    }
  }

  const selectedData: SelectedData = {
    driftType,
    metrics,
    driftAlerts,
    profile,
    profileUri,
  };

  return {
    status: "success",
    driftTypes,
    profiles,
    selectedData,
    uid,
    registryType,
    selectedTimeRange: timeRange,
  };
}
