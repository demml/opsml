use crate::cli::arg::{PullTarget, SkillInitArgs, SkillListArgs, SkillPullArgs, SkillPushArgs};
use crate::error::CliError;
use opsml_cards::skill::card::parse_skill_markdown;
use opsml_colors::Colorize;
use opsml_registry::download::download_card_from_registry;
use opsml_registry::registries::card::OpsmlCardRegistry;
use opsml_registry::registry::CardRegistry;
use opsml_types::RegistryType;
use opsml_types::contracts::{CardList, CardQueryArgs, CardRecord};
use opsml_utils::clean_string;
use std::path::PathBuf;
use tracing::instrument;

/// Parse a skill identifier into (space, name).
///
/// Accepts `space/name` or just `name` (requires `explicit_space`).
fn parse_skill_identifier(
    identifier: &str,
    explicit_space: Option<&str>,
) -> Result<(String, String), CliError> {
    if let Some((space, name)) = identifier.split_once('/') {
        if space.is_empty() || name.is_empty() {
            return Err(CliError::Error(format!(
                "Invalid skill identifier '{identifier}': both space and name must be non-empty"
            )));
        }
        Ok((space.to_string(), name.to_string()))
    } else if let Some(space) = explicit_space {
        Ok((space.to_string(), identifier.to_string()))
    } else {
        Err(CliError::Error(
            "Could not determine skill space. Use --space or the space/name format".into(),
        ))
    }
}

/// Determine the output path for a pulled skill.
fn resolve_pull_path(
    name: &str,
    output: Option<&PathBuf>,
    target: Option<&PullTarget>,
    global: bool,
) -> Result<PathBuf, CliError> {
    if let Some(output) = output {
        return Ok(output.clone());
    }

    if let Some(target) = target {
        if global {
            return target.global_skill_path(name);
        }
        return Ok(target.skill_path(name));
    }

    Ok(PathBuf::from(format!("{name}/SKILL.md")))
}

#[instrument(skip_all)]
pub fn push_skill(args: &SkillPushArgs) -> Result<(), CliError> {
    let content = std::fs::read_to_string(&args.path)
        .map_err(|e| CliError::Error(format!("Failed to read skill file {:?}: {e}", args.path)))?;

    let mut card = parse_skill_markdown(&content, Some(&args.path))?;

    let root = args.path.parent().unwrap_or(std::path::Path::new("."));
    card.skill
        .validate(root)
        .map_err(|e| CliError::Error(e.to_string()))?;

    if let Some(space) = &args.space {
        card.space = clean_string(space)?;
    }

    if let Some(tags) = &args.tags {
        card.tags.extend(tags.iter().cloned());
    }

    if let Some(tools) = &args.tools {
        card.compatible_tools.extend(tools.iter().cloned());
    }

    let registry = CardRegistry::rust_new(&RegistryType::Skill)?;
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
pub fn pull_skill(args: &SkillPullArgs) -> Result<(), CliError> {
    let (space, name) = parse_skill_identifier(&args.name, args.space.as_deref())?;

    let space_clean = clean_string(&space)?;
    let name_clean = clean_string(&name)?;

    let query_args = CardQueryArgs {
        space: Some(space_clean.clone()),
        name: Some(name_clean.clone()),
        version: args.version.clone(),
        registry_type: RegistryType::Skill,
        limit: Some(1),
        ..Default::default()
    };

    let tmp_dir = tempfile::Builder::new()
        .prefix("opsml_skill_pull_")
        .tempdir()
        .map_err(|e| CliError::Error(format!("Failed to create temp dir: {e}")))?;
    let tmp_path = tmp_dir.path().to_path_buf();

    download_card_from_registry(&query_args, tmp_path.clone())?;

    // find the Card.json in the downloaded artifacts
    let card_json = find_card_json(&tmp_path, 0)?;
    let card = opsml_cards::SkillCard::from_path(card_json)?;

    let markdown = card.to_markdown()?;
    // tmp_dir drops here, cleaning up automatically

    let output_path = resolve_pull_path(
        &name_clean,
        args.output.as_ref(),
        args.target.as_ref(),
        args.global,
    )?;

    if let Some(parent) = output_path.parent() {
        std::fs::create_dir_all(parent)?;
    }

    std::fs::write(&output_path, markdown)?;

    println!(
        "{} {}/{} v{} -> {}",
        Colorize::green("Pulled"),
        Colorize::purple(&card.space),
        card.name,
        Colorize::green(&card.version),
        output_path.display(),
    );

    Ok(())
}

/// Recursively find Card.json in the download directory.
fn find_card_json(dir: &std::path::Path, depth: usize) -> Result<PathBuf, CliError> {
    if depth > 20 {
        return Err(CliError::Error(format!(
            "Artifact directory too deeply nested (>20 levels) at {:?}",
            dir
        )));
    }
    if dir.is_dir() {
        for entry in std::fs::read_dir(dir)? {
            let entry = entry?;
            let path = entry.path();
            if path.is_symlink() {
                continue;
            }
            if path.is_dir() {
                if let Ok(found) = find_card_json(&path, depth + 1) {
                    return Ok(found);
                }
            } else if path.file_name() == Some(std::ffi::OsStr::new("Card.json")) {
                return Ok(path);
            }
        }
    }
    Err(CliError::Error(format!(
        "Card.json not found in downloaded artifacts at {:?}",
        dir
    )))
}

#[instrument(skip_all)]
pub fn list_skills(args: &SkillListArgs) -> Result<(), CliError> {
    println!("\nListing cards from {} registry", Colorize::green("skill"));

    let space = args.space.clone().map(|s| clean_string(&s)).transpose()?;

    let name = args.name.clone().map(|n| clean_string(&n)).transpose()?;

    let query_args = CardQueryArgs {
        space,
        name,
        tags: args.tags.clone(),
        limit: args.limit,
        registry_type: RegistryType::Skill,
        sort_by_timestamp: Some(true),
        ..Default::default()
    };

    let registry = OpsmlCardRegistry::new(RegistryType::Skill)?;
    let mut cards = registry.list_cards(&query_args)?;

    // post-filter by compatible tool if specified
    if let Some(tool) = &args.tool {
        cards.retain(|card| {
            if let CardRecord::Skill(r) = card {
                r.compatible_tools.iter().any(|t| t == tool)
            } else {
                false
            }
        });
    }

    CardList { cards }.as_skill_table();

    Ok(())
}

#[instrument(skip_all)]
pub fn init_skill(args: &SkillInitArgs) -> Result<(), CliError> {
    let raw_name = args.name.as_deref().unwrap_or("my-skill");
    let name = clean_string(raw_name)?;
    let name = if name.is_empty() {
        "my-skill".to_string()
    } else {
        name
    };
    let output = args
        .output
        .clone()
        .unwrap_or_else(|| PathBuf::from("SKILL.md"));

    if output.exists() {
        return Err(CliError::Error(format!(
            "File already exists: {}",
            output.display()
        )));
    }

    let template = format!(
        "---\nname: \"{name}\"\ndescription: \"TODO: Describe what this skill does\"\nlicense: MIT\n---\n# {name}\n\nTODO: Write your skill instructions here.\n"
    );

    if let Some(parent) = output.parent()
        && !parent.as_os_str().is_empty()
    {
        std::fs::create_dir_all(parent)?;
    }

    std::fs::write(&output, template)?;

    println!("{} {}", Colorize::green("Created"), output.display(),);

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pull_target_path_resolution() {
        assert_eq!(
            PullTarget::ClaudeCode.skill_path("my-skill"),
            PathBuf::from(".claude/skills/my-skill/SKILL.md")
        );
        assert_eq!(
            PullTarget::Codex.skill_path("my-skill"),
            PathBuf::from(".agents/skills/my-skill/SKILL.md")
        );
        assert_eq!(
            PullTarget::GeminiCli.skill_path("my-skill"),
            PathBuf::from(".gemini/skills/my-skill/SKILL.md")
        );
        assert_eq!(
            PullTarget::GithubCopilot.skill_path("my-skill"),
            PathBuf::from(".github/copilot/skills/my-skill/SKILL.md")
        );
    }

    #[test]
    fn test_pull_target_global_path() {
        let path = PullTarget::ClaudeCode
            .global_skill_path("my-skill")
            .unwrap();
        assert!(path.is_absolute());
        assert!(path.ends_with(".claude/skills/my-skill/SKILL.md"));
    }

    #[test]
    fn test_parse_skill_identifier_with_space() {
        let (space, name) = parse_skill_identifier("my-space/my-skill", None).unwrap();
        assert_eq!(space, "my-space");
        assert_eq!(name, "my-skill");
    }

    #[test]
    fn test_parse_skill_identifier_explicit_space() {
        let (space, name) = parse_skill_identifier("my-skill", Some("my-space")).unwrap();
        assert_eq!(space, "my-space");
        assert_eq!(name, "my-skill");
    }

    #[test]
    fn test_parse_skill_identifier_missing_space() {
        assert!(parse_skill_identifier("my-skill", None).is_err());
    }

    #[test]
    fn test_parse_skill_identifier_empty_parts() {
        assert!(parse_skill_identifier("/my-skill", None).is_err());
        assert!(parse_skill_identifier("my-space/", None).is_err());
    }

    #[test]
    fn test_resolve_pull_path_output_override() {
        let path = resolve_pull_path(
            "my-skill",
            Some(&PathBuf::from("custom/path.md")),
            Some(&PullTarget::ClaudeCode),
            true,
        )
        .unwrap();
        assert_eq!(path, PathBuf::from("custom/path.md"));
    }

    #[test]
    fn test_resolve_pull_path_target_repo() {
        let path =
            resolve_pull_path("my-skill", None, Some(&PullTarget::GithubCopilot), false).unwrap();
        assert_eq!(
            path,
            PathBuf::from(".github/copilot/skills/my-skill/SKILL.md")
        );
    }

    #[test]
    fn test_resolve_pull_path_default() {
        let path = resolve_pull_path("my-skill", None, None, false).unwrap();
        assert_eq!(path, PathBuf::from("my-skill/SKILL.md"));
    }

    #[test]
    fn test_init_creates_template() {
        let tmp = tempfile::tempdir().unwrap();
        let output = tmp.path().join("SKILL.md");

        let args = SkillInitArgs {
            name: Some("test-skill".to_string()),
            output: Some(output.clone()),
        };

        init_skill(&args).unwrap();

        let content = std::fs::read_to_string(&output).unwrap();
        assert!(content.contains("name: \"test-skill\""));
        assert!(content.contains("description: \"TODO:"));
        assert!(content.contains("# test-skill"));
    }

    #[test]
    fn test_init_refuses_overwrite() {
        let tmp = tempfile::tempdir().unwrap();
        let output = tmp.path().join("SKILL.md");
        std::fs::write(&output, "existing").unwrap();

        let args = SkillInitArgs {
            name: None,
            output: Some(output),
        };

        assert!(init_skill(&args).is_err());
    }

    #[test]
    fn test_init_creates_nested_path() {
        let tmp = tempfile::tempdir().unwrap();
        let output = tmp.path().join("nested/deep/SKILL.md");

        let args = SkillInitArgs {
            name: Some("deep-skill".to_string()),
            output: Some(output.clone()),
        };

        init_skill(&args).unwrap();

        assert!(output.exists());
        let content = std::fs::read_to_string(&output).unwrap();
        assert!(content.contains("name: \"deep-skill\""));
    }

    #[test]
    fn test_find_card_json_at_root() {
        let tmp = tempfile::tempdir().unwrap();
        std::fs::write(tmp.path().join("Card.json"), "{}").unwrap();
        let found = find_card_json(tmp.path(), 0).unwrap();
        assert_eq!(found.file_name().unwrap(), "Card.json");
    }

    #[test]
    fn test_find_card_json_nested() {
        let tmp = tempfile::tempdir().unwrap();
        let nested = tmp.path().join("a").join("b");
        std::fs::create_dir_all(&nested).unwrap();
        std::fs::write(nested.join("Card.json"), "{}").unwrap();
        let found = find_card_json(tmp.path(), 0).unwrap();
        assert_eq!(found.file_name().unwrap(), "Card.json");
    }

    #[test]
    fn test_find_card_json_not_found() {
        let tmp = tempfile::tempdir().unwrap();
        std::fs::write(tmp.path().join("other.json"), "{}").unwrap();
        assert!(find_card_json(tmp.path(), 0).is_err());
    }

    #[test]
    fn test_push_skill_invalid_version_type() {
        let tmp = tempfile::tempdir().unwrap();
        let skill_path = tmp.path().join("SKILL.md");
        std::fs::write(
            &skill_path,
            "---\nname: test-skill\ndescription: \"A test skill\"\n---\n# test-skill\n",
        )
        .unwrap();

        let args = SkillPushArgs {
            path: skill_path,
            space: None,
            tags: None,
            tools: None,
            version_type: VersionType::Minor, // valid type, this test checks parse-time safety
        };

        // With typed VersionType, invalid values are rejected by clap at parse time.
        // Verify that a valid VersionType is accepted without registry errors (registry will fail
        // with a config error since no registry is configured in unit tests, but not a version error).
        let result = push_skill(&args);
        // Should fail with a registry/config error, not a version type error
        assert!(result.is_err());
        let err_msg = result.unwrap_err().to_string();
        assert!(
            !err_msg.contains("Invalid version type"),
            "Error should not be about version type: {err_msg}"
        );
    }
}
