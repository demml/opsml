use anyhow::Context;
use axum::{
    Router,
    extract::{MatchedPath, Request},
    middleware::Next,
    response::IntoResponse,
    routing::get,
};
use metrics::{counter, histogram};
use metrics_exporter_prometheus::{Matcher, PrometheusBuilder, PrometheusHandle};
use std::{future::ready, time::Instant};
use tracing::info;

fn setup_metrics_recorder() -> Result<PrometheusHandle, anyhow::Error> {
    const EXPONENTIAL_SECONDS: &[f64] = &[
        0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0,
    ];

    let builder = PrometheusBuilder::new();
    let builder = builder
        .set_buckets_for_metric(
            Matcher::Full("http_requests_duration_seconds".to_string()),
            EXPONENTIAL_SECONDS,
        )
        .with_context(|| "Failed to set buckets for metric")?;

    builder
        .install_recorder()
        .with_context(|| "Failed to install recorder")
}

pub fn metrics_app() -> Result<Router, anyhow::Error> {
    let recorder_handle =
        setup_metrics_recorder().with_context(|| "Failed to setup metrics recorder")?;
    info!("Metrics recorder initialized successfully");
    let router = Router::new().route("/metrics", get(move || ready(recorder_handle.render())));

    Ok(router)
}

pub async fn track_metrics(req: Request, next: Next) -> impl IntoResponse {
    let start = Instant::now();

    // Extract method as Cow to avoid allocation for common methods
    let method = req.method().clone();
    let path = if let Some(matched_path) = req.extensions().get::<MatchedPath>() {
        matched_path.as_str().to_owned()
    } else {
        req.uri().path().to_owned()
    };

    // Get request size
    let request_size = req
        .headers()
        .get("content-length")
        .and_then(|cl| cl.to_str().ok())
        .and_then(|cls| cls.parse::<u64>().ok())
        .unwrap_or(0);

    let response = next.run(req).await;

    let latency = start.elapsed().as_secs_f64();
    let status = response.status().as_u16().to_string();

    // Response size
    let response_size = response
        .headers()
        .get("content-length")
        .and_then(|cl| cl.to_str().ok())
        .and_then(|cls| cls.parse::<u64>().ok())
        .unwrap_or(0);

    // Use .as_str() to get &str for metrics macros
    let label_arr = [
        ("method", method.to_string()),
        ("path", path.to_string()),
        ("status", status.to_string()),
    ];

    counter!("http_requests_total", &label_arr).increment(1);
    counter!("http_request_size_bytes", &[("path", path.to_string())]).increment(request_size);
    counter!("http_response_size_bytes", &[("path", path.to_string())]).increment(response_size);

    histogram!("http_request_duration_highr_seconds").record(latency);
    histogram!(
        "http_request_duration_seconds",
        &[("method", method.to_string()), ("path", path.to_string())]
    )
    .record(latency);

    response
}
