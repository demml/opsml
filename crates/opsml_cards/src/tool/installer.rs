use super::error::ToolError;
use opsml_types::contracts::tool::HookEvent;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use tracing::warn;

/// Typed representation of `.codex/config.yaml` that preserves unknown fields on round-trip.
/// Using a typed struct instead of `serde_json::Value` prevents block-scalar corruption.
#[derive(Debug, Default, Serialize, Deserialize)]
struct CodexConfig {
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    hooks: Vec<Value>,
    #[serde(flatten)]
    other: HashMap<String, Value>,
}

pub trait SlashCommandInstaller {
    fn command_dir(&self) -> PathBuf;
    fn global_command_dir(&self) -> Result<PathBuf, ToolError>;
}

pub trait McpConfigInstaller {
    fn mcp_config_path(&self) -> PathBuf;
    fn merge_mcp_entry(&self, name: &str, entry: serde_json::Value) -> Result<(), ToolError>;
}

pub(crate) fn default_merge_mcp_entry(
    mcp_config_path: &Path,
    name: &str,
    entry: serde_json::Value,
) -> Result<(), ToolError> {
    if let Some(parent) = mcp_config_path.parent()
        && !parent.as_os_str().is_empty()
    {
        std::fs::create_dir_all(parent)?;
    }

    let existing = if mcp_config_path.exists() {
        std::fs::read_to_string(mcp_config_path)?
    } else {
        String::new()
    };

    let existing = if existing.is_empty() { "{}" } else { &existing };

    let mut root: serde_json::Value = serde_json::from_str(existing)?;

    let mcp_servers = root
        .as_object_mut()
        .ok_or_else(|| ToolError::Error("mcp.json root is not an object".to_string()))?
        .entry("mcpServers")
        .or_insert_with(|| serde_json::Value::Object(serde_json::Map::new()));

    mcp_servers
        .as_object_mut()
        .ok_or_else(|| ToolError::Error("mcpServers is not an object".to_string()))?
        .insert(name.to_string(), entry);

    write_json(mcp_config_path, &root)
}

fn read_json_or_default(path: &Path) -> Value {
    if path.exists() {
        match std::fs::read_to_string(path) {
            Ok(content) => match serde_json::from_str::<Value>(&content) {
                Ok(v) => v,
                Err(e) => {
                    warn!(
                        "Failed to parse {}: {e} — starting with empty config",
                        path.display()
                    );
                    Value::Object(serde_json::Map::new())
                }
            },
            Err(e) => {
                warn!(
                    "Failed to read {}: {e} — starting with empty config",
                    path.display()
                );
                Value::Object(serde_json::Map::new())
            }
        }
    } else {
        Value::Object(serde_json::Map::new())
    }
}

fn write_json(path: &Path, value: &Value) -> Result<(), ToolError> {
    let parent = path.parent().unwrap_or_else(|| std::path::Path::new("."));
    if !parent.as_os_str().is_empty() {
        std::fs::create_dir_all(parent)?;
    }
    let content = serde_json::to_string_pretty(value)?;
    let mut tmp = tempfile::NamedTempFile::new_in(parent)
        .map_err(|e| ToolError::Error(format!("Failed to create temp file: {e}")))?;
    use std::io::Write;
    tmp.write_all(content.as_bytes())?;
    tmp.persist(path)
        .map_err(|e| ToolError::Error(format!("Failed to persist {}: {e}", path.display())))?;
    Ok(())
}

fn command_exists_in_arr(arr: &Value, script_path: &Path) -> bool {
    let script_str = script_path.to_string_lossy();
    arr.as_array()
        .map(|entries| {
            entries.iter().any(|entry| {
                entry
                    .get("hooks")
                    .and_then(|h| h.as_array())
                    .map(|hooks| {
                        hooks.iter().any(|h| {
                            h.get("command")
                                .and_then(|c| c.as_str())
                                .map(|c| c == script_str)
                                .unwrap_or(false)
                        })
                    })
                    .unwrap_or(false)
            })
        })
        .unwrap_or(false)
}

fn script_exists_in_arr(arr: &Value, script_path: &Path) -> bool {
    let script_str = script_path.to_string_lossy();
    arr.as_array()
        .map(|entries| {
            entries.iter().any(|entry| {
                entry
                    .get("script")
                    .and_then(|s| s.as_str())
                    .map(|s| s == script_str)
                    .unwrap_or(false)
            })
        })
        .unwrap_or(false)
}

fn validate_tool_string(s: &str) -> Result<(), ToolError> {
    const MAX_LEN: usize = 128;
    if s.len() > MAX_LEN {
        return Err(ToolError::Error(format!(
            "hook_matcher tool value exceeds {MAX_LEN} characters"
        )));
    }
    if !s
        .chars()
        .all(|c| c.is_ascii_alphanumeric() || c == '_' || c == '-' || c == ':')
    {
        return Err(ToolError::Error(format!(
            "hook_matcher tool value '{s}' must contain only [a-zA-Z0-9_-:]"
        )));
    }
    Ok(())
}

pub(crate) fn validate_hook_matcher(v: &serde_json::Value) -> Result<(), ToolError> {
    match v {
        serde_json::Value::Null | serde_json::Value::String(_) => Ok(()),
        serde_json::Value::Object(map) => {
            if map.len() == 1
                && let Some(tool_val) = map.get("tool")
            {
                match tool_val {
                    serde_json::Value::String(s) => return validate_tool_string(s),
                    serde_json::Value::Array(arr) if arr.iter().all(|v| v.is_string()) => {
                        for s in arr {
                            if let serde_json::Value::String(s) = s {
                                validate_tool_string(s)?;
                            }
                        }
                        return Ok(());
                    }
                    _ => {}
                }
            }
            Err(ToolError::Error(
                "hook_matcher must be null, a string, or an object with a single 'tool' key mapping to a string or array of strings".to_string(),
            ))
        }
        _ => Err(ToolError::Error(
            "hook_matcher must be null, a string, or an object with a single 'tool' key"
                .to_string(),
        )),
    }
}

fn validate_hook_args(events: &[HookEvent], matcher: Option<&Value>) -> Result<(), ToolError> {
    if events.is_empty() {
        return Err(ToolError::Error(
            "Hook tool has no hook_events configured; nothing to register".to_string(),
        ));
    }
    if let Some(m) = matcher {
        validate_hook_matcher(m)?;
    }
    Ok(())
}

pub trait HookInstaller {
    fn install_hook(
        &self,
        name: &str,
        script_path: &Path,
        events: &[HookEvent],
        matcher: Option<&Value>,
        global: bool,
    ) -> Result<(), ToolError>;
}

// ClaudeCodeInstaller

pub struct ClaudeCodeInstaller;

impl SlashCommandInstaller for ClaudeCodeInstaller {
    fn command_dir(&self) -> PathBuf {
        PathBuf::from(".claude/commands/")
    }

    fn global_command_dir(&self) -> Result<PathBuf, ToolError> {
        let home = dirs::home_dir()
            .ok_or_else(|| ToolError::Error("Could not determine home directory".to_string()))?;
        Ok(home.join(".claude/commands/"))
    }
}

impl McpConfigInstaller for ClaudeCodeInstaller {
    fn mcp_config_path(&self) -> PathBuf {
        PathBuf::from(".mcp.json")
    }

    fn merge_mcp_entry(&self, name: &str, entry: serde_json::Value) -> Result<(), ToolError> {
        default_merge_mcp_entry(&self.mcp_config_path(), name, entry)
    }
}

impl HookInstaller for ClaudeCodeInstaller {
    fn install_hook(
        &self,
        _name: &str,
        script_path: &Path,
        events: &[HookEvent],
        matcher: Option<&Value>,
        global: bool,
    ) -> Result<(), ToolError> {
        validate_hook_args(events, matcher)?;
        let settings_path = if global {
            dirs::home_dir()
                .ok_or_else(|| ToolError::Error("Could not determine home directory".to_string()))?
                .join(".claude/settings.json")
        } else {
            PathBuf::from(".claude/settings.json")
        };

        let mut settings = read_json_or_default(&settings_path);
        let hooks_obj = settings
            .as_object_mut()
            .ok_or_else(|| ToolError::Error("settings.json root is not an object".to_string()))?
            .entry("hooks")
            .or_insert_with(|| Value::Object(serde_json::Map::new()));
        let hooks_obj = hooks_obj
            .as_object_mut()
            .ok_or_else(|| ToolError::Error("hooks is not an object".to_string()))?;

        let script_str = script_path.to_string_lossy().to_string();
        let hook_entry = serde_json::json!({
            "type": "command",
            "command": script_str
        });
        let new_entry = serde_json::json!({
            "matcher": matcher.cloned().unwrap_or(Value::Null),
            "hooks": [hook_entry]
        });

        for event in events {
            let key = event.as_pascal_case();
            let arr = hooks_obj.entry(key).or_insert_with(|| Value::Array(vec![]));
            if !command_exists_in_arr(arr, script_path) {
                arr.as_array_mut()
                    .ok_or_else(|| {
                        ToolError::Error("hooks event array is not an array".to_string())
                    })?
                    .push(new_entry.clone());
            }
        }

        write_json(&settings_path, &settings)
    }
}

// GeminiCliInstaller

pub struct GeminiCliInstaller;

impl SlashCommandInstaller for GeminiCliInstaller {
    fn command_dir(&self) -> PathBuf {
        PathBuf::from(".gemini/commands/")
    }

    fn global_command_dir(&self) -> Result<PathBuf, ToolError> {
        let home = dirs::home_dir()
            .ok_or_else(|| ToolError::Error("Could not determine home directory".to_string()))?;
        Ok(home.join(".gemini/commands/"))
    }
}

impl McpConfigInstaller for GeminiCliInstaller {
    fn mcp_config_path(&self) -> PathBuf {
        PathBuf::from(".mcp.json")
    }

    fn merge_mcp_entry(&self, name: &str, entry: serde_json::Value) -> Result<(), ToolError> {
        default_merge_mcp_entry(&self.mcp_config_path(), name, entry)
    }
}

impl HookInstaller for GeminiCliInstaller {
    fn install_hook(
        &self,
        _name: &str,
        script_path: &Path,
        events: &[HookEvent],
        matcher: Option<&Value>,
        global: bool,
    ) -> Result<(), ToolError> {
        validate_hook_args(events, matcher)?;
        let settings_path = if global {
            dirs::home_dir()
                .ok_or_else(|| ToolError::Error("Could not determine home directory".to_string()))?
                .join(".gemini/settings.json")
        } else {
            PathBuf::from(".gemini/settings.json")
        };

        let mut settings = read_json_or_default(&settings_path);
        let hooks_obj = settings
            .as_object_mut()
            .ok_or_else(|| ToolError::Error("settings.json root is not an object".to_string()))?
            .entry("hooks")
            .or_insert_with(|| Value::Object(serde_json::Map::new()));
        let hooks_obj = hooks_obj
            .as_object_mut()
            .ok_or_else(|| ToolError::Error("hooks is not an object".to_string()))?;

        let script_str = script_path.to_string_lossy().to_string();
        let new_entry = serde_json::json!({
            "script": script_str,
            "matcher": matcher.cloned().unwrap_or(Value::Null)
        });

        for event in events {
            let key = event.as_snake_case();
            let arr = hooks_obj.entry(key).or_insert_with(|| Value::Array(vec![]));
            if !script_exists_in_arr(arr, script_path) {
                arr.as_array_mut()
                    .ok_or_else(|| {
                        ToolError::Error("hooks event array is not an array".to_string())
                    })?
                    .push(new_entry.clone());
            }
        }

        write_json(&settings_path, &settings)
    }
}

// CodexInstaller

pub struct CodexInstaller;

impl SlashCommandInstaller for CodexInstaller {
    fn command_dir(&self) -> PathBuf {
        PathBuf::from(".codex/commands/")
    }

    fn global_command_dir(&self) -> Result<PathBuf, ToolError> {
        let home = dirs::home_dir()
            .ok_or_else(|| ToolError::Error("Could not determine home directory".to_string()))?;
        Ok(home.join(".codex/commands/"))
    }
}

impl McpConfigInstaller for CodexInstaller {
    fn mcp_config_path(&self) -> PathBuf {
        PathBuf::from(".mcp.json")
    }

    fn merge_mcp_entry(&self, name: &str, entry: serde_json::Value) -> Result<(), ToolError> {
        default_merge_mcp_entry(&self.mcp_config_path(), name, entry)
    }
}

impl HookInstaller for CodexInstaller {
    fn install_hook(
        &self,
        _name: &str,
        script_path: &Path,
        events: &[HookEvent],
        matcher: Option<&Value>,
        global: bool,
    ) -> Result<(), ToolError> {
        validate_hook_args(events, matcher)?;
        let config_path = if global {
            dirs::home_dir()
                .ok_or_else(|| ToolError::Error("Could not determine home directory".to_string()))?
                .join(".codex/config.yaml")
        } else {
            PathBuf::from(".codex/config.yaml")
        };

        let mut config: CodexConfig = if config_path.exists() {
            let content = std::fs::read_to_string(&config_path)?;
            serde_yaml::from_str(&content)?
        } else {
            CodexConfig::default()
        };

        let script_str = script_path.to_string_lossy().to_string();

        for event in events {
            let event_name = event.as_snake_case();
            let already_exists = config.hooks.iter().any(|e| {
                e.get("script")
                    .and_then(|s| s.as_str())
                    .map(|s| s == script_str)
                    .unwrap_or(false)
                    && e.get("event")
                        .and_then(|ev| ev.as_str())
                        .map(|ev| ev == event_name)
                        .unwrap_or(false)
            });
            if !already_exists {
                let mut entry = serde_json::json!({
                    "event": event_name,
                    "script": script_str,
                });
                if let Some(m) = matcher {
                    entry
                        .as_object_mut()
                        .ok_or_else(|| ToolError::Error("hook entry is not an object".to_string()))?
                        .insert("filter".to_string(), m.clone());
                }
                config.hooks.push(entry);
            }
        }

        if let Some(parent) = config_path.parent()
            && !parent.as_os_str().is_empty()
        {
            std::fs::create_dir_all(parent)?;
        }
        let yaml_content = serde_yaml::to_string(&config)?;
        let parent = config_path
            .parent()
            .unwrap_or_else(|| std::path::Path::new("."));
        let mut tmp = tempfile::NamedTempFile::new_in(parent)
            .map_err(|e| ToolError::Error(format!("Failed to create temp file: {e}")))?;
        use std::io::Write;
        tmp.write_all(yaml_content.as_bytes())?;
        tmp.persist(&config_path)
            .map_err(|e| ToolError::Error(format!("Failed to persist config.yaml: {e}")))?;
        Ok(())
    }
}

// CopilotInstaller

pub struct CopilotInstaller;

impl SlashCommandInstaller for CopilotInstaller {
    fn command_dir(&self) -> PathBuf {
        PathBuf::from(".github/commands/")
    }

    fn global_command_dir(&self) -> Result<PathBuf, ToolError> {
        let home = dirs::home_dir()
            .ok_or_else(|| ToolError::Error("Could not determine home directory".to_string()))?;
        Ok(home.join(".github/commands/"))
    }
}

impl McpConfigInstaller for CopilotInstaller {
    fn mcp_config_path(&self) -> PathBuf {
        PathBuf::from(".mcp.json")
    }

    fn merge_mcp_entry(&self, name: &str, entry: serde_json::Value) -> Result<(), ToolError> {
        default_merge_mcp_entry(&self.mcp_config_path(), name, entry)
    }
}

impl HookInstaller for CopilotInstaller {
    fn install_hook(
        &self,
        _name: &str,
        script_path: &Path,
        _events: &[HookEvent],
        _matcher: Option<&Value>,
        _global: bool,
    ) -> Result<(), ToolError> {
        warn!(
            "GitHub Copilot does not support lifecycle hooks. Script written to {}. Register it manually if needed.",
            script_path.display()
        );
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn entry() -> serde_json::Value {
        serde_json::json!({"command": "npx", "args": ["-y", "test-server"]})
    }

    fn assert_idempotent(config_path: &Path) {
        let e = entry();
        default_merge_mcp_entry(config_path, "test-server", e.clone()).unwrap();
        default_merge_mcp_entry(config_path, "test-server", e).unwrap();

        let content = std::fs::read_to_string(config_path).unwrap();
        let parsed: serde_json::Value = serde_json::from_str(&content).unwrap();
        let mcp_servers = parsed["mcpServers"].as_object().unwrap();
        assert_eq!(mcp_servers.len(), 1, "idempotent: key must not duplicate");
        assert!(mcp_servers.contains_key("test-server"));
    }

    #[test]
    fn test_gemini_cli_slash_command_dirs() {
        let installer = GeminiCliInstaller;
        assert!(
            installer
                .command_dir()
                .to_str()
                .unwrap()
                .contains(".gemini")
        );
        let global = installer.global_command_dir().unwrap();
        assert!(global.to_str().unwrap().contains(".gemini"));
    }

    #[test]
    fn test_gemini_cli_merge_mcp_idempotent() {
        let tmp = tempfile::tempdir().unwrap();
        assert_idempotent(&tmp.path().join(".mcp.json"));
    }

    #[test]
    fn test_codex_slash_command_dirs() {
        let installer = CodexInstaller;
        assert!(installer.command_dir().to_str().unwrap().contains(".codex"));
        let global = installer.global_command_dir().unwrap();
        assert!(global.to_str().unwrap().contains(".codex"));
    }

    #[test]
    fn test_codex_merge_mcp_idempotent() {
        let tmp = tempfile::tempdir().unwrap();
        assert_idempotent(&tmp.path().join(".mcp.json"));
    }

    #[test]
    fn test_copilot_slash_command_dirs() {
        let installer = CopilotInstaller;
        assert!(
            installer
                .command_dir()
                .to_str()
                .unwrap()
                .contains(".github")
        );
        let global = installer.global_command_dir().unwrap();
        assert!(global.to_str().unwrap().contains(".github"));
    }

    #[test]
    fn test_copilot_merge_mcp_idempotent() {
        let tmp = tempfile::tempdir().unwrap();
        assert_idempotent(&tmp.path().join(".mcp.json"));
    }

    #[test]
    fn test_merge_mcp_creates_parent_dirs() {
        let tmp = tempfile::tempdir().unwrap();
        let config_path = tmp.path().join("nested/deep/.mcp.json");
        default_merge_mcp_entry(&config_path, "server", entry()).unwrap();
        assert!(config_path.exists());
    }

    // --- HookInstaller tests ---

    #[test]
    fn test_claude_code_hook_creates_settings_json() {
        crate::tool::test_util::with_tempdir(|tmp| {
            let script = Path::new(".opsml/hooks/my-hook.sh");
            ClaudeCodeInstaller
                .install_hook("my-hook", script, &[HookEvent::PostToolUse], None, false)
                .unwrap();

            let settings_path = tmp.join(".claude/settings.json");
            assert!(settings_path.exists());
            let content: Value =
                serde_json::from_str(&std::fs::read_to_string(&settings_path).unwrap()).unwrap();
            let hooks = &content["hooks"]["PostToolUse"];
            assert!(hooks.is_array());
            let arr = hooks.as_array().unwrap();
            assert_eq!(arr.len(), 1);
            assert_eq!(arr[0]["hooks"][0]["command"], ".opsml/hooks/my-hook.sh");
        });
    }

    #[test]
    fn test_claude_code_hook_idempotent() {
        crate::tool::test_util::with_tempdir(|tmp| {
            let script = Path::new(".opsml/hooks/my-hook.sh");
            ClaudeCodeInstaller
                .install_hook("my-hook", script, &[HookEvent::PostToolUse], None, false)
                .unwrap();
            ClaudeCodeInstaller
                .install_hook("my-hook", script, &[HookEvent::PostToolUse], None, false)
                .unwrap();

            let settings_path = tmp.join(".claude/settings.json");
            let content: Value =
                serde_json::from_str(&std::fs::read_to_string(&settings_path).unwrap()).unwrap();
            let arr = content["hooks"]["PostToolUse"].as_array().unwrap();
            assert_eq!(arr.len(), 1, "idempotent: must not duplicate");
        });
    }

    #[test]
    fn test_claude_code_hook_multiple_events() {
        crate::tool::test_util::with_tempdir(|tmp| {
            let script = Path::new(".opsml/hooks/my-hook.sh");
            ClaudeCodeInstaller
                .install_hook(
                    "my-hook",
                    script,
                    &[HookEvent::PostToolUse, HookEvent::PreToolUse],
                    None,
                    false,
                )
                .unwrap();

            let settings_path = tmp.join(".claude/settings.json");
            let content: Value =
                serde_json::from_str(&std::fs::read_to_string(&settings_path).unwrap()).unwrap();
            assert!(content["hooks"]["PostToolUse"].is_array());
            assert!(content["hooks"]["PreToolUse"].is_array());
        });
    }

    #[test]
    fn test_gemini_hook_snake_case_keys() {
        crate::tool::test_util::with_tempdir(|tmp| {
            let script = Path::new(".opsml/hooks/my-hook.sh");
            GeminiCliInstaller
                .install_hook("my-hook", script, &[HookEvent::PostToolUse], None, false)
                .unwrap();

            let settings_path = tmp.join(".gemini/settings.json");
            let content: Value =
                serde_json::from_str(&std::fs::read_to_string(&settings_path).unwrap()).unwrap();
            assert!(
                content["hooks"]["post_tool_use"].is_array(),
                "expected post_tool_use key"
            );
            assert!(
                !content["hooks"]
                    .as_object()
                    .map(|o| o.contains_key("PostToolUse"))
                    .unwrap_or(false)
            );
        });
    }

    #[test]
    fn test_gemini_hook_idempotent() {
        crate::tool::test_util::with_tempdir(|tmp| {
            let script = Path::new(".opsml/hooks/my-hook.sh");
            GeminiCliInstaller
                .install_hook("my-hook", script, &[HookEvent::PostToolUse], None, false)
                .unwrap();
            GeminiCliInstaller
                .install_hook("my-hook", script, &[HookEvent::PostToolUse], None, false)
                .unwrap();

            let settings_path = tmp.join(".gemini/settings.json");
            let content: Value =
                serde_json::from_str(&std::fs::read_to_string(&settings_path).unwrap()).unwrap();
            let arr = content["hooks"]["post_tool_use"].as_array().unwrap();
            assert_eq!(arr.len(), 1);
        });
    }

    #[test]
    fn test_codex_hook_yaml_format() {
        crate::tool::test_util::with_tempdir(|tmp| {
            let script = Path::new(".opsml/hooks/my-hook.sh");
            CodexInstaller
                .install_hook("my-hook", script, &[HookEvent::PostToolUse], None, false)
                .unwrap();

            let config_path = tmp.join(".codex/config.yaml");
            assert!(config_path.exists());
            let content = std::fs::read_to_string(&config_path).unwrap();
            let parsed: Value = serde_yaml::from_str(&content).unwrap();
            let hooks = parsed["hooks"].as_array().unwrap();
            assert_eq!(hooks.len(), 1);
            assert_eq!(hooks[0]["event"], "post_tool_use");
            assert_eq!(hooks[0]["script"], ".opsml/hooks/my-hook.sh");
        });
    }

    #[test]
    fn test_codex_hook_idempotent() {
        crate::tool::test_util::with_tempdir(|tmp| {
            let script = Path::new(".opsml/hooks/my-hook.sh");
            CodexInstaller
                .install_hook("my-hook", script, &[HookEvent::PostToolUse], None, false)
                .unwrap();
            CodexInstaller
                .install_hook("my-hook", script, &[HookEvent::PostToolUse], None, false)
                .unwrap();

            let config_path = tmp.join(".codex/config.yaml");
            let content = std::fs::read_to_string(&config_path).unwrap();
            let parsed: Value = serde_yaml::from_str(&content).unwrap();
            let hooks = parsed["hooks"].as_array().unwrap();
            assert_eq!(hooks.len(), 1, "idempotent");
        });
    }

    #[test]
    fn test_copilot_hook_returns_ok() {
        let tmp = tempfile::tempdir().unwrap();
        let script = tmp.path().join(".opsml/hooks/my-hook.sh");
        let result = CopilotInstaller.install_hook(
            "my-hook",
            &script,
            &[HookEvent::PostToolUse],
            None,
            false,
        );
        assert!(result.is_ok());
    }

    #[test]
    fn test_claude_code_hook_with_matcher() {
        crate::tool::test_util::with_tempdir(|_tmp| {
            let installer = ClaudeCodeInstaller;
            let script_path = std::path::Path::new(".opsml/hooks/my-hook.sh");
            let matcher = serde_json::json!({"tool": "Write"});
            installer
                .install_hook(
                    "my-hook",
                    script_path,
                    &[HookEvent::PostToolUse],
                    Some(&matcher),
                    false,
                )
                .unwrap();
            let content = std::fs::read_to_string(".claude/settings.json").unwrap();
            let parsed: serde_json::Value = serde_json::from_str(&content).unwrap();
            let entry = &parsed["hooks"]["PostToolUse"][0];
            assert_eq!(entry["matcher"], serde_json::json!({"tool": "Write"}));
        });
    }

    #[test]
    fn test_install_hook_empty_events_returns_error() {
        let installer = ClaudeCodeInstaller;
        let tmp = tempfile::tempdir().unwrap();
        let script_path = tmp.path().join("hook.sh");
        let result = installer.install_hook("my-hook", &script_path, &[], None, false);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("hook_events"));
    }

    #[test]
    fn test_validate_hook_matcher_non_string_tool_value_is_err() {
        let bad = serde_json::json!({"tool": 42});
        assert!(validate_hook_matcher(&bad).is_err());
    }

    #[test]
    fn test_validate_hook_matcher_non_object_top_level_is_err() {
        let bad = serde_json::json!(42);
        assert!(validate_hook_matcher(&bad).is_err());
    }

    #[test]
    fn test_validate_tool_string_too_long_is_err() {
        let long = "a".repeat(129);
        assert!(validate_tool_string(&long).is_err());
    }

    #[test]
    fn test_validate_tool_string_invalid_chars_is_err() {
        assert!(validate_tool_string("foo bar").is_err());
        assert!(validate_tool_string("foo;bar").is_err());
    }

    #[test]
    fn test_validate_tool_string_valid_passes() {
        assert!(validate_tool_string("Write").is_ok());
        assert!(validate_tool_string("my-tool_123:action").is_ok());
    }

    #[test]
    fn test_claude_code_hook_global() {
        let fake_home = tempfile::tempdir().unwrap();
        let original_home = std::env::var("HOME").ok();
        // SAFETY: test runs under --test-threads=1
        unsafe { std::env::set_var("HOME", fake_home.path()) };
        let result = std::panic::catch_unwind(|| {
            let installer = ClaudeCodeInstaller;
            let script_path = std::path::Path::new(".opsml/hooks/global-hook.sh");
            installer
                .install_hook(
                    "global-hook",
                    script_path,
                    &[HookEvent::PostToolUse],
                    None,
                    true,
                )
                .unwrap();
            let settings_path = fake_home.path().join(".claude/settings.json");
            assert!(
                settings_path.exists(),
                "settings.json not created in fake home"
            );
            let content = std::fs::read_to_string(&settings_path).unwrap();
            let parsed: serde_json::Value = serde_json::from_str(&content).unwrap();
            assert!(parsed["hooks"]["PostToolUse"].is_array());
        });
        // SAFETY: test runs under --test-threads=1
        unsafe {
            if let Some(h) = original_home {
                std::env::set_var("HOME", h);
            } else {
                std::env::remove_var("HOME");
            }
        }
        result.unwrap();
    }
}
