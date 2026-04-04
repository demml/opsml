use crate::actions::skill::find_card_json;
use crate::cli::arg::{AgentInitArgs, AgentListArgs, AgentPullArgs, AgentPushArgs};
use crate::error::CliError;
use opsml_cards::parse_subagent_markdown;
use opsml_colors::Colorize;
use opsml_registry::download::download_card_from_registry;
use opsml_registry::registry::CardRegistry;
use opsml_types::RegistryType;
use opsml_types::contracts::{CardList, CardQueryArgs};
use opsml_utils::clean_string;
use std::path::PathBuf;
use tracing::instrument;

fn parse_agent_identifier(
    identifier: &str,
    explicit_space: Option<&str>,
) -> Result<(String, String), CliError> {
    if let Some((space, name)) = identifier.split_once('/') {
        if space.is_empty() || name.is_empty() {
            return Err(CliError::Error(format!(
                "Invalid agent identifier '{identifier}': both space and name must be non-empty"
            )));
        }
        Ok((space.to_string(), name.to_string()))
    } else if let Some(space) = explicit_space {
        Ok((space.to_string(), identifier.to_string()))
    } else {
        Err(CliError::Error(
            "Could not determine agent space. Use --space or the space/name format".into(),
        ))
    }
}

#[instrument(skip_all)]
pub fn push_agent(args: &AgentPushArgs) -> Result<(), CliError> {
    let content = std::fs::read_to_string(&args.path).map_err(|e| {
        CliError::Error(format!(
            "Failed to read agent file {}: {e}",
            args.path.display()
        ))
    })?;

    let mut card: opsml_cards::SubAgentCard =
        parse_subagent_markdown(&content).map_err(|e| CliError::Error(e.to_string()))?;

    card.space = clean_string(args.space.as_deref().unwrap_or(&card.space))?;
    card.name = clean_string(&card.name)?;

    if let Some(tags) = &args.tags {
        card.tags.extend(tags.iter().cloned());
    }

    let registry = CardRegistry::rust_new(&RegistryType::SubAgent)?;
    registry.register_card_rs(&mut card, args.version_type.clone())?;

    println!(
        "{} {}/{} v{}",
        Colorize::green("Pushed"),
        Colorize::purple(&card.space),
        card.name,
        Colorize::green(&card.version),
    );

    Ok(())
}

#[instrument(skip_all)]
pub fn pull_agent(args: &AgentPullArgs) -> Result<(), CliError> {
    let (space, name) = parse_agent_identifier(&args.name, args.space.as_deref())?;

    let space_clean = clean_string(&space)?;
    let name_clean = clean_string(&name)?;

    let query_args = CardQueryArgs {
        space: Some(space_clean.clone()),
        name: Some(name_clean.clone()),
        version: args.version.clone(),
        registry_type: RegistryType::SubAgent,
        limit: Some(1),
        ..Default::default()
    };

    let tmp_dir = tempfile::Builder::new()
        .prefix("opsml_agent_pull_")
        .tempdir()
        .map_err(|e| CliError::Error(format!("Failed to create temp dir: {e}")))?;
    let tmp_path = tmp_dir.path().to_path_buf();

    download_card_from_registry(&query_args, tmp_path.clone())?;

    let card_json = find_card_json(&tmp_path, 0)?;
    let card = opsml_cards::SubAgentCard::from_path(card_json)?;

    let installed_path = if let Some(target) = &args.target {
        let cli_target = target.as_subagent_target();
        card.install(cli_target.as_ref(), !args.local)
            .map_err(|e| CliError::Error(e.to_string()))?
    } else {
        // Default: write canonical markdown to current directory
        let output_path = PathBuf::from(format!("{name_clean}.md"));
        let markdown = card
            .to_markdown()
            .map_err(|e| CliError::Error(e.to_string()))?;
        std::fs::write(&output_path, markdown)?;
        output_path
    };

    println!(
        "{} {}/{} v{} -> {}",
        Colorize::green("Pulled"),
        Colorize::purple(&card.space),
        card.name,
        Colorize::green(&card.version),
        installed_path.display(),
    );

    Ok(())
}

#[instrument(skip_all)]
pub fn list_agents(args: &AgentListArgs) -> Result<(), CliError> {
    println!(
        "\nListing cards from {} registry",
        Colorize::green("subagent")
    );

    let space = args.space.clone().map(|s| clean_string(&s)).transpose()?;
    let name = args.name.clone().map(|n| clean_string(&n)).transpose()?;

    let query_args = CardQueryArgs {
        space,
        name,
        tags: args.tags.clone(),
        limit: args.limit,
        registry_type: RegistryType::SubAgent,
        sort_by_timestamp: Some(true),
        ..Default::default()
    };

    let registry =
        opsml_registry::registries::card::OpsmlCardRegistry::new(RegistryType::SubAgent)?;
    let cards = registry.list_cards(&query_args)?;

    CardList { cards }.as_subagent_table();

    Ok(())
}

#[instrument(skip_all)]
pub fn init_agent(args: &AgentInitArgs) -> Result<(), CliError> {
    let raw_name = args.name.as_deref().unwrap_or("my-agent");
    let name = clean_string(raw_name)?;
    let name = if name.is_empty() {
        "my-agent".to_string()
    } else {
        name
    };

    let output = args
        .output
        .clone()
        .unwrap_or_else(|| PathBuf::from("AGENT.md"));

    if output.exists() {
        return Err(CliError::Error(format!(
            "File already exists: {}",
            output.display()
        )));
    }

    let template = format!(
        "---\nname: {name}\ndescription: \"TODO: Describe what this agent does\"\ncompatibleClis:\n  - ClaudeCode\n---\n# {name}\n\nTODO: Write your agent system prompt here.\n"
    );

    if let Some(parent) = output.parent()
        && !parent.as_os_str().is_empty()
    {
        std::fs::create_dir_all(parent)?;
    }

    std::fs::write(&output, template)?;

    println!("{} {}", Colorize::green("Created"), output.display());

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cli::arg::AgentInitArgs;

    #[test]
    fn test_parse_agent_identifier_slash_format() {
        let (space, name) = parse_agent_identifier("my-space/my-agent", None).unwrap();
        assert_eq!(space, "my-space");
        assert_eq!(name, "my-agent");
    }

    #[test]
    fn test_parse_agent_identifier_empty_space() {
        assert!(parse_agent_identifier("/my-agent", None).is_err());
    }

    #[test]
    fn test_parse_agent_identifier_empty_name() {
        assert!(parse_agent_identifier("my-space/", None).is_err());
    }

    #[test]
    fn test_parse_agent_identifier_no_space_provided() {
        assert!(parse_agent_identifier("my-agent", None).is_err());
    }

    #[test]
    fn test_parse_agent_identifier_explicit_space_fallback() {
        let (space, name) = parse_agent_identifier("my-agent", Some("explicit-space")).unwrap();
        assert_eq!(space, "explicit-space");
        assert_eq!(name, "my-agent");
    }

    #[test]
    fn test_init_agent_creates_parseable_template() {
        let tmp = tempfile::tempdir().unwrap();
        let output = tmp.path().join("AGENT.md");

        let args = AgentInitArgs {
            name: Some("test-init".to_string()),
            output: Some(output.clone()),
        };
        init_agent(&args).unwrap();

        assert!(output.exists());
        let content = std::fs::read_to_string(&output).unwrap();
        // Template must parse successfully with parse_subagent_markdown
        opsml_cards::parse_subagent_markdown(&content).unwrap();
    }

    #[test]
    fn test_init_agent_rejects_existing_file() {
        let tmp = tempfile::tempdir().unwrap();
        let output = tmp.path().join("AGENT.md");
        std::fs::write(&output, "existing").unwrap();

        let args = AgentInitArgs {
            name: Some("test".to_string()),
            output: Some(output),
        };
        let err = init_agent(&args).unwrap_err();
        assert!(err.to_string().contains("already exists"));
    }
}
