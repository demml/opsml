use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{header, Request, StatusCode},
};
use http_body_util::BodyExt;
use opsml_types::JwtToken; // for `collect`

use opsml_server::core::{
    auth::schema::{Authenticated, LoginRequest, LoginResponse, LogoutResponse},
    user::schema::*,
};

#[tokio::test]
async fn test_opsml_server_user_crud() {
    let helper = TestHelper::new(None).await;

    // 1. Create a new user
    let create_req = CreateUserRequest {
        username: "test_user".to_string(),
        password: "test_password".to_string(),
        email: "test_user@example.com".to_string(),
        permissions: Some(vec!["read:all".to_string(), "write:all".to_string()]),
        group_permissions: Some(vec!["user".to_string()]),
        role: Some("user".to_string()),
        active: Some(true),
    };

    let body = serde_json::to_string(&create_req).unwrap();

    let request = Request::builder()
        .uri("/opsml/api/user")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let user_response: CreateUserResponse = serde_json::from_slice(&body).unwrap();
    assert_eq!(user_response.user.username, "test_user");
    assert_eq!(
        user_response.user.permissions,
        vec!["read:all".to_string(), "write:all".to_string()]
    );
    assert_eq!(
        user_response.user.group_permissions,
        vec!["user".to_string()]
    );
    assert!(user_response.user.active);

    let recovery_codes = user_response.recovery_codes;

    // 2. Get the user
    let request = Request::builder()
        .uri("/opsml/api/user/test_user")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let user_response: UserResponse = serde_json::from_slice(&body).unwrap();
    assert_eq!(user_response.username, "test_user");

    // 3. Update the user
    let update_req = UpdateUserRequest {
        password: Some("new_password".to_string()),
        permissions: Some(vec![
            "read:all".to_string(),
            "write:all".to_string(),
            "execute:all".to_string(),
        ]),
        group_permissions: Some(vec!["user".to_string(), "developer".to_string()]),
        active: Some(true),
        favorite_spaces: None,
    };

    let body = serde_json::to_string(&update_req).unwrap();

    let request = Request::builder()
        .uri("/opsml/api/user/test_user")
        .method("PUT")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let mut user_response: UserResponse = serde_json::from_slice(&body).unwrap();
    user_response.permissions.sort();
    user_response.group_permissions.sort();

    assert_eq!(
        user_response.permissions,
        vec![
            "execute:all".to_string(),
            "read:all".to_string(),
            "write:all".to_string()
        ]
    );
    assert_eq!(
        user_response.group_permissions,
        vec!["developer".to_string(), "user".to_string()]
    );

    // 4. List all users
    let request = Request::builder()
        .uri("/opsml/api/user")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let list_response: UserListResponse = serde_json::from_slice(&body).unwrap();

    // Should have at least 2 users (admin and test_user)
    assert!(list_response.users.len() >= 2);

    // Find our test user in the list
    let test_user = list_response
        .users
        .iter()
        .find(|u| u.username == "test_user");
    assert!(test_user.is_some());

    // 5. Reset user password

    let body = serde_json::to_string(&RecoveryResetRequest {
        username: "test_user".to_string(),
        recovery_code: recovery_codes[0].clone(),
        new_password: "new_password".to_string(),
    })
    .unwrap();

    let request = Request::builder()
        .uri("/opsml/api/auth/reset-password/recovery")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let reset_response: ResetPasswordResponse = serde_json::from_slice(&body).unwrap();
    assert_eq!(reset_response.message, "Password updated successfully");
    assert_eq!(reset_response.remaining_recovery_codes, 3);

    // 6. Delete the user
    let request = Request::builder()
        .uri("/opsml/api/user/test_user")
        .method("DELETE")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // Verify the user is deleted by trying to get it
    let request = Request::builder()
        .uri("/opsml/api/user/test_user")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::NOT_FOUND);

    helper.cleanup();
}

#[tokio::test]
async fn test_opsml_login_logout() {
    let helper = TestHelper::new(None).await;

    // 1. Create a new user
    let create_req = CreateUserRequest {
        username: "test_user".to_string(),
        password: "test_password".to_string(),
        email: "test_user@example.com".to_string(),
        permissions: Some(vec!["read:all".to_string(), "write:all".to_string()]),
        group_permissions: Some(vec!["user".to_string()]),
        role: Some("user".to_string()),
        active: Some(true),
    };

    let body = serde_json::to_string(&create_req).unwrap();

    let request = Request::builder()
        .uri("/opsml/api/user")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    // 2. Login with the user
    let login_request = LoginRequest {
        username: "test_user".to_string(),
        password: "test_password".to_string(),
    };
    let body = serde_json::to_string(&login_request).unwrap();
    let request = Request::builder()
        .uri("/opsml/api/auth/ui/login")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let login_response: LoginResponse = serde_json::from_slice(&body).unwrap();

    assert!(login_response.authenticated);

    // 3. test api validate
    let request = Request::builder()
        .uri("/opsml/api/auth/validate")
        .method("GET")
        .header(
            header::AUTHORIZATION,
            format!("Bearer {}", login_response.jwt_token),
        )
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let auth_response: Authenticated = serde_json::from_slice(&body).unwrap();
    assert!(auth_response.is_authenticated);

    // 4. test api refresh token
    let request = Request::builder()
        .uri("/opsml/api/auth/refresh")
        .method("GET")
        .header(
            header::AUTHORIZATION,
            format!("Bearer {}", login_response.jwt_token),
        )
        .body(Body::empty())
        .unwrap();
    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);
    let body = response.into_body().collect().await.unwrap().to_bytes();
    let refresh_response: JwtToken = serde_json::from_slice(&body).unwrap();

    assert!(!refresh_response.token.is_empty());

    // 5. Logout the user - this returns a LogoutResponse
    let request = Request::builder()
        .uri("/opsml/api/auth/ui/logout")
        .method("GET")
        .header(
            header::AUTHORIZATION,
            format!("Bearer {}", refresh_response.token),
        )
        .body(Body::empty())
        .unwrap();
    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let logout_response: LogoutResponse = serde_json::from_slice(&body).unwrap();

    assert!(logout_response.logged_out);
}
