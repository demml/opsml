// test for scouter route integration
// mainly used to test internal opsml route logic while mocking scouter responses
use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use scouter_client::{DriftRequest, TimeInterval};

#[tokio::test]
async fn test_scouter_routes_spc_drift_features() {
    let helper = TestHelper::new(None).await;

    let drift_request = DriftRequest {
        space: helper.space.clone(),
        uid: "mocked_uid".to_string(),
        time_interval: TimeInterval::OneHour,
        max_data_points: 100,
        ..Default::default()
    };

    let query_string = serde_qs::to_string(&drift_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/drift/spc?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_psi_drift_features() {
    let helper = TestHelper::new(None).await;

    let drift_request = DriftRequest {
        uid: "mocked_uid".to_string(),
        space: helper.space.clone(),
        time_interval: TimeInterval::OneHour,
        max_data_points: 100,
        ..Default::default()
    };

    let query_string = serde_qs::to_string(&drift_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/drift/psi?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_custom_drift_features() {
    let helper = TestHelper::new(None).await;

    let drift_request = DriftRequest {
        space: helper.space.clone(),
        uid: "mocked_uid".to_string(),
        time_interval: TimeInterval::OneHour,
        max_data_points: 100,
        ..Default::default()
    };

    let query_string = serde_qs::to_string(&drift_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/drift/custom?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_genai_task_drift_metrics() {
    let helper = TestHelper::new(None).await;

    let drift_request = DriftRequest {
        space: helper.space.clone(),
        uid: "mocked_uid".to_string(),
        time_interval: TimeInterval::OneHour,
        max_data_points: 100,
        ..Default::default()
    };

    let query_string = serde_qs::to_string(&drift_request).unwrap();
    let request = Request::builder()
        .uri(format!(
            "/opsml/api/scouter/drift/genai/task?{query_string}"
        ))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_genai_workflow_drift_metrics() {
    let helper = TestHelper::new(None).await;

    let drift_request = DriftRequest {
        space: helper.space.clone(),
        uid: "mocked_uid".to_string(),
        time_interval: TimeInterval::OneHour,
        max_data_points: 100,
        ..Default::default()
    };

    let query_string = serde_qs::to_string(&drift_request).unwrap();
    let request = Request::builder()
        .uri(format!(
            "/opsml/api/scouter/drift/genai/workflow?{query_string}"
        ))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}
