-- Populate opsml_data_registry
INSERT INTO opsml_data_registry (uid, app_env, name, space, major, minor, patch, pre_tag, build_tag, version,  tags, data_type, experimentcard_uid,  auditcard_uid, interface_type) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'development', 'Data1', 'repo1', 1, 0, 0, 'alpha', 'build1', '1.0.0-alpha+build1',  '["key1", "key2"]', 'type1', 'experimentcard1',  'auditcard1', 'typeA'),
('550e8400-e29b-41d4-a716-446655440001', 'development', 'Data1', 'repo1', 1, 0, 1, 'beta', 'build2', '1.0.1-beta+build2',  '[]', 'type2', 'experimentcard2',  'auditcard2', 'typeB'),
('550e8400-e29b-41d4-a716-446655440002', 'development', 'Data1', 'repo1', 1, 1, 0, 'gamma', 'build3', '1.1.0-gamma+build3', '[]', 'type3', 'experimentcard3',  'auditcard3', 'typeC'),
('550e8400-e29b-41d4-a716-446655440003', 'development', 'Data1', 'repo1', 1, 1, 1, 'delta', 'build4', '1.1.1', '[]', 'type4', 'experimentcard4',  'auditcard4', 'typeD'),
('550e8400-e29b-41d4-a716-446655440004', 'development', 'Data1', 'repo1', 2, 0, 0, 'epsilon', 'build5', '2.0.0', '[]', 'type5', 'experimentcard5',  'auditcard5', 'typeE'),
('550e8400-e29b-41d4-a716-446655440005', 'development', 'Data1', 'repo1', 2, 0, 1, 'zeta', 'build6', '2.0.1', '[]', 'type6', 'experimentcard6',  'auditcard6', 'typeF'),
('550e8400-e29b-41d4-a716-446655440006', 'development', 'Data1', 'repo1', 2, 1, 0, 'eta', 'build7', '2.1.0', '[]', 'type7', 'experimentcard7',  'auditcard7', 'typeG'),
('550e8400-e29b-41d4-a716-446655440007', 'development', 'Data1', 'repo1', 2, 1, 1, 'theta', 'build8', '2.1.1', '[]', 'type8', 'experimentcard8',  'auditcard8', 'typeH'),
('550e8400-e29b-41d4-a716-446655440008', 'development', 'Data1', 'repo1', 3, 0, 0, 'iota', 'build9', '3.0.0', '[]', 'type9', 'experimentcard9',  'auditcard9', 'typeI'),
('550e8400-e29b-41d4-a716-446655440009', 'development', 'Data1', 'repo1', 3, 0, 1, 'kappa', 'build10', '3.0.1', '[]', 'type10', 'experimentcard10',  'auditcard10', 'typeJ');

-- Populate opsml_model_registry
INSERT INTO opsml_model_registry (uid, app_env, name, space, major, minor, patch, pre_tag, build_tag, version,  tags, datacard_uid, data_type, model_type, experimentcard_uid,  auditcard_uid, interface_type, task_type) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'development', 'Model1', 'repo1', 1, 0, 0, 'alpha', 'build1', '1.0.0', '["hello", "world"]', 'datacard1', 'sample1', 'type1', 'experimentcard1',  'auditcard1', 'typeA', 'task1'),
('550e8400-e29b-41d4-a716-446655440001', 'development', 'Model2', 'repo2', 1, 0, 1, 'beta', 'build2', '1.0.0', '["hello", "world"]', 'datacard2', 'sample2', 'type2', 'experimentcard2',  'auditcard2', 'typeB', 'task2'),
('550e8400-e29b-41d4-a716-446655440002', 'development', 'Model3', 'repo3', 1, 1, 0, 'gamma', 'build3', '1.0.0', '["v3"]', 'datacard3', 'sample3', 'type3', 'experimentcard3',  'auditcard3', 'typeC', 'task3'),
('550e8400-e29b-41d4-a716-446655440003', 'development', 'Model4', 'repo4', 1, 1, 1, 'delta', 'build4', '1.0.0', '[]', 'datacard4', 'sample4', 'type4', 'experimentcard4',  'auditcard4', 'typeD', 'task4'),
('550e8400-e29b-41d4-a716-446655440004', 'development', 'Model5', 'repo5', 2, 0, 0, 'epsilon', 'build5', '1.0.0', '[]', 'datacard5', 'sample5', 'type5', 'experimentcard5',  'auditcard5', 'typeE', 'task5'),
('550e8400-e29b-41d4-a716-446655440005', 'development', 'Model6', 'repo6', 2, 0, 1, 'zeta', 'build6', '1.0.0', '[]', 'datacard6', 'sample6', 'type6', 'experimentcard6',  'auditcard6', 'typeF', 'task6'),
('550e8400-e29b-41d4-a716-446655440006', 'development', 'Model7', 'repo7', 2, 1, 0, 'eta', 'build7', '1.0.0', '[]', 'datacard7', 'sample7', 'type7', 'experimentcard7',  'auditcard7', 'typeG', 'task7'),
('550e8400-e29b-41d4-a716-446655440007', 'development', 'Model8', 'repo8', 2, 1, 1, 'theta', 'build8', '1.0.0', '[]', 'datacard8', 'sample8', 'type8', 'experimentcard8',  'auditcard8', 'typeH', 'task8'),
('550e8400-e29b-41d4-a716-446655440008', 'development', 'Model9', 'repo9', 3, 0, 0, 'iota', 'build9', '1.0.0', '[]', 'datacard9', 'sample9', 'type9', 'experimentcard9',  'auditcard9', 'typeI', 'task9'),
('550e8400-e29b-41d4-a716-446655440009', 'development', 'Model10', 'repo10', 3, 0, 1, 'kappa', 'build10', '1.0.0', '[]', 'datacard10', 'sample10', 'type10', 'experimentcard10',  'auditcard10', 'typeJ', 'task10');

-- Populate opsml_experiment_registry
INSERT INTO opsml_experiment_registry (uid, created_at, app_env, name, space, major, minor, patch, pre_tag, build_tag, version,  tags, datacard_uids, modelcard_uids, promptcard_uids) VALUES 
('550e8400-e29b-41d4-a716-446655440000', '2023-11-28 00:00:00', 'development', 'Run1', 'repo1', 1, 0, 0, 'alpha', 'build1', '0.0.0',  '[]', '["datacard1"]', '["modelcard1"]', '["modelcard1"]'),
('550e8400-e29b-41d4-a716-446655440001', '2023-11-28 00:00:00', 'development', 'Run2', 'repo2', 1, 0, 1, 'beta', 'build2',  '0.0.0', '[]', '["datacard1"]', '["modelcard1"]',  '["modelcard1"]'),
('550e8400-e29b-41d4-a716-446655440002', '2023-11-29 00:00:00', 'development', 'Run3', 'repo3', 1, 1, 0, 'gamma', 'build3', '0.0.0', '[]', '["datacard1"]', '["modelcard1"]',  '["modelcard1"]'),
('550e8400-e29b-41d4-a716-446655440003', '2023-11-29 00:00:00', 'development', 'Run4', 'repo4', 1, 1, 1, 'delta', 'build4', '0.0.0', '[]', '["datacard1"]', '["modelcard1"]', '["modelcard1"]'),
('550e8400-e29b-41d4-a716-446655440004', '2023-11-29 00:00:00', 'development', 'Run5', 'repo5', 2, 0, 0, 'epsilon', 'build5', '0.0.0', '[]', '["datacard1"]', '["modelcard1"]', '["modelcard1"]'),
('550e8400-e29b-41d4-a716-446655440005', '2023-11-29 00:00:00', 'development', 'Run6', 'repo6', 2, 0, 1, 'zeta', 'build6', '0.0.0', '[]', '["datacard1"]', '["modelcard1"]', '["modelcard1"]'),
('550e8400-e29b-41d4-a716-446655440006', '2023-11-29 00:00:00', 'development', 'Run7', 'repo7', 2, 1, 0, 'eta', 'build7', '0.0.0', '[]', '["datacard1"]', '["modelcard1"]',  '["modelcard1"]'),
('550e8400-e29b-41d4-a716-446655440007', '2023-11-29 00:00:00', 'development', 'Run8', 'repo8', 2, 1, 1, 'theta', 'build8', '0.0.0', '[]', '["datacard1"]', '["modelcard1"]', '["modelcard1"]'),
('550e8400-e29b-41d4-a716-446655440008', '2023-11-29 00:00:00', 'development', 'Run9', 'repo9', 3, 0, 0, 'iota', 'build9', '0.0.0', '[]', '["datacard1"]', '["modelcard1"]',  '["modelcard1"]'),
('550e8400-e29b-41d4-a716-446655440009', '2023-11-29 00:00:00', 'development', 'Run10', 'repo10', 3, 0, 1, 'kappa', 'build10', '0.0.0', '[]', '["datacard1"]', '["modelcard1"]', '["modelcard1"]');

-- Populate opsml_skill_registry
INSERT INTO opsml_skill_registry
    (uid, created_at, app_env, space, name, major, minor, patch,
     pre_tag, build_tag, version, tags, compatible_tools, dependencies,
     description, license, content_hash, opsml_version, username)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', '2023-11-28 00:00:00', 'development',
     'repo1', 'Skill1', 1, 0, 0, NULL, NULL, '1.0.0',
     '["tag1","tag2"]', '["claude-code"]', '[]',
     'Skill one', 'MIT', '', '2.0.0', 'guest'),
    ('550e8400-e29b-41d4-a716-446655440002', '2023-11-28 00:00:00', 'development',
     'repo1', 'Skill2', 1, 1, 0, NULL, NULL, '1.1.0',
     '[]', '[]', '[]',
     'Skill two', 'Apache-2.0', '', '2.0.0', 'guest'),
    ('550e8400-e29b-41d4-a716-446655440003', '2023-11-28 00:00:00', 'development',
     'repo1', 'Skill3', 2, 0, 0, NULL, NULL, '2.0.0',
     '["tag1"]', '["codex"]', '[]',
     'Skill three', 'MIT', '', '2.0.0', 'guest'),
    ('550e8400-e29b-41d4-a716-446655440004', '2023-11-29 00:00:00', 'development',
     'repo1', 'Skill4', 1, 0, 1, NULL, NULL, '1.0.1',
     '[]', '[]', '[]',
     NULL, NULL, '', '2.0.0', 'guest'),
    ('550e8400-e29b-41d4-a716-446655440005', '2023-11-29 00:00:00', 'development',
     'repo2', 'Skill5', 1, 0, 0, NULL, NULL, '1.0.0',
     '[]', '["gemini-cli"]', '[]',
     'Skill five', 'MIT', '', '2.0.0', 'guest'),
    ('550e8400-e29b-41d4-a716-446655440006', '2023-11-29 00:00:00', 'development',
     'repo2', 'Skill6', 1, 1, 0, NULL, NULL, '1.1.0',
     '[]', '[]', '[]',
     NULL, NULL, '', '2.0.0', 'guest'),
    ('550e8400-e29b-41d4-a716-446655440007', '2023-11-29 00:00:00', 'development',
     'repo2', 'Skill7', 2, 0, 0, NULL, NULL, '2.0.0',
     '["tag2"]', '["claude-code","codex"]', '[]',
     'Skill seven', 'MIT', '', '2.0.0', 'guest'),
    ('550e8400-e29b-41d4-a716-446655440008', '2023-11-29 00:00:00', 'development',
     'repo1', 'Skill8', 3, 0, 0, NULL, NULL, '3.0.0',
     '[]', '[]', '[]',
     NULL, NULL, '', '2.0.0', 'guest'),
    ('550e8400-e29b-41d4-a716-446655440009', '2023-11-29 00:00:00', 'development',
     'repo1', 'Skill9', 1, 2, 0, NULL, NULL, '1.2.0',
     '[]', '[]', '[]',
     'Skill nine', 'Apache-2.0', '', '2.0.0', 'guest'),
    ('550e8400-e29b-41d4-a716-44665544000a', '2023-11-29 00:00:00', 'development',
     'repo2', 'Skill10', 1, 0, 2, NULL, NULL, '1.0.2',
     '["tag1","tag2"]', '[]', '[]',
     'Skill ten', 'MIT', '', '2.0.0', 'guest');

-- Populate opsml_subagent_registry
INSERT INTO opsml_subagent_registry
    (uid, created_at, app_env, space, name, major, minor, patch,
     pre_tag, build_tag, version, tags, compatible_clis,
     description, content_hash, opsml_version, username, download_count)
VALUES
    ('660e8400-e29b-41d4-a716-446655440001', '2023-11-28 00:00:00', 'development',
     'repo1', 'Agent1', 1, 0, 0, NULL, NULL, '1.0.0',
     '["tag1"]', '["claude-code"]',
     'A test agent', NULL, '2.0.0', 'guest', 0),
    ('660e8400-e29b-41d4-a716-446655440002', '2023-11-28 00:00:00', 'development',
     'repo1', 'Agent2', 1, 1, 0, NULL, NULL, '1.1.0',
     '["tag2"]', '["codex","claude-code"]',
     'Another test agent', NULL, '2.0.0', 'guest', 0),
    ('660e8400-e29b-41d4-a716-446655440003', '2023-11-28 00:00:00', 'development',
     'repo2', 'Agent3', 1, 0, 0, NULL, NULL, '1.0.0',
     '[]', '["gemini-cli"]',
     'Gemini agent', NULL, '2.0.0', 'guest', 0);

-- Populate opsml_audit_registry
INSERT INTO opsml_audit_registry (uid, app_env, name, space, major, minor, patch, pre_tag, build_tag, version,  tags, approved, datacard_uids, modelcard_uids, experimentcard_uids) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'development', 'Audit1', 'repo1', 1, 0, 0, 'alpha', 'build1', '0.0.0', '[]', 1, '[]', '[]', '[]'), 
('550e8400-e29b-41d4-a716-446655440001', 'development', 'Audit2', 'repo2', 1, 0, 1, 'beta', 'build2', '0.0.0', '[]', 0, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440002', 'development', 'Audit3', 'repo3', 1, 1, 0, 'gamma', 'build3', '0.0.0', '[]', 1, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440003', 'development', 'Audit4', 'repo4', 1, 1, 1, 'delta', 'build4', '0.0.0', '[]', 0, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440004', 'development', 'Audit5', 'repo5', 2, 0, 0, 'epsilon', 'build5', '0.0.0', '[]', 1, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440005', 'development', 'Audit6', 'repo6', 2, 0, 1, 'zeta', 'build6', '0.0.0', '[]', 0, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440006', 'development', 'Audit7', 'repo7', 2, 1, 0, 'eta', 'build7', '0.0.0', '[]', 1, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440007', 'development', 'Audit8', 'repo8', 2, 1, 1, 'theta', 'build8', '0.0.0', '[]', 0, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440008', 'development', 'Audit9', 'repo9', 3, 0, 0, 'iota', 'build9', '0.0.0', '[]', 1, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440009', 'development', 'Audit10', 'repo10', 3, 0, 1, 'kappa', 'build10', '0.0.0', '[]', 0, '[]', '[]', '[]');

-- Populate opsml_subagent_registry
INSERT INTO opsml_subagent_registry
    (uid, created_at, app_env, space, name, major, minor, patch,
     pre_tag, build_tag, version, tags, compatible_clis,
     description, content_hash, opsml_version, username, download_count)
VALUES
    ('660e8400-e29b-41d4-a716-446655440001', '2023-11-28 00:00:00', 'development',
     'repo1', 'Agent1', 1, 0, 0, NULL, NULL, '1.0.0',
     '["tag1"]', '["claude-code"]',
     'A test agent', NULL, '2.0.0', 'guest', 0),
    ('660e8400-e29b-41d4-a716-446655440002', '2023-11-28 00:00:00', 'development',
     'repo1', 'Agent2', 1, 1, 0, NULL, NULL, '1.1.0',
     '["tag2"]', '["codex","claude-code"]',
     'Another test agent', NULL, '2.0.0', 'guest', 0),
    ('660e8400-e29b-41d4-a716-446655440003', '2023-11-28 00:00:00', 'development',
     'repo2', 'Agent3', 1, 0, 0, NULL, NULL, '1.0.0',
     '[]', '["gemini-cli"]',
     'Gemini agent', NULL, '2.0.0', 'guest', 0);

-- Populate opsml_tool_registry
INSERT INTO opsml_tool_registry
    (uid, created_at, app_env, space, name, major, minor, patch,
     pre_tag, build_tag, version, tags, tool_type,
     args_schema, description, content_hash, opsml_version, username, download_count)
VALUES
    ('770e8400-e29b-41d4-a716-446655440001', '2023-11-28 00:00:00', 'development',
     'repo1', 'Tool1', 1, 0, 0, NULL, NULL, '1.0.0',
     '["tag1"]', 'ShellScript',
     NULL, 'A shell script tool', NULL, '2.0.0', 'guest', 0),
    ('770e8400-e29b-41d4-a716-446655440002', '2023-11-28 00:00:00', 'development',
     'repo1', 'Tool2', 1, 1, 0, NULL, NULL, '1.1.0',
     '["tag2"]', 'SlashCommand',
     NULL, 'A slash command tool', NULL, '2.0.0', 'guest', 5),
    ('770e8400-e29b-41d4-a716-446655440003', '2023-11-28 00:00:00', 'development',
     'repo1', 'Tool3', 1, 0, 0, NULL, NULL, '1.0.0',
     '[]', 'McpServer',
     NULL, 'An MCP server tool', NULL, '2.0.0', 'guest', 0);
