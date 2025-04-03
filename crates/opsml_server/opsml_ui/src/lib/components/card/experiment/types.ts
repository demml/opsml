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
