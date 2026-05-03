use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use chrono::{Duration, Utc};
use opsml_server::core::scouter::genai::route::GenAiDashboardRequest;
use reqwest::header;
use scouter_client::{
    AgentDashboardRequest, GenAiAgentActivityResponse, GenAiDashboardResponse,
    GenAiErrorBreakdownResponse, GenAiMetricsRequest, GenAiModelUsageResponse,
    GenAiOperationBreakdownResponse, GenAiSpanFilters, GenAiSpansResponse,
    GenAiTokenMetricsResponse, GenAiToolActivityResponse, GenAiTraceMetricsRequest,
    GenAiTraceMetricsResponse, ToolDashboardRequest,
};

fn metrics_request() -> GenAiMetricsRequest {
    let end_time = Utc::now();
    GenAiMetricsRequest {
        service_name: Some("opsml-service".to_string()),
        agent_name: None,
        start_time: end_time - Duration::minutes(15),
        end_time,
        bucket_interval: "hour".to_string(),
        operation_name: None,
        provider_name: None,
        model: None,
    }
}

fn agent_dashboard_request() -> AgentDashboardRequest {
    let end_time = Utc::now();
    AgentDashboardRequest {
        service_name: Some("opsml-service".to_string()),
        entity_id: None,
        start_time: end_time - Duration::minutes(15),
        end_time,
        bucket_interval: "hour".to_string(),
        agent_name: Some("agent-1".to_string()),
        provider_name: None,
        model_pricing: std::collections::HashMap::new(),
    }
}

fn tool_dashboard_request() -> ToolDashboardRequest {
    let end_time = Utc::now();
    ToolDashboardRequest {
        service_name: Some("opsml-service".to_string()),
        agent_name: None,
        start_time: end_time - Duration::minutes(15),
        end_time,
        model: None,
        provider_name: None,
        bucket_interval: "hour".to_string(),
    }
}

fn scouter_error_body() -> &'static str {
    r#"{"error":"upstream failed","code":"INTERNAL_ERROR","suggested_action":null,"retry":false}"#
}

#[tokio::test]
async fn test_scouter_routes_genai_endpoints() {
    let mut helper = TestHelper::new(None).await;

    let _token_mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/metrics/tokens")
        .with_status(200)
        .with_body(serde_json::to_string(&GenAiTokenMetricsResponse::default()).unwrap())
        .create_async()
        .await;
    let _ops_mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/metrics/operations")
        .with_status(200)
        .with_body(serde_json::to_string(&GenAiOperationBreakdownResponse::default()).unwrap())
        .create_async()
        .await;
    let _models_mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/metrics/models")
        .with_status(200)
        .with_body(serde_json::to_string(&GenAiModelUsageResponse::default()).unwrap())
        .create_async()
        .await;
    let _agents_mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/metrics/agents")
        .match_query(mockito::Matcher::UrlEncoded(
            "agent_name".into(),
            "agent-1".into(),
        ))
        .with_status(200)
        .with_body(serde_json::to_string(&GenAiAgentActivityResponse::default()).unwrap())
        .create_async()
        .await;
    let _tools_mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/metrics/tools")
        .with_status(200)
        .with_body(serde_json::to_string(&GenAiToolActivityResponse::default()).unwrap())
        .create_async()
        .await;
    let _errors_mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/metrics/errors")
        .with_status(200)
        .with_body(serde_json::to_string(&GenAiErrorBreakdownResponse::default()).unwrap())
        .create_async()
        .await;
    let _spans_mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/spans")
        .with_status(200)
        .with_body(serde_json::to_string(&GenAiSpansResponse::default()).unwrap())
        .create_async()
        .await;
    let _agent_dashboard_mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/agent/metrics")
        .with_status(200)
        .with_body(
            r#"{"summary":{"total_requests":0,"avg_duration_ms":0.0,"p50_duration_ms":null,"p95_duration_ms":null,"p99_duration_ms":null,"overall_error_rate":0.0,"total_input_tokens":0,"total_output_tokens":0,"total_cache_creation_tokens":0,"total_cache_read_tokens":0,"unique_agent_count":0,"unique_conversation_count":0,"cost_by_model":[]},"buckets":[]}"#,
        )
        .create_async()
        .await;
    let _tool_dashboard_mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/tool/metrics")
        .with_status(200)
        .with_body(r#"{"aggregates":[],"time_series":[]}"#)
        .create_async()
        .await;
    let _conversation_mock = helper
        .server
        .server
        .mock("GET", "/scouter/genai/conversation/convo:123")
        .match_query(mockito::Matcher::AllOf(vec![
            mockito::Matcher::UrlEncoded("start_time".into(), "2024-01-01T00:00:00Z".into()),
            mockito::Matcher::UrlEncoded("end_time".into(), "2024-01-01T01:00:00Z".into()),
        ]))
        .with_status(200)
        .with_body(serde_json::to_string(&GenAiSpansResponse::default()).unwrap())
        .create_async()
        .await;

    let metrics_body = serde_json::to_string(&metrics_request()).unwrap();

    for uri in [
        "/opsml/api/scouter/genai/metrics/tokens",
        "/opsml/api/scouter/genai/metrics/operations",
        "/opsml/api/scouter/genai/metrics/models",
        "/opsml/api/scouter/genai/metrics/tools",
        "/opsml/api/scouter/genai/metrics/errors",
    ] {
        let request = Request::builder()
            .uri(uri)
            .method("POST")
            .header(header::CONTENT_TYPE, "application/json")
            .body(Body::from(metrics_body.clone()))
            .unwrap();
        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);
    }

    let agents_request = Request::builder()
        .uri("/opsml/api/scouter/genai/metrics/agents?agent_name=agent-1")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(metrics_body.clone()))
        .unwrap();
    let agents_response = helper.send_oneshot(agents_request).await;
    assert_eq!(agents_response.status(), StatusCode::OK);

    let spans_request = Request::builder()
        .uri("/opsml/api/scouter/genai/spans")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(
            serde_json::to_string(&GenAiSpanFilters::default()).unwrap(),
        ))
        .unwrap();
    let spans_response = helper.send_oneshot(spans_request).await;
    assert_eq!(spans_response.status(), StatusCode::OK);

    let agent_dashboard_request = Request::builder()
        .uri("/opsml/api/scouter/genai/agent/metrics")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(
            serde_json::to_string(&agent_dashboard_request()).unwrap(),
        ))
        .unwrap();
    let agent_dashboard_response = helper.send_oneshot(agent_dashboard_request).await;
    assert_eq!(agent_dashboard_response.status(), StatusCode::OK);

    let tool_dashboard_request = Request::builder()
        .uri("/opsml/api/scouter/genai/tool/metrics")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(
            serde_json::to_string(&tool_dashboard_request()).unwrap(),
        ))
        .unwrap();
    let tool_dashboard_response = helper.send_oneshot(tool_dashboard_request).await;
    assert_eq!(tool_dashboard_response.status(), StatusCode::OK);

    let conversation_request = Request::builder()
        .uri("/opsml/api/scouter/genai/conversation/convo:123?start_time=2024-01-01T00:00:00Z&end_time=2024-01-01T01:00:00Z")
        .method("GET")
        .body(Body::empty())
        .unwrap();
    let conversation_response = helper.send_oneshot(conversation_request).await;
    assert_eq!(conversation_response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_scouter_routes_genai_conversation_invalid_id() {
    let helper = TestHelper::new(None).await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/genai/conversation/invalid%20id")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::BAD_REQUEST);
}

#[tokio::test]
async fn test_scouter_routes_genai_error_propagation() {
    let mut helper = TestHelper::new(None).await;

    let _mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/metrics/tokens")
        .with_status(502)
        .with_body(scouter_error_body())
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/genai/metrics/tokens")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(
            serde_json::to_string(&metrics_request()).unwrap(),
        ))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::BAD_GATEWAY);
}

fn genai_dashboard_request() -> GenAiDashboardRequest {
    let end_time = Utc::now();
    GenAiDashboardRequest {
        service_name: Some("test-space:test-service".to_string()),
        entity_id: None,
        start_time: (end_time - Duration::minutes(15)).to_rfc3339(),
        end_time: end_time.to_rfc3339(),
        bucket_interval: "hour".to_string(),
        agent_name: None,
        provider_name: None,
        operation_name: None,
        model: None,
        model_pricing: std::collections::HashMap::new(),
    }
}

fn trace_metrics_request() -> GenAiTraceMetricsRequest {
    let end_time = Utc::now();
    GenAiTraceMetricsRequest {
        start_time: Some(end_time - Duration::minutes(15)),
        end_time: Some(end_time),
        bucket_interval: "hour".to_string(),
        model_pricing: std::collections::HashMap::new(),
        span_limit: 100,
        include_sensitive_content: false,
    }
}

#[tokio::test]
async fn test_scouter_routes_genai_dashboard() {
    let mut helper = TestHelper::new(None).await;

    let _mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/dashboard")
        .with_status(200)
        .with_body(serde_json::to_string(&GenAiDashboardResponse::default()).unwrap())
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/genai/dashboard")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(
            serde_json::to_string(&genai_dashboard_request()).unwrap(),
        ))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    helper.cleanup();
}

#[tokio::test]
async fn test_scouter_routes_genai_trace_metrics() {
    let mut helper = TestHelper::new(None).await;

    let _mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/traces/abc123def456/metrics")
        .with_status(200)
        .with_body(serde_json::to_string(&GenAiTraceMetricsResponse::default()).unwrap())
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/genai/traces/abc123def456/metrics")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(
            serde_json::to_string(&trace_metrics_request()).unwrap(),
        ))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    helper.cleanup();
}

#[tokio::test]
async fn test_scouter_routes_genai_trace_metrics_invalid_id() {
    let helper = TestHelper::new(None).await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/genai/traces/invalid%20id/metrics")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(
            serde_json::to_string(&trace_metrics_request()).unwrap(),
        ))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::BAD_REQUEST);

    helper.cleanup();
}

#[tokio::test]
async fn test_scouter_routes_genai_trace_metrics_error_propagation() {
    let mut helper = TestHelper::new(None).await;

    let _mock = helper
        .server
        .server
        .mock("POST", "/scouter/genai/traces/abc123def456/metrics")
        .with_status(502)
        .with_body(scouter_error_body())
        .create_async()
        .await;

    let request = Request::builder()
        .uri("/opsml/api/scouter/genai/traces/abc123def456/metrics")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(
            serde_json::to_string(&trace_metrics_request()).unwrap(),
        ))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::BAD_GATEWAY);

    helper.cleanup();
}
