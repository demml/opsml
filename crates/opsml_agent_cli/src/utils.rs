use crate::error::FrameworkError;
use opsml_types::contracts::tool::HookEvent;
use serde_json::Value;
use std::path::Path;

// ── JSON I/O helpers ─────────────────────────────────────────────────────────

pub(crate) fn read_json_or_default(path: &Path) -> Result<Value, FrameworkError> {
    if !path.exists() {
        return Ok(Value::Object(serde_json::Map::new()));
    }
    let content = std::fs::read_to_string(path)?;
    serde_json::from_str::<Value>(&content)
        .map_err(|e| FrameworkError::CorruptConfig(format!("{}: {e}", path.display())))
}

pub(crate) fn write_json(path: &Path, value: &Value) -> Result<(), FrameworkError> {
    let parent = path.parent().unwrap_or_else(|| std::path::Path::new("."));
    if !parent.as_os_str().is_empty() {
        std::fs::create_dir_all(parent)?;
    }
    let content = serde_json::to_string_pretty(value)?;
    let mut tmp = tempfile::NamedTempFile::new_in(parent)
        .map_err(|e| FrameworkError::Error(format!("Failed to create temp file: {e}")))?;
    use std::io::Write;
    tmp.write_all(content.as_bytes())?;
    tmp.persist(path)
        .map_err(|e| FrameworkError::Error(format!("Failed to persist {}: {e}", path.display())))?;
    Ok(())
}

pub(crate) fn merge_mcp_entry(
    mcp_config_path: &Path,
    name: &str,
    entry: serde_json::Value,
) -> Result<(), FrameworkError> {
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
        .ok_or_else(|| FrameworkError::Error("mcp.json root is not an object".to_string()))?
        .entry("mcpServers")
        .or_insert_with(|| serde_json::Value::Object(serde_json::Map::new()));

    mcp_servers
        .as_object_mut()
        .ok_or_else(|| FrameworkError::Error("mcpServers is not an object".to_string()))?
        .insert(name.to_string(), entry);

    write_json(mcp_config_path, &root)
}

// ── Hook validation ───────────────────────────────────────────────────────────

fn validate_tool_string(s: &str) -> Result<(), FrameworkError> {
    const MAX_LEN: usize = 128;
    if s.len() > MAX_LEN {
        return Err(FrameworkError::Error(format!(
            "hook_matcher tool value exceeds {MAX_LEN} characters"
        )));
    }
    if !s
        .chars()
        .all(|c| c.is_ascii_alphanumeric() || c == '_' || c == '-' || c == ':')
    {
        return Err(FrameworkError::Error(format!(
            "hook_matcher tool value '{s}' must contain only [a-zA-Z0-9_-:]"
        )));
    }
    Ok(())
}

pub fn validate_hook_matcher(v: &serde_json::Value) -> Result<(), FrameworkError> {
    match v {
        serde_json::Value::Null => Ok(()),
        serde_json::Value::String(s) => {
            const MAX_LEN: usize = 128;
            if s.len() > MAX_LEN {
                return Err(FrameworkError::Error(format!(
                    "hook_matcher string exceeds {MAX_LEN} characters"
                )));
            }
            Ok(())
        }
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
            Err(FrameworkError::Error(
                "hook_matcher must be null, a string, or an object with a single 'tool' key mapping to a string or array of strings".to_string(),
            ))
        }
        _ => Err(FrameworkError::Error(
            "hook_matcher must be null, a string, or an object with a single 'tool' key"
                .to_string(),
        )),
    }
}

pub fn validate_hook_args(
    events: &[HookEvent],
    matcher: Option<&Value>,
) -> Result<(), FrameworkError> {
    if events.is_empty() {
        return Err(FrameworkError::Error(
            "Hook tool has no hook_events configured; nothing to register".to_string(),
        ));
    }
    if let Some(m) = matcher {
        validate_hook_matcher(m)?;
    }
    Ok(())
}

// ── Hook idempotency helpers ──────────────────────────────────────────────────

/// Check if any Claude Code hooks entry already registers the given command.
pub(crate) fn command_exists_in_arr(arr: &Value, script_path: &Path) -> bool {
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

/// Check if any Gemini hooks entry already registers the given command.
/// Gemini format: `[{ "matcher": ..., "hooks": [{ "type": "command", "command": "..." }] }]`
pub(crate) fn gemini_command_exists_in_arr(arr: &Value, script_path: &Path) -> bool {
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

/// Check if any Copilot hooks entry already registers the given bash command.
/// Copilot format: `[{ "type": "command", "bash": "..." }]`
pub(crate) fn copilot_command_exists_in_arr(arr: &Value, script_path: &Path) -> bool {
    let script_str = script_path.to_string_lossy();
    arr.as_array()
        .map(|entries| {
            entries.iter().any(|entry| {
                entry
                    .get("bash")
                    .and_then(|s| s.as_str())
                    .map(|s| s == script_str)
                    .unwrap_or(false)
            })
        })
        .unwrap_or(false)
}
