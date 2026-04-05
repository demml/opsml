use super::error::SubAgentError;
use opsml_types::contracts::subagent::SubAgentSpec;
use serde::Serialize;
use std::path::PathBuf;

pub trait SubAgentCliTarget {
    fn serialize(&self, spec: &SubAgentSpec) -> Result<String, SubAgentError>;
    fn file_name(&self, name: &str) -> String;
    fn agent_dir(&self, global: bool) -> PathBuf;
}

// ─── Claude Code ─────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct ClaudeCodeFrontmatter {
    name: String,
    description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    model: Option<String>,
    #[serde(skip_serializing_if = "Vec::is_empty", default)]
    tools: Vec<String>,
    #[serde(skip_serializing_if = "Vec::is_empty", default)]
    disallowed_tools: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    max_turns: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    permission_mode: Option<String>,
}

pub struct ClaudeCodeTarget;

impl SubAgentCliTarget for ClaudeCodeTarget {
    fn serialize(&self, spec: &SubAgentSpec) -> Result<String, SubAgentError> {
        let permission_mode = spec.permission_mode.as_ref().and_then(|m| {
            serde_json::to_value(m)
                .ok()
                .and_then(|v| v.as_str().map(str::to_string))
        });

        let fm = ClaudeCodeFrontmatter {
            name: spec.name.clone(),
            description: spec.description.clone(),
            model: spec.model.clone(),
            tools: spec.tools.clone(),
            disallowed_tools: spec.disallowed_tools.clone(),
            max_turns: spec.max_turns,
            permission_mode,
        };

        let yaml = serde_yaml::to_string(&fm)?;
        let yaml = yaml.trim_start_matches("---\n");
        let body = spec.system_prompt.as_deref().unwrap_or("");

        Ok(format!("---\n{yaml}---\n{body}"))
    }

    fn file_name(&self, name: &str) -> String {
        format!("{name}.md")
    }

    fn agent_dir(&self, global: bool) -> PathBuf {
        if global {
            dirs::home_dir()
                .unwrap_or_else(|| PathBuf::from("."))
                .join(".claude")
                .join("agents")
        } else {
            PathBuf::from(".claude").join("agents")
        }
    }
}

// ─── Gemini CLI ───────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize)]
struct GeminiFrontmatter {
    name: String,
    description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    model: Option<String>,
    #[serde(skip_serializing_if = "Vec::is_empty", default)]
    tools: Vec<String>,
    #[serde(skip_serializing_if = "Vec::is_empty", default)]
    compatible_clis: Vec<String>,
}

pub struct GeminiCliTarget;

impl SubAgentCliTarget for GeminiCliTarget {
    fn serialize(&self, spec: &SubAgentSpec) -> Result<String, SubAgentError> {
        let compatible_clis = spec.compatible_clis.iter().map(|c| c.to_string()).collect();

        let fm = GeminiFrontmatter {
            name: spec.name.clone(),
            description: spec.description.clone(),
            model: spec.model.clone(),
            tools: spec.tools.clone(),
            compatible_clis,
        };

        let yaml = serde_yaml::to_string(&fm)?;
        let yaml = yaml.trim_start_matches("---\n");
        let body = spec.system_prompt.as_deref().unwrap_or("");

        Ok(format!("---\n{yaml}---\n{body}"))
    }

    fn file_name(&self, name: &str) -> String {
        format!("{name}.md")
    }

    fn agent_dir(&self, global: bool) -> PathBuf {
        if global {
            dirs::home_dir()
                .unwrap_or_else(|| PathBuf::from("."))
                .join(".gemini")
                .join("agents")
        } else {
            PathBuf::from(".gemini").join("agents")
        }
    }
}

// ─── Codex ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize)]
struct CodexConfig {
    name: String,
    description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    model: Option<String>,
    #[serde(skip_serializing_if = "Vec::is_empty", default)]
    tools: Vec<String>,
    mcp_servers: Vec<String>,
    developer_instructions: String,
}

pub struct CodexTarget;

impl SubAgentCliTarget for CodexTarget {
    fn serialize(&self, spec: &SubAgentSpec) -> Result<String, SubAgentError> {
        let config = CodexConfig {
            name: spec.name.clone(),
            description: spec.description.clone(),
            model: spec.model.clone(),
            tools: spec.tools.clone(),
            mcp_servers: vec![],
            developer_instructions: spec.system_prompt.clone().unwrap_or_default(),
        };

        Ok(toml::to_string_pretty(&config)?)
    }

    fn file_name(&self, name: &str) -> String {
        format!("{name}.toml")
    }

    fn agent_dir(&self, global: bool) -> PathBuf {
        if global {
            dirs::home_dir()
                .unwrap_or_else(|| PathBuf::from("."))
                .join(".codex")
                .join("agents")
        } else {
            PathBuf::from(".codex").join("agents")
        }
    }
}

// ─── GitHub Copilot ──────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize)]
struct CopilotFrontmatter {
    name: String,
}

pub struct CopilotTarget;

impl SubAgentCliTarget for CopilotTarget {
    fn serialize(&self, spec: &SubAgentSpec) -> Result<String, SubAgentError> {
        let fm = CopilotFrontmatter {
            name: spec.name.clone(),
        };

        let yaml = serde_yaml::to_string(&fm)?;
        let yaml = yaml.trim_start_matches("---\n");
        let body = spec.system_prompt.as_deref().unwrap_or("");

        Ok(format!("---\n{yaml}---\n{body}"))
    }

    fn file_name(&self, name: &str) -> String {
        format!("{name}.agent.md")
    }

    fn agent_dir(&self, global: bool) -> PathBuf {
        if global {
            dirs::home_dir()
                .unwrap_or_else(|| PathBuf::from("."))
                .join(".github")
                .join("agents")
        } else {
            PathBuf::from(".github").join("agents")
        }
    }
}
