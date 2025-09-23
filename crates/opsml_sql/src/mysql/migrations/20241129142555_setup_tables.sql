-- Add migration script here
-- MySQL Migration Script

-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_data_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env VARCHAR(32) DEFAULT 'development',
    space VARCHAR(255),
    name VARCHAR(255),
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(255),
    build_tag VARCHAR(255),
    version VARCHAR(255),
    tags JSON,
    data_type VARCHAR(255),
    experimentcard_uid VARCHAR(64),
    auditcard_uid VARCHAR(64),
    interface_type VARCHAR(255) NOT NULL DEFAULT 'undefined',
    opsml_version VARCHAR(255) NOT NULL DEFAULT '0.0.0',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- ModelSchema
CREATE TABLE IF NOT EXISTS opsml_model_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env VARCHAR(32) DEFAULT 'development',
    space VARCHAR(255),
    name VARCHAR(128),
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(255),
    build_tag VARCHAR(255),
    version  VARCHAR(255),
    tags JSON,
    datacard_uid VARCHAR(64),
    data_type VARCHAR(64),
    model_type VARCHAR(64),
    experimentcard_uid VARCHAR(64),
    auditcard_uid VARCHAR(64),
    interface_type  VARCHAR(255) NOT NULL DEFAULT 'undefined',
    task_type VARCHAR(255) NOT NULL DEFAULT 'undefined',
    opsml_version VARCHAR(255) NOT NULL DEFAULT '0.0.0',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- RunSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env VARCHAR(32) DEFAULT 'development',
    space VARCHAR(255),
    name VARCHAR(255),
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(255),
    build_tag VARCHAR(255),
    version VARCHAR(255),
    tags JSON,
    datacard_uids JSON NOT NULL DEFAULT ('[]'),
    modelcard_uids JSON NOT NULL DEFAULT ('[]'),
    promptcard_uids JSON NOT NULL DEFAULT ('[]'),
    card_deck_uids JSON NOT NULL DEFAULT ('[]'),
    experimentcard_uids JSON NOT NULL DEFAULT ('[]'),
    opsml_version VARCHAR(255) NOT NULL DEFAULT '0.0.0',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- AuditSchema
CREATE TABLE IF NOT EXISTS opsml_audit_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env VARCHAR(32) DEFAULT 'development',
    space VARCHAR(255),
    name VARCHAR(255),
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(255),
    build_tag VARCHAR(255),
    version VARCHAR(255),
    tags JSON,
    approved BOOLEAN,
    datacard_uids JSON,
    modelcard_uids JSON,
    experimentcard_uids JSON,
    opsml_version VARCHAR(255) NOT NULL DEFAULT '0.0.0',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

CREATE TABLE IF NOT EXISTS opsml_deck_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env VARCHAR(32) DEFAULT 'development',
    space VARCHAR(255),
    name VARCHAR(255),
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(255),
    build_tag VARCHAR(255),
    version VARCHAR(255),
    cards JSON NOT NULL DEFAULT ('[]'),
    opsml_version VARCHAR(255) NOT NULL DEFAULT '0.0.0',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- MetricSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_metric (
    experiment_uid VARCHAR(64),
    name VARCHAR(255),
    value FLOAT,
    step INT,
    timestamp BIGINT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    idx INT PRIMARY KEY AUTO_INCREMENT
);

-- ParameterSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_parameter (
    experiment_uid VARCHAR(64),
    name VARCHAR(255),
    value JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    idx INT PRIMARY KEY AUTO_INCREMENT
);

-- HardwareSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_hardware_metric (
    experiment_uid VARCHAR(64) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    cpu_percent_utilization FLOAT,
    cpu_percent_per_core JSON, 
    free_memory BIGINT,
    total_memory BIGINT,
    used_memory BIGINT,
    available_memory BIGINT,
    used_percent_memory DOUBLE,
    bytes_recv BIGINT,
    bytes_sent BIGINT,
    idx INT AUTO_INCREMENT PRIMARY KEY,
    INDEX idx_experiment_uid (experiment_uid)
);

CREATE TABLE IF NOT EXISTS opsml_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    hashed_recovery_codes JSON NOT NULL,
    permissions JSON NOT NULL,
    group_permissions JSON NOT NULL,
    role VARCHAR(255) DEFAULT 'user',
    favorite_spaces JSON NOT NULL DEFAULT ('[]'),
    refresh_token VARCHAR(255),
    email VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS opsml_artifact_key (
    uid VARCHAR(64) PRIMARY KEY,
    space VARCHAR(255),
    registry_type VARCHAR(32),
    encrypted_key VARBINARY(255),
    storage_key VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS opsml_audit_event (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR(255) NOT NULL,
    client_ip VARCHAR(255) NOT NULL,
    user_agent VARCHAR(255), 
    operation VARCHAR(255) NOT NULL,  
    resource_type VARCHAR(255) NOT NULL,   
    resource_id VARCHAR(255) NOT NULL,              
    access_location VARCHAR(255),          
    status VARCHAR(255) NOT NULL,        
    error_message VARCHAR(255),          
    metadata VARCHAR(255),               
    registry_type VARCHAR(255),  
    route VARCHAR(512),
    INDEX idx_created_at (created_at)
);

-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_prompt_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(255),
    space VARCHAR(255),
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(255),
    build_tag VARCHAR(255),
    version VARCHAR(255),
    tags JSON,
    experimentcard_uid VARCHAR(64),
    auditcard_uid VARCHAR(64),
    opsml_version VARCHAR(64),
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

CREATE TABLE IF NOT EXISTS opsml_space (
    space VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS opsml_space_name (
    space VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(255) NOT NULL,
    registry_type VARCHAR(64) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (space, name, registry_type)
);