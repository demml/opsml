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
  metric: string[];
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

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  input_features: any;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ouput_features: any;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onnx_input_features: any;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
  sql_logic: Map<string, string> | undefined;
}

export enum RegistryName {
  Model = "OPSML_MODEL_REGISTRY",
  Data = "OPSML_DATA_REGISTRY",
  Run = "OPSML_RUN_REGISTRY",
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
}

export enum CommonErrors {
  USER_NOT_FOUND = "User not found",
  USER_EXISTS = "User already exists",
  INVALID_PASSWORD = "Invalid password",
  TOKEN_ERROR = "Error generating token",
  INCORRECT_ANSWER = "Incorrect answer",
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
  graphType: string;
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
  parent_id: number | null;
  created_at: number | null;
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
  updated_username: string | null;
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
  model_repository: string[] | null;
  data_repository: string[] | null;
  run_repository: string[] | null;
}

export interface UserRepositories {
  model_repository: string[];
  data_repository: string[];
  run_repository: string[];
}

export interface User {
  username: string;
  password: string | null;
  full_name: string | null;
  email: string | null;
  security_question: string;
  security_answer: string;
  is_active: boolean;
  scopes: UserScope;
  updated_username: string | null;
  watchlist: UserRepositories;
}

export interface UserResponse {
  user: User | null;
  error: string | null;
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
  pointRadius: number | null;
}

export interface ChartjsBarDataset {
  data: number[];
  borderColor: string[];
  backgroundColor: string[];
  borderWidth: number;
  borderRadius: number;
  borderSkipped: boolean;
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
  subdir: string | null;
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
