export enum PlotType {
  Line = "line",
  Bar = "bar",
}

export interface GetMetricRequest {
  experiment_uid: string;
  names: string[];
}

export interface GetMetricNamesRequest {
  experiment_uid: string;
}

export interface GetParameterRequest {
  experiment_uid: string;
  names: string[];
}

export interface Experiment {
  uid: string;
  version: string;
}

export interface UiMetricRequest {
  experiments: Experiment[];
  metric_names: string[];
}

export interface GroupedMetric {
  uid: string;
  version: string;
  value: number[];
  step: number[] | null;
  timestamp: number[] | null;
}

export interface GroupedMetrics {
  [metricName: string]: GroupedMetric[];
}

export interface GetHardwareMetricRequest {
  experiment_uid: string;
}

export interface HardwareMetrics {
  created_at: string; // String -> string
  cpu: CPUMetrics;
  memory: MemoryMetrics;
  network: NetworkRates;
}

export interface CPUMetrics {
  cpu_percent_utilization: number;
  cpu_percent_per_core: number[];
}

export interface MemoryMetrics {
  free_memory: number;
  total_memory: number;
  used_memory: number;
  available_memory: number;
  used_percent_memory: number;
}

export interface NetworkRates {
  bytes_recv: number;
  bytes_sent: number;
}

export interface UiHardwareMetrics {
  createdAt: string[];
  cpuUtilization: number[];
  usedPercentMemory: number[];
  networkMbRecv: number[];
  networkMbSent: number[];
}

export enum ArtifactType {
  Generic = "Generic",
  Figure = "Figure",
}

export interface ArtifactQueryArgs {
  uid?: string;
  name?: string;
  space?: string;
  version?: string;
  sort_by_timestamp?: boolean;
  artifact_type?: ArtifactType;
  limit?: number;
}

export interface ArtifactRecord {
  uid: string;
  name: string;
  space: string;
  version: string;
  media_type: string;
  artifact_type: ArtifactType;
  created_at: string;
}
