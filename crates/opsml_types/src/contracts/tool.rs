use serde::{Deserialize, Deserializer, Serialize, Serializer};
use serde_json::Value;
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Default)]
pub enum ToolType {
    #[default]
    ShellScript,
    McpServer,
    ApiCall,
    InternalFunction,
    SlashCommand,
    Hook,
    Custom(String),
}

impl std::fmt::Display for ToolType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ToolType::ShellScript => write!(f, "ShellScript"),
            ToolType::McpServer => write!(f, "McpServer"),
            ToolType::ApiCall => write!(f, "ApiCall"),
            ToolType::InternalFunction => write!(f, "InternalFunction"),
            ToolType::SlashCommand => write!(f, "SlashCommand"),
            ToolType::Hook => write!(f, "Hook"),
            ToolType::Custom(s) => write!(f, "{s}"),
        }
    }
}

impl From<&str> for ToolType {
    fn from(s: &str) -> Self {
        match s {
            "ShellScript" => ToolType::ShellScript,
            "McpServer" => ToolType::McpServer,
            "ApiCall" => ToolType::ApiCall,
            "InternalFunction" => ToolType::InternalFunction,
            "SlashCommand" => ToolType::SlashCommand,
            "Hook" => ToolType::Hook,
            other => ToolType::Custom(other.to_string()),
        }
    }
}

impl Serialize for ToolType {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        s.serialize_str(&self.to_string())
    }
}

impl<'de> Deserialize<'de> for ToolType {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let s = String::deserialize(d)?;
        Ok(ToolType::from(s.as_str()))
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ShellScriptConfig {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub script: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub shell: Option<String>,
}

fn default_method() -> String {
    "GET".to_string()
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ApiCallConfig {
    pub url: String,
    #[serde(default = "default_method")]
    pub method: String,
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub headers: HashMap<String, String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub body_template: Option<String>,
}

impl Default for ApiCallConfig {
    fn default() -> Self {
        Self {
            url: String::new(),
            method: default_method(),
            headers: HashMap::new(),
            body_template: None,
        }
    }
}

impl ApiCallConfig {
    pub fn sanitize_for_response(&self) -> Self {
        const SENSITIVE_KEYS: &[&str] = &[
            "authorization",
            "x-api-key",
            "x-auth-token",
            "cookie",
            "x-secret",
            "proxy-authorization",
            "x-amz-security-token",
            "x-goog-api-key",
            "x-functions-key",
            "apikey",
            "token",
        ];
        let headers = self
            .headers
            .iter()
            .filter(|(k, _)| !SENSITIVE_KEYS.contains(&k.to_lowercase().as_str()))
            .map(|(k, v)| (k.clone(), v.clone()))
            .collect();
        // Strip query string — credential-bearing params must never be returned to callers.
        let url = self
            .url
            .split_once('?')
            .map(|(base, _)| base.to_string())
            .unwrap_or_else(|| self.url.clone());
        Self {
            url,
            method: self.method.clone(),
            headers,
            body_template: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Default)]
#[serde(rename_all = "PascalCase")]
pub enum HookEvent {
    #[default]
    PostToolUse,
    PreToolUse,
    Stop,
    Notification,
}

impl HookEvent {
    pub fn as_snake_case(&self) -> &'static str {
        match self {
            HookEvent::PreToolUse => "pre_tool_use",
            HookEvent::PostToolUse => "post_tool_use",
            HookEvent::Stop => "stop",
            HookEvent::Notification => "notification",
        }
    }

    pub fn as_pascal_case(&self) -> &'static str {
        match self {
            HookEvent::PreToolUse => "PreToolUse",
            HookEvent::PostToolUse => "PostToolUse",
            HookEvent::Stop => "Stop",
            HookEvent::Notification => "Notification",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct ToolSpec {
    pub name: String,
    pub description: String,
    pub tool_type: ToolType,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub args_schema: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub output_schema: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub script_config: Option<ShellScriptConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub api_config: Option<ApiCallConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mcp_server_name: Option<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub allowed_tools: Vec<String>,
    pub requires_approval: bool,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub hook_events: Vec<HookEvent>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub hook_matcher: Option<serde_json::Value>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tool_spec_roundtrip_json() {
        let spec = ToolSpec {
            name: "run-linter".to_string(),
            description: "Run the linter".to_string(),
            tool_type: ToolType::ShellScript,
            script_config: Some(ShellScriptConfig {
                script: Some("cargo clippy".to_string()),
                shell: Some("/bin/bash".to_string()),
            }),
            requires_approval: false,
            ..Default::default()
        };
        let json = serde_json::to_string(&spec).unwrap();
        assert!(
            json.contains("\"toolType\""),
            "expected camelCase 'toolType' key, got: {json}"
        );
        let restored: ToolSpec = serde_json::from_str(&json).unwrap();
        assert_eq!(restored.name, spec.name);
        assert_eq!(restored.tool_type, ToolType::ShellScript);
    }

    #[test]
    fn test_tool_type_all_variants_roundtrip() {
        let variants = [
            (ToolType::ShellScript, "\"ShellScript\""),
            (ToolType::McpServer, "\"McpServer\""),
            (ToolType::ApiCall, "\"ApiCall\""),
            (ToolType::InternalFunction, "\"InternalFunction\""),
            (ToolType::SlashCommand, "\"SlashCommand\""),
            (ToolType::Hook, "\"Hook\""),
        ];
        for (variant, expected_json) in variants {
            let json = serde_json::to_string(&variant).unwrap();
            assert_eq!(json, expected_json);
            let restored: ToolType = serde_json::from_str(&json).unwrap();
            assert_eq!(restored, variant);
        }
    }

    #[test]
    fn test_tool_type_slash_command_roundtrip() {
        let t = ToolType::SlashCommand;
        let json = serde_json::to_string(&t).unwrap();
        assert_eq!(json, "\"SlashCommand\"");
        let restored: ToolType = serde_json::from_str(&json).unwrap();
        assert_eq!(restored, ToolType::SlashCommand);
    }

    #[test]
    fn test_tool_type_custom_roundtrip() {
        let t = ToolType::Custom("my-tool".to_string());
        let json = serde_json::to_string(&t).unwrap();
        assert_eq!(json, "\"my-tool\"");
        let restored: ToolType = serde_json::from_str(&json).unwrap();
        assert_eq!(restored, ToolType::Custom("my-tool".to_string()));
    }

    #[test]
    fn test_default_api_method_is_get() {
        let config = ApiCallConfig {
            url: "https://example.com".to_string(),
            ..Default::default()
        };
        let json = serde_json::to_string(&config).unwrap();
        let restored: ApiCallConfig = serde_json::from_str(&json).unwrap();
        assert_eq!(restored.method, "GET");
    }

    #[test]
    fn test_hook_event_pascal_case() {
        let json = serde_json::to_string(&HookEvent::PreToolUse).unwrap();
        assert_eq!(json, "\"PreToolUse\"");
    }

    #[test]
    fn test_tool_spec_hook_roundtrip() {
        let spec = ToolSpec {
            name: "my-hook".to_string(),
            description: "A hook tool".to_string(),
            tool_type: ToolType::Hook,
            hook_events: vec![HookEvent::PostToolUse],
            hook_matcher: Some(serde_json::json!({"tool": "Write"})),
            ..Default::default()
        };
        let json = serde_json::to_string(&spec).unwrap();
        let restored: ToolSpec = serde_json::from_str(&json).unwrap();
        assert_eq!(restored.name, spec.name);
        assert_eq!(restored.tool_type, ToolType::Hook);
        assert_eq!(restored.hook_events, vec![HookEvent::PostToolUse]);
        assert_eq!(
            restored.hook_matcher,
            Some(serde_json::json!({"tool": "Write"}))
        );
    }

    #[test]
    fn test_hook_variant_does_not_break_existing_serde() {
        let shell: ToolType = serde_json::from_str("\"ShellScript\"").unwrap();
        assert_eq!(shell, ToolType::ShellScript);
        let slash: ToolType = serde_json::from_str("\"SlashCommand\"").unwrap();
        assert_eq!(slash, ToolType::SlashCommand);
    }
}
