use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use chrono::{Duration, Utc};
use reqwest::header;

/// Representative clause-shaped trace filter body used to verify that the Rust
/// proxy accepts and forwards the same JSON shape emitted by the OpsML UI.
fn clause_filter_body() -> serde_json::Value {
    serde_json::json!({
        "clause": {
            "op": "and",
            "value": [
                { "op": "service", "value": "checkout" },
                { "op": "status_code", "value": 500 }
            ]
        }
    })
}

fn scouter_error_body() -> &'static str {
    r#"{"error":"upstream failed","code":"INTERNAL_ERROR","suggested_action":null,"retry":false}"#
}

#[tokio::test]
async fn test_scouter_routes_trace_paginated() {
    let mut helper = TestHelper::new(None).await;
    let body = serde_json::json!({
        "limit": 25,
        "clause": clause_filter_body()["clause"].clone(),
    });
    let body = serde_json::to_string(&body).unwrap();

    let _mock = helper
        .server
        .server
        .mock("POST", "/scouter/trace/paginated")
        .match_body(mockito::Matcher::PartialJson(serde_json::json!({
            "limit": 25,
            "clause": {
                "op": "and",
                "value": [
                    { "op": "service", "value": "checkout" },
                    { "op": "status_code", "value": 500 }
                ]
            }
        })))
        .with_status(200)
        .with_body(
            r#"{"items":[],"has_next":false,"next_cursor":null,"has_previous":false,"previous_cursor":null}"#,
        )
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/trace/paginated")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_trace_spans_query_forwarding() {
    let mut helper = TestHelper::new(None).await;

    let _mock = helper
        .server
        .server
        .mock("GET", "/scouter/trace/spans")
        .match_query(mockito::Matcher::UrlEncoded(
            "trace_id".into(),
            "trace-123".into(),
        ))
        .with_status(200)
        .with_body(r#"{"spans":[]}"#)
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/trace/spans?trace_id=trace-123")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_trace_metrics() {
    let mut helper = TestHelper::new(None).await;
    let end_time = Utc::now();
    let start_time = end_time - Duration::minutes(15);
    let body = serde_json::json!({
        "clause": clause_filter_body()["clause"].clone(),
        "start_time": start_time.to_rfc3339(),
        "end_time": end_time.to_rfc3339(),
        "bucket_interval": "hour",
        "entity_uid": "entity-1",
    });
    let body = serde_json::to_string(&body).unwrap();

    let _mock = helper
        .server
        .server
        .mock("POST", "/scouter/trace/metrics")
        .match_body(mockito::Matcher::PartialJson(serde_json::json!({
            "bucket_interval": "hour",
            "entity_uid": "entity-1",
            "clause": {
                "op": "and",
                "value": [
                    { "op": "service", "value": "checkout" },
                    { "op": "status_code", "value": 500 }
                ]
            }
        })))
        .with_status(200)
        .with_body(r#"{"metrics":[]}"#)
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/trace/metrics")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
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
async fn test_scouter_routes_trace_facets() {
    let mut helper = TestHelper::new(None).await;
    let body = serde_json::to_string(&clause_filter_body()).unwrap();

    let _mock = helper
        .server
        .server
        .mock("POST", "/scouter/trace/facets")
        .match_body(mockito::Matcher::PartialJson(serde_json::json!({
            "clause": {
                "op": "and",
                "value": [
                    { "op": "service", "value": "checkout" },
                    { "op": "status_code", "value": 500 }
                ]
            }
        })))
        .with_status(200)
        .with_body(r#"{"services":[],"status_codes":[],"total_count":0}"#)
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/trace/facets")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_trace_spans_by_id() {
    let mut helper = TestHelper::new(None).await;

    let _mock = helper
        .server
        .server
        .mock("GET", "/scouter/v1/traces/trace:123/spans")
        .with_status(200)
        .with_body(r#"{"spans":[]}"#)
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/trace/trace:123/spans")
        .method("GET")
        .body(Body::empty())
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
