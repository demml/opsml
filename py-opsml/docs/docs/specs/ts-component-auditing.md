# Technical Component Specification: Audit Events

## Overview
The Audit Events system provides comprehensive tracking and logging of system operations and is integrated with the OpsML server EventBus. The goal of Audit logging is to capture relevant information about how the OpsML server is being used and operational details. Audit events are currently opt-in and will expand as the server evolves.

Audit event capture is integrated via an audit middleware that parses response extensions for `AuditContext`. If `AuditContext` is present, it is extracted and used to create an `AuditEvent`. The event is then sent to the `EventBus` for asynchronous processing and storage in the connected SQL database. Thus for a server route to become `auditable`, it must return an `AuditContext` in the response extensions. **Note** that the `AuditContext` is a custom response extension and is removed after it is processed and is not exposed to the client.

## Component Definition

````rust
pub struct AuditContext {
    pub resource_id: String,
    pub resource_type: ResourceType,
    pub metadata: String,
    pub operation: Operation,
    pub registry_type: Option<RegistryType>,
    pub access_location: Option<String>,
}

pub struct AuditEvent {
    pub username: String,
    pub client_ip: String,
    pub user_agent: String,
    pub operation: Operation,
    pub resource_type: ResourceType,
    pub resource_id: String,
    pub access_location: Option<String>,
    pub status: AuditStatus,
    pub error_message: Option<String>,
    pub metadata: String,
    pub registry_type: Option<RegistryType>,
    pub route: String,
}
````

## Core Responsibilities

1. **Event Creation**
   - Request context capture
   - User identification
   - Operation tracking
   - Resource monitoring

2. **Audit Context Management**
   - Resource tracking
   - Operation classification
   - Registry type handling
   - Metadata collection

3. **Event Persistence**
   - Asynchronous storage
   - SQL backend integration
   - Error handling
   - Event querying

## Key Methods

### Event Creation
````rust
pub fn create_audit_event(
    addr: SocketAddr,
    agent: UserAgent,
    headers: HeaderMap,
    route: String,
    context: AuditContext,
) -> AuditEvent
````

### Event Logging
````rust
pub async fn log_audit_event(
    event: AuditEvent,
    sql_client: Arc<SqlClientEnum>,
) -> Result<(), EventError>
````

## Dependencies

- **External Crates**
  - `axum`: Web framework integration
  - `headers`: HTTP header handling
  - `tracing`: Logging and instrumentation
  - `sqlx`: Database operations

- **Internal Components**
  - `SqlClient`: Database interface
  - `EventBus`: Event distribution
  - `EventError`: Error handling

## Error Handling

- Custom `EventError` type
- SQL operation error handling
- Debug logging for failures
- Error context preservation

## Security Considerations

1. **User Tracking**
   - Username capture
   - IP address logging
   - User agent recording
   - Access location tracking

2. **Operation Auditing**
   - Resource access logging
   - Operation classification
   - Status tracking
   - Error message capture

3. **Data Privacy**
   - Sensitive data handling
   - User information protection
   - Access control integration

## Performance Considerations

1. **Asynchronous Processing**
   - Non-blocking event creation
   - Async database operations
   - Efficient event distribution

2. **Resource Usage**
   - Minimal memory overhead
   - Shared SQL connection via server AppState

## Future Considerations

1. Event aggregation capabilities
2. Enhanced filtering options
3. Real-time audit monitoring
4. Advanced security features
5. Audit data analysis tools
6. Compliance reporting features

---

*Version: 1.0*  
*Last Updated: 2025-04-04*  
*Component Owner: Steven Forrester*