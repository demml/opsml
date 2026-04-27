use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use http_body_util::BodyExt;
use test_utils::retry_flaky_test;

fn scouter_error_body() -> &'static str {
    r#"{"error":"upstream failed","code":"INTERNAL_ERROR","suggested_action":null,"retry":false}"#
}

#[tokio::test]
async fn test_scouter_routes_observability_metrics() {
    retry_flaky_test!({
        let mut helper = TestHelper::new(None).await;

        let _mock = helper
            .server
            .server
            .mock("GET", "/scouter/observability/metrics")
            .match_query(mockito::Matcher::AllOf(vec![
                mockito::Matcher::UrlEncoded("uid".into(), "abc".into()),
                mockito::Matcher::UrlEncoded("time_interval".into(), "1h".into()),
            ]))
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(r#"{"metrics":[],"total":0}"#)
            .create_async()
            .await;

        let request = Request::builder()
            .uri("/opsml/api/scouter/observability/metrics?uid=abc&time_interval=1h")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let json: serde_json::Value = serde_json::from_slice(&body).unwrap();
        assert!(
            json.get("metrics").is_some(),
            "response missing 'metrics' field: {json}"
        );

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_scouter_routes_observability_metrics_error_propagation() {
    retry_flaky_test!({
        let mut helper = TestHelper::new(None).await;

        let _mock = helper
            .server
            .server
            .mock("GET", "/scouter/observability/metrics")
            .match_query(mockito::Matcher::UrlEncoded("uid".into(), "abc".into()))
            .with_status(500)
            .with_header("content-type", "application/json")
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

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let json: serde_json::Value = serde_json::from_slice(&body).unwrap();
        assert!(
            json.get("error").is_some(),
            "error response missing 'error' field: {json}"
        );
        assert_eq!(
            json["error"].as_str().unwrap_or(""),
            "upstream failed",
            "unexpected error message"
        );

        helper.cleanup();
    });
}
