use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};

#[tokio::test]
async fn test_opsml_server_login() {
    let helper = TestHelper::new().await;

    let request = Request::builder()
        .uri("/opsml/api/healthcheck")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    helper.cleanup();
}
