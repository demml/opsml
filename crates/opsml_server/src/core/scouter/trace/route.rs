use crate::core::error::{OpsmlServerError, internal_server_error};

use crate::core::scouter;

use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    Extension, Json, Router,
    extract::{Query, State},
    http::StatusCode,
    routing::{get, post},
};
use opsml_auth::permission::UserPermissions;

use opsml_types::api::RequestType;

use tracing::debug;

use scouter_client::{
    ScouterServerError, TraceFilters, TraceMetricsRequest, TraceMetricsResponse,
    TracePaginationResponse, TraceRequest, TraceSpansResponse,
};
use std::panic::{AssertUnwindSafe, catch_unwind};
use std::sync::Arc;
use tracing::{error, instrument};

/// Get paginated traces
#[instrument(skip_all)]
pub async fn get_paginated_traces(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(req): Json<TraceFilters>,
) -> Result<Json<TracePaginationResponse>, (StatusCode, Json<OpsmlServerError>)> {
    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let response = state
        .scouter_client
        .request(
            scouter::Routes::TracePage,
            RequestType::Post,
            Some(serde_json::to_value(&req).map_err(|e| {
                error!("Failed to serialize trace filter request: {e}");
                internal_server_error(e, "Failed to serialize trace filter request", None)
            })?),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to acknowledge drift alerts: {e}");
            internal_server_error(e, "Failed to acknowledge drift alerts", None)
        })?;

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

/// Get paginated traces
#[instrument(skip_all)]
pub async fn get_trace_spans(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<TraceRequest>,
) -> Result<Json<TraceSpansResponse>, (StatusCode, Json<OpsmlServerError>)> {
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
#[instrument(skip_all)]
pub async fn trace_metrics(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<TraceMetricsRequest>,
) -> Result<Json<TraceMetricsResponse>, (StatusCode, Json<OpsmlServerError>)> {
    debug!("Getting trace metrics with params: {:?}", &body);
    let exchange_token = state.exchange_token_from_perms(&perms).await.map_err(|e| {
        error!("Failed to exchange token for scouter: {e}");
        internal_server_error(e, "Failed to exchange token for scouter", None)
    })?;

    let response = state
        .scouter_client
        .request(
            scouter::Routes::TraceMetrics,
            RequestType::Post,
            Some(serde_json::to_value(&body).map_err(|e| {
                error!("Failed to serialize trace metrics request: {e}");
                internal_server_error(e, "Failed to serialize trace metrics request", None)
            })?),
            None,
            None,
            &exchange_token,
        )
        .await
        .map_err(|e| {
            error!("Failed to get trace metrics: {e}");
            internal_server_error(e, "Failed to get trace metrics", None)
        })?;

    let status_code = response.status();
    match status_code.is_success() {
        true => {
            let body = response.json::<TraceMetricsResponse>().await.map_err(|e| {
                error!("Failed to parse scouter pagination response: {e}");
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
