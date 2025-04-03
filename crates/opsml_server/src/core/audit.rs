use axum::http::HeaderMap;
use headers::UserAgent;
use opsml_sql::enums::client::SqlClientEnum;

use anyhow::Result;
use opsml_error::error::ServerError;
use opsml_types::contracts::{AuditStatus, Operation, ResourceType};
use opsml_types::RegistryType;

use std::net::SocketAddr;
use std::sync::Arc;
use tracing::error;
use tracing::{debug, instrument};

#[derive(Debug, Clone)]
pub struct AuditArgs {
    pub addr: SocketAddr,
    pub agent: UserAgent,
    pub headers: HeaderMap,
    pub operation_type: Operation,
    pub resource_type: ResourceType,
    pub resource_id: String,
    pub status: AuditStatus,
    pub error_message: Option<String>,
    pub metadata: String,
    pub registry_type: RegistryType,
}

impl AuditArgs {
    pub fn new(
        addr: SocketAddr,
        agent: UserAgent,
        headers: HeaderMap,
        operation_type: Operation,
        resource_type: ResourceType,
        resource_id: String,
        metadata: String,
        registry_type: RegistryType,
    ) -> Self {
        Self {
            addr,
            agent,
            headers,
            operation_type,
            resource_type,
            resource_id,
            status: AuditStatus::Success,
            error_message: None,
            metadata,
            registry_type,
        }
    }

    pub fn with_error(mut self, error: impl ToString) -> Self {
        self.status = AuditStatus::Failed;
        self.error_message = Some(error.to_string());
        self
    }
}

#[instrument(skip_all)]
pub async fn log_to_audit(
    args: AuditArgs,
    sql_client: Arc<SqlClientEnum>,
) -> Result<(), ServerError> {
    let default_user = "guest".parse().unwrap();
    let username = args
        .headers
        .get("username")
        .unwrap_or(&default_user)
        .to_str()
        .map_err(|e| ServerError::Error(e.to_string()))?;

    // attempt to get forward first
    let client_ip = args
        .headers
        .get("X-Forwarded-For")
        .and_then(|hv| hv.to_str().ok())
        .map(|ip| ip.split(',').next().unwrap_or("unknown").to_string());

    // if not found, use the remote address
    let client_ip = client_ip.unwrap_or_else(|| args.addr.ip().to_string());
    let user_agent_string = args.agent.as_str();

    debug!("Client IP: {}", client_ip);
    debug!("Username: {}", username);
    debug!("User Agent: {}", user_agent_string);
    debug!("Operation Type: {}", args.operation_type);
    debug!("Resource Type: {}", args.resource_type);
    debug!("Resource ID: {}", args.resource_id);
    debug!("Status: {:?}", args.status);
    debug!("Error Message: {:?}", args.error_message);
    debug!("Metadata: {}", args.metadata);
    debug!("Registry Type: {:?}", args.registry_type);
    // Here you would typically log the audit event to your database or logging system

    //sql_client
    //.insert_operation(username, access_type, access_location)
    //.await?;

    Ok(())
}

#[instrument(skip_all)]
pub fn spawn_audit_task(args: AuditArgs, sql_client: Arc<SqlClientEnum>) {
    tokio::spawn(async move {
        if let Err(e) = log_to_audit(args, sql_client).await {
            error!("Failed to log audit event: {}", e);
        }
    });
}
