-- Add migration script here
ALTER TABLE opsml_artifact_registry ADD COLUMN IF NOT EXISTS artifact_type TEXT NOT NULL DEFAULT 'generic';