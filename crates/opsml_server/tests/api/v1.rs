use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use http_body_util::BodyExt;
use opsml_server::core::agentic::schema::{ArtifactMeta, MapResponse};
use opsml_types::contracts::skill::MarketplaceStats;
use test_utils::retry_flaky_test;

#[tokio::test]
async fn test_v1_map() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let request = Request::builder()
            .uri("/opsml/api/v1/map/repo1")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let result: MapResponse = serde_json::from_slice(&body).unwrap();

        assert_eq!(result.space, "repo1");
        assert!(!result.skills.is_empty());

        // Verify fields are present
        let skill = &result.skills[0];
        assert!(!skill.name.is_empty());
        assert!(!skill.latest_version.is_empty());

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_marketplace_tags() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let request = Request::builder()
            .uri("/opsml/api/v1/marketplace/tags")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let tags: Vec<String> = serde_json::from_slice(&body).unwrap();

        // Fixture has tag1, tag2 in the skill records
        assert!(tags.contains(&"tag1".to_string()));

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_marketplace_stats() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let request = Request::builder()
            .uri("/opsml/api/v1/marketplace/stats")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let stats: MarketplaceStats = serde_json::from_slice(&body).unwrap();

        assert!(stats.total_skills > 0);
        assert!(stats.total_spaces > 0);
        assert_eq!(stats.total_downloads, 0);

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_marketplace_featured() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let request = Request::builder()
            .uri("/opsml/api/v1/marketplace/featured")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let skills: Vec<ArtifactMeta> = serde_json::from_slice(&body).unwrap();

        assert!(!skills.is_empty());
        assert!(skills.len() <= 6);

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_skill_not_found() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let request = Request::builder()
            .uri("/opsml/api/v1/skill/no-such-space/no-such-skill")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::NOT_FOUND);

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_skill_pinned_not_found() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let request = Request::builder()
            .uri("/opsml/api/v1/skill/no-such-space/no-such-skill/1.0.0")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::NOT_FOUND);

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_capabilities() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let request = Request::builder()
            .uri("/opsml/api/v1/capabilities")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        // Verify version header is present
        assert!(response.headers().get("x-opsml-api-version").is_some());

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let caps: serde_json::Value = serde_json::from_slice(&body).unwrap();

        assert_eq!(caps["api_version"], "1.0.0");
        let registry_types = caps["registry_types"].as_array().unwrap();
        assert!(!registry_types.is_empty());
        assert!(registry_types.iter().any(|v| v == "data"));
        assert!(registry_types.iter().any(|v| v == "skill"));
        assert!(caps["features"]["scouter_enabled"].is_boolean());
        assert_eq!(caps["features"]["openapi_spec"], "/opsml/api/v1/openapi.json");
        assert_eq!(caps["auth"]["login_endpoint"], "/opsml/api/auth/login");

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_docs_list() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let request = Request::builder()
            .uri("/opsml/api/v1/docs")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let result: serde_json::Value = serde_json::from_slice(&body).unwrap();

        let docs = result["docs"].as_array().unwrap();
        assert!(!docs.is_empty());
        // All entries from /docs should be non-example category
        assert!(docs.iter().all(|d| d["category"] != "example"));

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_examples_list() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let request = Request::builder()
            .uri("/opsml/api/v1/examples")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let result: serde_json::Value = serde_json::from_slice(&body).unwrap();

        let docs = result["docs"].as_array().unwrap();
        // All entries from /examples should be example category
        assert!(docs.iter().all(|d| d["category"] == "example"));

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_doc_not_found() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let request = Request::builder()
            .uri("/opsml/api/v1/docs/no-such-doc")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::NOT_FOUND);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let err: serde_json::Value = serde_json::from_slice(&body).unwrap();
        assert_eq!(err["code"], "NOT_FOUND");

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_docs_search() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let request = Request::builder()
            .uri("/opsml/api/v1/docs/search?q=card")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let result: serde_json::Value = serde_json::from_slice(&body).unwrap();

        assert_eq!(result["query"], "card");

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_docs_search_query_too_long() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;
        let long_query = "a".repeat(201);

        let request = Request::builder()
            .uri(&format!("/opsml/api/v1/docs/search?q={long_query}"))
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::BAD_REQUEST);

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_openapi_json() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let request = Request::builder()
            .uri("/opsml/api/v1/openapi.json")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let body = response.into_body().collect().await.unwrap().to_bytes();
        let spec: serde_json::Value = serde_json::from_slice(&body).unwrap();

        assert!(spec["paths"].get("/opsml/api/v1/capabilities").is_some());
        assert!(spec["paths"].get("/opsml/api/v1/docs").is_some());
        assert_eq!(spec["info"]["version"], "1.0.0");

        helper.cleanup();
    });
}
