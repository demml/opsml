
-- Add artifact_type column to opsml_artifact_registry table
ALTER TABLE opsml_artifact_registry ADD COLUMN artifact_type TEXT NOT NULL DEFAULT 'generic';

-- Update existing artifacts to have artifact_type='generic'
UPDATE opsml_artifact_registry SET artifact_type = 'generic' WHERE artifact_type IS NULL;