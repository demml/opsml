CREATE TABLE IF NOT EXISTS opsml_role (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    permissions JSON NOT NULL,
    is_system   TINYINT(1) NOT NULL DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT IGNORE INTO opsml_role (name, description, permissions, is_system) VALUES
  ('admin',          'Full platform access',           '["read:all","write:all","delete:all"]', 1),
  ('user',           'Standard read/write access',     '["read:all","write:all"]', 1),
  ('viewer',         'Read-only across all spaces',    '["read:all"]', 1),
  ('data_scientist', 'Read/write; no delete or admin', '["read:all","write:all"]', 1);
