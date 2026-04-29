use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use reqwest::header;

fn scouter_error_body() -> &'static str {
    r#"{"error":"upstream failed","code":"INTERNAL_ERROR","suggested_action":null,"retry":false}"#
}

#[tokio::test]
async fn test_scouter_routes_trace_spans_filters() {
    let mut helper = TestHelper::new(None).await;

    let _mock = helper
        .server
        .server
        .mock("POST", "/scouter/trace/spans/filters")
        .with_status(200)
        .with_body(r#"{"spans":[]}"#)
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/trace/spans/filters")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from("{}"))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_trace_spans_filters_error_propagation() {
    let mut helper = TestHelper::new(None).await;

    let _mock = helper
        .server
        .server
        .mock("POST", "/scouter/trace/spans/filters")
        .with_status(502)
        .with_body(scouter_error_body())
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/trace/spans/filters")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from("{}"))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::BAD_GATEWAY);
}
