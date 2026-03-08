CREATE TABLE IF NOT EXISTS opsml_role (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    permissions JSONB NOT NULL DEFAULT '[]',
    is_system   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO opsml_role (name, description, permissions, is_system) VALUES
  ('admin',          'Full platform access',           '["read:all","write:all","delete:all"]', TRUE),
  ('user',           'Standard read/write access',     '["read:all","write:all"]', TRUE),
  ('viewer',         'Read-only across all spaces',    '["read:all"]', TRUE),
  ('data_scientist', 'Read/write; no delete or admin', '["read:all","write:all"]', TRUE)
ON CONFLICT (name) DO NOTHING;
