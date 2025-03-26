pub mod actions;
pub mod cli;

use crate::actions::list_cards;
use crate::cli::{Cli, Commands};

use anyhow::{Context, Result};
use clap::Parser;
use owo_colors::OwoColorize;

fn main() -> Result<()> {
    let cli = Cli::parse();

    match &cli.command {
        Some(Commands::ListCards(args)) => {
            list_cards(args).context("Failed to list cards")?;
            Ok(())
        }
        Some(Commands::DownloadCard(download_card)) => {
            println!("Downloading card: {:#?}", download_card);
            Ok(())
        }
        Some(Commands::LaunchServer(launch_server)) => {
            println!("Launching server: {:#?}", launch_server);
            Ok(())
        }
        Some(Commands::Version) => {
            println!("opsml-cli version: {}", env!("CARGO_PKG_VERSION").green());
            Ok(())
        }
        Some(Commands::Info) => {
            println!("{}", cli::LOGO_TEXT.green());
            println!("opsml-cli version: {}", env!("CARGO_PKG_VERSION").green());
            Ok(())
        }
        None => {
            println!("No command provided");
            Ok(())
        }
    }
}
