use crate::error::FrameworkError;
use opsml_types::contracts::subagent::SubAgentSpec;
use opsml_types::contracts::tool::HookEvent;
use serde_json::Value;
use std::path::{Path, PathBuf};

/// Unified per-framework trait for agentic CLI artifact installation.
///
/// Each CLI framework (Claude Code, Codex, Gemini CLI, GitHub Copilot) has a single
/// implementing struct that owns all path logic, config serialization, and artifact
/// installation for that framework. Callers dispatch through a `PullTarget::as_framework()`
/// factory instead of holding four separate trait objects.
///
/// # Path conventions
/// Every method that returns a path has both a project-local variant (relative to cwd)
/// and a `global` parameter / separate method for the user-global location under `$HOME`.
pub trait AgentCliFramework: Send + Sync {
    fn name(&self) -> &'static str;

    // ── Skill paths ─────────────────────────────────────────────────────────

    /// Project-local path for a skill's `SKILL.md`, relative to cwd.
    fn skill_path(&self, name: &str) -> PathBuf;

    /// User-global path for a skill's `SKILL.md`, under `$HOME`.
    fn global_skill_path(&self, name: &str) -> Result<PathBuf, FrameworkError>;

    // ── SubAgent serialization + paths ───────────────────────────────────────

    /// Directory where agent config files live (local or global).
    fn agent_dir(&self, global: bool) -> Result<PathBuf, FrameworkError>;

    /// Filename for an agent config (e.g. `{name}.md` or `{name}.toml`).
    fn agent_file_name(&self, name: &str) -> String;

    /// Serialize a `SubAgentSpec` into the framework-native config format.
    fn serialize_agent(&self, spec: &SubAgentSpec) -> Result<String, FrameworkError>;

    // ── Slash commands ───────────────────────────────────────────────────────

    /// Directory where slash-command markdown files live (local or global).
    fn command_dir(&self, global: bool) -> PathBuf;

    // ── MCP config ───────────────────────────────────────────────────────────

    /// Path to the framework's MCP server config file (relative to cwd).
    fn mcp_config_path(&self) -> PathBuf;

    /// Merge a single MCP server entry into the framework's MCP config file.
    fn merge_mcp_entry(&self, name: &str, entry: Value) -> Result<(), FrameworkError>;

    // ── Hooks ────────────────────────────────────────────────────────────────

    /// Install a hook script into the framework's hook config file.
    ///
    /// Implementations must be idempotent: calling this twice with the same
    /// `script_path` must not register the hook twice.
    fn install_hook(
        &self,
        name: &str,
        script_path: &Path,
        events: &[HookEvent],
        matcher: Option<&Value>,
        global: bool,
    ) -> Result<(), FrameworkError>;

    /// Whether this framework supports lifecycle hooks.
    fn supports_hooks(&self) -> bool {
        true
    }
}
