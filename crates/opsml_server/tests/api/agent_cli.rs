use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode, header},
};
use http_body_util::BodyExt;
use opsml_semver::VersionType;
use opsml_types::{
    RegistryType,
    contracts::{
        CardQueryArgs, CardRecord, CardVersionRequest, CreateCardRequest, CreateCardResponse,
        SubAgentCardClientRecord,
    },
};
use test_utils::retry_flaky_test;

async fn create_agent(
    helper: &TestHelper,
    name: &str,
    space: &str,
    compatible_clis: Vec<String>,
    description: Option<String>,
) -> CreateCardResponse {
    let card_request = CreateCardRequest {
        card: CardRecord::SubAgent(SubAgentCardClientRecord {
            name: name.to_string(),
            space: space.to_string(),
            version: "0.1.0".to_string(),
            compatible_clis,
            description,
            ..SubAgentCardClientRecord::default()
        }),
        registry_type: RegistryType::SubAgent,
        version_request: CardVersionRequest {
            name: name.to_string(),
            space: space.to_string(),
            version: Some("0.1.0".to_string()),
            version_type: VersionType::Minor,
            pre_tag: None,
            build_tag: None,
        },
    };

    let request = Request::builder()
        .uri("/opsml/api/card/create")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(serde_json::to_string(&card_request).unwrap()))
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let bytes = response.into_body().collect().await.unwrap().to_bytes();
    serde_json::from_slice(&bytes).unwrap()
}

async fn list_agents(helper: &TestHelper, query: &CardQueryArgs) -> Vec<CardRecord> {
    let query_string = serde_qs::to_string(query).unwrap();
    let request = Request::builder()
        .uri(format!("/opsml/api/card/list?{query_string}"))
        .method("GET")
        .body(Body::empty())
        .unwrap();

    let response = helper.send_oneshot(request).await;
    assert_eq!(response.status(), StatusCode::OK);

    let bytes = response.into_body().collect().await.unwrap().to_bytes();
    serde_json::from_slice(&bytes).unwrap()
}

#[tokio::test]
async fn test_agent_push_and_list() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let resp = create_agent(
            &helper,
            "list-test-agent",
            "agent-test",
            vec!["claude-code".into()],
            Some("A subagent for testing".into()),
        )
        .await;

        assert!(resp.registered);

        let cards = list_agents(
            &helper,
            &CardQueryArgs {
                space: Some("agent-test".into()),
                name: Some("list-test-agent".into()),
                registry_type: RegistryType::SubAgent,
                ..Default::default()
            },
        )
        .await;

        assert_eq!(cards.len(), 1);

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_agent_map_subagents_populated() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        create_agent(
            &helper,
            "map-agent",
            "map-space",
            vec!["claude-code".into()],
            Some("Map test agent".into()),
        )
        .await;

        let request = Request::builder()
            .uri("/opsml/api/v1/map/map-space")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let bytes = response.into_body().collect().await.unwrap().to_bytes();
        let map: serde_json::Value = serde_json::from_slice(&bytes).unwrap();

        let subagents = map["subagents"].as_array().unwrap();
        assert!(!subagents.is_empty());
        assert_eq!(subagents[0]["name"], "map-agent");

        helper.cleanup();
    });
}
