

INSERT INTO opsml_data_registry (uid, created_at, app_env, name, repository, major, minor, patch, pre_tag, build_tag, version, contact, tags, data_type, runcard_uid, pipelinecard_uid, auditcard_uid, interface_type) VALUES 
('550e8400-e29b-41d4-a716-446655440000', '2023-11-29 00:00:00', 'development', 'Data1', 'repo1', 1, 0, 0, 'alpha', 'build1',   '1.0.0', 'contact1', '{"key1": "value1", "key2": "value2"}'::jsonb, 'type1', 'runcard1', 'pipelinecard1', 'auditcard1', 'typeA'),
('550e8400-e29b-41d4-a716-446655440001', '2023-11-29 00:00:01', 'development', 'Data1', 'repo1', 1, 0, 1, 'beta', 'build2',    '1.0.1', 'contact2', '{}'::jsonb, 'type2', 'runcard2', 'pipelinecard2', 'auditcard2', 'typeB'),
('550e8400-e29b-41d4-a716-446655440002', '2023-11-29 00:00:02', 'development', 'Data1', 'repo1', 1, 1, 0, 'gamma', 'build3',   '1.1.0', 'contact3', '{}'::jsonb, 'type3', 'runcard3', 'pipelinecard3', 'auditcard3', 'typeC'),
('550e8400-e29b-41d4-a716-446655440003', '2023-11-29 00:00:03', 'development', 'Data1', 'repo1', 1, 1, 1, 'delta', 'build4',   '1.1.1', 'contact4', '{}'::jsonb, 'type4', 'runcard4', 'pipelinecard4', 'auditcard4', 'typeD'),
('550e8400-e29b-41d4-a716-446655440004', '2023-11-29 00:00:04', 'development', 'Data1', 'repo1', 2, 0, 0, 'epsilon', 'build5', '2.0.0', 'contact5', '{}'::jsonb, 'type5', 'runcard5', 'pipelinecard5', 'auditcard5', 'typeE'),
('550e8400-e29b-41d4-a716-446655440005', '2023-11-29 00:00:05', 'development', 'Data1', 'repo1', 2, 0, 1, 'zeta', 'build6',    '2.0.1', 'contact6', '{}'::jsonb, 'type6', 'runcard6', 'pipelinecard6', 'auditcard6', 'typeF'),
('550e8400-e29b-41d4-a716-446655440006', '2023-11-29 00:00:06', 'development', 'Data1', 'repo1', 2, 1, 0, 'eta', 'build7',     '2.1.0', 'contact7', '{}'::jsonb, 'type7', 'runcard7', 'pipelinecard7', 'auditcard7', 'typeG'),
('550e8400-e29b-41d4-a716-446655440007', '2023-11-29 00:00:07', 'development', 'Data1', 'repo1', 2, 1, 1, 'theta', 'build8',   '2.1.1', 'contact8', '{}'::jsonb, 'type8', 'runcard8', 'pipelinecard8', 'auditcard8', 'typeH'),
('550e8400-e29b-41d4-a716-446655440008', '2023-11-29 00:00:08', 'development', 'Data1', 'repo1', 3, 0, 0, 'iota', 'build9',    '3.0.0', 'contact9', '{}'::jsonb, 'type9', 'runcard9', 'pipelinecard9', 'auditcard9', 'typeI'),
('550e8400-e29b-41d4-a716-446655440009', '2023-11-29 00:00:09', 'development', 'Data1', 'repo1', 3, 0, 1, 'kappa', 'build10',  '3.0.1','contact10', '{}'::jsonb, 'type10', 'runcard10', 'pipelinecard10', 'auditcard10', 'typeJ');

-- Populate opsml_model_registry
INSERT INTO opsml_model_registry (uid, created_at, app_env, name, repository, major, minor, patch, pre_tag, build_tag, version, contact, tags, datacard_uid, sample_data_type, model_type, runcard_uid, pipelinecard_uid, auditcard_uid, interface_type, task_type) VALUES 
('550e8400-e29b-41d4-a716-446655440000', '2023-11-29 00:00:00', 'development', 'Model1', 'repo1', 1, 0, 0, 'alpha', 'build1', '1.0.0', 'contact1', '{}'::jsonb, 'datacard1', 'sample1', 'type1', 'runcard1', 'pipelinecard1', 'auditcard1', 'typeA', 'task1'),
('550e8400-e29b-41d4-a716-446655440001', '2023-11-29 00:00:00', 'development', 'Model2', 'repo2', 1, 0, 1, 'beta', 'build2', '1.0.0', 'contact2', '{}'::jsonb, 'datacard2', 'sample2', 'type2', 'runcard2', 'pipelinecard2', 'auditcard2', 'typeB', 'task2'),
('550e8400-e29b-41d4-a716-446655440003', '2023-11-29 00:00:00', 'development', 'Model4', 'repo4', 1, 1, 1, 'delta', 'build4', '1.0.0', 'contact4', '{}'::jsonb, 'datacard4', 'sample4', 'type4', 'runcard4', 'pipelinecard4', 'auditcard4', 'typeD', 'task4'),
('550e8400-e29b-41d4-a716-446655440004', '2023-11-29 00:00:00', 'development', 'Model5', 'repo5', 2, 0, 0, 'epsilon', 'build5', '1.0.0', 'contact5', '{}'::jsonb, 'datacard5', 'sample5', 'type5', 'runcard5', 'pipelinecard5', 'auditcard5', 'typeE', 'task5'),
('550e8400-e29b-41d4-a716-446655440005', '2023-11-29 00:00:00', 'development', 'Model6', 'repo6', 2, 0, 1, 'zeta', 'build6', '1.0.0', 'contact6', '{}'::jsonb, 'datacard6', 'sample6', 'type6', 'runcard6', 'pipelinecard6', 'auditcard6', 'typeF', 'task6'),
('550e8400-e29b-41d4-a716-446655440006', '2023-11-29 00:00:00', 'development', 'Model7', 'repo7', 2, 1, 0, 'eta', 'build7', '1.0.0', 'contact7', '{}'::jsonb, 'datacard7', 'sample7', 'type7', 'runcard7', 'pipelinecard7', 'auditcard7', 'typeG', 'task7'),
('550e8400-e29b-41d4-a716-446655440007', '2023-11-29 00:00:00', 'development', 'Model8', 'repo8', 2, 1, 1, 'theta', 'build8', '1.0.0', 'contact8', '{}'::jsonb, 'datacard8', 'sample8', 'type8', 'runcard8', 'pipelinecard8', 'auditcard8', 'typeH', 'task8'),
('550e8400-e29b-41d4-a716-446655440008', '2023-11-29 00:00:00', 'development', 'Model9', 'repo9', 3, 0, 0, 'iota', 'build9', '1.0.0', 'contact9', '{}'::jsonb, 'datacard9', 'sample9', 'type9', 'runcard9', 'pipelinecard9', 'auditcard9', 'typeI', 'task9'),
('550e8400-e29b-41d4-a716-446655440009', '2023-11-29 00:00:00', 'development', 'Model10', 'repo10', 3, 0, 1, 'kappa', 'build10', '1.0.0', 'contact10', '{}'::jsonb, 'datacard10', 'sample10', 'type10', 'runcard10', 'pipelinecard10', 'auditcard10', 'typeJ', 'task10');


-- Populate opsml_run_registry
INSERT INTO opsml_run_registry (uid, created_at, app_env, name, repository, major, minor, patch, pre_tag, build_tag, version, contact, tags, datacard_uids, modelcard_uids, pipelinecard_uid, project, artifact_uris, compute_environment) VALUES 
('550e8400-e29b-41d4-a716-446655440000', '2023-11-28 00:00:00', 'development', 'Run1', 'repo1', 1, 0, 0, 'alpha', 'build1', '1.0.0', 'contact1', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard1', 'project1', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440001', '2023-11-28 00:00:00', 'development', 'Run2', 'repo2', 1, 0, 1, 'beta', 'build2', '1.0.0', 'contact2', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard2', 'project2', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440002', '2023-11-29 00:00:00', 'development', 'Run3', 'repo3', 1, 1, 0, 'gamma', 'build3', '1.0.0', 'contact3', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard3', 'project3', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440003', '2023-11-29 00:00:00', 'development', 'Run4', 'repo4', 1, 1, 1, 'delta', 'build4', '1.0.0', 'contact4', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard4', 'project4', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440004', '2023-11-29 00:00:00', 'development', 'Run5', 'repo5', 2, 0, 0, 'epsilon', 'build5', '1.0.0', 'contact5', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard5', 'project5', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440005', '2023-11-29 00:00:00', 'development', 'Run6', 'repo6', 2, 0, 1, 'zeta', 'build6', '1.0.0', 'contact6', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard6', 'project6', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440006', '2023-11-29 00:00:00', 'development', 'Run7', 'repo7', 2, 1, 0, 'eta', 'build7', '1.0.0', 'contact7', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard7', 'project7', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440007', '2023-11-29 00:00:00', 'development', 'Run8', 'repo8', 2, 1, 1, 'theta', 'build8', '1.0.0', 'contact8', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard8', 'project8', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440008', '2023-11-29 00:00:00', 'development', 'Run9', 'repo9', 3, 0, 0, 'iota', 'build9', '1.0.0', 'contact9', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard9', 'project9', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440009', '2023-11-29 00:00:00', 'development', 'Run10', 'repo10', 3, 0, 1, 'kappa', 'build10', '1.0.0', 'contact10', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard10', 'project10', '{}', '{}');

-- Populate opsml_audit_registry
INSERT INTO opsml_audit_registry (uid, app_env, name, repository, major, minor, patch, pre_tag, build_tag, version, contact, tags, approved, datacard_uids, modelcard_uids, runcard_uids) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'development', 'Audit1', 'repo1', 1, 0, 0, 'alpha', 'build1', '1.0.0', 'contact1', '{}', true, '[]', '[]', '[]'), 
('550e8400-e29b-41d4-a716-446655440001', 'development', 'Audit2', 'repo2', 1, 0, 1, 'beta', 'build2', '1.0.0', 'contact2', '{}', false, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440002', 'development', 'Audit3', 'repo3', 1, 1, 0, 'gamma', 'build3', '1.0.0', 'contact3', '{}', true, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440003', 'development', 'Audit4', 'repo4', 1, 1, 1, 'delta', 'build4', '1.0.0', 'contact4', '{}', false, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440004', 'development', 'Audit5', 'repo5', 2, 0, 0, 'epsilon', 'build5', '1.0.0', 'contact5', '{}', true, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440005', 'development', 'Audit6', 'repo6', 2, 0, 1, 'zeta', 'build6', '1.0.0', 'contact6', '{}', false, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440006', 'development', 'Audit7', 'repo7', 2, 1, 0, 'eta', 'build7', '1.0.0', 'contact7', '{}', true, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440007', 'development', 'Audit8', 'repo8', 2, 1, 1, 'theta', 'build8', '1.0.0', 'contact8', '{}', false, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440008', 'development', 'Audit9', 'repo9', 3, 0, 0, 'iota', 'build9', '1.0.0', 'contact9', '{}', true, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440009', 'development', 'Audit10', 'repo10', 3, 0, 1, 'kappa', 'build10', '1.0.0', 'contact10', '{}', false, '[]', '[]', '[]');

