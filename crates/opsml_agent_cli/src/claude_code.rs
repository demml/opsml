use crate::error::FrameworkError;
use crate::framework::AgentCliFramework;
use crate::utils::{
    command_exists_in_arr, merge_mcp_entry, read_json_or_default, validate_hook_args, write_json,
};
use opsml_types::contracts::subagent::SubAgentSpec;
use opsml_types::contracts::tool::HookEvent;
use serde::Serialize;
use serde_json::Value;
use std::path::{Path, PathBuf};

// ── Paths ─────────────────────────────────────────────────────────────────────
//
// Local (project):  .claude/skills/{name}/SKILL.md
// Global (user):    ~/.claude/skills/{name}/SKILL.md
// Local agent:      .claude/agents/{name}.md
// Global agent:     ~/.claude/agents/{name}.md
// Local hooks:      .claude/settings.json
// Global hooks:     ~/.claude/settings.json
// MCP:              .mcp.json

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

pub struct ClaudeCodeFramework;

impl AgentCliFramework for ClaudeCodeFramework {
    fn name(&self) -> &'static str {
        "claude-code"
    }

    fn skill_path(&self, name: &str) -> PathBuf {
        PathBuf::from(format!(".claude/skills/{name}/SKILL.md"))
    }

    fn global_skill_path(&self, name: &str) -> Result<PathBuf, FrameworkError> {
        let home = dirs::home_dir()
            .ok_or_else(|| FrameworkError::Error("Cannot determine home directory".into()))?;
        Ok(home.join(format!(".claude/skills/{name}/SKILL.md")))
    }

    fn agent_dir(&self, global: bool) -> Result<PathBuf, FrameworkError> {
        if global {
            Ok(dirs::home_dir()
                .ok_or(FrameworkError::NoHomeDir)?
                .join(".claude/agents"))
        } else {
            Ok(PathBuf::from(".claude/agents"))
        }
    }

    fn agent_file_name(&self, name: &str) -> String {
        format!("{name}.md")
    }

    fn serialize_agent(&self, spec: &SubAgentSpec) -> Result<String, FrameworkError> {
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

    fn command_dir(&self, global: bool) -> PathBuf {
        if global {
            dirs::home_dir()
                .unwrap_or_else(|| PathBuf::from("."))
                .join(".claude/commands/")
        } else {
            PathBuf::from(".claude/commands/")
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
        let settings_path = if global {
            dirs::home_dir()
                .ok_or_else(|| FrameworkError::Error("Cannot determine home directory".into()))?
                .join(".claude/settings.json")
        } else {
            PathBuf::from(".claude/settings.json")
        };

        let mut settings = read_json_or_default(&settings_path)?;
        let hooks_obj = settings
            .as_object_mut()
            .ok_or_else(|| FrameworkError::Error("settings.json root is not an object".into()))?
            .entry("hooks")
            .or_insert_with(|| Value::Object(serde_json::Map::new()));
        let hooks_obj = hooks_obj
            .as_object_mut()
            .ok_or_else(|| FrameworkError::Error("hooks is not an object".into()))?;

        let script_str = script_path.to_string_lossy().to_string();
        let hook_entry =
            serde_json::json!({ "type": "command", "command": script_str, "timeout": 10000 });
        let new_entry = serde_json::json!({
            "matcher": matcher.cloned().unwrap_or(Value::Null),
            "hooks": [hook_entry]
        });

        for event in events {
            // Claude Code uses PascalCase event names (PreToolUse, PostToolUse, etc.)
            let key = event.as_pascal_case();
            let arr = hooks_obj.entry(key).or_insert_with(|| Value::Array(vec![]));
            if !command_exists_in_arr(arr, script_path) {
                arr.as_array_mut()
                    .ok_or_else(|| {
                        FrameworkError::Error("hooks event array is not an array".into())
                    })?
                    .push(new_entry.clone());
            }
        }

        write_json(&settings_path, &settings)
    }
}
