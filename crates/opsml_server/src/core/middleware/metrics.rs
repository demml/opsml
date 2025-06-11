use anyhow::Context;
use axum::{
    extract::{MatchedPath, Request},
    middleware::Next,
    response::IntoResponse,
    routing::get,
    Router,
};

use metrics::{counter, histogram};
use metrics_exporter_prometheus::{Matcher, PrometheusBuilder, PrometheusHandle};
use std::{future::ready, time::Instant};

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
    let router = Router::new().route("/metrics", get(move || ready(recorder_handle.render())));

    Ok(router)
}

pub async fn track_metrics(req: Request, next: Next) -> impl IntoResponse {
    let start = Instant::now();
    let path = if let Some(matched_path) = req.extensions().get::<MatchedPath>() {
        matched_path.as_str().to_owned()
    } else {
        req.uri().path().to_owned()
    };
    let method = req.method().clone();

    let response = next.run(req).await;

    let latency = start.elapsed().as_secs_f64();
    let status = response.status().as_u16().to_string();

    let labels = [
        ("method", method.to_string()),
        ("path", path),
        ("status", status),
    ];

    counter!("http_requests_total", &labels).increment(1);
    histogram!("http_requests_duration_seconds", &labels).record(latency);

    response
}
