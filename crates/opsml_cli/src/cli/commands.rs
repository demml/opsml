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
    /// opsml-cli list-cards --registry data
    ListCards(ListCards),
    /// Download card artifacts from a registry
    ///
    /// # Example
    ///
    /// opsml-cli download-card --registry model --name model_name --version 1.0.0
    DownloadCard(DownloadCard),

    ///  Show opsml-cli version
    ///
    /// # Example
    ///
    /// opsml-cli version
    Version,

    ///  Show opsml-cli info
    ///
    /// # Example
    ///
    /// opsml-cli info
    Info,
}

pub const LOGO_TEXT: &str = "
 ██████  ██████  ███████ ███    ███ ██             ██████ ██      ██ 
██    ██ ██   ██ ██      ████  ████ ██            ██      ██      ██ 
██    ██ ██████  ███████ ██ ████ ██ ██      █████ ██      ██      ██ 
██    ██ ██           ██ ██  ██  ██ ██            ██      ██      ██ 
 ██████  ██      ███████ ██      ██ ███████        ██████ ███████ ██ 
";
