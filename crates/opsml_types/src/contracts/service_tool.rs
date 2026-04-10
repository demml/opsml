/// Service-to-Tool conversion.
///
/// Reads existing metadata on a `ServiceCard` — deployment URLs, agent skills,
/// MCP config, workflow steps — and produces `Vec<ToolSpec>` that can be
/// registered as `ToolCard`s, served via the MCP handler, or installed into
/// agent CLI frameworks.
///
/// **No new config types** are introduced. Everything is derived from data
/// that already lives on the card.
use crate::contracts::agent::{AgentSpec, SkillFormat};
use crate::contracts::mcp::{McpConfig, McpTransport};
use crate::contracts::service::{DeploymentConfig, ServiceType};
use crate::contracts::tool::{ApiCallConfig, ToolSpec, ToolType};
use crate::contracts::workflow::WorkflowSpec;
use serde_json::{Value, json};
use std::collections::HashMap;

/// An intermediate representation of a callable endpoint derived from service
/// metadata. Not persisted — exists only during the conversion pipeline.
#[derive(Debug, Clone)]
pub struct ServiceEndpoint {
    /// Relative path appended to the base URL (e.g. "/v1/predict")
    pub path: String,
    /// HTTP method
    pub method: String,
    /// Human-readable description
    pub description: String,
    /// JSON Schema for the request body
    pub args_schema: Option<Value>,
    /// JSON Schema for the response body
    pub output_schema: Option<Value>,
    /// Content type (defaults to "application/json")
    pub content_type: Option<String>,
    /// Machine-friendly identifier (from OpenAPI operationId or skill name)
    pub operation_id: Option<String>,
}

// ── Public entry point ──────────────────────────────────────────────────────

/// Generate `ToolSpec`s from the metadata already present on a service card.
///
/// The caller provides the fields that live on `ServiceCard` / `ServiceConfig`;
/// this function inspects the `service_type` and whichever config is present to
/// produce tools. No external fetching happens here — for OpenAPI discovery,
/// pass the pre-fetched document as `openapi_doc`.
pub fn tools_from_service(
    service_name: &str,
    service_type: &ServiceType,
    deploy: &[DeploymentConfig],
    agent_spec: Option<&AgentSpec>,
    mcp_config: Option<&McpConfig>,
    workflow: Option<&WorkflowSpec>,
    openapi_doc: Option<&Value>,
) -> Vec<ToolSpec> {
    let base_url = resolve_base_url(deploy);

    // If an OpenAPI doc was provided, prefer it regardless of service type.
    if let Some(doc) = openapi_doc {
        let eps = endpoints_from_openapi(doc, &[], &[]);
        if !eps.is_empty() {
            return endpoints_to_tools(service_name, &base_url, &eps);
        }
    }

    // Otherwise, derive from the service type and its existing config.
    match service_type {
        ServiceType::Agent => {
            let eps = endpoints_from_agent(agent_spec);
            endpoints_to_tools(service_name, &base_url, &eps)
        }
        ServiceType::Mcp => {
            endpoints_from_mcp_to_tools(service_name, &base_url, deploy, mcp_config)
        }
        ServiceType::Workflow => {
            let eps = endpoints_from_workflow(workflow);
            endpoints_to_tools(service_name, &base_url, &eps)
        }
        ServiceType::Api => {
            // API services without an OpenAPI doc produce no tools automatically.
            // The user should point us at an OpenAPI spec via the openapi_doc param.
            vec![]
        }
    }
}

// ── Base URL resolution ─────────────────────────────────────────────────────

/// Pick the best base URL from the available deployment configs.
/// Prefers "production", then falls back to the first available URL.
fn resolve_base_url(deploy: &[DeploymentConfig]) -> String {
    deploy
        .iter()
        .find(|d| d.environment == "production")
        .or(deploy.first())
        .and_then(|d| d.urls.first())
        .cloned()
        .unwrap_or_default()
}

/// Pick the best base URL for a specific environment.
fn resolve_base_url_for_env(deploy: &[DeploymentConfig], environment: &str) -> String {
    deploy
        .iter()
        .find(|d| d.environment == environment)
        .and_then(|d| d.urls.first())
        .cloned()
        .unwrap_or_else(|| resolve_base_url(deploy))
}

// ── Endpoint → ToolSpec conversion ──────────────────────────────────────────

fn endpoints_to_tools(
    service_name: &str,
    base_url: &str,
    endpoints: &[ServiceEndpoint],
) -> Vec<ToolSpec> {
    endpoints
        .iter()
        .map(|ep| {
            let slug = ep.operation_id.clone().unwrap_or_else(|| {
                ep.path
                    .trim_matches('/')
                    .replace('/', "-")
            });
            let tool_name = if slug.is_empty() {
                service_name.to_string()
            } else {
                format!("{service_name}-{slug}")
            };

            let mut headers = HashMap::new();
            headers.insert(
                "Content-Type".to_string(),
                ep.content_type
                    .clone()
                    .unwrap_or_else(|| "application/json".to_string()),
            );

            ToolSpec {
                name: tool_name,
                description: ep.description.clone(),
                tool_type: ToolType::ApiCall,
                args_schema: ep.args_schema.clone(),
                output_schema: ep.output_schema.clone(),
                api_config: Some(ApiCallConfig {
                    url: format!("{base_url}{}", ep.path),
                    method: ep.method.clone(),
                    headers,
                    body_template: None,
                }),
                requires_approval: true,
                ..Default::default()
            }
        })
        .collect()
}

// ── Agent → endpoints ───────────────────────────────────────────────────────

/// Derive endpoints from A2A agent skills. Each skill becomes a POST endpoint
/// to the agent's invoke URL.
fn endpoints_from_agent(agent: Option<&AgentSpec>) -> Vec<ServiceEndpoint> {
    let Some(agent) = agent else {
        return vec![];
    };

    agent
        .skills
        .iter()
        .map(|skill| {
            let (skill_name, skill_desc) = match skill {
                SkillFormat::A2A(s) => (s.name.clone(), s.description.clone()),
                SkillFormat::Standard(s) => (s.name.clone(), s.description.clone()),
            };

            ServiceEndpoint {
                path: "/v1/agent/invoke".to_string(),
                method: "POST".to_string(),
                description: skill_desc,
                args_schema: Some(json!({
                    "type": "object",
                    "properties": {
                        "skill": {
                            "type": "string",
                            "const": skill_name,
                            "description": "The skill to invoke on the agent"
                        },
                        "message": {
                            "type": "string",
                            "description": "Input message for the agent skill"
                        }
                    },
                    "required": ["skill", "message"]
                })),
                output_schema: None,
                content_type: Some("application/json".to_string()),
                operation_id: Some(skill_name),
            }
        })
        .collect()
}

// ── MCP → tools (special case: produces ToolType::McpServer) ────────────────

/// MCP services are already tool servers. Rather than creating ApiCall tools,
/// we produce a single `McpServer`-typed tool that points at the service URL.
/// The MCP client (Claude Code, etc.) connects to it natively.
fn endpoints_from_mcp_to_tools(
    service_name: &str,
    base_url: &str,
    deploy: &[DeploymentConfig],
    mcp: Option<&McpConfig>,
) -> Vec<ToolSpec> {
    let Some(mcp) = mcp else {
        return vec![];
    };

    // Collect all URLs from all deployment configs for this MCP service
    let urls: Vec<String> = deploy
        .iter()
        .flat_map(|d| d.urls.iter().cloned())
        .collect();

    let url = urls.first().cloned().unwrap_or_else(|| base_url.to_string());

    let transport_desc = match mcp.transport {
        McpTransport::Http => "HTTP",
        McpTransport::Stdio => "stdio",
    };

    vec![ToolSpec {
        name: format!("{service_name}-mcp"),
        description: format!(
            "MCP server for {service_name} ({transport_desc} transport)"
        ),
        tool_type: ToolType::McpServer,
        mcp_server_name: Some(service_name.to_string()),
        api_config: Some(ApiCallConfig {
            url,
            method: "POST".to_string(),
            headers: HashMap::new(),
            body_template: None,
        }),
        requires_approval: false,
        ..Default::default()
    }]
}

// ── Workflow → endpoints ────────────────────────────────────────────────────

/// Derive endpoints from workflow steps. Each named step becomes a triggerable
/// endpoint, plus one "run" endpoint for the whole workflow.
fn endpoints_from_workflow(workflow: Option<&WorkflowSpec>) -> Vec<ServiceEndpoint> {
    let Some(wf) = workflow else {
        return vec![];
    };

    let mut endpoints = Vec::with_capacity(wf.steps.len() + 1);

    // Build the args_schema from the workflow's declared inputs.
    let workflow_args = if wf.inputs.is_empty() {
        None
    } else {
        let mut properties = serde_json::Map::new();
        let mut required = Vec::new();
        for (key, input) in &wf.inputs {
            let mut prop = serde_json::Map::new();
            prop.insert("type".to_string(), json!(&input.input_type));
            if let Some(desc) = &input.description {
                prop.insert("description".to_string(), json!(desc));
            }
            if let Some(default) = &input.default {
                prop.insert("default".to_string(), default.clone());
            }
            properties.insert(key.clone(), Value::Object(prop));
            if input.required {
                required.push(json!(key));
            }
        }
        Some(json!({
            "type": "object",
            "properties": properties,
            "required": required
        }))
    };

    // Top-level "run the entire workflow" endpoint.
    endpoints.push(ServiceEndpoint {
        path: "/v1/workflow/run".to_string(),
        method: "POST".to_string(),
        description: "Trigger the entire workflow".to_string(),
        args_schema: workflow_args,
        output_schema: None,
        content_type: Some("application/json".to_string()),
        operation_id: Some("run".to_string()),
    });

    endpoints
}

// ── OpenAPI → endpoints ─────────────────────────────────────────────────────

/// Parse an OpenAPI 3.x JSON document into `ServiceEndpoint`s.
///
/// Handles:
/// - `paths` → methods → requestBody schema + response schema
/// - `operationId` for stable tool naming
/// - `summary` / `description` for tool descriptions
/// - Include/exclude filters on operationId
///
/// Does NOT resolve `$ref` pointers — expects an already-bundled spec (most
/// real-world `/openapi.json` endpoints serve bundled specs). A `$ref` resolver
/// can be added later without changing this function's signature.
pub fn endpoints_from_openapi(
    doc: &Value,
    include_operations: &[String],
    exclude_operations: &[String],
) -> Vec<ServiceEndpoint> {
    let paths = match doc.get("paths").and_then(|p| p.as_object()) {
        Some(p) => p,
        None => return vec![],
    };

    let methods = ["get", "post", "put", "patch", "delete"];
    let mut endpoints = Vec::new();

    for (path, path_item) in paths {
        let Some(path_obj) = path_item.as_object() else {
            continue;
        };

        for method in &methods {
            let Some(operation) = path_obj.get(*method) else {
                continue;
            };

            let op_id = operation
                .get("operationId")
                .and_then(Value::as_str)
                .map(String::from);

            // Apply include/exclude filters
            if let Some(ref id) = op_id {
                if !include_operations.is_empty() && !include_operations.contains(id) {
                    continue;
                }
                if exclude_operations.contains(id) {
                    continue;
                }
            }

            let description = operation
                .get("summary")
                .or_else(|| operation.get("description"))
                .and_then(Value::as_str)
                .unwrap_or("No description")
                .to_string();

            // Extract request body JSON schema
            let args_schema = operation
                .get("requestBody")
                .and_then(|rb| rb.get("content"))
                .and_then(|c| c.get("application/json"))
                .and_then(|j| j.get("schema"))
                .cloned();

            // Extract 200/201 response schema
            let output_schema = operation
                .get("responses")
                .and_then(|r| r.get("200").or_else(|| r.get("201")))
                .and_then(|r| r.get("content"))
                .and_then(|c| c.get("application/json"))
                .and_then(|j| j.get("schema"))
                .cloned();

            endpoints.push(ServiceEndpoint {
                path: path.clone(),
                method: method.to_uppercase(),
                description,
                args_schema,
                output_schema,
                content_type: Some("application/json".to_string()),
                operation_id: op_id,
            });
        }
    }

    endpoints
}

// ── Helpers ─────────────────────────────────────────────────────────────────

/// Given a list of deployment configs, return the base URL for the requested
/// environment, falling back to the default resolution order.
pub fn base_url_for_environment(deploy: &[DeploymentConfig], env: &str) -> String {
    resolve_base_url_for_env(deploy, env)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contracts::agent::{
        AgentCapabilities, AgentInterface, AgentSkill, AgentSkillStandard, ProtocolBinding,
    };
    use crate::contracts::mcp::McpCapability;
    use crate::contracts::workflow::{WorkflowInput, WorkflowStep, CardRef};

    fn make_deploy(env: &str, url: &str) -> DeploymentConfig {
        DeploymentConfig {
            environment: env.to_string(),
            provider: None,
            location: None,
            urls: vec![url.to_string()],
            resources: None,
            links: None,
            healthcheck: None,
        }
    }

    fn make_agent_spec(skills: Vec<SkillFormat>) -> AgentSpec {
        AgentSpec {
            name: "test-agent".to_string(),
            description: "A test agent".to_string(),
            version: "1.0.0".to_string(),
            skills,
            capabilities: AgentCapabilities::default(),
            default_input_modes: vec!["text".into()],
            default_output_modes: vec!["text".into()],
            supported_interfaces: vec![AgentInterface::new_rs(
                "https://agent.example.com".to_string(),
                ProtocolBinding::HttpJson,
                "0.3.0".to_string(),
                None,
            )],
            provider: None,
            documentation_url: None,
            icon_url: None,
            security_requirements: None,
            security_schemes: None,
            signatures: None,
        }
    }

    // ── resolve_base_url ────────────────────────────────────────────────

    #[test]
    fn test_resolve_base_url_prefers_production() {
        let deploy = vec![
            make_deploy("staging", "https://staging.example.com"),
            make_deploy("production", "https://prod.example.com"),
        ];
        assert_eq!(resolve_base_url(&deploy), "https://prod.example.com");
    }

    #[test]
    fn test_resolve_base_url_falls_back_to_first() {
        let deploy = vec![make_deploy("dev", "https://dev.example.com")];
        assert_eq!(resolve_base_url(&deploy), "https://dev.example.com");
    }

    #[test]
    fn test_resolve_base_url_empty() {
        let deploy: Vec<DeploymentConfig> = vec![];
        assert_eq!(resolve_base_url(&deploy), "");
    }

    // ── Agent → tools ───────────────────────────────────────────────────

    #[test]
    fn test_tools_from_agent_service() {
        let skills = vec![
            SkillFormat::A2A(AgentSkill {
                id: "search".to_string(),
                name: "web-search".to_string(),
                description: "Search the web".to_string(),
                tags: vec![],
                examples: vec![],
                input_modes: None,
                output_modes: None,
                security_requirements: None,
            }),
            SkillFormat::Standard(AgentSkillStandard {
                name: "summarize".to_string(),
                description: "Summarize text".to_string(),
                ..Default::default()
            }),
        ];
        let agent = make_agent_spec(skills);
        let deploy = vec![make_deploy("production", "https://agent.example.com")];

        let tools = tools_from_service(
            "research-agent",
            &ServiceType::Agent,
            &deploy,
            Some(&agent),
            None,
            None,
            None,
        );

        assert_eq!(tools.len(), 2);
        assert_eq!(tools[0].name, "research-agent-web-search");
        assert_eq!(tools[0].description, "Search the web");
        assert_eq!(tools[0].tool_type, ToolType::ApiCall);
        assert!(tools[0].api_config.is_some());
        let api = tools[0].api_config.as_ref().unwrap();
        assert_eq!(api.url, "https://agent.example.com/v1/agent/invoke");
        assert_eq!(api.method, "POST");

        assert_eq!(tools[1].name, "research-agent-summarize");
        assert_eq!(tools[1].description, "Summarize text");
    }

    #[test]
    fn test_tools_from_agent_no_spec() {
        let deploy = vec![make_deploy("production", "https://agent.example.com")];
        let tools = tools_from_service(
            "my-agent",
            &ServiceType::Agent,
            &deploy,
            None,
            None,
            None,
            None,
        );
        assert!(tools.is_empty());
    }

    // ── MCP → tools ────────────────────────────────────────────────────

    #[test]
    fn test_tools_from_mcp_service() {
        let mcp = McpConfig {
            capabilities: vec![McpCapability::Tools],
            transport: McpTransport::Http,
        };
        let deploy = vec![make_deploy("production", "https://mcp.example.com")];

        let tools = tools_from_service(
            "my-mcp",
            &ServiceType::Mcp,
            &deploy,
            None,
            Some(&mcp),
            None,
            None,
        );

        assert_eq!(tools.len(), 1);
        assert_eq!(tools[0].name, "my-mcp-mcp");
        assert_eq!(tools[0].tool_type, ToolType::McpServer);
        assert_eq!(tools[0].mcp_server_name, Some("my-mcp".to_string()));
        let api = tools[0].api_config.as_ref().unwrap();
        assert_eq!(api.url, "https://mcp.example.com");
    }

    #[test]
    fn test_tools_from_mcp_no_config() {
        let deploy = vec![make_deploy("production", "https://mcp.example.com")];
        let tools = tools_from_service(
            "my-mcp",
            &ServiceType::Mcp,
            &deploy,
            None,
            None,
            None,
            None,
        );
        assert!(tools.is_empty());
    }

    // ── Workflow → tools ────────────────────────────────────────────────

    #[test]
    fn test_tools_from_workflow_service() {
        let wf = WorkflowSpec {
            inputs: {
                let mut m = HashMap::new();
                m.insert(
                    "repo_url".into(),
                    WorkflowInput {
                        input_type: "string".into(),
                        required: true,
                        default: None,
                        description: Some("Repository URL".into()),
                    },
                );
                m
            },
            steps: vec![
                WorkflowStep {
                    name: "fetch".into(),
                    skill: Some(CardRef {
                        space: "platform".into(),
                        name: "git-clone".into(),
                        version: None,
                    }),
                    ..Default::default()
                },
                WorkflowStep {
                    name: "review".into(),
                    depends_on: vec!["fetch".into()],
                    agent: Some(CardRef {
                        space: "platform".into(),
                        name: "reviewer".into(),
                        version: None,
                    }),
                    ..Default::default()
                },
            ],
            outputs: HashMap::new(),
        };

        let deploy = vec![make_deploy("production", "https://wf.example.com")];
        let tools = tools_from_service(
            "code-review-wf",
            &ServiceType::Workflow,
            &deploy,
            None,
            None,
            Some(&wf),
            None,
        );

        // One "run" endpoint for the whole workflow
        assert_eq!(tools.len(), 1);
        assert_eq!(tools[0].name, "code-review-wf-run");
        assert!(tools[0].description.contains("workflow"));
        // Should have args_schema from workflow inputs
        let schema = tools[0].args_schema.as_ref().unwrap();
        assert!(schema.get("properties").unwrap().get("repo_url").is_some());
    }

    #[test]
    fn test_tools_from_workflow_no_inputs() {
        let wf = WorkflowSpec {
            inputs: HashMap::new(),
            steps: vec![WorkflowStep {
                name: "step1".into(),
                skill: Some(CardRef {
                    space: "p".into(),
                    name: "s".into(),
                    version: None,
                }),
                ..Default::default()
            }],
            outputs: HashMap::new(),
        };
        let deploy = vec![make_deploy("production", "https://wf.example.com")];
        let tools = tools_from_service(
            "simple-wf",
            &ServiceType::Workflow,
            &deploy,
            None,
            None,
            Some(&wf),
            None,
        );
        assert_eq!(tools.len(), 1);
        assert!(tools[0].args_schema.is_none());
    }

    // ── API (no OpenAPI doc) ────────────────────────────────────────────

    #[test]
    fn test_tools_from_api_without_openapi_is_empty() {
        let deploy = vec![make_deploy("production", "https://api.example.com")];
        let tools = tools_from_service(
            "my-api",
            &ServiceType::Api,
            &deploy,
            None,
            None,
            None,
            None,
        );
        assert!(tools.is_empty());
    }

    // ── OpenAPI → tools ─────────────────────────────────────────────────

    #[test]
    fn test_tools_from_openapi_doc() {
        let openapi = json!({
            "openapi": "3.0.0",
            "info": { "title": "Test API", "version": "1.0.0" },
            "paths": {
                "/v1/predict": {
                    "post": {
                        "operationId": "predict",
                        "summary": "Run a prediction",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "input": { "type": "string" }
                                        },
                                        "required": ["input"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "prediction": { "type": "number" }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/v1/health": {
                    "get": {
                        "operationId": "healthcheck",
                        "summary": "Health check"
                    }
                }
            }
        });

        let deploy = vec![make_deploy("production", "https://api.example.com")];
        let tools = tools_from_service(
            "ml-api",
            &ServiceType::Api,
            &deploy,
            None,
            None,
            None,
            Some(&openapi),
        );

        assert_eq!(tools.len(), 2);

        let predict_tool = tools.iter().find(|t| t.name == "ml-api-predict").unwrap();
        assert_eq!(predict_tool.description, "Run a prediction");
        assert!(predict_tool.args_schema.is_some());
        assert!(predict_tool.output_schema.is_some());
        let api = predict_tool.api_config.as_ref().unwrap();
        assert_eq!(api.url, "https://api.example.com/v1/predict");
        assert_eq!(api.method, "POST");

        let health_tool = tools.iter().find(|t| t.name == "ml-api-healthcheck").unwrap();
        assert_eq!(health_tool.description, "Health check");
        assert!(health_tool.args_schema.is_none());
        let api = health_tool.api_config.as_ref().unwrap();
        assert_eq!(api.method, "GET");
    }

    #[test]
    fn test_openapi_include_filter() {
        let openapi = json!({
            "paths": {
                "/a": { "post": { "operationId": "op_a", "summary": "A" } },
                "/b": { "post": { "operationId": "op_b", "summary": "B" } },
                "/c": { "get": { "operationId": "op_c", "summary": "C" } }
            }
        });

        let eps = endpoints_from_openapi(
            &openapi,
            &["op_a".to_string(), "op_c".to_string()],
            &[],
        );
        assert_eq!(eps.len(), 2);
        let ids: Vec<_> = eps.iter().filter_map(|e| e.operation_id.as_ref()).collect();
        assert!(ids.contains(&&"op_a".to_string()));
        assert!(ids.contains(&&"op_c".to_string()));
    }

    #[test]
    fn test_openapi_exclude_filter() {
        let openapi = json!({
            "paths": {
                "/a": { "post": { "operationId": "op_a", "summary": "A" } },
                "/b": { "post": { "operationId": "op_b", "summary": "B" } }
            }
        });

        let eps = endpoints_from_openapi(&openapi, &[], &["op_b".to_string()]);
        assert_eq!(eps.len(), 1);
        assert_eq!(eps[0].operation_id, Some("op_a".to_string()));
    }

    #[test]
    fn test_openapi_no_paths() {
        let openapi = json!({ "info": { "title": "empty" } });
        let eps = endpoints_from_openapi(&openapi, &[], &[]);
        assert!(eps.is_empty());
    }

    #[test]
    fn test_openapi_overrides_service_type() {
        // Even for an Agent service, if openapi_doc is provided, it takes precedence.
        let openapi = json!({
            "paths": {
                "/custom": { "post": { "operationId": "custom_op", "summary": "Custom" } }
            }
        });
        let deploy = vec![make_deploy("production", "https://example.com")];
        let tools = tools_from_service(
            "my-svc",
            &ServiceType::Agent,
            &deploy,
            None,
            None,
            None,
            Some(&openapi),
        );
        assert_eq!(tools.len(), 1);
        assert_eq!(tools[0].name, "my-svc-custom_op");
    }

    // ── Edge cases ──────────────────────────────────────────────────────

    #[test]
    fn test_tool_name_with_empty_slug() {
        let eps = vec![ServiceEndpoint {
            path: "/".to_string(),
            method: "GET".to_string(),
            description: "Root".to_string(),
            args_schema: None,
            output_schema: None,
            content_type: None,
            operation_id: None,
        }];
        let tools = endpoints_to_tools("svc", "https://example.com", &eps);
        assert_eq!(tools[0].name, "svc");
    }

    #[test]
    fn test_all_tools_have_requires_approval_true_for_api_calls() {
        let openapi = json!({
            "paths": {
                "/a": { "post": { "operationId": "a", "summary": "A" } },
                "/b": { "get": { "operationId": "b", "summary": "B" } }
            }
        });
        let deploy = vec![make_deploy("production", "https://example.com")];
        let tools = tools_from_service(
            "svc",
            &ServiceType::Api,
            &deploy,
            None,
            None,
            None,
            Some(&openapi),
        );
        for tool in &tools {
            assert!(tool.requires_approval, "tool '{}' should require approval", tool.name);
        }
    }

    #[test]
    fn test_mcp_tool_does_not_require_approval() {
        let mcp = McpConfig {
            capabilities: vec![McpCapability::Tools],
            transport: McpTransport::Http,
        };
        let deploy = vec![make_deploy("production", "https://mcp.example.com")];
        let tools = tools_from_service(
            "my-mcp",
            &ServiceType::Mcp,
            &deploy,
            None,
            Some(&mcp),
            None,
            None,
        );
        assert!(!tools[0].requires_approval);
    }

    #[test]
    fn test_base_url_for_environment() {
        let deploy = vec![
            make_deploy("staging", "https://staging.example.com"),
            make_deploy("production", "https://prod.example.com"),
        ];
        assert_eq!(
            base_url_for_environment(&deploy, "staging"),
            "https://staging.example.com"
        );
        assert_eq!(
            base_url_for_environment(&deploy, "production"),
            "https://prod.example.com"
        );
        // Falls back to production (or first) if env not found
        assert_eq!(
            base_url_for_environment(&deploy, "unknown"),
            "https://prod.example.com"
        );
    }
}
