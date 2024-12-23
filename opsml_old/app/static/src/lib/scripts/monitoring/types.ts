import type {
  ChartjsData,
  ProfileType,
  SpcFeatureDriftProfile,
} from "$lib/scripts/types";

export interface MonitoringVizData {
  driftVizData: ChartjsData;
  featureDistVizData: ChartjsData;
}

export interface MonitorData {
  vizData: MonitoringVizData;
  feature: SpcFeatureDriftProfile;
}

export interface MonitoringLayoutPage {
  repository: string;
  name: string;
  version: string;
  feature: string | undefined;
  type: ProfileType;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  driftProfiles: Map<string, any>;
  showConfig: boolean;
  timeWindow: string;
  max_data_points: number;
}

export interface ObservabilityMetric {
  route_name: string;
  created_at: string[];
  total_request_count: number;
  total_error_count: number;
  p5: number[];
  p25: number[];
  p50: number[];
  p95: number[];
  p99: number[];
  request_per_sec: number[];
  error_per_sec: number[];
  error_latency: number[];
  status_counts: Record<string, number>[];
}

export interface ObservabilityMetrics {
  metrics: ObservabilityMetric[];
}
