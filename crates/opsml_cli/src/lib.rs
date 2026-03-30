pub mod actions;
pub mod cli;
pub mod error;
mod hooks;

use crate::actions::configure::configure_cli;
use crate::actions::skill::{init_skill, list_skills, pull_skill, push_skill, remove_skill};
use crate::actions::sync::sync_skills;
pub use crate::actions::{download_card, download_service, list_cards};
use crate::cli::{
    Cli, Commands, GenerateCommands, GetCommands, InstallCommands, LOGO_TEXT, ListCommands,
    SkillCommands,
};
pub use actions::{
    generate_key,
    lock::install_service,
    register::register_service,
    ui::{start_ui, stop_ui},
    update_drift_profile_status,
    validate::validate_project,
};
use anyhow::Context;
use clap::Parser;
pub use cli::arg::{DownloadCard, ScouterArgs};
use cli::commands::{ScouterCommands, UiCommands};
use opsml_colors::Colorize;
use opsml_types::RegistryType;

pub use actions::lock::lock_service;

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
            ListCommands::Service(args) => {
                list_cards(args, RegistryType::Service).context("Failed to list ServiceCards")
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
            GetCommands::Service(args) => download_service(args, RegistryType::Service)
                .context("Failed to download ServiceCard"),
            GetCommands::Agent(args) => download_service(args, RegistryType::Agent)
                .context("Failed to download Agent ServiceCard"),
            GetCommands::Mcp(args) => download_service(args, RegistryType::Mcp)
                .context("Failed to download MCP ServiceCard"),
        },

        Some(Commands::Install { command }) => match command {
            InstallCommands::Service => {
                let current_dir =
                    std::env::current_dir().context("Failed to get current directory")?;
                install_service(current_dir, None).context("Failed to install service")?;
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
        Some(Commands::Lock(args)) => {
            println!("Locking service...");
            // need to clone because lock_service is a pyo3-decorated function that takes ownership of the path
            lock_service(args.path.clone()).context("Failed to lock service")?;
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
                start_ui(version, &args.server_url, &args.ui_url, &args.dev_mode)
                    .context("Failed to start opsml-ui")?;
                Ok(())
            }
            UiCommands::Stop => {
                println!("Stopping opsml-ui...");
                stop_ui().context("Failed to stop opsml-ui")?;
                Ok(())
            }
        },
        Some(Commands::Validate) => {
            println!("Validating project...");
            validate_project(None, None).context("Failed to validate project")?;
            Ok(())
        }
        Some(Commands::Register(args)) => {
            println!("Registering service...");
            // need to clone because register_service is a pyo3-decorated function that takes ownership of the path
            register_service(args.path.clone()).context("Failed to register service")?;
            Ok(())
        }

        Some(Commands::Skill { command }) => match command {
            SkillCommands::Status => {
                actions::manifest::print_skill_status().context("Failed to show skill status")?;
                Ok(())
            }
            SkillCommands::Push(args) => push_skill(args).context("Failed to push skill"),
            SkillCommands::Pull(args) => pull_skill(args).context("Failed to pull skill"),
            SkillCommands::List(args) => list_skills(args).context("Failed to list skills"),
            SkillCommands::Init(args) => init_skill(args).context("Failed to init skill"),
            SkillCommands::Sync(args) => sync_skills(args).context("Failed to sync skills"),
            SkillCommands::Remove(args) => remove_skill(args).context("Failed to remove skill"),
        },

        Some(Commands::Configure(args)) => {
            configure_cli(args).context("Failed to configure CLI integration")
        }

        None => {
            println!("No command provided");
            Ok(())
        }
    }
}
