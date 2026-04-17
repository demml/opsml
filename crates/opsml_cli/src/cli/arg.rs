use std::path::PathBuf;

use crate::error::CliError;
use clap::{Args, ValueEnum};
use opsml_agent_cli::{
    AgentCliFramework, ClaudeCodeFramework, CodexFramework, CopilotFramework, GeminiCliFramework,
};
use opsml_semver::VersionType;
use opsml_service::service::DEFAULT_SERVICE_FILENAME;
use opsml_types::{RegistryType, contracts::CardQueryArgs};
use opsml_utils::clean_string;
#[cfg(feature = "python")]
use pyo3::{pyclass, pymethods};
use scouter_client::DriftType;

fn parse_version_type(s: &str) -> Result<VersionType, String> {
    s.parse::<VersionType>().map_err(|_| {
        format!(
            "Invalid version type '{s}'. Valid options: major, minor, patch, pre, build, pre_build"
        )
    })
}

fn parse_tool_type(s: &str) -> Result<opsml_types::contracts::tool::ToolType, String> {
    use opsml_types::contracts::tool::ToolType;
    match s {
        "ShellScript" | "shell_script" | "shell-script" => Ok(ToolType::ShellScript),
        "McpServer" | "mcp_server" | "mcp-server" => Ok(ToolType::McpServer),
        "ApiCall" | "api_call" | "api-call" => Ok(ToolType::ApiCall),
        "InternalFunction" | "internal_function" | "internal-function" => {
            Ok(ToolType::InternalFunction)
        }
        "SlashCommand" | "slash_command" | "slash-command" => Ok(ToolType::SlashCommand),
        "Hook" | "hook" => Ok(ToolType::Hook),
        other => Err(format!(
            "unknown tool type '{other}'; valid values: ShellScript, McpServer, ApiCall, InternalFunction, SlashCommand, Hook"
        )),
    }
}

fn default_spec_path() -> String {
    let path = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    let joined = path.join(DEFAULT_SERVICE_FILENAME);
    joined.to_string_lossy().to_string()
}

#[allow(clippy::wrong_self_convention)]
pub trait IntoQueryArgs {
    fn into_query_args(&self, registry_type: RegistryType) -> Result<CardQueryArgs, CliError>;
}

#[derive(Args)]
pub struct RegisterArgs {
    /// Path to the spec file. Defaults to `{current_dir}/opsmlspec.yaml`
    #[arg(long = "path", default_value = default_spec_path())]
    pub path: PathBuf,
}

#[derive(Args)]
pub struct LockArgs {
    /// Path to the spec file. Defaults to `{current_dir}/opsmlspec.yaml`
    #[arg(long = "path", default_value = default_spec_path())]
    pub path: PathBuf,
}

#[derive(Args)]
pub struct ListCards {
    /// space name
    #[arg(long = "space")]
    pub space: Option<String>,

    /// Name given to a card
    #[arg(long = "name")]
    pub name: Option<String>,

    /// Card version
    #[arg(long = "version")]
    pub version: Option<String>,

    /// Card uid
    #[arg(long = "uid")]
    pub uid: Option<String>,

    /// Card limit
    #[arg(long = "limit")]
    pub limit: Option<i32>,

    /// Tag name
    #[arg(long = "tags", use_value_delimiter = true, value_delimiter = ',')]
    pub tags: Option<Vec<String>>,

    /// max date
    #[arg(long = "max_date")]
    pub max_date: Option<String>,

    /// ignore release candidate
    #[arg(long = "sort_by_timestamp", default_value = "true")]
    pub sort_by_timestamp: bool,

    /// Service type
    #[arg(long = "service_type")]
    pub service_type: Option<String>,
}

impl IntoQueryArgs for ListCards {
    fn into_query_args(&self, registry_type: RegistryType) -> Result<CardQueryArgs, CliError> {
        let name = self
            .name
            .clone()
            .map(|name| clean_string(&name))
            .transpose()?;

        let space = self
            .space
            .clone()
            .map(|space| clean_string(&space))
            .transpose()?;

        Ok(CardQueryArgs {
            registry_type,
            space,
            name,
            version: self.version.clone(),
            uid: self.uid.clone(),
            limit: self.limit,
            tags: self.tags.clone(),
            max_date: self.max_date.clone(),
            sort_by_timestamp: Some(self.sort_by_timestamp),
        })
    }
}

#[derive(Args, Clone)]
#[cfg_attr(feature = "python", pyclass(skip_from_py_object))]
pub struct DownloadCard {
    /// Card space
    #[arg(long = "space")]
    pub space: Option<String>,

    /// Name given to card
    #[arg(long = "name")]
    pub name: Option<String>,

    /// Card version
    #[arg(long = "version")]
    pub version: Option<String>,

    /// Card uid
    #[arg(long = "uid")]
    pub uid: Option<String>,

    /// Write directory
    #[arg(long = "write-dir", default_value = "artifacts")]
    pub write_dir: String,
}

#[cfg(feature = "python")]
#[pymethods]
impl DownloadCard {
    /// Create a new DownloadCard
    #[new]
    #[pyo3(signature = (space=None, name=None, version=None, uid=None, write_dir=None))]
    pub fn new(
        space: Option<String>,
        name: Option<String>,
        version: Option<String>,
        uid: Option<String>,
        write_dir: Option<String>,
    ) -> Self {
        let write_dir = write_dir.unwrap_or_else(|| "artifacts".into());
        Self {
            space,
            name,
            version,
            uid,
            write_dir,
        }
    }
}

impl DownloadCard {
    pub fn write_path(&self) -> PathBuf {
        PathBuf::from(&self.write_dir)
    }

    pub fn service_path(&self) -> PathBuf {
        PathBuf::from(&self.write_dir)
    }
}

impl IntoQueryArgs for DownloadCard {
    fn into_query_args(&self, registry_type: RegistryType) -> Result<CardQueryArgs, CliError> {
        let name = self
            .name
            .clone()
            .map(|name| clean_string(&name))
            .transpose()?;

        let space = self
            .space
            .clone()
            .map(|space| clean_string(&space))
            .transpose()?;

        Ok(CardQueryArgs {
            uid: self.uid.clone(),
            name,
            space,
            version: self.version.clone(),
            registry_type,
            ..Default::default()
        })
    }
}

#[derive(Args)]
pub struct LaunchServer {
    /// Default port to use with the opsml server
    #[arg(long = "port", default_value = "8888")]
    pub port: i32,
}

#[derive(Args)]
pub struct KeyArgs {
    /// Password to use for the key
    #[arg(long = "key")]
    pub password: String,

    /// Number of rounds to use for the key
    #[arg(long = "rounds", default_value = "100000")]
    pub rounds: u32,
}

#[derive(Args, Clone)]
#[cfg_attr(feature = "python", pyclass(skip_from_py_object))]
pub struct ScouterArgs {
    /// Space name
    #[arg(long = "space")]
    pub space: String,

    /// Name
    #[arg(long = "name")]
    pub name: String,

    /// Version
    #[arg(long = "version")]
    pub version: String,

    /// Drift type
    #[arg(long = "drift-type")]
    pub drift_type: DriftType,

    /// Status
    #[arg(long = "active")]
    pub active: bool,

    #[arg(long = "deactivate-others", default_value = "false")]
    pub deactivate_others: bool,
}

#[cfg(feature = "python")]
#[pymethods]
impl ScouterArgs {
    /// Convert the ScouterArgs to a CardQueryArgs
    #[new]
    pub fn new(
        space: String,
        name: String,
        version: String,
        drift_type: DriftType,
        active: bool,
        deactivate_others: bool,
    ) -> Self {
        Self {
            space,
            name,
            version,
            drift_type,
            active,
            deactivate_others,
        }
    }
}

#[derive(Args, Clone)]
pub struct UiArgs {
    /// Version
    #[arg(long = "version")]
    pub version: Option<String>,

    /// Server binary url
    /// Optional URL to download the opsml-server binary from. This is typically used for testing purposes.
    #[arg(long = "server-url")]
    pub server_url: Option<String>,

    /// UI binary url
    /// Optional URL to download the opsml-ui binary from. This is typically used for testing purposes.
    #[arg(long = "ui-url")]
    pub ui_url: Option<String>,

    /// Development mode
    /// If set, the UI will execute the local debug server build and the ui build located in crates/opsml_server/opsml_ui
    /// This is only intended for development purposes.
    #[arg(long = "dev-mode", default_value = "false")]
    pub dev_mode: bool,
}

#[derive(Args, Clone)]
pub struct StopUiArgs {
    /// Development mode
    /// If set, the UI will execute the local debug server build and the ui build located in crates/opsml_server/opsml_ui
    /// This is only intended for development purposes.
    #[arg(long = "dev-mode", default_value = "false")]
    pub dev_mode: bool,
}

// -- Skill CLI types --

#[derive(Clone, Debug, PartialEq, clap::ValueEnum)]
pub enum PullTarget {
    ClaudeCode,
    Codex,
    GeminiCli,
    GithubCopilot,
}

impl PullTarget {
    pub fn skill_path(&self, name: &str) -> PathBuf {
        match self {
            Self::ClaudeCode => ClaudeCodeFramework.skill_path(name),
            Self::Codex => CodexFramework.skill_path(name),
            Self::GeminiCli => GeminiCliFramework.skill_path(name),
            Self::GithubCopilot => CopilotFramework.skill_path(name),
        }
    }

    pub fn global_skill_path(&self, name: &str) -> Result<PathBuf, CliError> {
        let result = match self {
            Self::ClaudeCode => ClaudeCodeFramework.global_skill_path(name),
            Self::Codex => CodexFramework.global_skill_path(name),
            Self::GeminiCli => GeminiCliFramework.global_skill_path(name),
            Self::GithubCopilot => CopilotFramework.global_skill_path(name),
        };
        result.map_err(|e| CliError::Error(e.to_string()))
    }
}

#[derive(Args, Clone)]
pub struct SkillPushArgs {
    /// Path to the skill markdown file
    pub path: PathBuf,

    /// Override the space for registration
    #[arg(long = "space")]
    pub space: Option<String>,

    /// Tags to apply to the skill (comma-separated)
    #[arg(long = "tags", use_value_delimiter = true, value_delimiter = ',')]
    pub tags: Option<Vec<String>>,

    /// Compatible CLI tools (comma-separated, e.g. claude-code,codex)
    #[arg(long = "tools", use_value_delimiter = true, value_delimiter = ',')]
    pub tools: Option<Vec<String>>,

    /// Version bump type (major, minor, patch, pre, build, pre_build)
    #[arg(long = "version-type", default_value = "minor", value_parser = parse_version_type)]
    pub version_type: VersionType,
}

#[derive(Args, Clone)]
pub struct SkillPullArgs {
    /// Skill identifier (space/name or just name with --space)
    pub name: String,

    /// Skill version
    #[arg(long = "version")]
    pub version: Option<String>,

    /// Space (alternative to space/name format)
    #[arg(long = "space")]
    pub space: Option<String>,

    /// Target CLI for auto-placement
    #[arg(long = "target")]
    pub target: Option<PullTarget>,

    /// Custom output path (overrides --target)
    #[arg(long = "output")]
    pub output: Option<PathBuf>,

    /// Write to current directory instead of home directory
    #[arg(long = "local", default_value = "false")]
    pub local: bool,

    /// Pull without adding to skills.yaml
    #[arg(long = "no-track", default_value = "false")]
    pub no_track: bool,
}

#[derive(Args, Clone)]
pub struct SkillListArgs {
    /// Filter by space
    #[arg(long = "space")]
    pub space: Option<String>,

    /// Filter by name
    #[arg(long = "name")]
    pub name: Option<String>,

    /// Filter by tags (comma-separated)
    #[arg(long = "tags", use_value_delimiter = true, value_delimiter = ',')]
    pub tags: Option<Vec<String>>,

    /// Filter by compatible tool
    #[arg(long = "tool")]
    pub tool: Option<String>,

    /// Maximum number of results
    #[arg(long = "limit")]
    pub limit: Option<i32>,
}

#[derive(Args, Clone)]
pub struct SkillInitArgs {
    /// Skill name for the template
    #[arg(long = "name")]
    pub name: Option<String>,

    /// Output path (defaults to ./SKILL.md)
    #[arg(long = "output")]
    pub output: Option<PathBuf>,
}

#[derive(Args, Clone)]
pub struct SkillRemoveArgs {
    /// Skill identifier (space/name or just name with --space)
    pub name: String,

    /// Space (alternative to space/name format)
    #[arg(long = "space")]
    pub space: Option<String>,

    /// Remove from project scope instead of global
    #[arg(long = "local", default_value = "false")]
    pub local: bool,
}

// ---- Agent CLI args ----

#[derive(Args, Clone)]
pub struct AgentPushArgs {
    /// Path to AGENT.md (YAML frontmatter + system prompt body)
    pub path: PathBuf,
    /// Override space for registration
    #[arg(long = "space")]
    pub space: Option<String>,
    /// Tags to apply (comma-separated)
    #[arg(long = "tags", use_value_delimiter = true, value_delimiter = ',')]
    pub tags: Option<Vec<String>>,
    /// Version bump type
    #[arg(long = "version-type", default_value = "minor", value_parser = parse_version_type)]
    pub version_type: VersionType,
}

#[derive(Args, Clone)]
pub struct AgentPullArgs {
    /// Agent identifier: space/name or name with --space
    pub name: String,
    #[arg(long = "version")]
    pub version: Option<String>,
    #[arg(long = "space")]
    pub space: Option<String>,
    /// Target CLI for auto-placement (claude-code, codex, gemini-cli, github-copilot)
    #[arg(long = "target")]
    pub target: Option<PullTarget>,
    /// Write to current directory instead of home directory
    #[arg(long = "local", default_value = "false")]
    pub local: bool,
}

#[derive(Args, Clone)]
pub struct AgentListArgs {
    /// Filter by space
    #[arg(long = "space")]
    pub space: Option<String>,
    /// Filter by agent name
    #[arg(long = "name")]
    pub name: Option<String>,
    /// Filter by tags (comma-separated)
    #[arg(long = "tags", use_value_delimiter = true, value_delimiter = ',')]
    pub tags: Option<Vec<String>>,
    /// Maximum number of results to return
    #[arg(long = "limit")]
    pub limit: Option<i32>,
}

#[derive(Args, Clone)]
pub struct AgentInitArgs {
    /// Agent name to use in the generated template
    #[arg(long = "name")]
    pub name: Option<String>,
    /// Output path (default: ./AGENT.md)
    #[arg(long = "output")]
    pub output: Option<PathBuf>,
}

#[derive(Args, Clone)]
pub struct SyncArgs {
    /// Force re-download even if cache entry is still fresh
    #[arg(long = "force", default_value = "false")]
    pub force: bool,

    /// Suppress all output (for hook usage)
    #[arg(long = "quiet", default_value = "false")]
    pub quiet: bool,

    /// Comma-separated target CLIs. Defaults to all four.
    #[arg(long = "target", use_value_delimiter = true, value_delimiter = ',')]
    pub targets: Option<Vec<PullTarget>>,

    /// Path to .opsml-skills.yaml (defaults to ./.opsml-skills.yaml)
    #[arg(long = "path")]
    pub path: Option<PathBuf>,
}

#[derive(Clone, ValueEnum)]
pub enum ConfigureTarget {
    #[value(name = "claude-code")]
    ClaudeCode,
    #[value(name = "codex")]
    Codex,
    #[value(name = "gemini-cli")]
    GeminiCli,
    #[value(name = "github-copilot")]
    GithubCopilot,
    #[value(name = "all")]
    All,
}

impl ConfigureTarget {
    pub fn to_pull_targets(&self) -> Vec<PullTarget> {
        match self {
            Self::ClaudeCode => vec![PullTarget::ClaudeCode],
            Self::Codex => vec![PullTarget::Codex],
            Self::GeminiCli => vec![PullTarget::GeminiCli],
            Self::GithubCopilot => vec![PullTarget::GithubCopilot],
            Self::All => vec![
                PullTarget::ClaudeCode,
                PullTarget::Codex,
                PullTarget::GeminiCli,
                PullTarget::GithubCopilot,
            ],
        }
    }
}

#[derive(Args, Clone)]
pub struct ConfigureArgs {
    /// Target CLI(s) to configure
    #[arg(long = "target", default_value = "all")]
    pub target: ConfigureTarget,

    /// Lazy mode: write startup hook instead of pulling skills immediately
    #[arg(long = "lazy", default_value = "false")]
    pub lazy: bool,
}

// ---- Tool CLI args ----

#[derive(Args, Clone)]
pub struct ToolPushArgs {
    /// Path to TOOL.md (YAML frontmatter + body)
    pub path: PathBuf,
    /// Override space for registration
    #[arg(long = "space")]
    pub space: Option<String>,
    /// Tags to apply (comma-separated)
    #[arg(long = "tags", use_value_delimiter = true, value_delimiter = ',')]
    pub tags: Option<Vec<String>>,
    /// Version bump type
    #[arg(long = "version-type", default_value = "minor", value_parser = parse_version_type)]
    pub version_type: VersionType,
}

#[derive(Args, Clone)]
pub struct ToolPullArgs {
    /// Tool identifier: space/name or name with --space
    pub name: String,
    #[arg(long = "version")]
    pub version: Option<String>,
    #[arg(long = "space")]
    pub space: Option<String>,
    /// Output directory (defaults to current directory)
    #[arg(long = "output")]
    pub output: Option<PathBuf>,
    /// Target CLI for hook registration (required for Hook tools)
    #[arg(long = "target")]
    pub target: Option<PullTarget>,
    /// Register hook globally (~/.claude/settings.json etc.) instead of project-local
    #[arg(long = "global", default_value_t = false)]
    pub global: bool,
}

#[derive(Args, Clone)]
pub struct ToolListArgs {
    /// Filter by space
    #[arg(long = "space")]
    pub space: Option<String>,
    /// Filter by name
    #[arg(long = "name")]
    pub name: Option<String>,
    /// Filter by tags (comma-separated)
    #[arg(long = "tags", use_value_delimiter = true, value_delimiter = ',')]
    pub tags: Option<Vec<String>>,
    /// Filter by tool type (ShellScript, SlashCommand, McpServer, ApiCall, InternalFunction, Hook)
    #[arg(long = "type", value_parser = parse_tool_type)]
    pub tool_type: Option<opsml_types::contracts::tool::ToolType>,
    /// Maximum number of results
    #[arg(long = "limit")]
    pub limit: Option<i32>,
}

#[derive(Args, Clone)]
pub struct ToolInitArgs {
    /// Tool name
    #[arg(long = "name")]
    pub name: Option<String>,
    /// Output path (defaults to ./TOOL.md)
    #[arg(long = "output")]
    pub output: Option<PathBuf>,
    /// Tool type template (shell, slash, mcp) — defaults to shell
    #[arg(long = "type", default_value = "shell")]
    pub tool_type: String,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_configure_target_all_returns_all_four_pull_targets() {
        let targets = ConfigureTarget::All.to_pull_targets();
        assert_eq!(targets.len(), 4);
        assert!(targets.contains(&PullTarget::ClaudeCode));
        assert!(targets.contains(&PullTarget::Codex));
        assert!(targets.contains(&PullTarget::GeminiCli));
        assert!(targets.contains(&PullTarget::GithubCopilot));
    }
}
