use crate::common::TestHelper;
use axum::{body::Body, http::{Request, StatusCode}};
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
        // Should return 500 since the space/name doesn't exist
        assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);

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
        assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);

        helper.cleanup();
    });
}
