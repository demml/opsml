export enum RoutePaths {
  // Auth
  VALIDATE_AUTH = "/opsml/api/auth/validate",
  LOGIN = "/opsml/api/auth/ui/login",
  LOGOUT = "/opsml/api/auth/ui/logout",
  REFRESH_TOKEN = "/opsml/api/auth/refresh",
  RESET_PASSWORD = "/opsml/api/user/reset-password/recovery",
  REGISTER = "/opsml/api/user/register",
  USER = "/opsml/api/user",
  SSO_AUTH = "/opsml/api/auth/sso/authorization",
  SSO_CALLBACK = "/opsml/api/auth/sso/callback",

  // Card
  LIST_CARDS = "/opsml/api/card/list",
  LIST_CARD_SPACES = "/opsml/api/card/spaces",
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
  FORGOT = "/opsml/user/forgot",
  USER = "/opsml/user",
  HOME = "/opsml/home",
  METRICS = "/opsml/metrics",
  SCOUTER = "/opsml/scouter",
  EXPERIMENT = "/opsml/experiment",
  ERROR = "/opsml/error",
}
