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
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12);