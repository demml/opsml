use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode, header},
};
use http_body_util::BodyExt;
use opsml_server::core::role::schema::{
    CreateRoleRequest, RoleListResponse, RoleResponse, UpdateRoleRequest,
};

#[tokio::test]
async fn test_opsml_server_role_crud() {
    let helper = TestHelper::new(None).await;

    // 1. List roles — expect 4 seeded system roles
    let request = Request::builder()
        .uri("/opsml/api/role")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let list_response: RoleListResponse = serde_json::from_slice(&body).unwrap();

    let system_role_names = ["admin", "user", "viewer", "data_scientist"];
    for role_name in &system_role_names {
        let role = list_response.roles.iter().find(|r| r.name == *role_name);
        assert!(role.is_some(), "Expected system role '{role_name}' not found");
        assert!(
            role.unwrap().is_system,
            "Role '{role_name}' should have is_system=true"
        );
    }

    // 2. Get system role
    let request = Request::builder()
        .uri("/opsml/api/role/admin")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let role_response: RoleResponse = serde_json::from_slice(&body).unwrap();
    assert_eq!(role_response.name, "admin");
    assert!(role_response.is_system);

    // 3. Get non-existent role — expect 404
    let request = Request::builder()
        .uri("/opsml/api/role/nonexistent")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::NOT_FOUND);

    // 4. Create custom role
    let create_req = CreateRoleRequest {
        name: "test_role".to_string(),
        description: Some("Test role".to_string()),
        permissions: vec!["read:all".to_string()],
    };

    let request = Request::builder()
        .uri("/opsml/api/role")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&create_req).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let role_response: RoleResponse = serde_json::from_slice(&body).unwrap();
    assert_eq!(role_response.name, "test_role");
    assert!(!role_response.is_system);

    // 5. Get created role
    let request = Request::builder()
        .uri("/opsml/api/role/test_role")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let role_response: RoleResponse = serde_json::from_slice(&body).unwrap();
    assert_eq!(role_response.name, "test_role");
    assert_eq!(role_response.description, "Test role");
    assert_eq!(role_response.permissions, vec!["read:all".to_string()]);
    assert!(!role_response.is_system);

    // 6. Update custom role
    let update_req = UpdateRoleRequest {
        description: Some("Updated description".to_string()),
        permissions: Some(vec!["read:all".to_string(), "write:all".to_string()]),
    };

    let request = Request::builder()
        .uri("/opsml/api/role/test_role")
        .method("PUT")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&update_req).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let mut role_response: RoleResponse = serde_json::from_slice(&body).unwrap();
    role_response.permissions.sort();
    assert_eq!(role_response.description, "Updated description");
    assert_eq!(
        role_response.permissions,
        vec!["read:all".to_string(), "write:all".to_string()]
    );

    // 7. Cannot update system role — expect 403
    let update_req = UpdateRoleRequest {
        description: Some("Hacked".to_string()),
        permissions: None,
    };

    let request = Request::builder()
        .uri("/opsml/api/role/admin")
        .method("PUT")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&update_req).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::FORBIDDEN);

    // 8. Cannot delete system role — expect 403
    let request = Request::builder()
        .uri("/opsml/api/role/user")
        .method("DELETE")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::FORBIDDEN);

    // 9. Delete custom role
    let request = Request::builder()
        .uri("/opsml/api/role/test_role")
        .method("DELETE")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let delete_response: serde_json::Value = serde_json::from_slice(&body).unwrap();
    assert_eq!(delete_response["success"], true);

    // 10. Verify deletion
    let request = Request::builder()
        .uri("/opsml/api/role/test_role")
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::NOT_FOUND);

    helper.cleanup();
}
