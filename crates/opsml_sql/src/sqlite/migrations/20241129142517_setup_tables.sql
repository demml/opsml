-- Add migration script here
-- SQLite Migration Script

-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_data_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags TEXT,
    data_type TEXT,
    experimentcard_uid TEXT,
    auditcard_uid TEXT,
    interface_type TEXT NOT NULL DEFAULT 'undefined',
    username TEXT NOT NULL DEFAULT 'guest'
);

-- ModelSchema
CREATE TABLE IF NOT EXISTS opsml_model_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags TEXT,
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags TEXT,
    datacard_uids TEXT,
    modelcard_uids TEXT,
    promptcard_uids TEXT,
    experimentcard_uids TEXT,
    username TEXT NOT NULL DEFAULT 'guest'
);

-- AuditSchema
CREATE TABLE IF NOT EXISTS opsml_audit_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags TEXT,
    approved BOOLEAN,
    datacard_uids TEXT,
    modelcard_uids TEXT,
    experimentcard_uids TEXT,
    username TEXT NOT NULL DEFAULT 'guest'
);


-- MetricSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_metric (
    experiment_uid TEXT,
    name TEXT,
    value REAL,
    step INTEGER,
    timestamp INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    idx INTEGER PRIMARY KEY AUTOINCREMENT
);

-- ParameterSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_parameter (
    experiment_uid TEXT,
    name TEXT,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    idx INTEGER PRIMARY KEY AUTOINCREMENT
);

-- HardwareMetricSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_hardware_metric (
    experiment_uid TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cpu_percent_utilization REAL,
    cpu_percent_per_core TEXT, -- JSONB is not supported in SQLite, use TEXT to store JSON strings
    free_memory INTEGER,
    total_memory INTEGER,
    used_memory INTEGER,
    available_memory INTEGER,
    used_percent_memory REAL,
    bytes_recv INTEGER,
    bytes_sent INTEGER,
    idx INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE IF NOT EXISTS opsml_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    permissions TEXT NOT NULL,
    group_permissions TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    refresh_token TEXT
);

CREATE TABLE IF NOT EXISTS opsml_artifact_key (
    uid TEXT PRIMARY KEY,
    registry_type TEXT,
    encrypted_key TEXT,
    storage_key TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS opsml_audit_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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


CREATE TABLE IF NOT EXISTS opsml_prompt_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags TEXT,
    experimentcard_uid TEXT,
    auditcard_uid TEXT,
    username TEXT NOT NULL DEFAULT 'guest'
);
