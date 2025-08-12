ALTER TABLE opsml_artifact_registry ADD COLUMN IF NOT EXISTS artifact_type TEXT NOT NULL DEFAULT 'generic';

UPDATE opsml_artifact_registry SET artifact_type = 'generic' WHERE artifact_type IS NULL;

CREATE INDEX idx_opsml_artifact_registry_uid_artifact_type ON opsml_artifact_registry (uid, artifact_type);