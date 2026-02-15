use crate::cli::arg::{
    DownloadCard, KeyArgs, ListCards, LockArgs, RegisterArgs, ScouterArgs, UiArgs,
};
use clap::Parser;
use clap::Subcommand;
use clap::builder::Styles;
use clap::builder::styling::{AnsiColor, Effects};
use serde::Serialize;
use std::fmt;

// Borrowed from uv - really like their style

#[derive(Serialize)]
pub struct VersionInfo {
    version: String,
}

impl VersionInfo {
    pub fn new() -> Self {
        VersionInfo {
            version: opsml_version::version(),
        }
    }
}

impl Default for VersionInfo {
    fn default() -> Self {
        Self::new()
    }
}

impl fmt::Display for VersionInfo {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "opsml-cli version {}", self.version)
    }
}

impl From<VersionInfo> for clap::builder::Str {
    fn from(val: VersionInfo) -> Self {
        val.to_string().into()
    }
}

const STYLES: Styles = Styles::styled()
    .header(AnsiColor::Green.on_default().effects(Effects::BOLD))
    .usage(AnsiColor::Green.on_default().effects(Effects::BOLD))
    .literal(AnsiColor::Magenta.on_default().effects(Effects::BOLD))
    .placeholder(AnsiColor::Magenta.on_default());

#[derive(Parser)]
#[command(styles=STYLES)]
#[command(name = "OpsML", author, long_version = VersionInfo::new())]
#[command(about = "CLI tool for Interacting with OpsML")]
#[command(propagate_version = false)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Option<Commands>,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Lists cards from a registry
    ///
    /// # Example
    /// opsml list --registry data
    List {
        #[command(subcommand)]
        command: ListCommands,
    },

    /// Download card artifacts from a registry
    ///
    /// # Example
    /// opsml get model --name model_name --version 1.0.0
    Get {
        #[command(subcommand)]
        command: GetCommands,
    },

    /// Creates and locks an opsml service from an opsmlspec.yaml file
    ///
    /// # Example
    /// opsml lock
    Lock(LockArgs),

    ///  Show opsml version
    ///
    /// # Example
    /// opsml version
    Version,

    ///  Show opsml-cli info
    ///
    /// # Example
    /// opsml-cli info
    Info,

    /// Install/download an opsml app
    ///
    /// # Example
    /// opsml install service
    Install {
        #[command(subcommand)]
        command: InstallCommands,
    },

    /// Generate an encryption key from a password
    ///
    /// # Example
    /// opsml generate key
    Generate {
        #[command(subcommand)]
        command: GenerateCommands,
    },

    /// Update Scouter Drift Profile Status
    ///
    /// # Example
    /// opsml scouter update-profile --space space --name name --version version --drift-type drift_type --status status
    Scouter {
        #[command(subcommand)]
        command: ScouterCommands,
    },

    /// Start commands for Opsml
    Ui {
        #[command(subcommand)]
        command: UiCommands,
    },

    /// Run a demo of OpsML that populates a registry with example cards
    Demo,

    /// Validate the pyproject.toml file opsml tool configuration
    Validate,

    /// Register a service card from an opsmlspec.yaml file without generating a lock file.
    /// This is useful for when you want to register a service without the need to download
    /// any service artifacts in a subsequent step.
    Register(RegisterArgs),
}

#[derive(Subcommand)]
#[command(version = None)]
pub enum GetCommands {
    /// Download card model artifacts
    ///
    /// # Example
    ///
    /// opsml get model --name model_name --version 1.0.0
    Model(DownloadCard),

    /// Download service card artifacts
    ///
    Service(DownloadCard),

    /// Download agent card artifacts
    ///
    /// # Example
    /// opsml get agent --name agent_name --version 1.0.0
    Agent(DownloadCard),

    /// Download MCP card artifacts
    ///
    /// # Example
    /// opsml get mcp --name mcp_name --version 1.0.0
    Mcp(DownloadCard),
}

#[derive(Subcommand)]
#[command(version = None)]
pub enum ListCommands {
    Model(ListCards),
    Service(ListCards),
    Data(ListCards),
    Experiment(ListCards),
    Audit(ListCards),
    Prompt(ListCards),
}

#[derive(Subcommand)]
pub enum InstallCommands {
    Service,
}

#[derive(Subcommand)]
pub enum GenerateCommands {
    Key(KeyArgs),
}

#[derive(Subcommand)]
#[command(version = None)]
pub enum ScouterCommands {
    /// Update Scouter Drift Profile Status
    ///
    /// # Example
    /// opsml scouter update-profile --space space --name name --version version --drift-type drift_type --status status
    UpdateProfileStatus(ScouterArgs),
}

#[derive(Subcommand)]
#[command(version = None)]
pub enum UiCommands {
    /// Start a local OpsML UI
    ///
    /// # Example
    /// opsml start ui
    Start(UiArgs),

    /// Stop the currently running OpsML UI
    ///
    /// # Example
    /// opsml stop ui
    Stop,
}

pub const LOGO_TEXT: &str = "
 ██████  ██████  ███████ ███    ███ ██             ██████ ██      ██ 
██    ██ ██   ██ ██      ████  ████ ██            ██      ██      ██ 
██    ██ ██████  ███████ ██ ████ ██ ██      █████ ██      ██      ██ 
██    ██ ██           ██ ██  ██  ██ ██            ██      ██      ██ 
 ██████  ██      ███████ ██      ██ ███████        ██████ ███████ ██ 
";
