use crate::core::audit::context::AuditableRequestType;
use crate::core::audit::schema::AuditError;
use crate::core::audit::AuditContext;
use crate::core::state::AppState;
use axum::http::StatusCode;
use axum::middleware::Next;
use axum::response::IntoResponse;
use axum::response::Json;
use axum::{
    body::Body,
    extract::{ConnectInfo, State},
    http::{HeaderMap, Request},
};

use axum_extra::TypedHeader;
use headers::UserAgent;
use opsml_events::create_audit_event;
use opsml_events::Event;
use opsml_types::contracts::{AuditableRequest, Operation};
use std::net::SocketAddr;
use std::sync::Arc;

fn operation_from_method(method: &str) -> Operation {
    match method {
        "GET" => Operation::Read,
        "POST" => Operation::Create,
        "PUT" => Operation::Update,
        "DELETE" => Operation::Delete,
        "PATCH" => Operation::Update,
        _ => Operation::Unknown,
    }
}

pub async fn audit_middleware(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    request: Request<Body>,
    next: Next,
) -> Result<impl IntoResponse, (StatusCode, Json<AuditError>)> {
    let method = request.method().clone();
    let path = request.uri().path().to_string();
    let operation_type = operation_from_method(method.as_str());

    // Get auditable before processing request
    let auditable = request.extensions().get::<AuditableRequestType>().cloned();

    // Process the request
    let mut response = next.run(request).await;

    // Get audit context and clone it early
    let audit_context = response.extensions().get::<AuditContext>().cloned();

    // remove the audit context from the response
    // This is important to avoid sending it back to the client
    response.extensions_mut().remove::<AuditContext>();

    if let Some(auditable) = auditable {
        let metadata = auditable.get_metadata().map_err(|_| {
            (
                StatusCode::BAD_REQUEST,
                Json(AuditError {
                    error: "Invalid metadata".to_string(),
                    message: "Failed to extract metadata".to_string(),
                }),
            )
        })?;

        let operation = audit_context
            .as_ref()
            .and_then(|ctx| ctx.operation.clone())
            .unwrap_or(operation_type);

        let resource_id = audit_context
            .as_ref()
            .and_then(|ctx| ctx.resource_id.clone())
            .unwrap_or_else(|| auditable.get_resource_id());

        let audit_event = create_audit_event(
            addr,
            agent,
            headers,
            operation,
            auditable.get_resource_type(),
            resource_id,
            None,
            metadata,
            auditable.get_registry_type(),
            path,
        );

        state.event_bus.publish(Event::Audit(audit_event));
    }

    Ok(response)
}
