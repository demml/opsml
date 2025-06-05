use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};

#[tokio::test]
async fn test_opsml_server_login() {
    let helper = TestHelper::new(None).await;

    let request = Request::builder()
        .uri("/opsml/api/healthcheck")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_server_sso_login() {
    let helper = TestHelper::new(Some("keycloak".to_string())).await;

    let request = Request::builder()
        .uri("/opsml/api/healthcheck")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // Check if the SSO login was successful
    assert!(helper.verify_sso_called());

    helper.cleanup();
}
