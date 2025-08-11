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
use opsml_types::contracts::SpaceNameEvent;
use std::net::SocketAddr;
use std::sync::Arc;

pub async fn event_middleware(
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

    // Handle audit events
    if let Some(ctx) = response.extensions().get::<AuditContext>().cloned() {
        let audit_event =
            create_audit_event(addr, agent.clone(), headers.clone(), path.clone(), ctx);

        state.event_bus.publish(Event::Audit(audit_event));
        response.extensions_mut().remove::<AuditContext>();
    }

    // Handle space name events
    if let Some(event) = response.extensions().get::<SpaceNameEvent>().cloned() {
        state.event_bus.publish(Event::SpaceName(event));
        response.extensions_mut().remove::<SpaceNameEvent>();
    }

    Ok(response)
}
