use super::error::ToolError;
use std::path::{Path, PathBuf};

pub trait SlashCommandInstaller {
    fn command_dir(&self) -> PathBuf;
    fn global_command_dir(&self) -> Result<PathBuf, ToolError>;
}

pub trait McpConfigInstaller {
    fn mcp_config_path(&self) -> PathBuf;
    fn merge_mcp_entry(&self, name: &str, entry: serde_json::Value) -> Result<(), ToolError>;
}

fn default_merge_mcp_entry(
    mcp_config_path: &Path,
    name: &str,
    entry: serde_json::Value,
) -> Result<(), ToolError> {
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

    let content = serde_json::to_string_pretty(&root)?;
    std::fs::write(&mcp_config_path, content)?;
    Ok(())
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
