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
        SkillCardClientRecord,
    },
};
use test_utils::retry_flaky_test;

/// Helper: create a skill card via the API and return the CreateCardResponse.
async fn create_skill(
    helper: &TestHelper,
    name: &str,
    space: &str,
    tags: Vec<String>,
    tools: Vec<String>,
    description: Option<String>,
    body: Option<String>,
) -> CreateCardResponse {
    let card_request = CreateCardRequest {
        card: CardRecord::Skill(SkillCardClientRecord {
            name: name.to_string(),
            space: space.to_string(),
            version: "0.1.0".to_string(),
            tags,
            compatible_tools: tools,
            description,
            body,
            ..SkillCardClientRecord::default()
        }),
        registry_type: RegistryType::Skill,
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

/// Helper: list skill cards via the API.
async fn list_skills(helper: &TestHelper, query: &CardQueryArgs) -> Vec<CardRecord> {
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

/// Push a skill card and verify it appears in a subsequent list query.
#[tokio::test]
async fn test_skill_push_and_list() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let resp = create_skill(
            &helper,
            "list-test-skill",
            "cli-test",
            vec!["rust".into(), "testing".into()],
            vec!["claude-code".into()],
            Some("A skill for testing list".into()),
            None,
        )
        .await;

        assert!(resp.registered);

        let cards = list_skills(
            &helper,
            &CardQueryArgs {
                space: Some("cli-test".into()),
                name: Some("list-test-skill".into()),
                registry_type: RegistryType::Skill,
                ..Default::default()
            },
        )
        .await;

        assert_eq!(cards.len(), 1);
        let card = match &cards[0] {
            CardRecord::Skill(c) => c,
            _ => panic!("Expected Skill card"),
        };
        assert_eq!(card.name, "list-test-skill");
        assert_eq!(card.space, "cli-test");
        assert_eq!(card.tags, vec!["rust", "testing"]);
        assert_eq!(card.compatible_tools, vec!["claude-code"]);
        assert_eq!(card.description.as_deref(), Some("A skill for testing list"));

        helper.cleanup();
    });
}

/// Push a skill card and retrieve it by UID — roundtrip verification.
#[tokio::test]
async fn test_skill_push_query_by_uid() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let resp = create_skill(
            &helper,
            "uid-test-skill",
            "cli-test",
            vec![],
            vec![],
            Some("UID roundtrip test".into()),
            Some("This is the skill body content.".into()),
        )
        .await;

        assert!(resp.registered);
        let uid = resp.key.uid.clone();

        let cards = list_skills(
            &helper,
            &CardQueryArgs {
                uid: Some(uid.clone()),
                registry_type: RegistryType::Skill,
                ..Default::default()
            },
        )
        .await;

        assert_eq!(cards.len(), 1);
        let card = match &cards[0] {
            CardRecord::Skill(c) => c,
            _ => panic!("Expected Skill card"),
        };
        assert_eq!(card.uid, uid);
        assert_eq!(card.name, "uid-test-skill");

        helper.cleanup();
    });
}

/// Push a skill card with CLI overrides (tags, tools) and verify they are persisted.
#[tokio::test]
async fn test_skill_push_with_overrides() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let resp = create_skill(
            &helper,
            "override-skill",
            "override-space",
            vec!["tag-a".into(), "tag-b".into(), "tag-c".into()],
            vec!["codex".into(), "gemini-cli".into()],
            Some("Skill with overrides".into()),
            None,
        )
        .await;

        assert!(resp.registered);

        let cards = list_skills(
            &helper,
            &CardQueryArgs {
                uid: Some(resp.key.uid),
                registry_type: RegistryType::Skill,
                ..Default::default()
            },
        )
        .await;

        assert_eq!(cards.len(), 1);
        let card = match &cards[0] {
            CardRecord::Skill(c) => c,
            _ => panic!("Expected Skill card"),
        };
        assert_eq!(card.tags, vec!["tag-a", "tag-b", "tag-c"]);
        assert_eq!(card.compatible_tools, vec!["codex", "gemini-cli"]);
        assert_eq!(card.space, "override-space");

        helper.cleanup();
    });
}

/// List pre-seeded skill cards from populate_db.sql, filtering by space.
#[tokio::test]
async fn test_skill_list_seeded_by_space() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        // populate_db.sql seeds skills in repo1 and repo2
        let repo1_cards = list_skills(
            &helper,
            &CardQueryArgs {
                space: Some("repo1".into()),
                registry_type: RegistryType::Skill,
                sort_by_timestamp: Some(true),
                ..Default::default()
            },
        )
        .await;

        // repo1 has Skill1, Skill2, Skill3, Skill4, Skill8, Skill9
        assert_eq!(repo1_cards.len(), 6);
        for card in &repo1_cards {
            match card {
                CardRecord::Skill(c) => assert_eq!(c.space, "repo1"),
                _ => panic!("Expected Skill card"),
            }
        }

        let repo2_cards = list_skills(
            &helper,
            &CardQueryArgs {
                space: Some("repo2".into()),
                registry_type: RegistryType::Skill,
                sort_by_timestamp: Some(true),
                ..Default::default()
            },
        )
        .await;

        // repo2 has Skill5, Skill6, Skill7 (and possibly more depending on fixture)
        assert!(repo2_cards.len() >= 3);
        for card in &repo2_cards {
            match card {
                CardRecord::Skill(c) => assert_eq!(c.space, "repo2"),
                _ => panic!("Expected Skill card"),
            }
        }

        helper.cleanup();
    });
}

/// List pre-seeded skill cards filtering by tags.
#[tokio::test]
async fn test_skill_list_seeded_by_tags() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        // Skill1 has tags ["tag1","tag2"], Skill3 has ["tag1"]
        let tagged = list_skills(
            &helper,
            &CardQueryArgs {
                tags: Some(vec!["tag1".into()]),
                registry_type: RegistryType::Skill,
                ..Default::default()
            },
        )
        .await;

        assert!(tagged.len() >= 2);
        for card in &tagged {
            match card {
                CardRecord::Skill(c) => {
                    assert!(c.tags.contains(&"tag1".to_string()));
                }
                _ => panic!("Expected Skill card"),
            }
        }

        helper.cleanup();
    });
}

/// Post-filter by compatible tool (simulates CLI --tool flag behavior).
#[tokio::test]
async fn test_skill_list_post_filter_by_tool() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        // Fetch all skill cards, then post-filter (same as list_skills CLI action)
        let all_cards = list_skills(
            &helper,
            &CardQueryArgs {
                registry_type: RegistryType::Skill,
                sort_by_timestamp: Some(true),
                ..Default::default()
            },
        )
        .await;

        // Post-filter for "claude-code" — Skill1 has this tool
        let claude_skills: Vec<_> = all_cards
            .iter()
            .filter(|card| {
                if let CardRecord::Skill(r) = card {
                    r.compatible_tools.iter().any(|t| t == "claude-code")
                } else {
                    false
                }
            })
            .collect();

        assert!(
            !claude_skills.is_empty(),
            "At least Skill1 should have claude-code"
        );

        // Post-filter for "codex" — Skill3 has this tool
        let codex_skills: Vec<_> = all_cards
            .iter()
            .filter(|card| {
                if let CardRecord::Skill(r) = card {
                    r.compatible_tools.iter().any(|t| t == "codex")
                } else {
                    false
                }
            })
            .collect();

        assert!(
            !codex_skills.is_empty(),
            "At least Skill3 should have codex"
        );

        helper.cleanup();
    });
}

/// Create multiple skill versions and verify limit works.
#[tokio::test]
async fn test_skill_list_with_limit() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        // populate_db.sql has 10 seeded skills across repo1/repo2/repo3
        let limited = list_skills(
            &helper,
            &CardQueryArgs {
                registry_type: RegistryType::Skill,
                limit: Some(3),
                sort_by_timestamp: Some(true),
                ..Default::default()
            },
        )
        .await;

        assert_eq!(limited.len(), 3);

        helper.cleanup();
    });
}
