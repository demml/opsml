use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode, header},
};
use http_body_util::BodyExt; // for `collect`
use opsml_server::core::experiment::types::GroupedMetric;
use opsml_types::{
    cards::{HardwareMetrics, Metric, Parameter, ParameterValue},
    contracts::*,
};
use std::collections::HashMap;
#[tokio::test]
async fn test_opsml_server_experiment_routes() {
    let helper = TestHelper::new(None).await;
    let experiment_uid = "550e8400-e29b-41d4-a716-446655440000".to_string();

    let request = MetricRequest {
        experiment_uid: experiment_uid.clone(),
        metrics: vec![
            Metric {
                name: "metric1".to_string(),
                value: 1.0,
                ..Default::default()
            },
            Metric {
                name: "metric2".to_string(),
                value: 1.0,
                is_eval: true,
                ..Default::default()
            },
        ],
    };

    let body = serde_json::to_string(&request).unwrap();

    let request = Request::builder()
        .uri("/opsml/api/experiment/metrics")
        .method("PUT")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let query_string = serde_qs::to_string(&GetMetricNamesRequest {
        experiment_uid: experiment_uid.clone(),
    })
    .unwrap();

    let request = Request::builder()
        .uri(format!(
            "/opsml/api/experiment/metrics/names?{query_string}",
        ))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let metric_names: Vec<String> = serde_json::from_slice(&body).unwrap();

    assert_eq!(metric_names.len(), 2);

    // get metric by experiment_uid
    let body = GetMetricRequest::new(experiment_uid.clone(), None, None);

    let request = Request::builder()
        .uri("/opsml/api/experiment/metrics") // should be post
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&body).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let metrics: Vec<Metric> = serde_json::from_slice(&body).unwrap();

    assert_eq!(metrics.len(), 2);

    // get metric by experiment_uid
    let body = GetMetricRequest::new(
        experiment_uid.clone(),
        Some(vec!["metric1".to_string()]),
        None,
    );

    let request = Request::builder()
        .uri("/opsml/api/experiment/metrics") // should be post
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&body).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let metrics: Vec<Metric> = serde_json::from_slice(&body).unwrap();

    assert_eq!(metrics.len(), 1);

    // get eval metric
    let body = GetMetricRequest::new(experiment_uid.clone(), None, Some(true));
    let request = Request::builder()
        .uri("/opsml/api/experiment/metrics") // should be post
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&body).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let metrics: Vec<Metric> = serde_json::from_slice(&body).unwrap();

    assert_eq!(metrics.len(), 1);
    assert!(metrics[0].is_eval);

    // insert parameter

    let request = ParameterRequest {
        experiment_uid: experiment_uid.clone(),
        parameters: vec![
            Parameter {
                name: "param1".to_string(),
                value: ParameterValue::Int(1),
            },
            Parameter {
                name: "param2".to_string(),
                value: ParameterValue::Int(1),
            },
        ],
    };

    let body = serde_json::to_string(&request).unwrap();

    let request = Request::builder()
        .uri("/opsml/api/experiment/parameters")
        .method("PUT")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // get parameters by experiment_uid
    let body = GetParameterRequest::new(experiment_uid.clone(), None);
    let request = Request::builder()
        .uri("/opsml/api/experiment/parameters") // should be post
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&body).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let parameters: Vec<Parameter> = serde_json::from_slice(&body).unwrap();
    assert_eq!(parameters.len(), 2);

    // get parameters by experiment_uid and parameter name
    let body = GetParameterRequest::new(experiment_uid.clone(), Some(vec!["param1".to_string()]));

    let request = Request::builder()
        .uri("/opsml/api/experiment/parameters") // should be post
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&body).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let parameters: Vec<Parameter> = serde_json::from_slice(&body).unwrap();
    assert_eq!(parameters.len(), 1);

    // insert hardware metrics

    let request = HardwareMetricRequest {
        experiment_uid: experiment_uid.clone(),
        metrics: HardwareMetrics::default(),
    };

    let body = serde_json::to_string(&request).unwrap();

    let request = Request::builder()
        .uri("/opsml/api/experiment/hardware/metrics")
        .method("PUT")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // get hardware metrics by experiment_uid
    let body = GetHardwareMetricRequest {
        experiment_uid: experiment_uid.clone(),
    };

    let query_string = serde_qs::to_string(&body).unwrap();

    let request = Request::builder()
        .uri(format!(
            "/opsml/api/experiment/hardware/metrics?{query_string}"
        ))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let metrics: Vec<HardwareMetrics> = serde_json::from_slice(&body).unwrap();

    assert_eq!(metrics.len(), 1);

    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_server_grouped_experiment_metrics() {
    let helper = TestHelper::new(None).await;
    let experiment_uid1 = "550e8400-e29b-41d4-a716-446655440000".to_string();

    let request = MetricRequest {
        experiment_uid: experiment_uid1.clone(),
        metrics: vec![
            Metric {
                name: "metric1".to_string(),
                value: 1.0,
                step: Some(1),
                ..Default::default()
            },
            Metric {
                name: "metric1".to_string(),
                value: 2.0,
                step: Some(2),
                ..Default::default()
            },
            Metric {
                name: "metric2".to_string(),
                value: 1.0,
                ..Default::default()
            },
        ],
    };

    let body = serde_json::to_string(&request).unwrap();

    let request = Request::builder()
        .uri("/opsml/api/experiment/metrics")
        .method("PUT")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let experiment_uid2 = "550e8401-e29b-41d4-a716-446655440000".to_string();

    let request = MetricRequest {
        experiment_uid: experiment_uid2.clone(),
        metrics: vec![
            Metric {
                name: "metric1".to_string(),
                value: 1.0,
                step: Some(1),
                ..Default::default()
            },
            Metric {
                name: "metric1".to_string(),
                value: 2.0,
                step: Some(2),
                ..Default::default()
            },
            Metric {
                name: "metric2".to_string(),
                value: 1.0,
                is_eval: true,
                ..Default::default()
            },
        ],
    };

    let body = serde_json::to_string(&request).unwrap();

    let request = Request::builder()
        .uri("/opsml/api/experiment/metrics")
        .method("PUT")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // experiment 3
    let experiment_uid3 = "550e8402-e29b-41d4-a716-446655440000".to_string();

    let request = MetricRequest {
        experiment_uid: experiment_uid3.clone(),
        metrics: vec![Metric {
            name: "metric3".to_string(),
            value: 1.0,
            ..Default::default()
        }],
    };

    let body = serde_json::to_string(&request).unwrap();

    let request = Request::builder()
        .uri("/opsml/api/experiment/metrics")
        .method("PUT")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = UiMetricRequest {
        experiments: vec![
            Experiment {
                uid: experiment_uid1.clone(),
                version: "1".to_string(),
            },
            Experiment {
                uid: experiment_uid2.clone(),
                version: "1".to_string(),
            },
            Experiment {
                uid: experiment_uid3.clone(),
                version: "2".to_string(),
            },
        ],
        metric_names: vec!["metric1".to_string(), "metric2".to_string()],
        is_eval: None,
    };

    let request = Request::builder()
        .uri("/opsml/api/experiment/metrics/grouped") // should be post
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&body).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let metrics: HashMap<String, Vec<GroupedMetric>> = serde_json::from_slice(&body).unwrap();

    assert_eq!(metrics.len(), 2);
    assert_eq!(metrics["metric1"].len(), 2);
}
