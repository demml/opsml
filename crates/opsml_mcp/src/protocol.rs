use serde::de::Deserializer;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[cfg(feature = "server")]
pub use opsml_types::contracts::{CardQueryArgs, RegistrySpaceRequest};

// ---- JSON-RPC 2.0 response ----

#[derive(Serialize, Deserialize)]
pub struct JsonRpcResponse {
    pub jsonrpc: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub id: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub result: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<JsonRpcError>,
}

impl JsonRpcResponse {
    pub fn ok<T: Serialize>(id: Option<Value>, result: T) -> Self {
        Self {
            jsonrpc: "2.0".to_string(),
            id,
            result: Some(serde_json::to_value(result).unwrap_or(Value::Null)),
            error: None,
        }
    }

    pub fn err(id: Option<Value>, code: i32, message: impl Into<String>) -> Self {
        Self {
            jsonrpc: "2.0".to_string(),
            id,
            result: None,
            error: Some(JsonRpcError {
                code,
                message: message.into(),
            }),
        }
    }
}

#[derive(Serialize, Deserialize)]
pub struct JsonRpcError {
    pub code: i32,
    pub message: String,
}

// ---- Typed request: enum-per-method ----

/// Fully typed JSON-RPC request. The `method` field is consumed during
/// deserialization — the resulting `call` variant carries exactly the params
/// that method expects.
pub struct JsonRpcRequest {
    /// `Option<Value>` because JSON-RPC allows string, number, or null.
    pub id: Option<Value>,
    pub call: McpCall,
}

impl<'de> Deserialize<'de> for JsonRpcRequest {
    fn deserialize<D: Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        use serde::de::Error;

        let val = Value::deserialize(deserializer)?;
        let obj = val
            .as_object()
            .ok_or_else(|| Error::custom("expected JSON object"))?;

        let id = obj.get("id").cloned();
        let method = obj
            .get("method")
            .and_then(Value::as_str)
            .ok_or_else(|| Error::missing_field("method"))?;
        let params = obj.get("params").cloned().unwrap_or(Value::Null);

        let call = match method {
            "initialize" => McpCall::Initialize(
                serde_json::from_value::<InitializeParams>(params).map_err(Error::custom)?,
            ),
            "tools/list" => McpCall::ToolsList,
            "tools/call" => {
                let raw = serde_json::from_value::<RawToolCall>(params).map_err(Error::custom)?;
                McpCall::ToolsCall(ToolCall::from(raw))
            }
            other => McpCall::Unknown(other.to_string()),
        };

        Ok(JsonRpcRequest { id, call })
    }
}

/// One variant per recognized MCP method.
pub enum McpCall {
    Initialize(InitializeParams),
    /// `tools/list` carries no params.
    ToolsList,
    ToolsCall(ToolCall),
    /// Unrecognised method — handler returns -32601.
    Unknown(String),
}

// ---- Initialize params ----

/// Accepted for protocol compliance; `protocol_version` is informational only.
#[derive(Deserialize, Default)]
pub struct InitializeParams {
    #[serde(rename = "protocolVersion", default)]
    pub protocol_version: String,
}

// ---- tools/call: typed dispatch ----

/// Wire shape of a `tools/call` params object.
#[derive(Deserialize)]
struct RawToolCall {
    name: String,
    arguments: Option<Value>,
}

/// One variant per recognized tool name.
pub enum ToolCall {
    ListDocs,
    ReadDoc(ReadDocArgs),
    ListExamples,
    ReadExample(ReadExampleArgs),
    SearchDocs(SearchDocsArgs),
    // Registry query tools (server feature only)
    #[cfg(feature = "server")]
    ListCards(CardQueryArgs),
    #[cfg(feature = "server")]
    GetCard(CardQueryArgs),
    #[cfg(feature = "server")]
    ListSpaces(RegistrySpaceRequest),
    #[cfg(feature = "server")]
    SearchCards(CardQueryArgs),
    /// Unknown tool name — handler returns -32602.
    Unknown(String),
    /// Known tool with malformed arguments — handler returns -32602.
    InvalidArgs {
        name: String,
        reason: String,
    },
}

impl From<RawToolCall> for ToolCall {
    fn from(raw: RawToolCall) -> Self {
        let RawToolCall { name, arguments } = raw;
        let args = arguments.unwrap_or(Value::Null);

        match name.as_str() {
            "list_docs" => ToolCall::ListDocs,
            "list_examples" => ToolCall::ListExamples,
            "read_doc" => serde_json::from_value::<ReadDocArgs>(args)
                .map(ToolCall::ReadDoc)
                .unwrap_or_else(|e| ToolCall::InvalidArgs {
                    name: name.clone(),
                    reason: e.to_string(),
                }),
            "read_example" => serde_json::from_value::<ReadExampleArgs>(args)
                .map(ToolCall::ReadExample)
                .unwrap_or_else(|e| ToolCall::InvalidArgs {
                    name: name.clone(),
                    reason: e.to_string(),
                }),
            "search_docs" => serde_json::from_value::<SearchDocsArgs>(args)
                .map(ToolCall::SearchDocs)
                .unwrap_or_else(|e| ToolCall::InvalidArgs {
                    name: name.clone(),
                    reason: e.to_string(),
                }),
            #[cfg(feature = "server")]
            "list_cards" => serde_json::from_value::<CardQueryArgs>(args)
                .map(ToolCall::ListCards)
                .unwrap_or_else(|e| ToolCall::InvalidArgs {
                    name: name.clone(),
                    reason: e.to_string(),
                }),
            #[cfg(feature = "server")]
            "get_card" => serde_json::from_value::<CardQueryArgs>(args)
                .map(ToolCall::GetCard)
                .unwrap_or_else(|e| ToolCall::InvalidArgs {
                    name: name.clone(),
                    reason: e.to_string(),
                }),
            #[cfg(feature = "server")]
            "list_spaces" => serde_json::from_value::<RegistrySpaceRequest>(args)
                .map(ToolCall::ListSpaces)
                .unwrap_or_else(|e| ToolCall::InvalidArgs {
                    name: name.clone(),
                    reason: e.to_string(),
                }),
            #[cfg(feature = "server")]
            "search_cards" => serde_json::from_value::<CardQueryArgs>(args)
                .map(ToolCall::SearchCards)
                .unwrap_or_else(|e| ToolCall::InvalidArgs {
                    name: name.clone(),
                    reason: e.to_string(),
                }),
            _ => ToolCall::Unknown(name),
        }
    }
}

// ---- Per-tool argument structs ----

#[derive(Deserialize)]
pub struct ReadDocArgs {
    pub topic: String,
}

#[derive(Deserialize)]
pub struct ReadExampleArgs {
    pub name: String,
}

#[derive(Deserialize)]
pub struct SearchDocsArgs {
    pub query: String,
}

// ---- Response payload types ----

#[derive(Serialize)]
pub struct TextContent {
    #[serde(rename = "type")]
    pub content_type: &'static str,
    pub text: String,
}

impl TextContent {
    pub fn text(text: impl Into<String>) -> Self {
        Self {
            content_type: "text",
            text: text.into(),
        }
    }
}

#[derive(Serialize)]
pub struct ToolCallResult {
    pub content: Vec<TextContent>,
}

#[derive(Serialize)]
pub struct DocSummary {
    pub id: &'static str,
    pub title: &'static str,
    pub category: &'static str,
}

#[derive(Serialize)]
pub struct ExampleSummary {
    pub id: &'static str,
    pub title: &'static str,
}

#[derive(Serialize)]
pub struct SearchResult {
    pub id: &'static str,
    pub title: &'static str,
    pub category: &'static str,
    pub snippet: String,
}

/// `input_schema` stays `Value` — JSON Schema is recursive and has no clean
/// fixed-shape Rust representation without a dedicated library.
#[derive(Serialize)]
pub struct ToolDef {
    pub name: &'static str,
    pub description: &'static str,
    #[serde(rename = "inputSchema")]
    pub input_schema: Value,
}

#[derive(Serialize)]
pub struct ToolsListResult {
    pub tools: Vec<ToolDef>,
}

#[derive(Serialize)]
pub struct ServerInfo {
    pub name: &'static str,
    pub version: &'static str,
}

/// Serializes to `{}` — the MCP spec uses an empty object to signal support.
#[derive(Serialize)]
pub struct ToolsCapability {}

#[derive(Serialize)]
pub struct Capabilities {
    pub tools: ToolsCapability,
}

#[derive(Serialize)]
pub struct InitializeResult {
    #[serde(rename = "protocolVersion")]
    pub protocol_version: &'static str,
    #[serde(rename = "serverInfo")]
    pub server_info: ServerInfo,
    pub capabilities: Capabilities,
    pub instructions: &'static str,
}
