pub mod actions;
pub mod cli;
pub mod error;

use crate::actions::{download_card, list_cards};
use crate::cli::{Cli, Commands, GenerateCommands, GetCommands, InstallCommands, ListCommands};
use actions::download::download_deck;
pub use actions::{
    demo::run_python_code,
    generate_key,
    lock::install_app,
    ui::{start_ui, stop_ui},
    update_drift_profile_status,
    validate::validate_project,
};
use anyhow::Context;
use clap::Parser;
pub use cli::arg::ScouterArgs;
use cli::commands::{ScouterCommands, UiCommands};
use opsml_colors::Colorize;
use opsml_types::RegistryType;

pub use actions::lock::lock_project;

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
            println!(
                "opsml-cli version {}",
                Colorize::purple(&opsml_version::version())
            );
            Ok(())
        }
        Some(Commands::Info) => {
            println!(
                "\n{}\nopsml-cli version {}\n2025 Demml\n",
                Colorize::green(LOGO_TEXT),
                Colorize::purple(&opsml_version::version())
            );

            Ok(())
        }
        Some(Commands::Lock) => {
            println!("Locking project...");
            lock_project(None, None).context("Failed to lock project")?;
            Ok(())
        }

        Some(Commands::Generate { command }) => match command {
            GenerateCommands::Key(args) => {
                generate_key(&args.password, args.rounds).context("Failed to generate key")?;
                Ok(())
            }
        },
        Some(Commands::Scouter { command }) => match command {
            // Scouter commands can be added here
            ScouterCommands::UpdateProfileStatus(args) => {
                update_drift_profile_status(args)
                    .context("Failed to update Scouter profile status")?;
                Ok(())
            }
        },

        Some(Commands::Ui { command }) => match command {
            // Start commands can be added here
            UiCommands::Start(args) => {
                println!("Starting opsml-ui...");
                let default_version = opsml_version::version();
                let version = args.version.as_deref().unwrap_or_else(|| &default_version);
                start_ui(version, None).context("Failed to start opsml-ui")?;
                Ok(())
            }
            UiCommands::Stop => {
                println!("Stopping opsml-ui...");
                stop_ui().context("Failed to stop opsml-ui")?;
                Ok(())
            }
        },
        Some(Commands::Demo) => {
            println!("Running demo...");
            run_python_code().context("Failed to run demo")?;
            Ok(())
        }

        Some(Commands::Validate) => {
            println!("Validating project...");
            validate_project(None, None).context("Failed to validate project")?;
            Ok(())
        }

        None => {
            println!("No command provided");
            Ok(())
        }
    }
}
