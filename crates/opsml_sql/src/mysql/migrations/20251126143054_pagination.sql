
-- Data Registry
CREATE INDEX idx_data_grouped
ON opsml_data_registry(space, name, created_at DESC);

-- Model Registry
CREATE INDEX idx_model_grouped
ON opsml_model_registry(space, name, created_at DESC);

-- Experiment Registry
CREATE INDEX idx_experiment_grouped
ON opsml_experiment_registry(space, name, created_at DESC);

-- Deck Registry
CREATE INDEX idx_deck_grouped
ON opsml_deck_registry(space, name, created_at DESC);

-- Prompt Registry
CREATE INDEX idx_prompt_grouped
ON opsml_prompt_registry(space, name, created_at DESC);

-- MCP Registry
CREATE INDEX idx_mcp_grouped
ON opsml_mcp_registry(space, name, created_at DESC);