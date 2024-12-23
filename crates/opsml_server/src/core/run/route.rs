/// Route for checking if a card UID exists
use crate::core::state::AppState;
use anyhow::{Context, Result};
use axum::{
    extract::{Query, State},
    http::StatusCode,
    routing::{get, post, put},
    Json, Router,
};
use opsml_sql::base::SqlClient;
use opsml_sql::schemas::schema::{
    CardResults, HardwareMetricsRecord, MetricRecord, ParameterRecord,
};
use opsml_types::*;

use opsml_utils::utils::get_utc_datetime;
use sqlx::types::Json as SqlxJson;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::path::Path;
use std::sync::Arc;
use tempfile::TempDir;
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
                req.run_uid.clone(),
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
        .get_run_metric(&req.run_uid, &req.names)
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
        .get_run_metric_names(&req.run_uid)
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
        .map(|p| ParameterRecord::new(req.run_uid.clone(), p.name.clone(), p.value.clone()))
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
        .get_run_parameter(&req.run_uid, &req.names)
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

    let records = req
        .metrics
        .iter()
        .map(|p| HardwareMetricsRecord {
            run_uid: req.run_uid.clone(),
            created_at,
            cpu_percent_utilization: p.cpu.cpu_percent_utilization,
            cpu_percent_per_core: p.cpu.cpu_percent_per_core.clone().map(SqlxJson),
            compute_overall: p.cpu.compute_overall,
            compute_utilized: p.cpu.compute_utilized,
            load_avg: p.cpu.load_avg,
            sys_ram_total: p.memory.sys_ram_total,
            sys_ram_used: p.memory.sys_ram_used,
            sys_ram_available: p.memory.sys_ram_available,
            sys_ram_percent_used: p.memory.sys_ram_percent_used,
            sys_swap_total: p.memory.sys_swap_total,
            sys_swap_used: p.memory.sys_swap_used,
            sys_swap_free: p.memory.sys_swap_free,
            sys_swap_percent: p.memory.sys_swap_percent,
            bytes_recv: p.network.bytes_recv,
            bytes_sent: p.network.bytes_sent,
            gpu_percent_utilization: p.gpu.as_ref().map(|gpu| gpu.gpu_percent_utilization),
            gpu_percent_per_core: p
                .gpu
                .as_ref()
                .and_then(|gpu| gpu.gpu_percent_per_core.clone().map(SqlxJson)),
        })
        .collect::<Vec<_>>();

    state
        .sql_client
        .insert_hardware_metrics(&records)
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
        .get_hardware_metric(&req.run_uid)
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
        .map(|m| {
            let gpu = if let Some(gpu_percent_utilization) = m.gpu_percent_utilization {
                Some(GPUMetrics {
                    gpu_percent_utilization,
                    gpu_percent_per_core: m.gpu_percent_per_core.map(|c| c.0),
                })
            } else {
                None
            };

            HardwareMetrics {
                cpu: CPUMetrics {
                    cpu_percent_utilization: m.cpu_percent_utilization,
                    cpu_percent_per_core: m.cpu_percent_per_core.map(|c| c.0),
                    compute_overall: m.compute_overall,
                    compute_utilized: m.compute_utilized,
                    load_avg: m.load_avg,
                },
                memory: MemoryMetrics {
                    sys_ram_total: m.sys_ram_total,
                    sys_ram_used: m.sys_ram_used,
                    sys_ram_available: m.sys_ram_available,
                    sys_ram_percent_used: m.sys_ram_percent_used,
                    sys_swap_total: m.sys_swap_total,
                    sys_swap_used: m.sys_swap_used,
                    sys_swap_free: m.sys_swap_free,
                    sys_swap_percent: m.sys_swap_percent,
                },
                network: NetworkRates {
                    bytes_recv: m.bytes_recv,
                    bytes_sent: m.bytes_sent,
                },
                gpu,
            }
        })
        .collect::<Vec<_>>();

    Ok(Json(metrics))
}

pub async fn get_run_graphs(
    State(state): State<Arc<AppState>>,
    Query(req): Query<GetRunGraphsRequest>,
) -> Result<Json<Vec<RunGraph>>, (StatusCode, Json<serde_json::Value>)> {
    // get the run card
    let args = CardQueryArgs {
        uid: Some(req.run_uid.to_owned()),
        ..Default::default()
    };

    let card_result = state
        .sql_client
        .query_cards(&CardSQLTableNames::Run, &args)
        .await
        .map_err(|e| {
            error!("Failed to get run graphs: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    // get first run card from CardResults enum
    let (repo, name, version) = match card_result {
        CardResults::Run(card) => {
            // get the card UID
            let run_card = card.first().ok_or_else(|| {
                error!("Failed to get run card");
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({})),
                )
            })?;

            (
                run_card.repository.to_owned(),
                run_card.name.to_owned(),
                run_card.version.to_owned(),
            )
        }

        _ => {
            error!("Failed to get run card");
            return Err((
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            ));
        }
    };

    // format uri to get the run graphs (this is a standardized route for all run graphs)
    let uri = format!(
        "{}/{}/{}/v{}/{}",
        CardSQLTableNames::Run,
        repo,
        name,
        version,
        SaveName::Graphs
    );

    let rpath = Path::new(&uri);

    // create temporary directory
    let tmp_dir = TempDir::new().map_err(|e| {
        error!("Failed to create temporary directory: {}", e);
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(serde_json::json!({})),
        )
    })?;

    let tmp_path = tmp_dir.path();

    state
        .storage_client
        .get(tmp_path, rpath, true)
        .await
        .map_err(|e| {
            error!("Failed to get run graphs: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?;

    // load all files in the temp directory as Vec<RunGraph>

    let files: Vec<RunGraph> = std::fs::read_dir(tmp_path)
        .map_err(|e| {
            error!("Failed to read temp directory: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({})),
            )
        })?
        .filter_map(|entry| {
            entry.ok().and_then(|e| {
                let path = e.path();
                let run_graph = match std::fs::read_to_string(&path) {
                    Ok(content) => content,
                    Err(e) => {
                        error!("Failed to read file: {}", e);
                        return None;
                    }
                };

                let run_graph: RunGraph = match serde_json::from_str(&run_graph) {
                    Ok(parsed) => parsed,
                    Err(e) => {
                        error!("Failed to parse run graph: {}", e);
                        return None;
                    }
                };

                Some(run_graph)
            })
        })
        .collect();

    Ok(Json(files))

    // load all run graphs. Can be either SingleRunGraph or MultiRunGraph
}

pub async fn get_run_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(&format!("{}/run/metrics", prefix), put(insert_metrics))
            .route(&format!("{}/run/metrics", prefix), post(get_metrics))
            .route(
                &format!("{}/run/metrics/names", prefix),
                get(get_metric_names),
            )
            .route(
                &format!("{}/run/parameters", prefix),
                put(insert_parameters),
            )
            .route(&format!("{}/run/parameters", prefix), post(get_parameter))
            .route(
                &format!("{}/run/hardware/metrics", prefix),
                put(insert_hardware_metrics),
            )
            .route(
                &format!("{}/run/hardware/metrics", prefix),
                get(get_hardware_metrics),
            )
            .route(&format!("{}/run/graphs", prefix), get(get_run_graphs))
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
