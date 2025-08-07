
CREATE TABLE IF NOT EXISTS opsml_artifact_registry (
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
    filename VARCHAR(255),
    data_type VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);