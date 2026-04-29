export enum RoutePaths {
  // Auth
  VALIDATE_AUTH = "/opsml/api/auth/validate",
  LOGIN = "/opsml/api/auth/ui/login",
  LOGOUT = "/opsml/api/auth/ui/logout",
  REFRESH_TOKEN = "/opsml/api/auth/refresh",
  RESET_PASSWORD = "/opsml/api/auth/reset-password/recovery",
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
  GET_DASHBOARD_STATS = "/opsml/api/card/dashboard/stats",

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
  // Agent Evaluation
  AGENT_EVAL_TASK_DRIFT = "/opsml/api/scouter/drift/agent/task",
  AGENT_EVAL_WORKFLOW_DRIFT = "/opsml/api/scouter/drift/agent/workflow",
  AGENT_EVAL_TASK_RECORD = "/opsml/api/scouter/agent/task",
  AGENT_EVAL_RECORD_PAGE = "/opsml/api/scouter/agent/page/record",
  AGENT_EVAL_WORKFLOW_PAGE = "/opsml/api/scouter/agent/page/workflow",

  DRIFT_PROFILE = "/opsml/api/scouter/profile",
  DRIFT_PROFILE_EXISTS = "/opsml/api/scouter/profile/exists",
  DRIFT_ALERT = "/opsml/api/scouter/alerts",
  TRACE_PAGE = "/opsml/api/scouter/trace/paginated",
  TRACE_METRICS = "/opsml/api/scouter/trace/metrics",
  TRACE_SPANS = "/opsml/api/scouter/trace/spans",
  ENTITY_ID_TAGS = "/opsml/api/scouter/tags/entity",
  // Observability
  OBSERVABILITY_METRICS = "/opsml/api/scouter/observability/metrics",
  // Trace extensions
  TRACE_SPANS_FILTERS = "/opsml/api/scouter/trace/spans/filters",
  TRACE_FACETS = "/opsml/api/scouter/trace/facets",
  PROFILES_LIST = "/opsml/api/scouter/profiles",
  // GenAI
  GENAI_TOKEN_METRICS = "/opsml/api/scouter/genai/metrics/tokens",
  GENAI_OPERATIONS = "/opsml/api/scouter/genai/metrics/operations",
  GENAI_MODELS = "/opsml/api/scouter/genai/metrics/models",
  GENAI_AGENTS = "/opsml/api/scouter/genai/metrics/agents",
  GENAI_TOOLS = "/opsml/api/scouter/genai/metrics/tools",
  GENAI_ERRORS = "/opsml/api/scouter/genai/metrics/errors",
  GENAI_SPANS = "/opsml/api/scouter/genai/spans",
  GENAI_CONVERSATION = "/opsml/api/scouter/genai/conversation",
  GENAI_AGENT_METRICS = "/opsml/api/scouter/genai/agent/metrics",
  GENAI_TOOL_METRICS = "/opsml/api/scouter/genai/tool/metrics",

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
  UPDATE_USER = "/api/user/update",
  REGISTRY_PAGE = "/api/card/registry/page",
  REGISTRY_STATS = "/api/card/registry/stats",
  METADATA = "/api/card/metadata",
  CARD_FROM_UID = "/api/card/uid",
  VERSION_PAGE = "/api/card/registry/version/page",

  // scouter
  // profile
  MONITORING_PROFILES = "/api/scouter/profiles/hydrate",
  MONITORING_PROFILE_EXISTS = "/api/scouter/profile/exists",
  UPDATE_MONITORING_PROFILE = "/api/scouter/profile/update",

  // drift
  SPC_DRIFT = "/api/scouter/drift/spc",
  PSI_DRIFT = "/api/scouter/drift/psi",
  CUSTOM_DRIFT = "/api/scouter/drift/custom",
  AGENT_TASK_DRIFT = "/api/scouter/drift/agent/task",
  AGENT_WORKFLOW_DRIFT = "/api/scouter/drift/agent/workflow",

  // drift alerts
  MONITORING_ALERTS = "/api/scouter/alerts",
  ACKNOWLEDGE_ALERT = "/api/scouter/alerts/acknowledge",

  // agent
  AGENT_EVAL_RECORD_PAGE = "/api/scouter/agent/page/record",
  AGENT_EVAL_WORKFLOW_PAGE = "/api/scouter/agent/page/workflow",
  AGENT_EVAL_TASK = "/api/scouter/agent/task",

  // observability
  TRACE_METRICS = "/api/scouter/observability/trace/metrics",
  TRACE_SPANS = "/api/scouter/observability/trace/spans",
  TRACE_PAGE = "/api/scouter/observability/trace",
  ENTITY_ID_TAGS = "/api/scouter/tags/entity",
  // GenAI
  GENAI_TOKEN_METRICS = "/api/scouter/genai/metrics/tokens",
  GENAI_OPERATIONS = "/api/scouter/genai/metrics/operations",
  GENAI_MODELS = "/api/scouter/genai/metrics/models",
  GENAI_AGENTS = "/api/scouter/genai/metrics/agents",
  GENAI_TOOLS = "/api/scouter/genai/metrics/tools",
  GENAI_ERRORS = "/api/scouter/genai/metrics/errors",
  GENAI_SPANS = "/api/scouter/genai/spans",
  GENAI_CONVERSATION = "/api/scouter/genai/conversation",
  GENAI_AGENT_METRICS = "/api/scouter/genai/agent/metrics",
  GENAI_TOOL_METRICS = "/api/scouter/genai/tool/metrics",
  OBSERVABILITY_METRICS = "/api/scouter/observability/metrics",
  TRACE_FACETS = "/api/scouter/trace/facets",

  EXPERIMENT_GROUPED_METRICS = "/api/card/experiment/metrics/grouped",
  DATA_PROFILE = "/api/card/data/profile",
  EXPERIMENT_METRIC_NAMES = "/api/card/experiment/metrics/names",
  EXPERIMENT_RECENT = "/api/card/experiment/recent",
  EXPERIMENT_HARDWARE = "/api/card/experiment/hardware",
  CREATE_SPACE = "/api/space/create",
  HEALTHCHECK = "/api/health",
}
