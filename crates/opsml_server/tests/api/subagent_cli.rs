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

async fn create_subagent(
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

async fn list_subagents(helper: &TestHelper, query: &CardQueryArgs) -> Vec<CardRecord> {
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
async fn test_subagent_push_and_list() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let resp = create_subagent(
            &helper,
            "list-test-agent",
            "agent-test",
            vec!["claude-code".into()],
            Some("A subagent for testing list".into()),
        )
        .await;

        assert!(resp.registered);

        let cards = list_subagents(
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
        let card = match &cards[0] {
            CardRecord::SubAgent(c) => c,
            _ => panic!("Expected SubAgent card"),
        };
        assert_eq!(card.name, "list-test-agent");
        assert_eq!(card.space, "agent-test");
        assert_eq!(card.description.as_deref(), Some("A subagent for testing list"));

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_subagent_push_query_by_uid() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let resp = create_subagent(
            &helper,
            "uid-test-agent",
            "agent-test",
            vec!["codex".into()],
            Some("UID roundtrip test".into()),
        )
        .await;

        assert!(resp.registered);
        let uid = resp.key.uid.clone();

        let cards = list_subagents(
            &helper,
            &CardQueryArgs {
                uid: Some(uid),
                registry_type: RegistryType::SubAgent,
                ..Default::default()
            },
        )
        .await;

        assert_eq!(cards.len(), 1);
        match &cards[0] {
            CardRecord::SubAgent(c) => assert_eq!(c.name, "uid-test-agent"),
            _ => panic!("Expected SubAgent card"),
        };

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_subagent_versioning() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let resp1 = create_subagent(
            &helper,
            "versioned-agent",
            "agent-test",
            vec!["claude-code".into()],
            Some("version 1".into()),
        )
        .await;

        let resp2 = create_subagent(
            &helper,
            "versioned-agent",
            "agent-test",
            vec!["claude-code".into()],
            Some("version 2".into()),
        )
        .await;

        assert!(resp1.registered);
        assert!(resp2.registered);
        assert_ne!(resp1.version, resp2.version);

        let cards = list_subagents(
            &helper,
            &CardQueryArgs {
                space: Some("agent-test".into()),
                name: Some("versioned-agent".into()),
                registry_type: RegistryType::SubAgent,
                ..Default::default()
            },
        )
        .await;

        assert!(!cards.is_empty());

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_map_includes_subagents() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        // repo1 has Agent1 and Agent2 from fixtures
        let request = Request::builder()
            .uri("/opsml/api/v1/map/repo1")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let bytes = response.into_body().collect().await.unwrap().to_bytes();
        let body: serde_json::Value = serde_json::from_slice(&bytes).unwrap();

        assert_eq!(body["space"], "repo1");
        let subagents = body["subagents"].as_array().expect("subagents must be array");
        assert!(!subagents.is_empty(), "repo1 should have fixture subagents");
        let names: Vec<&str> = subagents
            .iter()
            .filter_map(|a| a["name"].as_str())
            .collect();
        assert!(names.contains(&"Agent1") || names.contains(&"Agent2"));

        helper.cleanup();
    });
}
