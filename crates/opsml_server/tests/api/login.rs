use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use http_body_util::BodyExt;
use opsml_server::core::auth::schema::{LoginResponse, SsoAuthUrl, SsoCallbackParams};

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
async fn test_opsml_server_keycloak_sso_programmatic_login() {
    let helper = TestHelper::new(Some("keycloak".to_string())).await;

    let request = Request::builder()
        .uri("/opsml/api/healthcheck")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // Check if the SSO login was successful
    assert!(helper.verify_keycloak_sso_called());

    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_server_okta_sso_programmatic_login() {
    let helper = TestHelper::new(Some("okta".to_string())).await;

    let request = Request::builder()
        .uri("/opsml/api/healthcheck")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // Check if the SSO login was successful
    assert!(helper.verify_okta_sso_called());

    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_server_default_sso_programmatic_login() {
    let helper = TestHelper::new(Some("default".to_string())).await;

    let request = Request::builder()
        .uri("/opsml/api/healthcheck")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // Check if the SSO login was successful
    assert!(helper.verify_default_sso_called());

    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_server_keycloak_sso_ui_login() {
    let helper = TestHelper::new(Some("keycloak".to_string())).await;
    let mock_url = helper.sso_server.as_ref().unwrap().url.clone();

    // (1) Test SSO login URL generation
    let request = Request::builder()
        .uri("/opsml/api/auth/sso/authorization")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
    let sso_auth_url: SsoAuthUrl = serde_json::from_slice(&body_bytes).unwrap();

    // build the expected URL
    let expected_url = format!(
        "{mock_url}/realms/opsml/protocol/openid-connect/auth?client_id=opsml-client&response_type=code&scope=openid email profile&redirect_uri=http://localhost:8080/callback"
    );

    assert!(sso_auth_url.url.contains(&expected_url));

    assert!(helper.verify_keycloak_sso_called());

    // (2) Test SSO login callback to verify authentication
    let code = "mock_code";
    let parms = SsoCallbackParams {
        code: code.to_string(),
        code_verifier: "mock_code_verifier".to_string(),
    };

    let query_string = serde_qs::to_string(&parms).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/auth/sso/callback?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
    let login: LoginResponse = serde_json::from_slice(&body_bytes).unwrap();

    assert!(login.authenticated);

    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_server_okta_sso_ui_login() {
    let helper = TestHelper::new(Some("okta".to_string())).await;
    let mock_url = helper.sso_server.as_ref().unwrap().url.clone();

    // (1) Test SSO login URL generation
    let request = Request::builder()
        .uri("/opsml/api/auth/sso/authorization")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
    let sso_auth_url: SsoAuthUrl = serde_json::from_slice(&body_bytes).unwrap();

    // build the expected URL
    let expected_url = format!(
        "{mock_url}/oauth2/v1/authorize?client_id=opsml-client&response_type=code&scope=openid email profile&redirect_uri=http://localhost:8080/callback"
    );

    assert!(sso_auth_url.url.contains(&expected_url));

    assert!(helper.verify_okta_sso_called());

    // (2) Test SSO login callback to verify authentication
    let code = "mock_code";
    let parms = SsoCallbackParams {
        code: code.to_string(),
        code_verifier: "mock_code_verifier".to_string(),
    };

    let query_string = serde_qs::to_string(&parms).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/auth/sso/callback?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
    let login: LoginResponse = serde_json::from_slice(&body_bytes).unwrap();

    assert!(login.authenticated);

    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_server_default_sso_ui_login() {
    let helper = TestHelper::new(Some("default".to_string())).await;
    let mock_url = helper.sso_server.as_ref().unwrap().url.clone();

    // (1) Test SSO login URL generation
    let request = Request::builder()
        .uri("/opsml/api/auth/sso/authorization")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
    let sso_auth_url: SsoAuthUrl = serde_json::from_slice(&body_bytes).unwrap();

    // build the expected URL
    let expected_url = format!(
        "{mock_url}/oauth/authorize?client_id=opsml-client&response_type=code&scope=openid email profile&redirect_uri=http://localhost:8080/callback"
    );

    assert!(sso_auth_url.url.contains(&expected_url));

    assert!(helper.verify_default_sso_called());

    // (2) Test SSO login callback to verify authentication
    let code = "mock_code";
    let parms = SsoCallbackParams {
        code: code.to_string(),
        code_verifier: "mock_code_verifier".to_string(),
    };

    let query_string = serde_qs::to_string(&parms).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/auth/sso/callback?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body_bytes = response.into_body().collect().await.unwrap().to_bytes();
    let login: LoginResponse = serde_json::from_slice(&body_bytes).unwrap();

    assert!(login.authenticated);

    helper.cleanup();
}
