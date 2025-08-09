use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{header, Request, StatusCode},
};
use http_body_util::BodyExt; // for `collect`

use opsml_types::{contracts::*, RegistryType};

#[tokio::test]
async fn test_opsml_server_render_file() {
    let mut helper = TestHelper::new(None).await;

    helper.create_modelcard().await;
    let path = helper.create_files();

    let list_query = ListFileQuery { path };

    let query_string = serde_qs::to_string(&list_query).unwrap();

    // check if a card UID exists (get request with UidRequest params)
    let request = Request::builder()
        .uri(format!("/opsml/api/files/tree?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // get response text
    let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
    let file_tree: FileTreeResponse = serde_json::from_slice(&body_bytes).unwrap();

    assert!(file_tree.files.len() == 2);

    let file1req = RawFileRequest {
        path: file_tree.files[0].path.clone(),
        uid: helper.key.uid.clone(),
        registry_type: RegistryType::Model,
    };

    let request = Request::builder()
        .uri("/opsml/api/files/content")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&file1req).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
    let file1: RawFile = serde_json::from_slice(&body_bytes).unwrap();
    assert!(file1.mime_type == "application/json");

    let file2req = RawFileRequest {
        path: file_tree.files[1].path.clone(),
        uid: helper.key.uid.clone(),
        registry_type: RegistryType::Model,
    };

    let request = Request::builder()
        .uri("/opsml/api/files/content")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&file2req).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
    let file2: RawFile = serde_json::from_slice(&body_bytes).unwrap();
    assert!(file2.mime_type == "image/png");
}

#[tokio::test]
async fn test_opsml_server_log_artifact() {
    let helper = TestHelper::new(None).await;

    let artifact_request = CreateArtifactRequest {
        space: "space".to_string(),
        name: "test.txt".to_string(),
        version: "0.0.0".to_string(),
        media_type: "text/plain".to_string(),
    };

    let request = Request::builder()
        .uri("/opsml/api/files/artifact")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(
            serde_json::to_string(&artifact_request).unwrap(),
        ))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let query_request = ArtifactQueryArgs {
        uid: None,
        name: Some("name".to_string()),
        space: Some("space".to_string()),
        version: None,
        sort_by_timestamp: Some(true),
        limit: Some(1),
    };

    let query_string = serde_qs::to_string(&query_request).unwrap();

    // get request
    let request = Request::builder()
        .uri(format!("/opsml/api/files/artifact?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
    let records: Vec<ArtifactRecord> = serde_json::from_slice(&body_bytes).unwrap();
    assert!(records.len() == 1);
}
