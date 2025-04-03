-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_data_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT,
    tags JSONB DEFAULT '[]',
    data_type TEXT,
    experimentcard_uid TEXT,
    auditcard_uid TEXT,
    interface_type TEXT NOT NULL DEFAULT 'undefined',
    username TEXT NOT NULL DEFAULT 'guest'
);

-- ModelSchema
CREATE TABLE IF NOT EXISTS opsml_model_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT,
    tags JSONB DEFAULT '[]',
    datacard_uid TEXT,
    data_type TEXT,
    model_type TEXT,
    experimentcard_uid TEXT,
    auditcard_uid TEXT,
    interface_type TEXT NOT NULL DEFAULT 'undefined',
    task_type TEXT NOT NULL DEFAULT 'undefined',
    username TEXT NOT NULL DEFAULT 'guest'
);

-- RunSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT,
    tags JSONB DEFAULT '[]',
    datacard_uids JSONB,
    modelcard_uids JSONB,
    promptcard_uids JSONB,
    experimentcard_uids JSONB,
    compute_environment JSONB,
    username TEXT NOT NULL DEFAULT 'guest'
);

-- AuditSchema
CREATE TABLE IF NOT EXISTS opsml_audit_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT,
    tags JSONB DEFAULT '[]',
    approved BOOLEAN,
    datacard_uids JSONB,
    modelcard_uids JSONB,
    experimentcard_uids JSONB NOT NULL DEFAULT '{}',
    username TEXT NOT NULL DEFAULT 'guest'
);


-- MetricSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_metric (
    experiment_uid TEXT,
    name TEXT,
    value FLOAT,
    step INT,
    timestamp BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    idx SERIAL PRIMARY KEY
);

-- ParameterSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_parameter (
    experiment_uid TEXT,
    name TEXT,
    value JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    idx SERIAL PRIMARY KEY
);

-- HardwareSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_hardware_metric (
    experiment_uid TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    cpu_percent_utilization REAL,
    cpu_percent_per_core JSONB, -- JSONB is not supported in SQLite, use TEXT to store JSON strings
    free_memory BIGINT,
    total_memory BIGINT,
    used_memory BIGINT,
    available_memory BIGINT,
    used_percent_memory DOUBLE PRECISION,
    bytes_recv BIGINT,
    bytes_sent BIGINT,
    idx SERIAL PRIMARY KEY
);
CREATE INDEX idx_experiment_hardware_metrics_created_at ON opsml_experiment_hardware_metric (created_at);

CREATE TABLE IF NOT EXISTS opsml_user (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    permissions JSONB NOT NULL,
    group_permissions JSONB NOT NULL,
    role TEXT DEFAULT 'user',
    refresh_token TEXT

);

  
CREATE TABLE IF NOT EXISTS opsml_artifact_key (
    uid TEXT PRIMARY KEY,
    registry_type TEXT,
    encrypted_key BYTEA,
    storage_key TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS opsml_operation (
    username TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    access_type TEXT NOT NULL,
    access_location TEXT NOT NULL
);

CREATE INDEX idx_opsml_operation_created_at ON opsml_operation (created_at);

CREATE TABLE IF NOT EXISTS opsml_audit_trail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    operation_type TEXT NOT NULL,  -- CREATE, READ, UPDATE, DELETE, LOGIN, etc.
    resource_type TEXT NOT NULL,   -- model, data, experiment, prompt, etc.
    resource_id TEXT,              -- UUID/ID of the accessed resource
    access_location TEXT,          -- IP address or endpoint
    user_agent TEXT,              -- Client application/browser info
    status TEXT NOT NULL,         -- SUCCESS, FAILURE, DENIED
    error_message JSONB,          -- Details if operation failed
    metadata JSONB                -- JSON field for additional context
);

CREATE INDEX idx_opsml_audit_trail_created_at ON opsml_audit_trail (created_at);

-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_prompt_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT,
    tags JSONB DEFAULT '[]',
    experimentcard_uid TEXT,
    auditcard_uid TEXT,
    username TEXT NOT NULL DEFAULT 'guest'
);
