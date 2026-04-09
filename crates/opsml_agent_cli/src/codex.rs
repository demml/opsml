use crate::error::FrameworkError;
use crate::framework::AgentCliFramework;
use crate::utils::{merge_mcp_entry, read_json_or_default, validate_hook_args, write_json};
use opsml_types::contracts::subagent::{SubAgentPermissionMode, SubAgentSpec};
use opsml_types::contracts::tool::HookEvent;
use serde::Serialize;
use serde_json::Value;
use std::collections::HashMap;
use std::path::{Path, PathBuf};

// ── Paths ─────────────────────────────────────────────────────────────────────
//
// Local (project):  .codex/skills/{name}/SKILL.md
// Global (user):    ~/.codex/skills/{name}/SKILL.md
// Local agent:      .codex/agents/{name}.toml
// Global agent:     ~/.codex/agents/{name}.toml
// Local hooks:      .codex/hooks.json
// Global hooks:     ~/.codex/hooks.json
// MCP:              .mcp.json

#[derive(Debug, Clone, Serialize)]
struct CodexMcpEntry {
    command: String,
    #[serde(skip_serializing_if = "Vec::is_empty", default)]
    args: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    env: Option<HashMap<String, String>>,
}

#[derive(Debug, Clone, Serialize)]
struct CodexConfig {
    name: String,
    description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    model: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sandbox_mode: Option<String>,
    #[serde(skip_serializing_if = "HashMap::is_empty", default)]
    mcp_servers: HashMap<String, CodexMcpEntry>,
    developer_instructions: String,
}

fn parse_mcp_entry(v: &serde_json::Value) -> Option<CodexMcpEntry> {
    let command = v.get("command")?.as_str()?.to_string();
    let args = v
        .get("args")
        .and_then(|a| a.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|s| s.as_str().map(str::to_string))
                .collect()
        })
        .unwrap_or_default();
    let env = v.get("env").and_then(|e| e.as_object()).map(|obj| {
        obj.iter()
            .filter_map(|(k, v)| v.as_str().map(|s| (k.clone(), s.to_string())))
            .collect()
    });
    Some(CodexMcpEntry { command, args, env })
}

fn permission_mode_to_sandbox(mode: Option<&SubAgentPermissionMode>) -> Option<String> {
    match mode? {
        SubAgentPermissionMode::DontAsk => Some("danger-full-access".into()),
        SubAgentPermissionMode::Default
        | SubAgentPermissionMode::AcceptEdits
        | SubAgentPermissionMode::Plan => Some("workspace-write".into()),
    }
}

/// Maps a `HookEvent` to the Codex hook event name (PascalCase, same as Claude Code).
fn codex_event_name(event: &HookEvent) -> &'static str {
    match event {
        HookEvent::PreToolUse => "PreToolUse",
        HookEvent::PostToolUse => "PostToolUse",
        HookEvent::Stop => "Stop",
        HookEvent::Notification => "Notification",
        HookEvent::SessionStart => "SessionStart",
        HookEvent::UserPromptSubmit => "UserPromptSubmit",
    }
}

pub struct CodexFramework;

impl AgentCliFramework for CodexFramework {
    fn name(&self) -> &'static str {
        "codex"
    }

    fn skill_path(&self, name: &str) -> PathBuf {
        PathBuf::from(format!(".codex/skills/{name}/SKILL.md"))
    }

    fn global_skill_path(&self, name: &str) -> Result<PathBuf, FrameworkError> {
        let home = dirs::home_dir()
            .ok_or_else(|| FrameworkError::Error("Cannot determine home directory".into()))?;
        Ok(home.join(format!(".codex/skills/{name}/SKILL.md")))
    }

    fn agent_dir(&self, global: bool) -> Result<PathBuf, FrameworkError> {
        if global {
            Ok(dirs::home_dir()
                .ok_or(FrameworkError::NoHomeDir)?
                .join(".codex/agents"))
        } else {
            Ok(PathBuf::from(".codex/agents"))
        }
    }

    fn agent_file_name(&self, name: &str) -> String {
        format!("{name}.toml")
    }

    fn serialize_agent(&self, spec: &SubAgentSpec) -> Result<String, FrameworkError> {
        let mcp_servers = spec
            .mcp_servers
            .iter()
            .filter_map(|(k, v)| parse_mcp_entry(v).map(|e| (k.clone(), e)))
            .collect();

        let sandbox_mode = spec
            .sandbox_mode
            .clone()
            .or_else(|| permission_mode_to_sandbox(spec.permission_mode.as_ref()));

        let config = CodexConfig {
            name: spec.name.clone(),
            description: spec.description.clone(),
            model: spec.model.clone(),
            sandbox_mode,
            mcp_servers,
            developer_instructions: spec.system_prompt.clone().unwrap_or_default(),
        };

        Ok(toml::to_string_pretty(&config)?)
    }

    fn command_dir(&self, global: bool) -> PathBuf {
        if global {
            dirs::home_dir()
                .unwrap_or_else(|| PathBuf::from("."))
                .join(".codex/commands/")
        } else {
            PathBuf::from(".codex/commands/")
        }
    }

    fn mcp_config_path(&self) -> PathBuf {
        PathBuf::from(".mcp.json")
    }

    fn merge_mcp_entry(&self, name: &str, entry: Value) -> Result<(), FrameworkError> {
        merge_mcp_entry(&self.mcp_config_path(), name, entry)
    }

    fn install_hook(
        &self,
        _name: &str,
        script_path: &Path,
        events: &[HookEvent],
        matcher: Option<&Value>,
        global: bool,
    ) -> Result<(), FrameworkError> {
        validate_hook_args(events, matcher)?;
        let hooks_path = if global {
            dirs::home_dir()
                .ok_or_else(|| FrameworkError::Error("Cannot determine home directory".into()))?
                .join(".codex/hooks.json")
        } else {
            PathBuf::from(".codex/hooks.json")
        };

        let mut root = read_json_or_default(&hooks_path)?;
        let hooks_arr = root
            .as_object_mut()
            .ok_or_else(|| FrameworkError::Error("hooks.json root must be an object".into()))?
            .entry("hooks")
            .or_insert_with(|| Value::Array(vec![]));

        let script_str = script_path.to_string_lossy().to_string();

        for event in events {
            let event_name = codex_event_name(event);
            let already_exists = hooks_arr
                .as_array()
                .map(|arr| {
                    arr.iter().any(|e| {
                        e.get("command")
                            .and_then(|c| c.as_str())
                            .map(|c| c == script_str)
                            .unwrap_or(false)
                            && e.get("event")
                                .and_then(|ev| ev.as_str())
                                .map(|ev| ev == event_name)
                                .unwrap_or(false)
                    })
                })
                .unwrap_or(false);

            if !already_exists {
                let entry = serde_json::json!({
                    "event": event_name,
                    "command": script_str,
                    "timeout": 10000
                });
                hooks_arr
                    .as_array_mut()
                    .ok_or_else(|| FrameworkError::Error("hooks must be an array".into()))?
                    .push(entry);
            }
        }

        write_json(&hooks_path, &root)
    }
}
