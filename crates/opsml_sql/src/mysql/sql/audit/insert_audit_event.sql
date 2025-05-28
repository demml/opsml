INSERT INTO opsml_audit_event (
    username, 
    client_ip, 
    user_agent, 
    operation, 
    resource_type, 
    resource_id,
    access_location,
    status,
    error_message,
    metadata,
    registry_type,
    route
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);