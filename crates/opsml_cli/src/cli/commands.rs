use crate::cli::arg::{DownloadCard, ListCards};

use clap::command;
use clap::Parser;
use clap::Subcommand;

#[derive(Parser)]
#[command(about = "CLI tool for Interacting with an Opsml server")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Option<Commands>,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Lists cards from a registry
    ///
    /// # Example
    ///
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

    ///  Show opsml version
    ///
    /// # Example
    ///
    /// opsml version
    Version,

    ///  Show opsml-cli info
    ///
    /// # Example
    ///
    /// opsml-cli info
    Info,
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

pub const LOGO_TEXT: &str = "
 ██████  ██████  ███████ ███    ███ ██             ██████ ██      ██ 
██    ██ ██   ██ ██      ████  ████ ██            ██      ██      ██ 
██    ██ ██████  ███████ ██ ████ ██ ██      █████ ██      ██      ██ 
██    ██ ██           ██ ██  ██  ██ ██            ██      ██      ██ 
 ██████  ██      ███████ ██      ██ ███████        ██████ ███████ ██ 
";
