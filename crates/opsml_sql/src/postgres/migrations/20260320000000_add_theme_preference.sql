-- Add theme_preference column to opsml_user
ALTER TABLE opsml_user ADD COLUMN theme_preference TEXT DEFAULT 'system';
