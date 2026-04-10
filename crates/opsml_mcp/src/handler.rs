use crate::content::DOCS;
use crate::protocol::{
    Capabilities, DocSummary, ExampleSummary, InitializeResult, JsonRpcRequest, JsonRpcResponse,
    McpCall, ReadDocArgs, ReadExampleArgs, SearchDocsArgs, SearchResult, ServerInfo, TextContent,
    ToolCall, ToolCallResult, ToolDef, ToolsCapability, ToolsListResult,
};
use serde_json::{Value, json};

#[cfg(feature = "server")]
use {
    crate::protocol::{CardQueryArgs, RegistrySpaceRequest, ServiceToolsArgs},
    opsml_auth::permission::UserPermissions,
    opsml_sql::enums::client::SqlClientEnum,
    opsml_sql::traits::CardLogicTrait,
    opsml_types::cards::CardTable,
    std::sync::Arc,
};

pub struct McpHandler {
    #[cfg(feature = "server")]
    pub sql: Option<Arc<SqlClientEnum>>,
}

impl McpHandler {
    pub async fn handle(
        &self,
        req: JsonRpcRequest,
        #[cfg(feature = "server")] perms: UserPermissions,
    ) -> JsonRpcResponse {
        let JsonRpcRequest { id, call } = req;
        match call {
            McpCall::Initialize(_) => self.initialize(id),
            McpCall::ToolsList => self.tools_list(id),
            McpCall::ToolsCall(tool_call) => {
                self.dispatch_tool(
                    id,
                    tool_call,
                    #[cfg(feature = "server")]
                    perms,
                )
                .await
            }
            McpCall::Unknown(method) => {
                JsonRpcResponse::err(id, -32601, format!("Method not found: {method}"))
            }
        }
    }

    fn initialize(&self, id: Option<Value>) -> JsonRpcResponse {
        JsonRpcResponse::ok(
            id,
            InitializeResult {
                protocol_version: "2024-11-05",
                server_info: ServerInfo {
                    name: "opsml-mcp",
                    version: env!("CARGO_PKG_VERSION"),
                },
                capabilities: Capabilities {
                    tools: ToolsCapability {},
                },
                instructions: "\
This MCP server exposes OpsML documentation and Python code examples.\n\
\n\
AUTHENTICATION REQUIRED\n\
Every request must include an Authorization header. Two formats are accepted:\n\
\n\
  HTTP Basic Auth (recommended for direct configuration):\n\
    Authorization: Basic <base64(username:password)>\n\
\n\
  Bearer token (obtain via POST /opsml/api/auth/login):\n\
    Authorization: Bearer <jwt_token>\n\
\n\
Configure your MCP client with the Authorization header before calling any tool.\n\
For Claude Desktop, set the header in claude_desktop_config.json under the server entry.",
            },
        )
    }

    fn tools_list(&self, id: Option<Value>) -> JsonRpcResponse {
        #[allow(unused_mut)]
        let mut tools = vec![
            ToolDef {
                name: "list_docs",
                description: "List all available OpsML documentation topics (cards, setup, CLI, deployment, monitoring).",
                input_schema: json!({ "type": "object", "properties": {}, "required": [] }),
            },
            ToolDef {
                name: "read_doc",
                description: "Read the full content of an OpsML documentation topic by its ID.",
                input_schema: json!({
                    "type": "object",
                    "properties": {
                        "topic": { "type": "string", "description": "The document ID (e.g. 'cards/datacard', 'setup/overview')" }
                    },
                    "required": ["topic"]
                }),
            },
            ToolDef {
                name: "list_examples",
                description: "List all available OpsML Python code examples.",
                input_schema: json!({ "type": "object", "properties": {}, "required": [] }),
            },
            ToolDef {
                name: "read_example",
                description: "Read the full content of an OpsML Python example by its ID.",
                input_schema: json!({
                    "type": "object",
                    "properties": {
                        "name": { "type": "string", "description": "The example ID (e.g. 'example/data/numpy', 'example/experiment/basic', 'example/getting_started')" }
                    },
                    "required": ["name"]
                }),
            },
            ToolDef {
                name: "search_docs",
                description: "Search across all OpsML documentation and examples for a query string.",
                input_schema: json!({
                    "type": "object",
                    "properties": {
                        "query": { "type": "string", "description": "Case-insensitive search term" }
                    },
                    "required": ["query"]
                }),
            },
        ];

        #[cfg(feature = "server")]
        tools.extend([
            ToolDef {
                name: "list_cards",
                description: "List cards from the live OpsML registry, optionally filtered by space, name, tags, or recency.",
                input_schema: json!({
                    "type": "object",
                    "properties": {
                        "registry_type": { "type": "string", "description": "Registry type: model, data, experiment, prompt, or service" },
                        "space": { "type": "string", "description": "Filter by space name" },
                        "name": { "type": "string", "description": "Filter by card name" },
                        "tags": { "type": "array", "items": { "type": "string" }, "description": "Filter by tags" },
                        "limit": { "type": "integer", "description": "Maximum number of results (default 20)" },
                        "sort_by_timestamp": { "type": "boolean", "description": "Sort by creation time descending (default true)" }
                    },
                    "required": ["registry_type"]
                }),
            },
            ToolDef {
                name: "list_spaces",
                description: "List all unique space names for a given registry type.",
                input_schema: json!({
                    "type": "object",
                    "properties": {
                        "registry_type": { "type": "string", "description": "Registry type: model, data, experiment, prompt, or service" }
                    },
                    "required": ["registry_type"]
                }),
            },
            ToolDef {
                name: "search_cards",
                description: "Search cards by name across a registry type.",
                input_schema: json!({
                    "type": "object",
                    "properties": {
                        "registry_type": { "type": "string", "description": "Registry type: model, data, experiment, prompt, or service" },
                        "name": { "type": "string", "description": "Search term matched against card name" },
                        "limit": { "type": "integer", "description": "Maximum number of results (default 20)" }
                    },
                    "required": ["registry_type", "name"]
                }),
            },
            ToolDef {
                name: "service_tools",
                description: "Generate callable tool definitions from a deployed OpsML service. \
                    Works with any service type: Agent (generates one tool per skill), \
                    MCP (generates server connection tool), Workflow (generates trigger tool). \
                    Returns tool specs with full API call configuration.",
                input_schema: json!({
                    "type": "object",
                    "properties": {
                        "space": { "type": "string", "description": "The service's space name" },
                        "name": { "type": "string", "description": "The service name" }
                    },
                    "required": ["space", "name"]
                }),
            },
        ]);

        JsonRpcResponse::ok(id, ToolsListResult { tools })
    }

    async fn dispatch_tool(
        &self,
        id: Option<Value>,
        call: ToolCall,
        #[cfg(feature = "server")] perms: UserPermissions,
    ) -> JsonRpcResponse {
        match call {
            ToolCall::ListDocs => self.tool_list_docs(id),
            ToolCall::ReadDoc(args) => self.tool_read_doc(id, args),
            ToolCall::ListExamples => self.tool_list_examples(id),
            ToolCall::ReadExample(args) => self.tool_read_example(id, args),
            ToolCall::SearchDocs(args) => self.tool_search_docs(id, args),
            #[cfg(feature = "server")]
            ToolCall::ListCards(args) => self.tool_list_cards(id, args, perms).await,
            #[cfg(feature = "server")]
            ToolCall::ListSpaces(args) => self.tool_list_spaces(id, args, perms).await,
            #[cfg(feature = "server")]
            ToolCall::SearchCards(args) => self.tool_search_cards(id, args, perms).await,
            #[cfg(feature = "server")]
            ToolCall::ServiceTools(args) => self.tool_service_tools(id, args, perms).await,
            ToolCall::Unknown(name) => {
                JsonRpcResponse::err(id, -32602, format!("Unknown tool: {name}"))
            }
            ToolCall::InvalidArgs { name, reason } => JsonRpcResponse::err(
                id,
                -32602,
                format!("Invalid arguments for '{name}': {reason}"),
            ),
        }
    }

    fn tool_list_docs(&self, id: Option<Value>) -> JsonRpcResponse {
        let docs: Vec<DocSummary> = DOCS
            .iter()
            .filter(|e| e.category != "example")
            .map(|e| DocSummary {
                id: e.id,
                title: e.title,
                category: e.category,
            })
            .collect();
        let text = serde_json::to_string_pretty(&docs).unwrap_or_default();
        JsonRpcResponse::ok(
            id,
            ToolCallResult {
                content: vec![TextContent::text(text)],
            },
        )
    }

    fn tool_read_doc(
        &self,
        id: Option<Value>,
        ReadDocArgs { topic }: ReadDocArgs,
    ) -> JsonRpcResponse {
        match DOCS.iter().find(|e| e.id == topic) {
            Some(entry) => JsonRpcResponse::ok(
                id,
                ToolCallResult {
                    content: vec![TextContent::text(entry.content)],
                },
            ),
            None => JsonRpcResponse::err(id, -32602, format!("Document not found: {topic}")),
        }
    }

    fn tool_list_examples(&self, id: Option<Value>) -> JsonRpcResponse {
        let examples: Vec<ExampleSummary> = DOCS
            .iter()
            .filter(|e| e.category == "example")
            .map(|e| ExampleSummary {
                id: e.id,
                title: e.title,
            })
            .collect();
        let text = serde_json::to_string_pretty(&examples).unwrap_or_default();
        JsonRpcResponse::ok(
            id,
            ToolCallResult {
                content: vec![TextContent::text(text)],
            },
        )
    }

    fn tool_read_example(
        &self,
        id: Option<Value>,
        ReadExampleArgs { name }: ReadExampleArgs,
    ) -> JsonRpcResponse {
        match DOCS
            .iter()
            .find(|e| e.id == name && e.category == "example")
        {
            Some(entry) => JsonRpcResponse::ok(
                id,
                ToolCallResult {
                    content: vec![TextContent::text(entry.content)],
                },
            ),
            None => JsonRpcResponse::err(id, -32602, format!("Example not found: {name}")),
        }
    }

    fn tool_search_docs(
        &self,
        id: Option<Value>,
        SearchDocsArgs { query }: SearchDocsArgs,
    ) -> JsonRpcResponse {
        let query_lower = query.to_lowercase();
        let mut results: Vec<SearchResult> = Vec::new();

        for entry in DOCS {
            let content_lower = entry.content.to_lowercase();
            if let Some(pos) = content_lower.find(&query_lower) {
                let raw_start = pos.saturating_sub(100);
                let raw_end = (pos + query_lower.len() + 100).min(entry.content.len());
                let start = (0..=raw_start)
                    .rev()
                    .find(|&i| entry.content.is_char_boundary(i))
                    .unwrap_or(0);
                let end = (raw_end..=entry.content.len())
                    .find(|&i| entry.content.is_char_boundary(i))
                    .unwrap_or(entry.content.len());
                results.push(SearchResult {
                    id: entry.id,
                    title: entry.title,
                    category: entry.category,
                    snippet: entry.content[start..end].to_string(),
                });
            }
        }

        let text = if results.is_empty() {
            format!("No results found for '{query}'")
        } else {
            serde_json::to_string_pretty(&results).unwrap_or_default()
        };

        JsonRpcResponse::ok(
            id,
            ToolCallResult {
                content: vec![TextContent::text(text)],
            },
        )
    }

    // ---- Registry tools ----

    #[cfg(feature = "server")]
    async fn tool_list_cards(
        &self,
        id: Option<Value>,
        args: CardQueryArgs,
        _perms: UserPermissions,
    ) -> JsonRpcResponse {
        let sql = match self.sql.as_ref() {
            Some(s) => s,
            None => return JsonRpcResponse::err(id, -32603, "No database connection available"),
        };
        let table = CardTable::from_registry_type(&args.registry_type);
        match sql.query_cards(&table, &args).await {
            Ok(results) => {
                let text = serde_json::to_string_pretty(&results).unwrap_or_default();
                JsonRpcResponse::ok(
                    id,
                    ToolCallResult {
                        content: vec![TextContent::text(text)],
                    },
                )
            }
            Err(e) => JsonRpcResponse::err(id, -32603, format!("Query failed: {e}")),
        }
    }

    #[cfg(feature = "server")]
    async fn tool_list_spaces(
        &self,
        id: Option<Value>,
        args: RegistrySpaceRequest,
        _perms: UserPermissions,
    ) -> JsonRpcResponse {
        let sql = match self.sql.as_ref() {
            Some(s) => s,
            None => return JsonRpcResponse::err(id, -32603, "No database connection available"),
        };
        let table = CardTable::from_registry_type(&args.registry_type);
        match sql.get_unique_space_names(&table).await {
            Ok(spaces) => {
                let text = serde_json::to_string_pretty(&spaces).unwrap_or_default();
                JsonRpcResponse::ok(
                    id,
                    ToolCallResult {
                        content: vec![TextContent::text(text)],
                    },
                )
            }
            Err(e) => JsonRpcResponse::err(id, -32603, format!("Query failed: {e}")),
        }
    }

    #[cfg(feature = "server")]
    async fn tool_search_cards(
        &self,
        id: Option<Value>,
        args: CardQueryArgs,
        _perms: UserPermissions,
    ) -> JsonRpcResponse {
        let sql = match self.sql.as_ref() {
            Some(s) => s,
            None => return JsonRpcResponse::err(id, -32603, "No database connection available"),
        };
        let table = CardTable::from_registry_type(&args.registry_type);
        match sql.query_cards(&table, &args).await {
            Ok(results) => {
                let text = serde_json::to_string_pretty(&results).unwrap_or_default();
                JsonRpcResponse::ok(
                    id,
                    ToolCallResult {
                        content: vec![TextContent::text(text)],
                    },
                )
            }
            Err(e) => JsonRpcResponse::err(id, -32603, format!("Query failed: {e}")),
        }
    }

    #[cfg(feature = "server")]
    async fn tool_service_tools(
        &self,
        id: Option<Value>,
        args: ServiceToolsArgs,
        _perms: UserPermissions,
    ) -> JsonRpcResponse {
        use opsml_types::contracts::service::AgentConfig;
        use opsml_types::contracts::service_tool::tools_from_service;

        let sql = match self.sql.as_ref() {
            Some(s) => s,
            None => return JsonRpcResponse::err(id, -32603, "No database connection available"),
        };

        // Query the service card
        let query_args = CardQueryArgs {
            space: Some(args.space.clone()),
            name: Some(args.name.clone()),
            sort_by_timestamp: Some(true),
            limit: Some(1),
            ..Default::default()
        };

        let results = match sql.query_cards(&CardTable::Service, &query_args).await {
            Ok(r) => r,
            Err(e) => {
                return JsonRpcResponse::err(
                    id,
                    -32603,
                    format!("Failed to query service {}/{}: {e}", args.space, args.name),
                );
            }
        };

        let records = match results {
            opsml_sql::schemas::CardResults::Service(recs) => recs,
            _ => {
                return JsonRpcResponse::err(id, -32603, "Unexpected result type");
            }
        };

        let record = match records.into_iter().next() {
            Some(r) => r,
            None => {
                return JsonRpcResponse::err(
                    id,
                    -32602,
                    format!("Service {}/{} not found", args.space, args.name),
                );
            }
        };

        let deploy = record
            .deployment
            .as_ref()
            .map(|d| d.0.as_slice())
            .unwrap_or(&[]);

        let service_type =
            opsml_types::contracts::ServiceType::from(record.service_type.as_str());

        let agent_spec = record
            .service_config
            .as_ref()
            .and_then(|c| c.0.agent.as_ref())
            .and_then(|a| match a {
                AgentConfig::Spec(spec) => Some(spec.as_ref()),
                AgentConfig::Path(_) => None,
            });

        let mcp_config = record
            .service_config
            .as_ref()
            .and_then(|c| c.0.mcp.as_ref());

        let workflow = record
            .service_config
            .as_ref()
            .and_then(|c| c.0.workflow.as_ref());

        let tools = tools_from_service(
            &args.name,
            &service_type,
            deploy,
            agent_spec,
            mcp_config,
            workflow,
            None,
        );

        let text = serde_json::to_string_pretty(&tools).unwrap_or_default();
        JsonRpcResponse::ok(
            id,
            ToolCallResult {
                content: vec![TextContent::text(text)],
            },
        )
    }
}
