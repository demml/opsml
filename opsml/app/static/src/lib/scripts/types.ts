type record = [string, string, number, number, number, number];

export interface registryPage {
  page: record[];
}

export interface registryStats {
  nbr_names: number;
  nbr_versions: number;
  nbr_repos: number;
}

export interface repositories {
  repositories: string[];
}

export interface metadataRequest {
  repository?: string;
  name?: string;
  version?: string;
  uid?: string;
}

export interface CardRequest {
  repository: string;
  name: string;
  version?: string;
  registry_type: string;
  uid?: string;
  page?: number;
}

export interface Metric {
  run_uid: string;
  name: string;
  value: number;
  step: number | null;
  timestamp: number | null;
}

export interface Metrics {
  metric: Metric[];
}

export interface RunMetrics {
  [key: string]: Metric[];
}

export interface MetricNames {
  metric;
}

export interface Parameter {
  name: string;
  value: number | string;
  step: number | null;
  timestamp: number | null;
}

export interface Parameters {
  parameter: Parameter[];
}

export interface Card {
  date: string;
  uid: string;
  repository: string;
  contact: string;
  name: string;
  version: string;
  timestamp: number;
  tags: Map<string, string>;
  datacard_uid: string | null;
  runcard_uid: string | null;
  modelcard_uids: string[];
  datacard_uids: string[];
}

export interface Artifact {
  local_path: string;
  remote_path: string;
  name: string;
}

export interface RunCard {
  name: string;
  repository: string;
  version: string;
  uid: string;
  contact: string;
  datacard_uids: string[];
  modelcard_uids: string[];
  pipelinecard_uid: string | null;
  parameters: Map<string, Parameter[]>;
  artifact_uris: Map<string, Artifact>;
  tags: Map<string, string | number>;
  project: string | null;
}

export interface CardResponse {
  cards: Card[];
}

export interface DataSchema {
  data_type: string;
  input_features: any;
  ouput_features: any;
  onnx_input_features: any;
  onnx_output_features: any;
  onnx_data_type: string | undefined;
  onnx_version: string | undefined;
}

export interface ModelMetadata {
  model_name: string;
  model_class: string;
  model_type: string;
  model_interface: string;
  onnx_uri?: string;
  onnx_version?: string;
  model_uri: string;
  model_version: string;
  model_repository: string;
  opsml_version: string;
  data_schema: DataSchema;
  preprocessor_uri?: string;
  preprocessor_name?: string;
  quantized_model_uri?: string;
  tokenizer_uri?: string;
  tokenizer_name?: string;
  feature_extractor_uri?: string;
  feature_extractor_name?: string;
  uid: string;
  task_type?: string;
  onnx_args?: Map<string, string | boolean>;
}

export interface DataSplit {
  name: string;
  uri: string;
}

export interface DataCardMetadata {
  name: string;
  repository: string;
  version: string;
  uid: string;
  contact: string;
  interface_type: string;
  data_splits: string | null;
  feature_map: string | null;
  sql_logic: Map<string, string>;
}

export enum RegistryName {
  Model = "OPSML_MODEL_REGISTRY",
  Data = "OPSML_DATA_REGISTRY",
  Run = "OPSML_RUN_REGISTRY",
}

export interface FileExists {
  exists: boolean;
}

export interface FileInfo {
  name: string;
  size: number;
  type: string;
  created: number;
  islink: boolean;
  mode: number;
  uid: number;
  gid: number;
  mtime: number;
  ino: number;
  nlink: number;
  uri: string;
  suffix: string;
}

export interface ViewContent {
  content: string | null;
  view_type: string | null;
}

export interface FileView {
  file_info: FileInfo;
  content: ViewContent;
}

export interface Files {
  files: FileInfo[];
  mtime: number;
}

export interface Graph {
  name: string;
  x_label: string;
  y_label: string;
  x: number[] | Map<string, number[]>;
  y: number[] | Map<string, number[]>;
  graph_type: string;
  graph_style: string;
}

export enum CardRegistries {
  Run = "run",
  Data = "data",
  Model = "model",
  Service = "service",
}

export interface CompareMetricPage {
  cards: Card[];
  name: string;
  repository: string;
  version: string;
  card: RunCard;
  metricNames: string[];
  metrics: RunMetrics;
  searchableMetrics: string[];
}
