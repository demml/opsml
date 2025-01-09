-- Populate opsml_data_registry
INSERT INTO opsml_data_registry (uid, app_env, name, repository, major, minor, patch, pre_tag, build_tag, version, contact, tags, data_type, runcard_uid, pipelinecard_uid, auditcard_uid, interface_type) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'development', 'Data1', 'repo1', 1, 0, 0, 'alpha', 'build1', '1.0.0-alpha+build1', 'contact1', '{"key1": "value1", "key2": "value2"}', 'type1', 'runcard1', 'pipelinecard1', 'auditcard1', 'typeA'),
('550e8400-e29b-41d4-a716-446655440001', 'development', 'Data1', 'repo1', 1, 0, 1, 'beta', 'build2', '1.0.1-beta+build2', 'contact2', '{}', 'type2', 'runcard2', 'pipelinecard2', 'auditcard2', 'typeB'),
('550e8400-e29b-41d4-a716-446655440002', 'development', 'Data1', 'repo1', 1, 1, 0, 'gamma', 'build3', '1.1.0-gamma+build3','contact3', '{}', 'type3', 'runcard3', 'pipelinecard3', 'auditcard3', 'typeC'),
('550e8400-e29b-41d4-a716-446655440003', 'development', 'Data1', 'repo1', 1, 1, 1, 'delta', 'build4', '1.1.1','contact4', '{}', 'type4', 'runcard4', 'pipelinecard4', 'auditcard4', 'typeD'),
('550e8400-e29b-41d4-a716-446655440004', 'development', 'Data1', 'repo1', 2, 0, 0, 'epsilon', 'build5', '2.0.0','contact5', '{}', 'type5', 'runcard5', 'pipelinecard5', 'auditcard5', 'typeE'),
('550e8400-e29b-41d4-a716-446655440005', 'development', 'Data1', 'repo1', 2, 0, 1, 'zeta', 'build6', '2.0.1','contact6', '{}', 'type6', 'runcard6', 'pipelinecard6', 'auditcard6', 'typeF'),
('550e8400-e29b-41d4-a716-446655440006', 'development', 'Data1', 'repo1', 2, 1, 0, 'eta', 'build7', '2.1.0','contact7', '{}', 'type7', 'runcard7', 'pipelinecard7', 'auditcard7', 'typeG'),
('550e8400-e29b-41d4-a716-446655440007', 'development', 'Data1', 'repo1', 2, 1, 1, 'theta', 'build8', '2.1.1','contact8', '{}', 'type8', 'runcard8', 'pipelinecard8', 'auditcard8', 'typeH'),
('550e8400-e29b-41d4-a716-446655440008', 'development', 'Data1', 'repo1', 3, 0, 0, 'iota', 'build9', '3.0.0','contact9', '{}', 'type9', 'runcard9', 'pipelinecard9', 'auditcard9', 'typeI'),
('550e8400-e29b-41d4-a716-446655440009', 'development', 'Data1', 'repo1', 3, 0, 1, 'kappa', 'build10', '3.0.1','contact10', '{}', 'type10', 'runcard10', 'pipelinecard10', 'auditcard10', 'typeJ');

-- Populate opsml_model_registry
INSERT INTO opsml_model_registry (uid, app_env, name, repository, major, minor, patch, pre_tag, build_tag, version, contact, tags, datacard_uid, sample_data_type, model_type, runcard_uid, pipelinecard_uid, auditcard_uid, interface_type, task_type) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'development', 'Model1', 'repo1', 1, 0, 0, 'alpha', 'build1', '1.0.0','contact1', '{}', 'datacard1', 'sample1', 'type1', 'runcard1', 'pipelinecard1', 'auditcard1', 'typeA', 'task1'),
('550e8400-e29b-41d4-a716-446655440001', 'development', 'Model2', 'repo2', 1, 0, 1, 'beta', 'build2', '1.0.0','contact2', '{}', 'datacard2', 'sample2', 'type2', 'runcard2', 'pipelinecard2', 'auditcard2', 'typeB', 'task2'),
('550e8400-e29b-41d4-a716-446655440002', 'development', 'Model3', 'repo3', 1, 1, 0, 'gamma', 'build3', '1.0.0','contact3', '{}', 'datacard3', 'sample3', 'type3', 'runcard3', 'pipelinecard3', 'auditcard3', 'typeC', 'task3'),
('550e8400-e29b-41d4-a716-446655440003', 'development', 'Model4', 'repo4', 1, 1, 1, 'delta', 'build4', '1.0.0','contact4', '{}', 'datacard4', 'sample4', 'type4', 'runcard4', 'pipelinecard4', 'auditcard4', 'typeD', 'task4'),
('550e8400-e29b-41d4-a716-446655440004', 'development', 'Model5', 'repo5', 2, 0, 0, 'epsilon', 'build5', '1.0.0','contact5', '{}', 'datacard5', 'sample5', 'type5', 'runcard5', 'pipelinecard5', 'auditcard5', 'typeE', 'task5'),
('550e8400-e29b-41d4-a716-446655440005', 'development', 'Model6', 'repo6', 2, 0, 1, 'zeta', 'build6', '1.0.0','contact6', '{}', 'datacard6', 'sample6', 'type6', 'runcard6', 'pipelinecard6', 'auditcard6', 'typeF', 'task6'),
('550e8400-e29b-41d4-a716-446655440006', 'development', 'Model7', 'repo7', 2, 1, 0, 'eta', 'build7', '1.0.0','contact7', '{}', 'datacard7', 'sample7', 'type7', 'runcard7', 'pipelinecard7', 'auditcard7', 'typeG', 'task7'),
('550e8400-e29b-41d4-a716-446655440007', 'development', 'Model8', 'repo8', 2, 1, 1, 'theta', 'build8', '1.0.0','contact8', '{}', 'datacard8', 'sample8', 'type8', 'runcard8', 'pipelinecard8', 'auditcard8', 'typeH', 'task8'),
('550e8400-e29b-41d4-a716-446655440008', 'development', 'Model9', 'repo9', 3, 0, 0, 'iota', 'build9', '1.0.0','contact9', '{}', 'datacard9', 'sample9', 'type9', 'runcard9', 'pipelinecard9', 'auditcard9', 'typeI', 'task9'),
('550e8400-e29b-41d4-a716-446655440009', 'development', 'Model10', 'repo10', 3, 0, 1, 'kappa', 'build10', '1.0.0','contact10', '{}', 'datacard10', 'sample10', 'type10', 'runcard10', 'pipelinecard10', 'auditcard10', 'typeJ', 'task10');

-- Populate opsml_run_registry
INSERT INTO opsml_run_registry (uid, created_at, app_env, name, repository, major, minor, patch, pre_tag, build_tag, version, contact, tags, datacard_uids, modelcard_uids, pipelinecard_uid, project, artifact_uris, compute_environment) VALUES 
('550e8400-e29b-41d4-a716-446655440000', '2023-11-28 00:00:00', 'development', 'Run1', 'repo1', 1, 0, 0, 'alpha', 'build1', '0.0.0', 'contact1', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard1', 'project1', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440001', '2023-11-28 00:00:00', 'development', 'Run2', 'repo2', 1, 0, 1, 'beta', 'build2',  '0.0.1','contact2', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard2', 'project2', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440002', '2023-11-29 00:00:00', 'development', 'Run3', 'repo3', 1, 1, 0, 'gamma', 'build3', '0.0.2','contact3', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard3', 'project3', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440003', '2023-11-29 00:00:00', 'development', 'Run4', 'repo4', 1, 1, 1, 'delta', 'build4', '0.0.3','contact4', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard4', 'project4', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440004', '2023-11-29 00:00:00', 'development', 'Run5', 'repo5', 2, 0, 0, 'epsilon', 'build5', '0.0.4','contact5', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard5', 'project5', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440005', '2023-11-29 00:00:00', 'development', 'Run6', 'repo6', 2, 0, 1, 'zeta', 'build6', '0.0.5','contact6', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard6', 'project6', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440006', '2023-11-29 00:00:00', 'development', 'Run7', 'repo7', 2, 1, 0, 'eta', 'build7', '0.0.6','contact7', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard7', 'project7', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440007', '2023-11-29 00:00:00', 'development', 'Run8', 'repo8', 2, 1, 1, 'theta', 'build8', '0.0.7','contact8', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard8', 'project8', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440008', '2023-11-29 00:00:00', 'development', 'Run9', 'repo9', 3, 0, 0, 'iota', 'build9', '0.0.8','contact9', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard9', 'project9', '{}', '{}'),
('550e8400-e29b-41d4-a716-446655440009', '2023-11-29 00:00:00', 'development', 'Run10', 'repo10', 3, 0, 1, 'kappa', 'build10', '0.0.9','contact10', '{}', '["datacard1"]', '["modelcard1"]', 'pipelinecard10', 'project10', '{}', '{}');

-- Populate opsml_audit_registry
INSERT INTO opsml_audit_registry (uid, app_env, name, repository, major, minor, patch, pre_tag, build_tag, version, contact, tags, approved, datacard_uids, modelcard_uids, runcard_uids) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'development', 'Audit1', 'repo1', 1, 0, 0, 'alpha', 'build1', '0.0.0','contact1', '{}', 1, '[]', '[]', '[]'), 
('550e8400-e29b-41d4-a716-446655440001', 'development', 'Audit2', 'repo2', 1, 0, 1, 'beta', 'build2', '0.0.0','contact2', '{}', 0, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440002', 'development', 'Audit3', 'repo3', 1, 1, 0, 'gamma', 'build3', '0.0.0','contact3', '{}', 1, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440003', 'development', 'Audit4', 'repo4', 1, 1, 1, 'delta', 'build4', '0.0.0','contact4', '{}', 0, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440004', 'development', 'Audit5', 'repo5', 2, 0, 0, 'epsilon', 'build5', '0.0.0','contact5', '{}', 1, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440005', 'development', 'Audit6', 'repo6', 2, 0, 1, 'zeta', 'build6', '0.0.0','contact6', '{}', 0, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440006', 'development', 'Audit7', 'repo7', 2, 1, 0, 'eta', 'build7', '0.0.0','contact7', '{}', 1, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440007', 'development', 'Audit8', 'repo8', 2, 1, 1, 'theta', 'build8', '0.0.0','contact8', '{}', 0, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440008', 'development', 'Audit9', 'repo9', 3, 0, 0, 'iota', 'build9', '0.0.0','contact9', '{}', 1, '[]', '[]', '[]'),
('550e8400-e29b-41d4-a716-446655440009', 'development', 'Audit10', 'repo10', 3, 0, 1, 'kappa', 'build10', '0.0.0','contact10', '{}', 0, '[]', '[]', '[]');



INSERT INTO opsml_users (username, password_hash, permissions, group_permissions, refresh_token) VALUES
('admin', '$argon2id$v=19$m=19456,t=2,p=1$+OB+o3Q2x9jwj0Tz1Y8vcA$TXAyajadxyCdaYwjU3zvEylBt9KMosfwfx7xC6PERgI', '["read", "write"]', '["admin"]', NULL)