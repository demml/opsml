type record = [string, string, string, number, number, number, number];

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
  repository?: string;
  name?: string;
  version?: string;
  registry_type: string;
  uid?: string;
  page?: number;
  limit?: number;
}

export interface Metric {
  run_uid: string;
  name: string;
  value: number;
  step?: number;
  timestamp?: number;
}

export interface Metrics {
  metric: Metric[];
}

export interface RunMetrics {
  [key: string]: Metric[];
}

export interface MetricNames {
  metric: string[];
}

export interface Parameter {
  name: string;
  value: number | string;
  step?: number;
  timestamp?: number;
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
  datacard_uid?: string;
  runcard_uid?: string;
  modelcard_uids: string[];
  datacard_uids: string[];
}

export interface Artifact {
  local_path: string;
  remote_path: string;
  name: string;
}

export interface ComputeEnvironment {
  cpu_count: number;
  memory: number;
  disk_space: number;
  system: string;
  release: string;
  architecture_bits: string;
  python_version: string;
  python_compiler: string;
  gpu_count: number;
  gpu_devices: string[];
  gpu_device_memory: Map<string, number>;
}

export interface RunCard {
  name: string;
  repository: string;
  version: string;
  uid: string;
  contact: string;
  datacard_uids: string[];
  modelcard_uids: string[];
  pipelinecard_uid?: string;
  parameters: Map<string, Parameter[]>;
  artifact_uris: Map<string, Artifact>;
  tags: Map<string, string | number>;
  project?: string;
  compute_environment: ComputeEnvironment;
}

export interface CardResponse {
  cards: Card[];
}

export interface DataSchema {
  data_type: string;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  input_features: any;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ouput_features: any;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onnx_input_features?: any;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onnx_output_features?: any;

  onnx_data_type?: string;
  onnx_version?: string;
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
  data_splits?: string;
  feature_map?: string;
  sql_logic: Map<string, string> | undefined;
}

export enum RegistryName {
  Model = "OPSML_MODEL_REGISTRY",
  Data = "OPSML_DATA_REGISTRY",
  Run = "OPSML_RUN_REGISTRY",
}

export enum ProfileType {
  SPC = "SPC",
  PSI = "PSI",
}

export enum AlertStatus {
  ACTIVE = "active",
  ACKNOWLEDGED = "acknowledged",
}

export enum CommonPaths {
  HOME = "/opsml",
  LOGIN = "/opsml/auth/login",
  REGISTER = "/opsml/auth/register",
  UPDATE = "/opsml/auth/update",
  VERIFY = "/opsml/auth/verify",
  TOKEN = "/opsml/auth/token",
  USER_AUTH = "/opsml/auth/user",
  EXISTS = "/opsml/auth/user/exists",
  LIST_CARDS = "/opsml/cards/list",
  REGISTRY_STATS = "/opsml/cards/registry/stats",
  QUERY_PAGE = "/opsml/cards/registry/query/page",
  DATACARD = "/opsml/data/card",
  RUNCARD = "/opsml/run/card",
  METRICS = "/opsml/metrics",
  PARAMETERS = "/opsml/parameters",
  GRAPHS = "/opsml/runs/graphs",
  REPOSITORIES = "/opsml/cards/repositories",
  FILE_EXISTS = "/opsml/files/exists",
  FILES_VIEW = "/opsml/files/view",
  MODEL_METADATA = "/opsml/models/metadata",
  FILE_INFO = "/opsml/files/list/info",
  README = "/opsml/files/readme",
  FORGOT = "/opsml/auth/forgot",
  SECURITY_QUESTION = "/opsml/auth/security",
  TEMP_TOKEN = "/opsml/auth/temp",
  ROTATE_TOKEN = "/opsml/auth/token/rotate",
  REFRESH_TOKEN = "/opsml/auth/token/refresh",
  ERROR = "/opsml/error/page",
  HARDWARE = "/opsml/metrics/hardware",
  DRIFT_PROFILE = "/opsml/scouter/drift/profile",
  DRIFT_VALUES = "/opsml/scouter/drift/values",
  FEATURE_DISTRIBUTION = "/opsml/scouter/feature/distribution",
  MONITOR_ALERTS = "/opsml/scouter/alerts",
  MONITOR_ALERT_METRICS = "/opsml/scouter/alerts/metrics",
}

export enum CommonErrors {
  USER_NOT_FOUND = "User not found",
  USER_EXISTS = "User already exists",
  INVALID_PASSWORD = "Invalid password",
  TOKEN_ERROR = "Error generating token",
  INCORRECT_ANSWER = "Incorrect answer",
}

export enum TimeWindow {
  FiveMinutes = "5minute",
  FifteenMinutes = "15minute",
  ThirtyMinutes = "30minute",
  OneHour = "1hour",
  ThreeHours = "3hour",
  SixHours = "6hour",
  TwelveHours = "12hour",
  TwentyFourHours = "24hour",
  TwoDays = "2day",
  FiveDays = "5day",
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
  content?: string;
  view_type?: string;
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
  graphType: string;
}

export interface RunGraph {
  name: string;
  x_label: string;
  y_label: string;
  x: number[];
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
  cards: Map<string, Card>;
  name: string;
  repository: string;
  version: string;
  card: RunCard;
  metricNames: string[];
  metrics: RunMetrics;
  searchableMetrics: string[];
  show: boolean;
  metricVizData: ChartjsData | undefined;
  referenceMetrics: Map<string, number>;
}

export interface Message {
  uid: string;
  registry: string;
  user: string;
  votes: number;
  content: string;
  parent_id?: number;
  created_at?: number;
}

export interface MessageWithReplies {
  message: Message;
  replies: MessageWithReplies[];
}

export type MessageThread = MessageWithReplies[];

export interface RegisterUser {
  username: string;
  full_name: string;
  password: string;
  email: string;
  security_question: string;
  security_answer: string;
}

export interface UpdateUserRequest {
  username: string;
  updated_username?: string;
  full_name: string;
  password: string;
  email: string;
  security_question: string;
  security_answer: string;
  scopes: UserScope;
  is_active: boolean;
}

export interface UpdateUserResponse {
  updated: boolean;
}

export interface UserScope {
  read: boolean;
  write: boolean;
  delete: boolean;
  admin: boolean;
  model_repository?: string[];
  data_repository?: string[];
  run_repository?: string[];
}

export interface UserRepositories {
  model_repository: string[];
  data_repository: string[];
  run_repository: string[];
}

export interface User {
  username: string;
  password?: string;
  full_name?: string;
  email?: string;
  security_question: string;
  security_answer: string;
  is_active: boolean;
  scopes: UserScope;
  updated_username?: string;
  watchlist: UserRepositories;
}

export interface UserResponse {
  user?: User;
  error?: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface UserExistsResponse {
  exists: boolean;
  username: string;
}

export interface Readme {
  readme: string;
  exists: boolean;
}

export interface FileSetup {
  fileInfo: Files;
  prevPath: string;
  displayPath: string[];
}

export interface registryPageReturn {
  repos: string[];
  registry: string;
  registryStats: registryStats;
  registryPage: registryPage;
}

export interface securityQuestionResponse {
  question: string;
  exists: boolean;
  error: string;
}

export interface PasswordStrength {
  power: number;
  color: string;
  message: string;
}

export interface TableMetric {
  name: string;
  value: string | number;
  step: string | number;
}

export interface ChartData {
  x: number[] | string[];
  y: number[];
}

export interface ChartjsData {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  options: any;
  type: string;
}

export interface ChartjsLineDataset {
  label: string;
  data: number[];
  borderColor: string;
  backgroundColor: string;
  pointRadius?: number;
  fill?: boolean;
  tension?: number;
}

export interface ChartjsBarDataset {
  data: number[];
  borderColor: string[];
  backgroundColor: string[];
  borderWidth: number;
  borderRadius: number;
  borderSkipped: boolean;
}

export interface ScatterData {
  x: number;
  y: number;
}

export interface ChartjsScatterDataset {
  label: string;
  data: ScatterData[];
  borderColor: string;
  backgroundColor: string;
  pointRadius: number;
}

export interface ChartjsGroupedBarDataset {
  label: string;
  data: number[];
  borderColor: string;
  backgroundColor: string;
  borderWidth: number;
  borderRadius: number;
  borderSkipped: boolean;
}

export interface FileSystemAttr {
  files: Files;
  name: string;
  repository: string;
  version: string;
  registry: string;
  subdir?: string;
  modifiedAt: string;
  basePath: string;
  displayPath: string[];
  prevPath: string;
  baseRedirectPath: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface FileViewResponse {
  file_info: FileInfo;
  content: ViewContent;
}

export interface UserUpdated {
  updated: boolean;
}

export interface CPUMetrics {
  cpu_percent_utilization: number;
  cpu_percent_per_core: number[] | undefined;
  compute_overall: number | undefined;
  compute_utilized: number | undefined;
  load_avg: number;
}

export interface MemoryMetrics {
  sys_ram_total: number;
  sys_ram_used: number;
  sys_ram_available: number;
  sys_ram_percent_used: number;
  sys_swap_total: number | undefined;
  sys_swap_used: number | undefined;
  sys_swap_free: number | undefined;
  sys_swap_percent: number | undefined;
}

export interface NetworkMetrics {
  bytes_recv: number;
  bytes_sent: number;
}

export interface GPUMetrics {
  gpu_percent_utilization: number;
  gpu_percent_per_core: number[] | undefined;
}

export interface HardwareMetrics {
  cpu: CPUMetrics;
  memory: MemoryMetrics;
  network: NetworkMetrics;
  gpu: GPUMetrics | undefined;
}

export interface HardwareMetricRecord {
  run_uid: string;
  created_at: Date;
  metrics: HardwareMetrics;
}

export interface HardwareMetricsResponse {
  metrics: HardwareMetricRecord[];
}

export interface ParsedHardwareMetrics {
  x: Date[];
  cpu_overall: number[];
  cpu_per_core: number[][];
  network_rx: number[];
  network_tx: number[];
  memory: number[];
  gpu_overall: number[];
  gpu_per_core: number[][];
}

export interface HardwareCharts {
  cpu_overall: ChartjsData;
  cpu_per_core: ChartjsData | undefined;
  memory: ChartjsData;
  network_tx: ChartjsData;
  network_rx: ChartjsData;
  gpu_overall: ChartjsData | undefined;
  gpu_per_core: ChartjsData | undefined;
}

export interface RunPageReturn {
  registry: string;
  repository: string;
  name: string;
  card: Card;
  metadata: RunCard;
  metricNames: string[];
  metrics: RunMetrics;
  tableMetrics: Metric[];
  parameters: Parameter[];
  searchableMetrics: string[];
  metricVizData: ChartjsData | undefined;
  parsedMetrics: ParsedHardwareMetrics | undefined;
}

export interface SpcFeatureDriftProfile {
  id: string;
  center: number;
  one_ucl: number;
  one_lcl: number;
  two_ucl: number;
  two_lcl: number;
  three_ucl: number;
  three_lcl: number;
  timestamp: string;
}

export interface FeatureMap {
  features: Record<string, Record<string, number>>;
}

export interface SpcAlertRule {
  rule: string;
  zones_to_monitor: string[];
}

export interface SpcAlertConfig {
  dispatch_type: string;
  rule: SpcAlertRule;
  schedule: string;
  features_to_monitor: string[];
  dispatch_kwargs: Record<string, string | number>;
}

export interface SpcDriftConfig {
  sample_size: number;
  sample: boolean;
  repository: string;
  name: string;
  version: string;
  alert_config: SpcAlertConfig;
  feature_map: FeatureMap | undefined;
  targets: string[];
  drift_type: string;
}

export interface SpcDriftProfile {
  features: Record<string, SpcFeatureDriftProfile>;
  config: SpcDriftConfig;
  scouter_version: string;
}

export interface DriftProfileResponse {
  profile: SpcDriftProfile | undefined;
}

export interface UpdateProfileResponse {
  complete: boolean;
  message: string;
}

export interface DriftValues {
  created_at: string[];
  values: number[];
}

export interface FeatureDriftValues {
  features: Record<string, DriftValues>;
}

export interface FeatureDriftValuesResponse {
  data: FeatureDriftValues;
  status: string;
}

export interface MonitoringPageReturn {
  repository: string;
  name: string;
  version: string;
  profile: SpcDriftProfile | undefined;
}

export interface SpcFeatureDistribution {
  name: string;
  repository: string;
  version: string;
  percentile_10: number;
  percentile_20: number;
  percentile_30: number;
  percentile_40: number;
  percentile_50: number;
  percentile_60: number;
  percentile_70: number;
  percentile_80: number;
  percentile_90: number;
  percentile_100: number;
  val_10: number;
  val_20: number;
  val_30: number;
  val_40: number;
  val_50: number;
  val_60: number;
  val_70: number;
  val_80: number;
  val_90: number;
  val_100: number;
}

export interface TimestampData {
  timestamps: string[];
  zeros: number[];
}

export interface MonitorAlert {
  created_at: string;
  name: string;
  repository: string;
  version: string;
  feature: string;
  alert: Record<string, string>;
  status: string;
  id: number;
}

export interface MonitorAlerts {
  alerts: MonitorAlert[];
}

export interface UpdateAlert {
  status: string;
  message: string;
}

export interface AlertMetrics {
  created_at: string[];
  acknowledged: number[];
  active: number[];
  alert_count: number[];
}
