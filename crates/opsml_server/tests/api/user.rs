use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{header, Request, StatusCode},
};
use http_body_util::BodyExt; // for `collect`

use opsml_server::core::user::schema::*;

#[tokio::test]
async fn test_opsml_server_user_crud() {
    let helper = TestHelper::new().await;

    // 1. Create a new user
    let create_req = CreateUserRequest {
        username: "test_user".to_string(),
        password: "test_password".to_string(),
        email: "test_user@example.com".to_string(),
        permissions: Some(vec!["read".to_string(), "write".to_string()]),
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
        vec!["read".to_string(), "write".to_string()]
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
            "read".to_string(),
            "write".to_string(),
            "execute".to_string(),
        ]),
        group_permissions: Some(vec!["user".to_string(), "developer".to_string()]),
        active: Some(true),
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
    let user_response: UserResponse = serde_json::from_slice(&body).unwrap();
    assert_eq!(
        user_response.permissions,
        vec![
            "read".to_string(),
            "write".to_string(),
            "execute".to_string()
        ]
    );
    assert_eq!(
        user_response.group_permissions,
        vec!["user".to_string(), "developer".to_string()]
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
        .uri("/opsml/api/user/reset-password/recovery")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let reset_response: ResetPasswordResponse = serde_json::from_slice(&body).unwrap();
    assert_eq!(reset_response.message, "Password updated successfully");
    assert_eq!(reset_response.remaining_recovery_codes, 7);

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
