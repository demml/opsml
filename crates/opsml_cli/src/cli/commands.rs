use crate::cli::arg::{DownloadCard, KeyArgs, ListCards};
use clap::builder::styling::{AnsiColor, Effects};
use clap::builder::Styles;
use clap::command;
use clap::Parser;
use clap::Subcommand;
use serde::Serialize;
use std::fmt;

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
#[command(propagate_version = true)]
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

    /// Loads a pyproject.toml file and creates a lock file for an app
    ///
    /// # Example
    /// opsml lock
    Lock,

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
    /// opsml install app
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
}

#[derive(Subcommand)]
pub enum GetCommands {
    /// Download card model artifacts
    ///
    /// # Example
    ///
    /// opsml get model --name model_name --version 1.0.0
    Model(DownloadCard),

    /// Download card deck artifacts
    ///
    Deck(DownloadCard),
}

#[derive(Subcommand)]

pub enum ListCommands {
    Model(ListCards),
    Deck(ListCards),
    Data(ListCards),
    Experiment(ListCards),
    Audit(ListCards),
    Prompt(ListCards),
}

#[derive(Subcommand)]
pub enum InstallCommands {
    App,
}

#[derive(Subcommand)]
pub enum GenerateCommands {
    Key(KeyArgs),
}

pub const LOGO_TEXT: &str = "
 ██████  ██████  ███████ ███    ███ ██             ██████ ██      ██ 
██    ██ ██   ██ ██      ████  ████ ██            ██      ██      ██ 
██    ██ ██████  ███████ ██ ████ ██ ██      █████ ██      ██      ██ 
██    ██ ██           ██ ██  ██  ██ ██            ██      ██      ██ 
 ██████  ██      ███████ ██      ██ ███████        ██████ ███████ ██ 
";
