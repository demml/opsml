-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_data_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags JSONB DEFAULT '[]',
    data_type VARCHAR(64),
    experimentcard_uid VARCHAR(64),
    auditcard_uid VARCHAR(64),
    interface_type VARCHAR(64) NOT NULL DEFAULT 'undefined',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- ModelSchema
CREATE TABLE IF NOT EXISTS opsml_model_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags JSONB DEFAULT '[]',
    datacard_uid VARCHAR(64),
    data_type VARCHAR(64),
    model_type VARCHAR(64),
    experimentcard_uid VARCHAR(64),
    auditcard_uid VARCHAR(64),
    interface_type VARCHAR(64) NOT NULL DEFAULT 'undefined',
    task_type VARCHAR(64) NOT NULL DEFAULT 'undefined',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- RunSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags JSONB DEFAULT '[]',
    datacard_uids JSONB,
    modelcard_uids JSONB,
    experimentcard_uids JSONB,
    artifact_uris JSONB,
    compute_environment JSONB,
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- AuditSchema
CREATE TABLE IF NOT EXISTS opsml_audit_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags JSONB DEFAULT '[]',
    approved BOOLEAN,
    datacard_uids JSONB,
    modelcard_uids JSONB,
    experimentcard_uids JSONB NOT NULL DEFAULT '{}',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);


-- MetricSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_metrics (
    experiment_uid VARCHAR(64),
    name VARCHAR(128),
    value FLOAT,
    step INT,
    timestamp BIGINT,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    idx SERIAL PRIMARY KEY
);

-- ParameterSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_parameters (
    experiment_uid VARCHAR(64),
    name VARCHAR(128),
    value VARCHAR(128),
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    idx SERIAL PRIMARY KEY
);

-- HardwareSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_hardware_metrics (
    experiment_uid VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    cpu_percent_utilization REAL,
    cpu_percent_per_core JSONB, -- JSONB is not supported in SQLite, use TEXT to store JSON strings
    free_memory INT,
    total_memory INT,
    used_memory INT,
    available_memory INT,
    used_percent_memory REAL,
    bytes_recv REAL,
    bytes_sent REAL,
    idx SERIAL PRIMARY KEY
);
CREATE INDEX idx_experiment_hardware_metrics_created_at ON opsml_experiment_hardware_metrics (created_at);

CREATE TABLE IF NOT EXISTS opsml_users (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    active BOOLEAN DEFAULT TRUE,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    permissions JSONB NOT NULL,
    group_permissions JSONB NOT NULL,
    refresh_token VARCHAR(255)

);

  
CREATE TABLE IF NOT EXISTS opsml_artifact_key (
    uid VARCHAR(64) PRIMARY KEY,
    registry_type VARCHAR(32),
    encrypted_key BYTEA,
    storage_key VARCHAR(255),
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW()))
);

CREATE TABLE IF NOT EXISTS opsml_operations (
    username VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    access_type VARCHAR(16) NOT NULL,
    access_location VARCHAR(255) NOT NULL
);
CREATE INDEX idx_opsml_operations_created_at ON opsml_operations (created_at);