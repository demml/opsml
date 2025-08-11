ALTER TABLE opsml_artifact_registry ADD COLUMN artifact_type VARCHAR(255) NOT NULL DEFAULT 'generic';

UPDATE opsml_artifact_registry SET artifact_type = 'basic' WHERE artifact_type IS NULL;