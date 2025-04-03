import type { RegistryType } from "$lib/utils";

// Metric types
export interface Metric {
  name: string;
  value: number;
  step?: number;
  timestamp?: number;
  created_at?: string; // ISO datetime string
}

export interface Metrics {
  metrics: Metric[];
}

// Parameter types
export type ParameterValue =
  | { Int: number }
  | { Float: number }
  | { Str: string };

export interface Parameter {
  name: string;
  value: ParameterValue;
}

export interface Parameters {
  parameters: Parameter[];
}

// Hardware metrics
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

export interface HardwareMetrics {
  cpu: CPUMetrics;
  memory: MemoryMetrics;
  network: NetworkRates;
}

// Compute environment
export interface ComputeEnvironment {
  cpu_count: number;
  total_memory: number;
  total_swap: number;
  system: string;
  os_version: string;
  hostname: string;
  python_version: string;
}

// UID metadata
export interface UidMetadata {
  datacard_uids: string[];
  modelcard_uids: string[];
  promptcard_uids: string[];
  experimentcard_uids: string[];
}

// Main ExperimentCard interface
export interface ExperimentCard {
  repository: string;
  name: string;
  version: string;
  uid: string;
  tags: string[];
  uids: UidMetadata;
  compute_environment: ComputeEnvironment;
  registry_type: RegistryType.Experiment;
  app_env: string;
  created_at: string; // ISO datetime string
  subexperiment: boolean;
  is_card: boolean;
  opsml_version: string;
}
