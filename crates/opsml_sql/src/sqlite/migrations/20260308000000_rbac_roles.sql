CREATE TABLE IF NOT EXISTS opsml_role (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    permissions TEXT NOT NULL DEFAULT '[]',
    is_system   INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO opsml_role (name, description, permissions, is_system) VALUES
  ('admin',          'Full platform access',           '["read:all","write:all","delete:all"]', 1),
  ('user',           'Standard read/write access',     '["read:all","write:all"]', 1),
  ('viewer',         'Read-only across all spaces',    '["read:all"]', 1),
  ('data_scientist', 'Read/write; no delete or admin', '["read:all","write:all"]', 1);
