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
        ToolCardClientRecord,
    },
};
use test_utils::retry_flaky_test;

async fn create_tool(
    helper: &TestHelper,
    name: &str,
    space: &str,
    tool_type: &str,
    description: Option<String>,
) -> CreateCardResponse {
    let card_request = CreateCardRequest {
        card: CardRecord::Tool(ToolCardClientRecord {
            name: name.to_string(),
            space: space.to_string(),
            version: "0.1.0".to_string(),
            tool_type: tool_type.to_string(),
            description,
            ..ToolCardClientRecord::default()
        }),
        registry_type: RegistryType::Tool,
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

async fn list_tools(helper: &TestHelper, query: &CardQueryArgs) -> Vec<CardRecord> {
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
async fn test_tool_push_and_list() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let resp = create_tool(
            &helper,
            "list-test-tool",
            "tool-test",
            "ShellScript",
            Some("A shell script tool for testing".into()),
        )
        .await;

        assert!(resp.registered);

        let cards = list_tools(
            &helper,
            &CardQueryArgs {
                space: Some("tool-test".into()),
                name: Some("list-test-tool".into()),
                registry_type: RegistryType::Tool,
                ..Default::default()
            },
        )
        .await;

        assert_eq!(cards.len(), 1);
        let card = match &cards[0] {
            CardRecord::Tool(c) => c,
            _ => panic!("Expected Tool card"),
        };
        assert_eq!(card.name, "list-test-tool");
        assert_eq!(card.space, "tool-test");
        assert_eq!(
            card.description.as_deref(),
            Some("A shell script tool for testing")
        );
        assert_eq!(card.tool_type, "ShellScript");

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_tool_push_query_by_uid() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let resp = create_tool(
            &helper,
            "uid-test-tool",
            "tool-test",
            "SlashCommand",
            Some("UID roundtrip test".into()),
        )
        .await;

        assert!(resp.registered);
        let uid = resp.key.uid.clone();

        let cards = list_tools(
            &helper,
            &CardQueryArgs {
                uid: Some(uid),
                registry_type: RegistryType::Tool,
                ..Default::default()
            },
        )
        .await;

        assert_eq!(cards.len(), 1);
        match &cards[0] {
            CardRecord::Tool(c) => assert_eq!(c.name, "uid-test-tool"),
            _ => panic!("Expected Tool card"),
        };

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_tool_versioning() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        let resp1 = create_tool(
            &helper,
            "versioned-tool",
            "tool-test",
            "McpServer",
            Some("version 1".into()),
        )
        .await;

        let resp2 = create_tool(
            &helper,
            "versioned-tool",
            "tool-test",
            "McpServer",
            Some("version 2".into()),
        )
        .await;

        assert!(resp1.registered);
        assert!(resp2.registered);
        assert_ne!(resp1.version, resp2.version);

        let cards = list_tools(
            &helper,
            &CardQueryArgs {
                space: Some("tool-test".into()),
                name: Some("versioned-tool".into()),
                registry_type: RegistryType::Tool,
                ..Default::default()
            },
        )
        .await;

        assert!(!cards.is_empty());

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_map_includes_tools() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        // repo1 has Tool1, Tool2, Tool3 from fixtures
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
        let tools = body["tools"].as_array().expect("tools must be array");
        assert!(!tools.is_empty(), "repo1 should have fixture tools");

        let names: Vec<&str> = tools
            .iter()
            .filter_map(|t| t["name"].as_str())
            .collect();
        assert!(
            names.contains(&"Tool1") || names.contains(&"Tool2") || names.contains(&"Tool3"),
            "expected at least one of Tool1/Tool2/Tool3 in tools"
        );

        helper.cleanup();
    });
}

#[tokio::test]
async fn test_v1_map_commands_are_slash_commands() {
    retry_flaky_test!({
        let helper = TestHelper::new(None).await;

        // repo1 has Tool2 as SlashCommand from fixtures
        let request = Request::builder()
            .uri("/opsml/api/v1/map/repo1")
            .method("GET")
            .body(Body::empty())
            .unwrap();

        let response = helper.send_oneshot(request).await;
        assert_eq!(response.status(), StatusCode::OK);

        let bytes = response.into_body().collect().await.unwrap().to_bytes();
        let body: serde_json::Value = serde_json::from_slice(&bytes).unwrap();

        let commands = body["commands"].as_array().expect("commands must be array");
        assert!(!commands.is_empty(), "repo1 should have SlashCommand tools in commands");

        for cmd in commands {
            let compatible_tools = cmd["compatible_tools"]
                .as_array()
                .expect("compatible_tools must be array");
            let tool_types: Vec<&str> = compatible_tools
                .iter()
                .filter_map(|t| t.as_str())
                .collect();
            assert!(
                tool_types.contains(&"SlashCommand"),
                "commands array must only contain SlashCommand tools, got: {tool_types:?}"
            );
        }

        let cmd_names: Vec<&str> = commands
            .iter()
            .filter_map(|c| c["name"].as_str())
            .collect();
        assert!(cmd_names.contains(&"Tool2"), "Tool2 (SlashCommand) must be in commands");

        helper.cleanup();
    });
}
