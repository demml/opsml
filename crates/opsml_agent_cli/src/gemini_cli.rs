use crate::error::FrameworkError;
use crate::framework::AgentCliFramework;
use crate::utils::{
    gemini_command_exists_in_arr, merge_mcp_entry, read_json_or_default, validate_hook_args,
    write_json,
};
use opsml_types::contracts::subagent::SubAgentSpec;
use opsml_types::contracts::tool::HookEvent;
use serde::Serialize;
use serde_json::Value;
use std::path::{Path, PathBuf};

// ── Paths ─────────────────────────────────────────────────────────────────────
//
// Local (project):  .gemini/skills/{name}/SKILL.md
// Global (user):    ~/.gemini/skills/{name}/SKILL.md
// Local agent:      .gemini/agents/{name}.md
// Global agent:     ~/.gemini/agents/{name}.md
// Local hooks:      .gemini/settings.json
// Global hooks:     ~/.gemini/settings.json
// MCP:              .mcp.json
//
// Hook event names (PascalCase per Gemini CLI docs):
//   PreToolUse  → BeforeTool
//   PostToolUse → AfterTool
//   SessionStart→ SessionStart
//   Stop        → SessionEnd
//   Notification→ Notification
//   UserPromptSubmit → BeforeModel
//
// Hook entry format (Gemini settings.json):
// {
//   "hooks": {
//     "BeforeTool": [
//       {
//         "matcher": "bash|shell",
//         "sequential": true,
//         "hooks": [
//           { "type": "command", "command": "/path/to/script.sh", "timeout": 10000 }
//         ]
//       }
//     ]
//   }
// }

#[derive(Debug, Clone, Serialize)]
struct GeminiFrontmatter {
    name: String,
    description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    model: Option<String>,
    #[serde(skip_serializing_if = "Vec::is_empty", default)]
    tools: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    temperature: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    max_turns: Option<u32>,
}

/// Maps a `HookEvent` to the Gemini CLI hook event name.
fn gemini_event_name(event: &HookEvent) -> &'static str {
    match event {
        HookEvent::PreToolUse => "BeforeTool",
        HookEvent::PostToolUse => "AfterTool",
        HookEvent::SessionStart => "SessionStart",
        HookEvent::Stop => "SessionEnd",
        HookEvent::Notification => "Notification",
        HookEvent::UserPromptSubmit => "BeforeModel",
    }
}

pub struct GeminiCliFramework;

impl AgentCliFramework for GeminiCliFramework {
    fn name(&self) -> &'static str {
        "gemini-cli"
    }

    fn skill_path(&self, name: &str) -> PathBuf {
        PathBuf::from(format!(".gemini/skills/{name}/SKILL.md"))
    }

    fn global_skill_path(&self, name: &str) -> Result<PathBuf, FrameworkError> {
        let home = dirs::home_dir()
            .ok_or_else(|| FrameworkError::Error("Cannot determine home directory".into()))?;
        Ok(home.join(format!(".gemini/skills/{name}/SKILL.md")))
    }

    fn agent_dir(&self, global: bool) -> Result<PathBuf, FrameworkError> {
        if global {
            Ok(dirs::home_dir()
                .ok_or(FrameworkError::NoHomeDir)?
                .join(".gemini/agents"))
        } else {
            Ok(PathBuf::from(".gemini/agents"))
        }
    }

    fn agent_file_name(&self, name: &str) -> String {
        format!("{name}.md")
    }

    fn serialize_agent(&self, spec: &SubAgentSpec) -> Result<String, FrameworkError> {
        let fm = GeminiFrontmatter {
            name: spec.name.clone(),
            description: spec.description.clone(),
            model: spec.model.clone(),
            tools: spec.tools.clone(),
            temperature: spec.temperature,
            max_turns: spec.max_turns,
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
                .join(".gemini/commands/")
        } else {
            PathBuf::from(".gemini/commands/")
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
                .join(".gemini/settings.json")
        } else {
            PathBuf::from(".gemini/settings.json")
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

        // Build the inner hook entry per Gemini docs format:
        // { "type": "command", "command": "...", "timeout": 10000 }
        let inner_hook = serde_json::json!({
            "type": "command",
            "command": script_str,
            "timeout": 10000
        });

        // Build the outer group entry:
        // { "matcher": "...", "sequential": false, "hooks": [inner_hook] }
        let matcher_val = matcher.cloned().unwrap_or(Value::Null);
        let new_group = serde_json::json!({
            "matcher": matcher_val,
            "sequential": false,
            "hooks": [inner_hook]
        });

        for event in events {
            let key = gemini_event_name(event);
            let arr = hooks_obj.entry(key).or_insert_with(|| Value::Array(vec![]));
            if !gemini_command_exists_in_arr(arr, script_path) {
                arr.as_array_mut()
                    .ok_or_else(|| {
                        FrameworkError::Error("hooks event array is not an array".into())
                    })?
                    .push(new_group.clone());
            }
        }

        write_json(&settings_path, &settings)
    }
}
