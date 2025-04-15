pub mod actions;
pub mod cli;

use crate::actions::{download_card, list_cards};
use crate::cli::{Cli, Commands, GenerateCommands, GetCommands, InstallCommands, ListCommands};
use actions::download::download_deck;
use actions::generate::generate_pbkdf2_key;
pub use actions::lock::install_app;
use anyhow::Context;
use clap::Parser;
use opsml_colors::Colorize;
use opsml_types::RegistryType;

pub use actions::lock::lock_project;

pub const VERSION: &str = env!("CARGO_PKG_VERSION");

pub const LOGO_TEXT: &str = "
 ██████  ██████  ███████ ███    ███ ██             ██████ ██      ██ 
██    ██ ██   ██ ██      ████  ████ ██            ██      ██      ██ 
██    ██ ██████  ███████ ██ ████ ██ ██      █████ ██      ██      ██ 
██    ██ ██           ██ ██  ██  ██ ██            ██      ██      ██ 
 ██████  ██      ███████ ██      ██ ███████        ██████ ███████ ██ 
";

pub fn run_cli(args: Vec<String>) -> anyhow::Result<()> {
    let cli = Cli::parse_from(args.into_iter().skip(1));

    match &cli.command {
        Some(Commands::List { command }) => match command {
            ListCommands::Data(args) => {
                list_cards(args, RegistryType::Data).context("Failed to list DataCards")
            }
            ListCommands::Model(args) => {
                list_cards(args, RegistryType::Model).context("Failed to list ModelCards")
            }
            ListCommands::Deck(args) => {
                list_cards(args, RegistryType::Deck).context("Failed to list CardDecks")
            }
            ListCommands::Experiment(args) => {
                list_cards(args, RegistryType::Experiment).context("Failed to list ExperimentCards")
            }
            ListCommands::Audit(args) => {
                list_cards(args, RegistryType::Audit).context("Failed to list AuditCards")
            }
            ListCommands::Prompt(args) => {
                list_cards(args, RegistryType::Prompt).context("Failed to list PromptCards")
            }
        },
        Some(Commands::Get { command }) => match command {
            GetCommands::Model(args) => {
                download_card(args, RegistryType::Model).context("Failed to download ModelCard")
            }
            GetCommands::Deck(args) => download_deck(args).context("Failed to download CardDeck"),
        },

        Some(Commands::Install { command }) => match command {
            InstallCommands::App => {
                let current_dir =
                    std::env::current_dir().context("Failed to get current directory")?;
                install_app(current_dir, None).context("Failed to install app")?;
                Ok(())
            }
        },

        Some(Commands::Version) => {
            println!("opsml-cli version {}", Colorize::purple(VERSION));
            Ok(())
        }
        Some(Commands::Info) => {
            println!(
                "\n{}\nopsml-cli version {}\n2025 Demml\n",
                Colorize::green(LOGO_TEXT),
                Colorize::purple(VERSION)
            );

            Ok(())
        }
        Some(Commands::Lock) => {
            println!("opsml-cli lock");
            Ok(())
        }

        Some(Commands::GenerateKey { command }) => match command {
            GenerateCommands::Key(args) => {
                generate_pbkdf2_key(&args.password, args.rounds)
                    .context("Failed to generate key")?;
                Ok(())
            }
        },
        None => {
            println!("No command provided");
            Ok(())
        }
    }
}
