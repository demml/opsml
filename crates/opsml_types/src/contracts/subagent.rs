use crate::contracts::CompatibleTool;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
#[serde(rename_all = "camelCase")]
pub enum SubAgentPermissionMode {
    #[default]
    Default,
    AcceptEdits,
    DontAsk,
    // Note: BypassPermissions is intentionally excluded — it disables all tool-use prompts on
    // the developer's machine and would be a supply chain attack vector if stored in the registry.
    Plan,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
#[serde(rename_all = "camelCase")]
pub enum MemoryScope {
    #[default]
    None,
    User,
    Project,
    Local,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
#[serde(rename_all = "camelCase")]
pub enum EffortLevel {
    #[default]
    Inherit,
    Low,
    Medium,
    High,
    Max,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(default, rename_all = "camelCase")]
pub struct SubAgentSpec {
    pub name: String,
    pub description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub system_prompt: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub model: Option<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub tools: Vec<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub disallowed_tools: Vec<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub skills: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_turns: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub permission_mode: Option<SubAgentPermissionMode>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub memory: Option<MemoryScope>,
    #[serde(default)]
    pub background: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub effort: Option<EffortLevel>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub isolation: Option<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub compatible_clis: Vec<CompatibleTool>,
    /// MCP server definitions keyed by server name.
    /// Used by Codex to populate the `[mcp_servers]` TOML table.
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub mcp_servers: HashMap<String, serde_json::Value>,
    /// Codex sandbox mode override. When None, Codex uses its own default.
    /// Valid values: "read-only", "workspace-write", "danger-full-access".
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sandbox_mode: Option<String>,
    /// Model sampling temperature (0.0–2.0). Used by Gemini CLI agent frontmatter.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub temperature: Option<f32>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_subagent_spec_roundtrip_json() {
        let spec = SubAgentSpec {
            name: "test-agent".to_string(),
            description: "A test agent".to_string(),
            system_prompt: Some("You are helpful.".to_string()),
            model: Some("sonnet".to_string()),
            tools: vec!["Read".to_string(), "Grep".to_string()],
            max_turns: Some(10),
            permission_mode: Some(SubAgentPermissionMode::Plan),
            compatible_clis: vec![CompatibleTool::ClaudeCode, CompatibleTool::Codex],
            ..Default::default()
        };

        let json = serde_json::to_string(&spec).unwrap();
        let roundtrip: SubAgentSpec = serde_json::from_str(&json).unwrap();

        assert_eq!(spec.name, roundtrip.name);
        assert_eq!(spec.description, roundtrip.description);
        assert_eq!(spec.system_prompt, roundtrip.system_prompt);
        assert_eq!(spec.model, roundtrip.model);
        assert_eq!(spec.tools, roundtrip.tools);
        assert_eq!(spec.max_turns, roundtrip.max_turns);
        assert_eq!(spec.compatible_clis, roundtrip.compatible_clis);
    }

    #[test]
    fn test_subagent_spec_defaults_empty() {
        let spec = SubAgentSpec::default();
        let json = serde_json::to_string(&spec).unwrap();
        let roundtrip: SubAgentSpec = serde_json::from_str(&json).unwrap();

        assert_eq!(roundtrip.name, "");
        assert_eq!(roundtrip.description, "");
        assert!(roundtrip.system_prompt.is_none());
        assert!(roundtrip.model.is_none());
        assert!(roundtrip.tools.is_empty());
        assert!(!roundtrip.background);
    }
}
