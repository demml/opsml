// test for scouter route integration
// mainly used to test internal opsml route logic while mocking scouter responses
use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use http_body_util::BodyExt;
use reqwest::header;
use scouter_client::{
    AgentEvalTaskRequest, AgentEvalTaskResponse, AgentEvalWorkflowPaginationResponse,
    EvalRecordPaginationRequest, EvalRecordPaginationResponse,
};

#[tokio::test]
async fn test_scouter_routes_record_page() {
    let helper = TestHelper::new(None).await;

    let record_request = EvalRecordPaginationRequest::default();

    let body = serde_json::to_string(&record_request).unwrap();
    let request = Request::builder()
        .uri("/opsml/api/scouter/agent/page/record".to_string())
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let _page_response: EvalRecordPaginationResponse = serde_json::from_slice(&body).unwrap();
}

#[tokio::test]
async fn test_scouter_routes_workflow_page() {
    let helper = TestHelper::new(None).await;

    let record_request = EvalRecordPaginationRequest::default();

    let body = serde_json::to_string(&record_request).unwrap();
    let request = Request::builder()
        .uri("/opsml/api/scouter/agent/page/workflow".to_string())
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let _page_response: AgentEvalWorkflowPaginationResponse =
        serde_json::from_slice(&body).unwrap();
}

#[tokio::test]
async fn test_scouter_routes_workflow_task() {
    let helper = TestHelper::new(None).await;

    let record_request = AgentEvalTaskRequest {
        record_uid: "test-record-uid".to_string(),
    };

    let query_string = serde_qs::to_string(&record_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/agent/task?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let _page_response: AgentEvalTaskResponse = serde_json::from_slice(&body).unwrap();
}
