use crate::common::TestHelper;
use axum::{
    body::Body,
    http::{Request, StatusCode, header},
};
use http_body_util::BodyExt;
use opsml_mcp::protocol::JsonRpcResponse;
use serde_json::{Value, json};

fn mcp_request(body: Value) -> Request<Body> {
    Request::builder()
        .uri("/opsml/api/mcp")
        .method("POST")
        .header(header::CONTENT_TYPE, "application/json")
        .body(Body::from(body.to_string()))
        .unwrap()
}

async fn send_mcp(helper: &TestHelper, body: Value) -> JsonRpcResponse {
    let response = helper.send_oneshot(mcp_request(body)).await;
    assert_eq!(response.status(), StatusCode::OK);
    let bytes = response.into_body().collect().await.unwrap().to_bytes();
    serde_json::from_slice(&bytes).unwrap()
}

#[tokio::test]
async fn test_mcp_requires_auth() {
    let helper = TestHelper::new(None).await;

    // Unauthenticated request — no auth header added.
    let response = helper
        .send_no_auth(mcp_request(
            json!({"jsonrpc":"2.0","id":1,"method":"tools/list"}),
        ))
        .await;

    assert_eq!(response.status(), StatusCode::UNAUTHORIZED);

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_initialize() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": { "protocolVersion": "2024-11-05" }
        }),
    )
    .await;

    assert!(resp.error.is_none());
    let result = resp.result.unwrap();
    assert_eq!(result["protocolVersion"], "2024-11-05");
    assert_eq!(result["serverInfo"]["name"], "opsml-mcp");
    assert!(result["capabilities"]["tools"].is_object());

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_tools_list() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}),
    )
    .await;

    assert!(resp.error.is_none());
    let tools = resp.result.unwrap()["tools"].clone();
    let tools: Vec<Value> = serde_json::from_value(tools).unwrap();

    let names: Vec<&str> = tools.iter().map(|t| t["name"].as_str().unwrap()).collect();

    assert!(names.contains(&"list_docs"));
    assert!(names.contains(&"read_doc"));
    assert!(names.contains(&"list_examples"));
    assert!(names.contains(&"read_example"));
    assert!(names.contains(&"search_docs"));

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_list_docs() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": { "name": "list_docs", "arguments": {} }
        }),
    )
    .await;

    assert!(resp.error.is_none());
    let text = &resp.result.unwrap()["content"][0]["text"];
    let entries: Vec<Value> = serde_json::from_str(text.as_str().unwrap()).unwrap();

    assert!(!entries.is_empty());
    // No examples in the doc list
    assert!(entries.iter().all(|e| e["category"] != "example"));
    // Spot-check a known doc
    assert!(entries.iter().any(|e| e["id"] == "cards/datacard"));

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_read_doc() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": { "name": "read_doc", "arguments": { "topic": "cards/datacard" } }
        }),
    )
    .await;

    assert!(resp.error.is_none());
    let text = resp.result.unwrap()["content"][0]["text"].clone();
    assert!(text.as_str().unwrap().contains("DataCard"));

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_read_doc_not_found() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": { "name": "read_doc", "arguments": { "topic": "does/not/exist" } }
        }),
    )
    .await;

    assert!(resp.result.is_none());
    let err = resp.error.unwrap();
    assert_eq!(err.code, -32602);

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_list_examples() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": { "name": "list_examples", "arguments": {} }
        }),
    )
    .await;

    assert!(resp.error.is_none());
    let text = &resp.result.unwrap()["content"][0]["text"];
    let entries: Vec<Value> = serde_json::from_str(text.as_str().unwrap()).unwrap();

    assert!(!entries.is_empty());
    assert!(entries.iter().any(|e| e["id"] == "example/data/numpy"));
    assert!(entries.iter().any(|e| e["id"] == "example/model/sklearn"));

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_read_example() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": { "name": "read_example", "arguments": { "name": "example/data/numpy" } }
        }),
    )
    .await;

    assert!(resp.error.is_none());
    let text = resp.result.unwrap()["content"][0]["text"].clone();
    assert!(text.as_str().unwrap().len() > 10);

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_search_docs() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": { "name": "search_docs", "arguments": { "query": "DataCard" } }
        }),
    )
    .await;

    assert!(resp.error.is_none());
    let text = resp.result.unwrap()["content"][0]["text"].clone();
    let text = text.as_str().unwrap();
    // Should find results across multiple docs
    let results: Vec<Value> = serde_json::from_str(text).unwrap();
    assert!(!results.is_empty());
    assert!(results.iter().any(|r| r["id"] == "cards/datacard"));

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_search_docs_no_results() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": { "name": "search_docs", "arguments": { "query": "xyzzy_not_in_any_doc_ever" } }
        }),
    )
    .await;

    assert!(resp.error.is_none());
    let text = resp.result.unwrap()["content"][0]["text"].clone();
    assert!(text.as_str().unwrap().contains("No results found"));

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_unknown_method() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({"jsonrpc": "2.0", "id": 1, "method": "not_a_method"}),
    )
    .await;

    assert!(resp.result.is_none());
    let err = resp.error.unwrap();
    assert_eq!(err.code, -32601);

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_unknown_tool() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": { "name": "not_a_tool", "arguments": {} }
        }),
    )
    .await;

    assert!(resp.result.is_none());
    let err = resp.error.unwrap();
    assert_eq!(err.code, -32602);

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_invalid_tool_args() {
    let helper = TestHelper::new(None).await;

    // read_doc requires "topic" — omit it
    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": { "name": "read_doc", "arguments": {} }
        }),
    )
    .await;

    assert!(resp.result.is_none());
    let err = resp.error.unwrap();
    assert_eq!(err.code, -32602);
    assert!(err.message.contains("read_doc"));

    helper.cleanup();
}

// ---- Registry query tool tests ----

#[tokio::test]
async fn test_mcp_tools_list_includes_registry_tools() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}),
    )
    .await;

    assert!(resp.error.is_none());
    let tools = resp.result.unwrap()["tools"].clone();
    let tools: Vec<Value> = serde_json::from_value(tools).unwrap();
    let names: Vec<&str> = tools.iter().map(|t| t["name"].as_str().unwrap()).collect();

    assert!(names.contains(&"list_cards"));
    assert!(names.contains(&"get_card"));
    assert!(names.contains(&"list_spaces"));
    assert!(names.contains(&"search_cards"));

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_list_cards_model() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "list_cards",
                "arguments": { "registry_type": "model" }
            }
        }),
    )
    .await;

    assert!(resp.error.is_none());
    let text = resp.result.unwrap()["content"][0]["text"].clone();
    let text = text.as_str().unwrap();
    // Seeded data has Model1–Model10
    assert!(text.contains("Model1") || text.contains("model"));

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_list_cards_data() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "list_cards",
                "arguments": { "registry_type": "data", "limit": 5 }
            }
        }),
    )
    .await;

    assert!(resp.error.is_none());
    let text = resp.result.unwrap()["content"][0]["text"].clone();
    assert!(text.as_str().unwrap().contains("Data1"));

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_list_cards_invalid_registry_type() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "list_cards",
                "arguments": { "registry_type": "bogus" }
            }
        }),
    )
    .await;

    assert!(resp.result.is_none());
    let err = resp.error.unwrap();
    assert_eq!(err.code, -32602);

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_get_card_by_uid() {
    let helper = TestHelper::new(None).await;

    // uid seeded in populate_db.sql for model registry
    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_card",
                "arguments": {
                    "registry_type": "model",
                    "uid": "550e8400-e29b-41d4-a716-446655440000"
                }
            }
        }),
    )
    .await;

    assert!(resp.error.is_none());
    let text = resp.result.unwrap()["content"][0]["text"].clone();
    assert!(text.as_str().unwrap().contains("Model1"));

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_list_spaces_model() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "list_spaces",
                "arguments": { "registry_type": "model" }
            }
        }),
    )
    .await;

    assert!(resp.error.is_none());
    let text = resp.result.unwrap()["content"][0]["text"].clone();
    let spaces: Vec<String> = serde_json::from_str(text.as_str().unwrap()).unwrap();
    // Seeded models have spaces repo1–repo10
    assert!(!spaces.is_empty());
    assert!(spaces.contains(&"repo1".to_string()));

    helper.cleanup();
}

#[tokio::test]
async fn test_mcp_search_cards() {
    let helper = TestHelper::new(None).await;

    let resp = send_mcp(
        &helper,
        json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "search_cards",
                "arguments": { "registry_type": "data", "name": "Data1" }
            }
        }),
    )
    .await;

    assert!(resp.error.is_none());
    let text = resp.result.unwrap()["content"][0]["text"].clone();
    assert!(text.as_str().unwrap().contains("Data1"));

    helper.cleanup();
}
