use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};

fn scouter_error_body() -> &'static str {
    r#"{"error":"upstream failed","code":"INTERNAL_ERROR","suggested_action":null,"retry":false}"#
}

#[tokio::test]
async fn test_scouter_routes_observability_metrics() {
    let mut helper = TestHelper::new(None).await;

    let _mock = helper
        .server
        .server
        .mock("GET", "/scouter/observability/metrics")
        .match_query(mockito::Matcher::Any)
        .with_status(200)
        .with_body(r#"{"metrics":[]}"#)
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/observability/metrics?uid=abc&time_interval=1h")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_observability_metrics_error_propagation() {
    let mut helper = TestHelper::new(None).await;

    let _mock = helper
        .server
        .server
        .mock("GET", "/scouter/observability/metrics")
        .match_query(mockito::Matcher::Any)
        .with_status(500)
        .with_body(scouter_error_body())
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/observability/metrics?uid=abc")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);
}
