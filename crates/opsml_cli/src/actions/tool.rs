use crate::actions::skill::find_card_json;
use crate::cli::arg::{ToolInitArgs, ToolListArgs, ToolPullArgs, ToolPushArgs};
use crate::error::CliError;
use opsml_cards::parse_tool_markdown;
use opsml_colors::Colorize;
use opsml_registry::download::download_card_from_registry;
use opsml_registry::registry::CardRegistry;
use opsml_types::RegistryType;
use opsml_types::contracts::{CardList, CardQueryArgs};
use opsml_utils::clean_string;
use std::path::PathBuf;
use tracing::instrument;

fn parse_tool_identifier(
    identifier: &str,
    explicit_space: Option<&str>,
) -> Result<(String, String), CliError> {
    if let Some((space, name)) = identifier.split_once('/') {
        if space.is_empty() || name.is_empty() {
            return Err(CliError::Error(format!(
                "Invalid tool identifier '{identifier}': both space and name must be non-empty"
            )));
        }
        Ok((space.to_string(), name.to_string()))
    } else if let Some(space) = explicit_space {
        Ok((space.to_string(), identifier.to_string()))
    } else {
        Err(CliError::Error(
            "Could not determine tool space. Use --space or the space/name format".into(),
        ))
    }
}

#[instrument(skip_all)]
pub fn push_tool(args: &ToolPushArgs) -> Result<(), CliError> {
    let content = std::fs::read_to_string(&args.path).map_err(|e| {
        CliError::Error(format!(
            "Failed to read tool file {}: {e}",
            args.path.display()
        ))
    })?;

    let mut card: opsml_cards::ToolCard =
        parse_tool_markdown(&content).map_err(|e| CliError::Error(e.to_string()))?;

    card.space = clean_string(args.space.as_deref().unwrap_or(&card.space))?;
    card.name = clean_string(&card.name)?;

    if let Some(tags) = &args.tags {
        card.tags.extend(tags.iter().cloned());
    }

    let registry = CardRegistry::rust_new(&RegistryType::Tool)?;
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
pub fn pull_tool(args: &ToolPullArgs) -> Result<(), CliError> {
    let (space, name) = parse_tool_identifier(&args.name, args.space.as_deref())?;

    let space_clean = clean_string(&space)?;
    let name_clean = clean_string(&name)?;

    let query_args = CardQueryArgs {
        space: Some(space_clean),
        name: Some(name_clean),
        version: args.version.clone(),
        registry_type: RegistryType::Tool,
        limit: Some(1),
        ..Default::default()
    };

    let tmp_dir = tempfile::Builder::new()
        .prefix("opsml_tool_pull_")
        .tempdir()
        .map_err(|e| CliError::Error(format!("Failed to create temp dir: {e}")))?;
    let tmp_path = tmp_dir.path().to_path_buf();

    download_card_from_registry(&query_args, tmp_path.clone())?;

    let card_json = find_card_json(&tmp_path, 0)?;
    let card = opsml_cards::ToolCard::from_path(card_json)?;

    let output_dir = args.output.clone().unwrap_or_else(|| PathBuf::from("."));
    let is_hook = matches!(
        card.spec.tool_type,
        opsml_types::contracts::tool::ToolType::Hook
    );
    if is_hook && args.target.is_none() {
        return Err(CliError::Error(
            "Hook tools require --target (claudecode|geminicli|codex|githubcopilot)".into(),
        ));
    }
    let hook_installer = args.target.as_ref().map(|t| t.as_hook_installer());
    let installed_path = card
        .pull_artifacts(output_dir, hook_installer.as_deref(), args.global)
        .map_err(|e| CliError::Error(e.to_string()))?;

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
pub fn list_tools(args: &ToolListArgs) -> Result<(), CliError> {
    println!(
        "\nListing cards from {} registry",
        Colorize::green("tool")
    );

    let space = args.space.clone().map(|s| clean_string(&s)).transpose()?;
    let name = args.name.clone().map(|n| clean_string(&n)).transpose()?;

    let query_args = CardQueryArgs {
        space,
        name,
        tags: args.tags.clone(),
        limit: args.limit,
        registry_type: RegistryType::Tool,
        sort_by_timestamp: Some(true),
        ..Default::default()
    };

    let registry =
        opsml_registry::registries::card::OpsmlCardRegistry::new(RegistryType::Tool)?;
    let mut cards = registry.list_cards(&query_args)?;

    if let Some(tool_type) = &args.tool_type {
        cards.retain(|c| {
            if let opsml_types::contracts::CardRecord::Tool(r) = c {
                &r.tool_type == tool_type
            } else {
                false
            }
        });
    }

    CardList { cards }.as_tool_table();

    Ok(())
}

#[instrument(skip_all)]
pub fn init_tool(args: &ToolInitArgs) -> Result<(), CliError> {
    let raw_name = args.name.as_deref().unwrap_or("my-tool");
    let name = clean_string(raw_name)?;
    let name = if name.is_empty() {
        "my-tool".to_string()
    } else {
        name
    };

    let output = args
        .output
        .clone()
        .unwrap_or_else(|| PathBuf::from("TOOL.md"));

    if output.exists() {
        return Err(CliError::Error(format!(
            "File already exists: {}",
            output.display()
        )));
    }

    let template = match args.tool_type.as_str() {
        "slash" => format!(
            "---\nname: {name}\ndescription: \"TODO: Describe what this command does\"\ntoolType: SlashCommand\nallowedTools:\n  - Read\n  - Grep\n---\n# {name}\n\nTODO: Write the slash command prompt here.\n"
        ),
        "mcp" => format!(
            "---\nname: {name}\ndescription: \"TODO: Describe what this MCP server does\"\ntoolType: McpServer\nmcpServerName: \"{name}\"\n---\n# {name}\n\nTODO: Describe the MCP server configuration here.\n"
        ),
        "hook" => format!(
            "---\nname: {name}\ndescription: \"TODO: Describe what this hook does\"\ntoolType: Hook\nhookEvents:\n  - PostToolUse\nhookMatcher:\n  tool: Write\nrequiresApproval: false\n---\n#!/bin/bash\n# Hook body: runs after each Write tool call.\n"
        ),
        _ => format!(
            "---\nname: {name}\ndescription: \"TODO: Describe what this tool does\"\ntoolType: ShellScript\nscriptConfig:\n  script: \"echo hello\"\n  shell: \"/bin/bash\"\n---\n# {name}\n\nTODO: Write the shell script body here.\n"
        ),
    };

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
    use crate::cli::arg::ToolInitArgs;

    #[test]
    fn test_parse_tool_identifier_slash_format() {
        let (space, name) = parse_tool_identifier("my-space/my-tool", None).unwrap();
        assert_eq!(space, "my-space");
        assert_eq!(name, "my-tool");
    }

    #[test]
    fn test_parse_tool_identifier_empty_space() {
        assert!(parse_tool_identifier("/my-tool", None).is_err());
    }

    #[test]
    fn test_parse_tool_identifier_empty_name() {
        assert!(parse_tool_identifier("my-space/", None).is_err());
    }

    #[test]
    fn test_parse_tool_identifier_no_space_provided() {
        assert!(parse_tool_identifier("my-tool", None).is_err());
    }

    #[test]
    fn test_parse_tool_identifier_explicit_space_fallback() {
        let (space, name) = parse_tool_identifier("my-tool", Some("explicit-space")).unwrap();
        assert_eq!(space, "explicit-space");
        assert_eq!(name, "my-tool");
    }

    #[test]
    fn test_init_tool_creates_parseable_template() {
        let tmp = tempfile::tempdir().unwrap();
        let output = tmp.path().join("TOOL.md");

        let args = ToolInitArgs {
            name: Some("test-init".to_string()),
            output: Some(output.clone()),
            tool_type: "shell".to_string(),
        };
        init_tool(&args).unwrap();

        assert!(output.exists());
        let content = std::fs::read_to_string(&output).unwrap();
        let card = opsml_cards::parse_tool_markdown(&content).unwrap();
        assert_eq!(card.spec.name, "test-init");
    }

    #[test]
    fn test_init_tool_slash_creates_parseable_template() {
        let tmp = tempfile::tempdir().unwrap();
        let output = tmp.path().join("TOOL.md");

        let args = ToolInitArgs {
            name: Some("my-slash".to_string()),
            output: Some(output.clone()),
            tool_type: "slash".to_string(),
        };
        init_tool(&args).unwrap();

        assert!(output.exists());
        let content = std::fs::read_to_string(&output).unwrap();
        let card = opsml_cards::parse_tool_markdown(&content).unwrap();
        assert_eq!(card.spec.name, "my-slash");
        assert_eq!(
            card.spec.tool_type,
            opsml_types::contracts::tool::ToolType::SlashCommand
        );
    }

    #[test]
    fn test_init_tool_mcp_creates_parseable_template() {
        let tmp = tempfile::tempdir().unwrap();
        let output = tmp.path().join("TOOL.md");

        let args = ToolInitArgs {
            name: Some("my-mcp".to_string()),
            output: Some(output.clone()),
            tool_type: "mcp".to_string(),
        };
        init_tool(&args).unwrap();

        assert!(output.exists());
        let content = std::fs::read_to_string(&output).unwrap();
        let card = opsml_cards::parse_tool_markdown(&content).unwrap();
        assert_eq!(card.spec.name, "my-mcp");
        assert_eq!(
            card.spec.tool_type,
            opsml_types::contracts::tool::ToolType::McpServer
        );
    }

    #[test]
    fn test_init_tool_hook_creates_parseable_template() {
        let tmp = tempfile::tempdir().unwrap();
        let output = tmp.path().join("TOOL.md");

        let args = ToolInitArgs {
            name: Some("my-hook".to_string()),
            output: Some(output.clone()),
            tool_type: "hook".to_string(),
        };
        init_tool(&args).unwrap();

        assert!(output.exists());
        let content = std::fs::read_to_string(&output).unwrap();
        let card = opsml_cards::parse_tool_markdown(&content).unwrap();
        assert_eq!(card.spec.name, "my-hook");
        assert_eq!(
            card.spec.tool_type,
            opsml_types::contracts::tool::ToolType::Hook
        );
        assert!(!card.spec.hook_events.is_empty());
    }

    #[test]
    fn test_list_tools_type_filter_retain() {
        use opsml_types::contracts::{CardRecord, ToolCardClientRecord};

        fn make_tool_record(tool_type: &str) -> CardRecord {
            CardRecord::Tool(ToolCardClientRecord {
                uid: "uid".to_string(),
                created_at: chrono::Utc::now(),
                app_env: "dev".to_string(),
                space: "test".to_string(),
                name: "tool".to_string(),
                version: "0.0.1".to_string(),
                tags: vec![],
                opsml_version: "0.0.0".to_string(),
                username: "guest".to_string(),
                tool_type: tool_type.to_string(),
                args_schema: None,
                content_hash: None,
                download_count: 0,
                description: None,
            })
        }

        let mut cards = vec![
            make_tool_record("ShellScript"),
            make_tool_record("SlashCommand"),
            make_tool_record("McpServer"),
            make_tool_record("SlashCommand"),
        ];

        let filter = "SlashCommand".to_string();
        cards.retain(|c| {
            if let CardRecord::Tool(r) = c {
                &r.tool_type == &filter
            } else {
                false
            }
        });

        assert_eq!(cards.len(), 2);
        for c in &cards {
            if let CardRecord::Tool(r) = c {
                assert_eq!(r.tool_type, "SlashCommand");
            }
        }

        // Case sensitivity: "slashcommand" must not match "SlashCommand"
        let mut cards2 = vec![make_tool_record("SlashCommand")];
        let wrong_case = "slashcommand".to_string();
        cards2.retain(|c| {
            if let CardRecord::Tool(r) = c {
                &r.tool_type == &wrong_case
            } else {
                false
            }
        });
        assert_eq!(cards2.len(), 0, "case-insensitive match must not occur");
    }

    #[test]
    fn test_init_tool_rejects_existing_file() {
        let tmp = tempfile::tempdir().unwrap();
        let output = tmp.path().join("TOOL.md");
        std::fs::write(&output, "existing").unwrap();

        let args = ToolInitArgs {
            name: Some("test".to_string()),
            output: Some(output),
            tool_type: "shell".to_string(),
        };
        let err = init_tool(&args).unwrap_err();
        assert!(err.to_string().contains("already exists"));
    }
}
