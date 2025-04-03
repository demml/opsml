export enum RoutePaths {
  VALIDATE_AUTH = "/opsml/api/auth/validate",
  LOGIN = "/opsml/api/auth/ui/login",
  LIST_CARDS = "/opsml/api/card/list",
  LIST_SPACES = "/opsml/api/card/repositories",
  GET_STATS = "/opsml/api/card/registry/stats",
  GET_REGISTRY_PAGE = "/opsml/api/card/registry/page",

  ERROR = "/opsml/error",
  HOME = "/opsml/home",
  METADATA = "/opsml/api/card/metadata",
  README = "/opsml/api/card/readme",
  FILE_INFO = "/opsml/api/files/list/info",
  FILE_TREE = "/opsml/api/files/tree",
  FILE_CONTENT = "/opsml/api/files/content",

  // scouter
  DRIFT_PROFILE_UI = "/opsml/api/scouter/profile/ui",
  SPC_DRIFT = "/opsml/api/scouter/drift/spc",
  PSI_DRIFT = "/opsml/api/scouter/drift/psi",
  CUSTOM_DRIFT = "/opsml/api/scouter/drift/custom",
  DRIFT_PROFILE = "/opsml/api/scouter/profile",
  DRIFT_ALERT = "/opsml/api/scouter/alerts",

  // Experiment
  EXPERIMENT_METRICS = "/opsml/api/experiment/metrics",
  EXPERIMENT_GROUPED_METRICS = "/opsml/api/experiment/metrics/grouped",
  EXPERIMENT_METRIC_NAMES = "/opsml/api/experiment/metrics/names",
  EXPERIMENT_PARAMETERS = "/opsml/api/experiment/parameters",

  // everything below is old and may be removed

  REGISTER = "/opsml/auth/register",
  UPDATE = "/opsml/auth/update",
  AUTH_SETTINGS = "/opsml/auth/verify",
  TOKEN = "/opsml/auth/token",
  USER_AUTH = "/opsml/auth/user",
  EXISTS = "/opsml/auth/user/exists",
  REGISTRY_STATS = "/opsml/cards/registry/stats",
  QUERY_PAGE = "/opsml/cards/registry/query/page",
  DATACARD = "/opsml/data/card",
  RUNCARD = "/opsml/run/card",
  METRICS = "/opsml/metrics",

  GRAPHS = "/opsml/runs/graphs",
  REPOSITORIES = "/opsml/cards/repositories",
  FILE_EXISTS = "/opsml/files/exists",
  FILES_VIEW = "/opsml/files/view",
  MODEL_METADATA = "/opsml/models/metadata",

  FORGOT = "/opsml/auth/forgot",
  SECURITY_QUESTION = "/opsml/auth/security",
  TEMP_TOKEN = "/opsml/auth/temp",
  ROTATE_TOKEN = "/opsml/auth/token/rotate",
  REFRESH_TOKEN = "/opsml/auth/token/refresh",

  HARDWARE = "/opsml/metrics/hardware",
  DRIFT_VALUES = "/opsml/scouter/drift/values",
  FEATURE_DISTRIBUTION = "/opsml/scouter/feature/distribution",
  MONITOR_ALERTS = "/opsml/scouter/alerts",
  MONITOR_ALERT_METRICS = "/opsml/scouter/alerts/metrics",
  OBSERVABILITY_METRICS = "/opsml/scouter/observability/metrics",
}
