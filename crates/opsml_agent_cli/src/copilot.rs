use crate::error::FrameworkError;
use crate::framework::AgentCliFramework;
use crate::utils::{
    copilot_command_exists_in_arr, merge_mcp_entry, read_json_or_default, validate_hook_args,
    write_json,
};
use opsml_types::contracts::subagent::SubAgentSpec;
use opsml_types::contracts::tool::HookEvent;
use serde::Serialize;
use serde_json::Value;
use std::path::{Path, PathBuf};

// ── Paths ─────────────────────────────────────────────────────────────────────
//
// Local (project):  .github/skills/{name}/SKILL.md
// Global (user):    ~/.copilot/skills/{name}/SKILL.md
// Local agent:      .github/agents/{name}.agent.md
// Global agent:     ~/.copilot/agents/{name}.agent.md
// Local hooks:      .github/hooks/hooks.json
// Global hooks:     ~/.copilot/hooks/hooks.json
// MCP:              .mcp.json
//
// Hook event names (camelCase per GitHub Copilot CLI docs):
//   PreToolUse      → preToolUse
//   PostToolUse     → postToolUse
//   SessionStart    → sessionStart
//   Stop            → sessionEnd
//   Notification    → errorOccurred
//   UserPromptSubmit→ userPromptSubmitted
//
// Hook config format (.github/hooks/hooks.json):
// {
//   "version": 1,
//   "hooks": {
//     "preToolUse": [
//       {
//         "type": "command",
//         "bash": "/path/to/script.sh",
//         "timeoutSec": 30
//       }
//     ]
//   }
// }

#[derive(Debug, Clone, Serialize)]
struct CopilotFrontmatter {
    name: String,
    description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    instructions: Option<String>,
    #[serde(skip_serializing_if = "Vec::is_empty", default)]
    tools: Vec<String>,
}

/// Maps a `HookEvent` to the GitHub Copilot CLI hook event name (camelCase).
fn copilot_event_name(event: &HookEvent) -> &'static str {
    match event {
        HookEvent::PreToolUse => "preToolUse",
        HookEvent::PostToolUse => "postToolUse",
        HookEvent::SessionStart => "sessionStart",
        HookEvent::Stop => "sessionEnd",
        HookEvent::Notification => "errorOccurred",
        HookEvent::UserPromptSubmit => "userPromptSubmitted",
    }
}

pub struct CopilotFramework;

impl AgentCliFramework for CopilotFramework {
    fn name(&self) -> &'static str {
        "github-copilot"
    }

    fn skill_path(&self, name: &str) -> PathBuf {
        PathBuf::from(format!(".github/skills/{name}/SKILL.md"))
    }

    fn global_skill_path(&self, name: &str) -> Result<PathBuf, FrameworkError> {
        let home = dirs::home_dir()
            .ok_or_else(|| FrameworkError::Error("Cannot determine home directory".into()))?;
        Ok(home.join(format!(".copilot/skills/{name}/SKILL.md")))
    }

    fn agent_dir(&self, global: bool) -> Result<PathBuf, FrameworkError> {
        if global {
            Ok(dirs::home_dir()
                .ok_or(FrameworkError::NoHomeDir)?
                .join(".copilot/agents"))
        } else {
            Ok(PathBuf::from(".github/agents"))
        }
    }

    fn agent_file_name(&self, name: &str) -> String {
        format!("{name}.agent.md")
    }

    fn serialize_agent(&self, spec: &SubAgentSpec) -> Result<String, FrameworkError> {
        let fm = CopilotFrontmatter {
            name: spec.name.clone(),
            description: spec.description.clone(),
            instructions: spec.system_prompt.clone(),
            tools: spec.tools.clone(),
        };

        let yaml = serde_yaml::to_string(&fm)?;
        let yaml = yaml.trim_start_matches("---\n");

        Ok(format!("---\n{yaml}---\n"))
    }

    fn command_dir(&self, global: bool) -> PathBuf {
        if global {
            dirs::home_dir()
                .unwrap_or_else(|| PathBuf::from("."))
                .join(".copilot/commands/")
        } else {
            PathBuf::from(".github/commands/")
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
                .join(".copilot/hooks/hooks.json")
        } else {
            PathBuf::from(".github/hooks/hooks.json")
        };

        let mut root = read_json_or_default(&hooks_path)?;
        let root_obj = root
            .as_object_mut()
            .ok_or_else(|| FrameworkError::Error("hooks.json root must be an object".into()))?;

        // Ensure version:1 is present at the root
        root_obj
            .entry("version")
            .or_insert_with(|| Value::Number(1.into()));

        let hooks_obj = root_obj
            .entry("hooks")
            .or_insert_with(|| Value::Object(serde_json::Map::new()));
        let hooks_obj = hooks_obj
            .as_object_mut()
            .ok_or_else(|| FrameworkError::Error("hooks is not an object".into()))?;

        let script_str = script_path.to_string_lossy().to_string();

        // Copilot hook entry format:
        // { "type": "command", "bash": "path/to/script.sh", "timeoutSec": 30 }
        let new_entry = serde_json::json!({
            "type": "command",
            "bash": script_str,
            "timeoutSec": 30
        });

        for event in events {
            let key = copilot_event_name(event);
            let arr = hooks_obj.entry(key).or_insert_with(|| Value::Array(vec![]));
            if !copilot_command_exists_in_arr(arr, script_path) {
                arr.as_array_mut()
                    .ok_or_else(|| {
                        FrameworkError::Error("hooks event array is not an array".into())
                    })?
                    .push(new_entry.clone());
            }
        }

        write_json(&hooks_path, &root)
    }
}
