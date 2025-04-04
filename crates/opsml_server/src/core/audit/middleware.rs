use crate::core::audit::context::AuditableRequestType;
use crate::core::audit::schema::AuditError;
use crate::core::audit::AuditContext;
use crate::core::state::AppState;
use axum::http::{header, StatusCode};
use axum::middleware::Next;
use axum::response::Json;
use axum::response::{IntoResponse, Response};
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

    let auditable = match request.extensions().get::<AuditableRequestType>() {
        Some(req) => Some(req.clone()),
        None => None,
    };
    // Process the request
    let mut response = next.run(request).await;

    // Get audit context from response extensions if present
    let audit_context = response.extensions().get::<AuditContext>().cloned();

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
        let audit_event = create_audit_event(
            addr,
            agent,
            headers,
            operation_type,
            auditable.get_resource_type(),
            // Only use context for dynamic IDs, otherwise use request data
            audit_context
                .and_then(|ctx| ctx.resource_id)
                .unwrap_or_else(|| auditable.get_resource_id()),
            None,
            metadata,
            auditable.get_registry_type(),
            path,
        );

        state.event_bus.publish(Event::Audit(audit_event));
    }

    Ok(response)
}
