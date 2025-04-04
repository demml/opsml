use crate::core::audit::schema::AuditError;
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
use opsml_events::{AuditContext, Event};
use std::net::SocketAddr;
use std::sync::Arc;

pub async fn audit_middleware(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    request: Request<Body>,
    next: Next,
) -> Result<impl IntoResponse, (StatusCode, Json<AuditError>)> {
    let path = request.uri().path().to_string();

    // Process the request
    let mut response = next.run(request).await;

    // Get audit context and clone it early
    let audit_context = response.extensions().get::<AuditContext>().cloned();

    // remove the audit context from the response
    // This is important to avoid sending it back to the client
    response.extensions_mut().remove::<AuditContext>();

    if let Some(ctx) = audit_context {
        let audit_event = create_audit_event(addr, agent, headers, path, ctx);
        state.event_bus.publish(Event::Audit(audit_event));
    }

    Ok(response)
}
