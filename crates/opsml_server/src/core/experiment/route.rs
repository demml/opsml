use crate::core::experiment::types::GroupedMetric;
/// Route for checking if a card UID exists
use crate::core::{error::internal_server_error, state::AppState};
use anyhow::{Context, Result};
use axum::{
    extract::{ConnectInfo, Query, State},
    http::{HeaderMap, StatusCode},
    routing::{get, post, put},
    Json, Router,
};
use axum_extra::TypedHeader;
use headers::UserAgent;
use opsml_client::Routes;
use opsml_events::{create_audit_event, Event};
use opsml_sql::base::SqlClient;
use opsml_sql::schemas::schema::{HardwareMetricsRecord, MetricRecord, ParameterRecord};
use opsml_types::{cards::*, contracts::*, RegistryType};
use opsml_utils::utils::get_utc_datetime;
use sqlx::types::Json as SqlxJson;
use std::net::SocketAddr;
use std::sync::Arc;
use std::{
    collections::HashMap,
    panic::{catch_unwind, AssertUnwindSafe},
};
use tracing::error;

pub async fn insert_metrics(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Json(req): Json<MetricRequest>,
) -> Result<Json<MetricResponse>, (StatusCode, Json<serde_json::Value>)> {
    let audit_event = create_audit_event(
        addr,
        agent,
        headers,
        Operation::Write,
        ResourceType::Database,
        req.experiment_uid.clone(),
        None,
        serde_json::to_string(&req).unwrap_or_default(),
        Some(RegistryType::Experiment),
        Routes::ExperimentMetrics,
    );

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
        .insert_experiment_metrics(&records)
        .await
        .map_err(|e| {
            error!("Failed to insert metric: {}", e);
            internal_server_error(e, "Failed to insert metric")
        })?;

    // Spawn audit task
    state.event_bus.publish(Event::Audit(audit_event));
    Ok(Json(MetricResponse { success: true }))
}

pub async fn get_metrics(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Json(req): Json<GetMetricRequest>,
) -> Result<Json<Vec<Metric>>, (StatusCode, Json<serde_json::Value>)> {
    let audit_event = create_audit_event(
        addr,
        agent,
        headers,
        Operation::Read,
        ResourceType::Database,
        req.experiment_uid.clone(),
        None,
        serde_json::to_string(&req).unwrap_or_default(),
        Some(RegistryType::Experiment),
        Routes::ExperimentMetrics,
    );
    let metrics = state
        .sql_client
        .get_experiment_metric(&req.experiment_uid, &req.names)
        .await
        .map_err(|e| {
            error!("Failed to get metrics: {}", e);
            internal_server_error(e, "Failed to get metrics")
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

    state.event_bus.publish(Event::Audit(audit_event));
    Ok(Json(metrics))
}

pub async fn get_grouped_metrics(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Json(req): Json<UiMetricRequest>,
) -> Result<Json<HashMap<String, Vec<GroupedMetric>>>, (StatusCode, Json<serde_json::Value>)> {
    let mut metric_data: HashMap<String, Vec<GroupedMetric>> = HashMap::new();

    let audit_event = create_audit_event(
        addr,
        agent,
        headers,
        Operation::Read,
        ResourceType::Database,
        Routes::ExperimentGroupedMetrics.to_string(),
        None,
        serde_json::to_string(&req).unwrap_or_default(),
        Some(RegistryType::Experiment),
        Routes::ExperimentGroupedMetrics,
    );

    for experiment in req.experiments {
        let metrics = state
            .sql_client
            .get_experiment_metric(&experiment.uid, &req.metric_names)
            .await
            .map_err(|e| {
                error!("Failed to get metrics: {}", e);
                internal_server_error(e, "Failed to get metrics")
            })?;

        let mut grouped_by_name: HashMap<String, Vec<MetricRecord>> = HashMap::new();
        for metric in metrics {
            grouped_by_name
                .entry(metric.name.clone())
                .or_default()
                .push(metric);
        }

        for (metric_name, metric_records) in grouped_by_name {
            let grouped_metric = GroupedMetric {
                uid: experiment.uid.clone(),
                version: experiment.version.clone(),
                value: metric_records.iter().map(|m| m.value).collect(),
                step: if metric_records.iter().any(|m| m.step.is_some()) {
                    Some(
                        metric_records
                            .iter()
                            .filter_map(|m| m.step.map(|s| s as i64))
                            .collect(),
                    )
                } else {
                    None
                },
                timestamp: if metric_records.iter().any(|m| m.timestamp.is_some()) {
                    Some(metric_records.iter().filter_map(|m| m.timestamp).collect())
                } else {
                    None
                },
            };

            // Add GroupedMetric to the final result
            metric_data
                .entry(metric_name)
                .or_default()
                .push(grouped_metric);
        }
    }

    state.event_bus.publish(Event::Audit(audit_event));
    Ok(Json(metric_data))
}

pub async fn get_metric_names(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Query(req): Query<GetMetricNamesRequest>,
) -> Result<Json<Vec<String>>, (StatusCode, Json<serde_json::Value>)> {
    let audit_event = create_audit_event(
        addr,
        agent,
        headers,
        Operation::Read,
        ResourceType::Database,
        req.experiment_uid.clone(),
        None,
        serde_json::to_string(&req).unwrap_or_default(),
        Some(RegistryType::Experiment),
        Routes::ExperimentMetricNames,
    );
    let names = state
        .sql_client
        .get_experiment_metric_names(&req.experiment_uid)
        .await
        .map_err(|e| {
            error!("Failed to get metrics: {}", e);
            internal_server_error(e, "Failed to get metrics")
        })?;

    state.event_bus.publish(Event::Audit(audit_event));
    Ok(Json(names))
}

pub async fn insert_parameters(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Json(req): Json<ParameterRequest>,
) -> Result<Json<ParameterResponse>, (StatusCode, Json<serde_json::Value>)> {
    let audit_event = create_audit_event(
        addr,
        agent,
        headers,
        Operation::Write,
        ResourceType::Database,
        req.experiment_uid.clone(),
        None,
        serde_json::to_string(&req).unwrap_or_default(),
        Some(RegistryType::Experiment),
        Routes::ExperimentParameters,
    );
    let records = req
        .parameters
        .iter()
        .map(|p| ParameterRecord::new(req.experiment_uid.clone(), p.name.clone(), p.value.clone()))
        .collect::<Vec<_>>();

    state
        .sql_client
        .insert_experiment_parameters(&records)
        .await
        .map_err(|e| {
            error!("Failed to insert parameter: {}", e);
            internal_server_error(e, "Failed to insert parameter")
        })?;

    state.event_bus.publish(Event::Audit(audit_event));
    Ok(Json(ParameterResponse { success: true }))
}

pub async fn get_parameter(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Json(req): Json<GetParameterRequest>,
) -> Result<Json<Vec<Parameter>>, (StatusCode, Json<serde_json::Value>)> {
    let audit_event = create_audit_event(
        addr,
        agent,
        headers,
        Operation::Read,
        ResourceType::Database,
        req.experiment_uid.clone(),
        None,
        serde_json::to_string(&req).unwrap_or_default(),
        Some(RegistryType::Experiment),
        Routes::ExperimentParameters,
    );
    let params = state
        .sql_client
        .get_experiment_parameter(&req.experiment_uid, &req.names)
        .await
        .map_err(|e| {
            error!("Failed to get metrics: {}", e);
            internal_server_error(e, "Failed to get metrics")
        })?;

    // map all entries in the metrics to the Metric struct
    let params = params
        .into_iter()
        .map(|m| Parameter {
            name: m.name,
            value: m.value.0,
        })
        .collect::<Vec<_>>();

    state.event_bus.publish(Event::Audit(audit_event));
    Ok(Json(params))
}

pub async fn insert_hardware_metrics(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    TypedHeader(agent): TypedHeader<UserAgent>,
    headers: HeaderMap,
    Json(req): Json<HardwareMetricRequest>,
) -> Result<Json<HardwareMetricResponse>, (StatusCode, Json<serde_json::Value>)> {
    let audit_event = create_audit_event(
        addr,
        agent,
        headers,
        Operation::Write,
        ResourceType::Database,
        req.experiment_uid.clone(),
        None,
        serde_json::to_string(&req).unwrap_or_default(),
        Some(RegistryType::Experiment),
        Routes::ExperimentHardwareMetrics,
    );
    let created_at = get_utc_datetime();

    let record = HardwareMetricsRecord {
        experiment_uid: req.experiment_uid.clone(),
        created_at,
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
            internal_server_error(e, "Failed to insert hardware metrics")
        })?;

    state.event_bus.publish(Event::Audit(audit_event));
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
            internal_server_error(e, "Failed to get metrics")
        })?;

    // map to the HardwareMetrics struct
    let metrics = metrics
        .into_iter()
        .map(|m| HardwareMetrics {
            created_at: m.created_at,
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

pub async fn get_experiment_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{}/experiment/metrics", prefix),
                put(insert_metrics).post(get_metrics),
            )
            .route(
                &format!("{}/experiment/metrics/grouped", prefix),
                post(get_grouped_metrics),
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
