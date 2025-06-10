
-- Add authentication_type column to opsml_user table
ALTER TABLE opsml_user ADD COLUMN IF NOT EXISTS authentication_type TEXT NOT NULL DEFAULT 'basic';

-- Update existing users to have authentication_type='basic'
UPDATE opsml_user SET authentication_type = 'basic' WHERE authentication_type IS NULL;