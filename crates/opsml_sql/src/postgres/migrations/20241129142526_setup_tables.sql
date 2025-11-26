-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_data_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    space TEXT,
    name TEXT,
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
    opsml_version TEXT NOT NULL DEFAULT '0.0.0',
    username TEXT NOT NULL DEFAULT 'guest'
);

CREATE INDEX idx_opsml_data_registry_space_name_version ON opsml_data_registry (space, name, version, created_at);
CREATE INDEX idx_opsml_data_registry_uid ON opsml_data_registry (uid);


-- ModelSchema
CREATE TABLE IF NOT EXISTS opsml_model_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    space TEXT,
    name TEXT,
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
    opsml_version TEXT NOT NULL DEFAULT '0.0.0',
    username TEXT NOT NULL DEFAULT 'guest'
);

CREATE INDEX idx_opsml_model_registry_space_name_version ON opsml_model_registry (space, name, version, created_at);
CREATE INDEX idx_opsml_model_registry_uid ON opsml_model_registry (uid);


-- RunSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    space TEXT,
    name TEXT,
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT,
    tags JSONB DEFAULT '[]',
    datacard_uids JSONB DEFAULT '[]',
    modelcard_uids JSONB DEFAULT '[]',
    promptcard_uids JSONB DEFAULT '[]',
    card_deck_uids JSONB DEFAULT '[]',
    experimentcard_uids JSONB DEFAULT '[]',
    compute_environment JSONB,
    opsml_version TEXT NOT NULL DEFAULT '0.0.0',
    username TEXT NOT NULL DEFAULT 'guest'
);

CREATE INDEX idx_opsml_experiment_registry_space_name_version ON opsml_experiment_registry (space, name, version, created_at);
CREATE INDEX idx_opsml_experiment_registry_uid ON opsml_experiment_registry (uid);

-- AuditSchema
CREATE TABLE IF NOT EXISTS opsml_audit_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    name TEXT,
    space TEXT,
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
    opsml_version TEXT NOT NULL DEFAULT '0.0.0',
    username TEXT NOT NULL DEFAULT 'guest'
);

CREATE INDEX idx_opsml_audit_registry_space_name_version ON opsml_audit_registry (space, name, version, created_at);
CREATE INDEX idx_opsml_audit_registry_uid ON opsml_audit_registry (uid);

CREATE TABLE IF NOT EXISTS opsml_deck_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    space TEXT,
    name TEXT,
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT,
    cards JSONB NOT NULL DEFAULT '[]',
    opsml_version TEXT NOT NULL DEFAULT '0.0.0',
    username TEXT NOT NULL DEFAULT 'guest'
);
CREATE INDEX idx_opsml_deck_registry_space_name_version ON opsml_deck_registry (space, name, version, created_at);
CREATE INDEX idx_opsml_deck_registry_uid ON opsml_deck_registry (uid);

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
CREATE INDEX idx_experiment_hardware_metrics_created_at ON opsml_experiment_hardware_metric (experiment_uid, created_at);

CREATE TABLE IF NOT EXISTS opsml_user (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    hashed_recovery_codes JSONB NOT NULL,
    permissions JSONB NOT NULL,
    group_permissions JSONB NOT NULL,
    role TEXT DEFAULT 'user',
    favorite_spaces JSONB DEFAULT '[]',
    refresh_token TEXT,
    email TEXT NOT NULL UNIQUE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS opsml_artifact_key (
    uid TEXT PRIMARY KEY,
    space TEXT,
    registry_type TEXT,
    encrypted_key BYTEA,
    storage_key TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS opsml_audit_event (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    username TEXT NOT NULL,
    client_ip TEXT NOT NULL,
    user_agent TEXT,
    operation TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    access_location TEXT,
    status TEXT NOT NULL,
    error_message TEXT,
    metadata TEXT,
    registry_type TEXT,
    route TEXT
);

CREATE INDEX idx_opsml_audit_event_created_at ON opsml_audit_event (created_at);

-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_prompt_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    name TEXT,
    space TEXT,
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT,
    tags JSONB DEFAULT '[]',
    experimentcard_uid TEXT,
    auditcard_uid TEXT,
    opsml_version TEXT NOT NULL DEFAULT '0.0.0',
    username TEXT NOT NULL DEFAULT 'guest'
);
CREATE INDEX idx_opsml_prompt_registry_space_name_version ON opsml_prompt_registry (space, name, version, created_at);
CREATE INDEX idx_opsml_prompt_registry_uid ON opsml_prompt_registry (uid);

CREATE TABLE IF NOT EXISTS opsml_space (
    space TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS opsml_space_name (
    space TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    name TEXT NOT NULL,
    registry_type TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (space, name, registry_type)
);
