CREATE UNIQUE INDEX IF NOT EXISTS uq_skill_space_name_version
ON opsml_skill_registry (space, name, version);
