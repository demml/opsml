pub mod actions;
pub mod cli;

use crate::actions::{download_card, list_cards};
use crate::cli::{Cli, Commands};
use anyhow::{Context, Result};
use clap::Parser;
use owo_colors::OwoColorize;

#[cfg(feature = "server")]
use crate::actions::server::start_server;

pub const LOGO_TEXT: &str = "
 ██████  ██████  ███████ ███    ███ ██             ██████ ██      ██ 
██    ██ ██   ██ ██      ████  ████ ██            ██      ██      ██ 
██    ██ ██████  ███████ ██ ████ ██ ██      █████ ██      ██      ██ 
██    ██ ██           ██ ██  ██  ██ ██            ██      ██      ██ 
 ██████  ██      ███████ ██      ██ ███████        ██████ ███████ ██ 
";

fn main() -> Result<()> {
    let cli = Cli::parse();

    match &cli.command {
        Some(Commands::ListCards(args)) => {
            list_cards(args).context("Failed to list cards")?;
            Ok(())
        }
        Some(Commands::DownloadCard(args)) => {
            download_card(args).context("Failed to download card")?;
            Ok(())
        }

        #[cfg(feature = "server")]
        Some(Commands::LaunchServer(_args)) => {
            start_server().context("Failed to start server")?;
            Ok(())
        }

        Some(Commands::Version) => {
            println!(
                "opsml-cli version {}",
                env!("CARGO_PKG_VERSION").bold().green()
            );
            Ok(())
        }
        Some(Commands::Info) => {
            println!(
                "\n{}\nopsml-cli version {}\n2025 Demml\n",
                LOGO_TEXT.green(),
                env!("CARGO_PKG_VERSION").bold().purple(),
            );

            Ok(())
        }
        None => {
            println!("No command provided");
            Ok(())
        }
    }
}
