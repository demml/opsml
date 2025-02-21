/// Route for checking if a card UID exists
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::{Query, State},
    http::StatusCode,
    routing::{get, put},
    Json, Router,
};
use opsml_sql::base::SqlClient;
use opsml_sql::schemas::schema::{HardwareMetricsRecord, MetricRecord, ParameterRecord};
use opsml_types::{cards::*, contracts::*};
use opsml_utils::utils::get_utc_datetime;
use sqlx::types::Json as SqlxJson;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use tracing::error;

pub async fn insert_metrics(
    State(state): State<Arc<AppState>>,
    Json(req): Json<MetricRequest>,
) -> Result<Json<MetricResponse>, (StatusCode, Json<serde_json::Value>)> {
    let records = req
        .metrics
        .iter()
        .map(|m| {
            MetricRecord::new(
                req.experiment_uid.clone(),
                m.name.clone(),
                m.value,
                m.step,
                m.timestamp,
            )
        })
        .collect::<Vec<_>>();

    state
        .sql_client
        .insert_run_metrics(&records)
        .await
        .map_err(|e| {
            error!("Failed to insert metric: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    Ok(Json(MetricResponse { success: true }))
}

pub async fn get_metrics(
    State(state): State<Arc<AppState>>,
    Json(req): Json<GetMetricRequest>,
) -> Result<Json<Vec<Metric>>, (StatusCode, Json<serde_json::Value>)> {
    // something is going on with how serde_qs is parsing the query when using names as a list
    let metrics = state
        .sql_client
        .get_run_metric(&req.experiment_uid, &req.names)
        .await
        .map_err(|e| {
            error!("Failed to get metrics: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    // map all entries in the metrics to the Metric struct
    let metrics = metrics
        .into_iter()
        .map(|m| Metric {
            name: m.name,
            value: m.value,
            step: m.step,
            timestamp: m.timestamp,
            created_at: m.created_at,
        })
        .collect::<Vec<_>>();

    Ok(Json(metrics))
}

pub async fn get_metric_names(
    State(state): State<Arc<AppState>>,
    Query(req): Query<GetMetricNamesRequest>,
) -> Result<Json<Vec<String>>, (StatusCode, Json<serde_json::Value>)> {
    let names = state
        .sql_client
        .get_run_metric_names(&req.experiment_uid)
        .await
        .map_err(|e| {
            error!("Failed to get metrics: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    Ok(Json(names))
}

pub async fn insert_parameters(
    State(state): State<Arc<AppState>>,
    Json(req): Json<ParameterRequest>,
) -> Result<Json<ParameterResponse>, (StatusCode, Json<serde_json::Value>)> {
    let records = req
        .parameters
        .iter()
        .map(|p| ParameterRecord::new(req.experiment_uid.clone(), p.name.clone(), p.value.clone()))
        .collect::<Vec<_>>();

    state
        .sql_client
        .insert_run_parameters(&records)
        .await
        .map_err(|e| {
            error!("Failed to insert parameter: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    Ok(Json(ParameterResponse { success: true }))
}

pub async fn get_parameter(
    State(state): State<Arc<AppState>>,
    Json(req): Json<GetParameterRequest>,
) -> Result<Json<Vec<Parameter>>, (StatusCode, Json<serde_json::Value>)> {
    let params = state
        .sql_client
        .get_run_parameter(&req.experiment_uid, &req.names)
        .await
        .map_err(|e| {
            error!("Failed to get metrics: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    // map all entries in the metrics to the Metric struct
    let params = params
        .into_iter()
        .map(|m| Parameter {
            name: m.name,
            value: m.value,
            created_at: m.created_at,
        })
        .collect::<Vec<_>>();

    Ok(Json(params))
}

pub async fn insert_hardware_metrics(
    State(state): State<Arc<AppState>>,
    Json(req): Json<HardwareMetricRequest>,
) -> Result<Json<HardwareMetricResponse>, (StatusCode, Json<serde_json::Value>)> {
    let created_at = get_utc_datetime();

    let record = HardwareMetricsRecord {
        experiment_uid: req.experiment_uid.clone(),
        created_at: created_at.clone(),
        cpu_percent_utilization: req.metrics.cpu.cpu_percent_utilization,
        cpu_percent_per_core: SqlxJson(req.metrics.cpu.cpu_percent_per_core.clone()),
        free_memory: req.metrics.memory.free_memory,
        total_memory: req.metrics.memory.total_memory,
        used_memory: req.metrics.memory.used_memory,
        available_memory: req.metrics.memory.available_memory,
        used_percent_memory: req.metrics.memory.used_percent_memory,
        bytes_recv: req.metrics.network.bytes_recv,
        bytes_sent: req.metrics.network.bytes_sent,
    };

    state
        .sql_client
        .insert_hardware_metrics(&record)
        .await
        .map_err(|e| {
            error!("Failed to insert hardware metrics: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    Ok(Json(HardwareMetricResponse { success: true }))
}

pub async fn get_hardware_metrics(
    State(state): State<Arc<AppState>>,
    Query(req): Query<GetHardwareMetricRequest>,
) -> Result<Json<Vec<HardwareMetrics>>, (StatusCode, Json<serde_json::Value>)> {
    let metrics = state
        .sql_client
        .get_hardware_metric(&req.experiment_uid)
        .await
        .map_err(|e| {
            error!("Failed to get metrics: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    // map to the HardwareMetrics struct
    let metrics = metrics
        .into_iter()
        .map(|m| HardwareMetrics {
            cpu: CPUMetrics {
                cpu_percent_utilization: m.cpu_percent_utilization,
                cpu_percent_per_core: m.cpu_percent_per_core.to_vec(),
            },
            memory: MemoryMetrics {
                free_memory: m.free_memory,
                total_memory: m.total_memory,
                used_memory: m.used_memory,
                available_memory: m.available_memory,
                used_percent_memory: m.used_percent_memory,
            },
            network: NetworkRates {
                bytes_recv: m.bytes_recv,
                bytes_sent: m.bytes_sent,
            },
        })
        .collect::<Vec<_>>();

    Ok(Json(metrics))
}

pub async fn get_run_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{}/experiment/metrics", prefix),
                put(insert_metrics).post(get_metrics),
            )
            .route(
                &format!("{}/experiment/metrics/names", prefix),
                get(get_metric_names),
            )
            .route(
                &format!("{}/experiment/parameters", prefix),
                put(insert_parameters).post(get_parameter),
            )
            .route(
                &format!("{}/experiment/hardware/metrics", prefix),
                put(insert_hardware_metrics).get(get_hardware_metrics),
            )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create run router");
            // panic
            Err(anyhow::anyhow!("Failed to create run router"))
                .context("Panic occurred while creating the router")
        }
    }
}
