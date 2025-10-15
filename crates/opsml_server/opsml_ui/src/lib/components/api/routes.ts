export enum RoutePaths {
  // Auth
  VALIDATE_AUTH = "/opsml/api/auth/validate",
  LOGIN = "/opsml/api/auth/ui/login",
  LOGOUT = "/opsml/api/auth/ui/logout",
  REFRESH_TOKEN = "/opsml/api/auth/refresh",
  RESET_PASSWORD = "/opsml/api/user/reset-password/recovery",
  REGISTER = "/opsml/api/auth/register",
  USER = "/opsml/api/user",
  SSO_AUTH = "/opsml/api/auth/sso/authorization",
  SSO_CALLBACK = "/opsml/api/auth/sso/callback",

  // Card
  LIST_CARDS = "/opsml/api/card/list",
  LIST_CARD_SPACES = "/opsml/api/card/spaces",
  LIST_CARD_TAGS = "/opsml/api/card/tags",
  ALL_SPACES = "/opsml/api/card/space/stats",
  SPACES = "/opsml/api/card/space",
  GET_STATS = "/opsml/api/card/registry/stats",
  GET_REGISTRY_PAGE = "/opsml/api/card/registry/page",
  GET_VERSION_PAGE = "/opsml/api/card/registry/version/page",

  METADATA = "/opsml/api/card/metadata",
  README = "/opsml/api/card/readme",
  FILE_INFO = "/opsml/api/files/list/info",
  FILE_TREE = "/opsml/api/files/tree",
  FILE_CONTENT = "/opsml/api/files/content",
  FILE_CONTENT_BATCH = "/opsml/api/files/content/batch",
  ARTIFACT_RECORD = "/opsml/api/files/artifact",

  // scouter
  DRIFT_PROFILE_UI = "/opsml/api/scouter/profile/ui",
  SPC_DRIFT = "/opsml/api/scouter/drift/spc",
  PSI_DRIFT = "/opsml/api/scouter/drift/psi",
  CUSTOM_DRIFT = "/opsml/api/scouter/drift/custom",
  LLM_DRIFT = "/opsml/api/scouter/drift/llm",
  LLM_RECORD_PAGE = "/opsml/api/scouter/drift/llm/records",
  DRIFT_PROFILE = "/opsml/api/scouter/profile",
  DRIFT_ALERT = "/opsml/api/scouter/alerts",

  // Experiment
  EXPERIMENT_METRICS = "/opsml/api/experiment/metrics",
  EXPERIMENT_GROUPED_METRICS = "/opsml/api/experiment/metrics/grouped",
  EXPERIMENT_METRIC_NAMES = "/opsml/api/experiment/metrics/names",
  EXPERIMENT_PARAMETERS = "/opsml/api/experiment/parameters",
  HARDWARE_METRICS = "/opsml/api/experiment/hardware/metrics",

  // Space
  CREATE_SPACE = "/opsml/api/space/create",
  DELETE_SPACE = "/opsml/api/space/delete",

  // Settings
  SETTINGS = "/opsml/api/ui/settings",
}

export enum UiPaths {
  LOGIN = "/opsml/user/login",
  REGISTER = "/opsml/user/register",
  REGISTER_SUCCESS = "/opsml/user/register/success",
  RESET = "/opsml/user/reset",
  FORGOT = "/opsml/user/forgot",
  SSO_AUTH = "/opsml/user/sso",
  SSO_CALLBACK = "/opsml/user/sso/callback",
  USER = "/opsml/user",
  HOME = "/opsml/home",
  METRICS = "/opsml/metrics",
  SCOUTER = "/opsml/scouter",
  EXPERIMENT = "/opsml/experiment",
  ERROR = "/opsml/error",
}

export enum ServerPaths {
  LOGIN = "/api/user/login",
  LOGOUT = "/api/user/logout",
  RESET_PASSWORD = "/api/user/reset",
  REGISTER_USER = "/api/user/register",
  SSO_AUTH = "/api/user/sso",
  SSO_CALLBACK = "/api/user/sso/callback",
  USER = "/api/user/info",
  REGISTRY_PAGE = "/api/card/registry/page",
  REGISTRY_STATS = "/api/card/registry/stats",
  METADATA = "/api/card/metadata",
  CARD_FROM_UID = "/api/card/uid",
  VERSION_PAGE = "/api/card/registry/version/page",
  MONITORING_METRICS = "/api/card/monitoring/metrics",
  MONITORING_PROFILES = "/api/card/monitoring/profiles",
  MONITORING_ALERTS = "/api/card/monitoring/alerts",
  ACKNOWLEDGE_ALERT = "/api/card/monitoring/alerts/acknowledge",
  UPDATE_MONITORING_PROFILE = "/api/card/monitoring/profile/update",
  LLM_MONITORING_RECORDS = "/api/card/monitoring/llm/records",
  EXPERIMENT_GROUPED_METRICS = "/api/card/experiment/metrics/grouped",
  DATA_PROFILE = "/api/card/data/profile",
  EXPERIMENT_METRIC_NAMES = "/api/card/experiment/metrics/names",
  EXPERIMENT_RECENT = "/api/card/experiment/recent",
  EXPERIMENT_HARDWARE = "/api/card/experiment/hardware",
}
