-- Add theme_preference column to opsml_user
ALTER TABLE opsml_user ADD COLUMN theme_preference VARCHAR(50) DEFAULT 'system';
