use crate::core::error::{OpsmlServerError, internal_server_error};

use crate::core::scouter;

use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    Extension, Json, Router,
    extract::{Path, Query, State},
    http::StatusCode,
    routing::{get, post},
};
use opsml_auth::permission::UserPermissions;
use opsml_events::AuditContext;
use opsml_types::api::RequestType;
use opsml_types::contracts::{Operation, ResourceType};

use tracing::debug;

use scouter_client::{
    ScouterServerError, TraceFilters, TraceMetricsRequest, TraceMetricsResponse,
    TracePaginationResponse, TraceRequest, TraceSpansResponse,
};
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tracing::{error, instrument};

/// Get paginated traces
#[utoipa::path(
    post,
    path = "/opsml/api/scouter/trace/paginated",
    request_body(content = inline(serde_json::Value), description = "Trace filter request"),
    responses(
        (status = 200, description = "Paginated traces", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn get_paginated_traces(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<TraceFilters>,
) -> Result<Json<TracePaginationResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !state.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let req = serde_json::to_value(&body)
        .map_err(|e| internal_server_error(e, "Failed to serialize trace filter request", None))?;

    let mut response = state
        .scouter_client
        .request(
            scouter::Routes::TracePage,
            RequestType::Post,
            Some(req),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get paginated traces: {e}");
            internal_server_error(e, "Failed to get paginated traces", None)
        })?;

    response.extensions_mut().insert(AuditContext {
        resource_id: "trace_page".to_string(),
        resource_type: ResourceType::Drift,
        metadata: String::new(),
        registry_type: None,
        operation: Operation::Read,
        access_location: None,
    });

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response
                .json::<TracePaginationResponse>()
                .await
                .map_err(|e| {
                    error!("Failed to parse scouter pagination response: {e}");
                    internal_server_error(e, "Failed to parse scouter response", None)
                })?;
            Ok(Json(body))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {e}");
                internal_server_error(e, "Failed to parse scouter error response", None)
            })?;
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

/// Get trace spans
#[utoipa::path(
    get,
    path = "/opsml/api/scouter/trace/spans",
    params(
        ("trace_id" = String, Query, description = "Trace ID to fetch spans for"),
    ),
    responses(
        (status = 200, description = "Trace spans", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn get_trace_spans(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<TraceRequest>,
) -> Result<Json<TraceSpansResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !state.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let query_string = serde_qs::to_string(&params).map_err(|e| {
        error!("Failed to serialize query string: {e}");
        internal_server_error(e, "Failed to serialize query string", None)
    })?;

    let response = state
        .scouter_client
        .request(
            scouter::Routes::TraceSpans,
            RequestType::Get,
            None,
            Some(query_string),
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get trace spans: {e}");
            internal_server_error(e, "Failed to get trace spans", None)
        })?;

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<TraceSpansResponse>().await.map_err(|e| {
                error!("Failed to parse scouter pagination response: {e}");
                internal_server_error(e, "Failed to parse scouter response", None)
            })?;
            Ok(Json(body))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {e}");
                internal_server_error(e, "Failed to parse scouter error response", None)
            })?;
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

/// Get trace metrics
#[utoipa::path(
    post,
    path = "/opsml/api/scouter/trace/metrics",
    request_body(content = inline(serde_json::Value), description = "Trace metrics request"),
    responses(
        (status = 200, description = "Trace metrics response", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn trace_metrics(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<TraceMetricsRequest>,
) -> Result<Json<TraceMetricsResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !state.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    debug!("Getting trace metrics with params: {:?}", &body);
    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let req = serde_json::to_value(&body)
        .map_err(|e| internal_server_error(e, "Failed to serialize trace metrics request", None))?;

    let mut response = state
        .scouter_client
        .request(
            scouter::Routes::TraceMetrics,
            RequestType::Post,
            Some(req),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get trace metrics: {e}");
            internal_server_error(e, "Failed to get trace metrics", None)
        })?;

    response.extensions_mut().insert(AuditContext {
        resource_id: "trace_metrics".to_string(),
        resource_type: ResourceType::Drift,
        metadata: String::new(),
        registry_type: None,
        operation: Operation::Read,
        access_location: None,
    });

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<TraceMetricsResponse>().await.map_err(|e| {
                error!("Failed to parse scouter metrics response: {e}");
                internal_server_error(e, "Failed to parse scouter response", None)
            })?;
            debug!("Trace metrics response: {:?}", &body);
            Ok(Json(body))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {e}");
                internal_server_error(e, "Failed to parse scouter error response", None)
            })?;
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

/// Get trace spans from filters
#[utoipa::path(
    post,
    path = "/opsml/api/scouter/trace/spans/filters",
    request_body(content = inline(serde_json::Value), description = "Trace filter request for spans"),
    responses(
        (status = 200, description = "Trace spans matching filters", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn get_trace_spans_from_filters(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<TraceFilters>,
) -> Result<Json<TraceSpansResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !state.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let req = serde_json::to_value(&body)
        .map_err(|e| internal_server_error(e, "Failed to serialize trace filter request", None))?;

    let mut response = state
        .scouter_client
        .request(
            scouter::Routes::TraceSpansFilters,
            RequestType::Post,
            Some(req),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get trace spans from filters: {e}");
            internal_server_error(e, "Failed to get trace spans from filters", None)
        })?;

    response.extensions_mut().insert(AuditContext {
        resource_id: "trace_spans_filters".to_string(),
        resource_type: ResourceType::Drift,
        metadata: String::new(),
        registry_type: None,
        operation: Operation::Read,
        access_location: None,
    });

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<TraceSpansResponse>().await.map_err(|e| {
                error!("Failed to parse scouter response: {e}");
                internal_server_error(e, "Failed to parse scouter response", None)
            })?;
            Ok(Json(body))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {e}");
                internal_server_error(e, "Failed to parse scouter error response", None)
            })?;
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

/// Get trace facets (aggregated service and status_code counts) from scouter
#[utoipa::path(
    post,
    path = "/opsml/api/scouter/trace/facets",
    request_body(content = inline(serde_json::Value), description = "Trace filter request for facets"),
    responses(
        (status = 200, description = "Trace facets response", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn get_trace_facets(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(req): Json<serde_json::Value>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<OpsmlServerError>)> {
    if !state.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let mut response = state
        .scouter_client
        .request(
            scouter::Routes::TraceFacets,
            RequestType::Post,
            Some(req),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get trace facets: {e}");
            internal_server_error(e, "Failed to get trace facets", None)
        })?;

    response.extensions_mut().insert(AuditContext {
        resource_id: "trace_facets".to_string(),
        resource_type: ResourceType::Drift,
        metadata: String::new(),
        registry_type: None,
        operation: Operation::Read,
        access_location: None,
    });

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<serde_json::Value>().await.map_err(|e| {
                error!("Failed to parse scouter facets response: {e}");
                internal_server_error(e, "Failed to parse scouter response", None)
            })?;
            Ok(Json(body))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {e}");
                internal_server_error(e, "Failed to parse scouter error response", None)
            })?;
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

/// Get trace spans by trace ID (no time bounds)
#[utoipa::path(
    get,
    path = "/opsml/api/scouter/trace/{id}/spans",
    params(
        ("id" = String, Path, description = "Trace ID (hex-encoded)"),
    ),
    responses(
        (status = 200, description = "Trace spans by ID", body = inline(serde_json::Value)),
        (status = 500, description = "Internal error", body = OpsmlServerError),
    ),
    security(("bearer_token" = [])),
    tag = "scouter"
)]
#[instrument(skip_all)]
pub async fn get_trace_spans_by_id(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Path(id): Path<String>,
) -> Result<Json<TraceSpansResponse>, (StatusCode, Json<OpsmlServerError>)> {
    if !state.scouter_client.is_enabled() {
        return Err((
            StatusCode::SERVICE_UNAVAILABLE,
            Json(OpsmlServerError::new(
                "Scouter service is not available".to_string(),
            )),
        ));
    }

    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let mut response = state
        .scouter_client
        .request_with_path(
            scouter::Routes::TraceSpansById,
            &[id.as_str(), "spans"],
            RequestType::Get,
            None,
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get trace spans by id: {e}");
            internal_server_error(e, "Failed to get trace spans by id", None)
        })?;

    response.extensions_mut().insert(AuditContext {
        resource_id: id.clone(),
        resource_type: ResourceType::Drift,
        metadata: String::new(),
        registry_type: None,
        operation: Operation::Read,
        access_location: None,
    });

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<TraceSpansResponse>().await.map_err(|e| {
                error!("Failed to parse trace spans response: {e}");
                internal_server_error(e, "Failed to parse scouter response", None)
            })?;
            Ok(Json(body))
        }
        false => {
            let body = response.json::<ScouterServerError>().await.map_err(|e| {
                error!("Failed to parse scouter error response: {e}");
                internal_server_error(e, "Failed to parse scouter error response", None)
            })?;
            Err((status_code, Json(OpsmlServerError::new(body.error))))
        }
    }
}

pub async fn get_scouter_trace_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{prefix}/scouter/trace/paginated"),
                post(get_paginated_traces),
            )
            .route(
                &format!("{prefix}/scouter/trace/spans"),
                get(get_trace_spans),
            )
            .route(
                &format!("{prefix}/scouter/trace/metrics"),
                post(trace_metrics),
            )
            .route(
                &format!("{prefix}/scouter/trace/spans/filters"),
                post(get_trace_spans_from_filters),
            )
            .route(
                &format!("{prefix}/scouter/trace/facets"),
                post(get_trace_facets),
            )
            .route(
                &format!("{prefix}/scouter/trace/{{id}}/spans"),
                get(get_trace_spans_by_id),
            )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create scouter trace router");
            Err(anyhow::anyhow!("Failed to create scouter trace router"))
                .context("Panic occurred while creating the trace router")
        }
    }
}
