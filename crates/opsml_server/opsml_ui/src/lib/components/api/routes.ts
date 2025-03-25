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

  // everything below is old

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
  PARAMETERS = "/opsml/parameters",
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
  DRIFT_PROFILE = "/opsml/scouter/drift/profile",
  DRIFT_VALUES = "/opsml/scouter/drift/values",
  FEATURE_DISTRIBUTION = "/opsml/scouter/feature/distribution",
  MONITOR_ALERTS = "/opsml/scouter/alerts",
  MONITOR_ALERT_METRICS = "/opsml/scouter/alerts/metrics",
  OBSERVABILITY_METRICS = "/opsml/scouter/observability/metrics",
}
