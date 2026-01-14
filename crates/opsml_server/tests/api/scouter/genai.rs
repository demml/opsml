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
    GenAIEvalRecordPaginationRequest, GenAIEvalRecordPaginationResponse, GenAIEvalTaskRequest,
    GenAIEvalTaskResponse, GenAIEvalWorkflowPaginationResponse,
};

#[tokio::test]
async fn test_scouter_routes_record_page() {
    let helper = TestHelper::new(None).await;

    let record_request = GenAIEvalRecordPaginationRequest::default();

    let body = serde_json::to_string(&record_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/genai/page/record"))
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // deserialize into GenAIEvalRecordPaginationResponse
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let _page_response: GenAIEvalRecordPaginationResponse = serde_json::from_slice(&body).unwrap();
}

#[tokio::test]
async fn test_scouter_routes_workflow_page() {
    let helper = TestHelper::new(None).await;

    let record_request = GenAIEvalRecordPaginationRequest::default();

    let body = serde_json::to_string(&record_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/genai/page/workflow"))
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // deserialize into GenAIEvalRecordPaginationResponse
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let _page_response: GenAIEvalWorkflowPaginationResponse =
        serde_json::from_slice(&body).unwrap();
}

#[tokio::test]
async fn test_scouter_routes_workflow_task() {
    let helper = TestHelper::new(None).await;

    let record_request = GenAIEvalTaskRequest {
        record_uid: "test-record-uid".to_string(),
    };

    let query_string = serde_json::to_string(&record_request).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/scouter/genai/task?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // deserialize into GenAIEvalRecordPaginationResponse
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let _page_response: GenAIEvalTaskResponse = serde_json::from_slice(&body).unwrap();
}
