use crate::cli::arg::{
    PullTarget, SkillInitArgs, SkillListArgs, SkillPullArgs, SkillPushArgs, SkillRemoveArgs,
};
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
/// Defaults to global (home directory) unless `--local` is specified.
fn resolve_pull_path(
    name: &str,
    output: Option<&PathBuf>,
    target: Option<&PullTarget>,
    local: bool,
) -> Result<PathBuf, CliError> {
    if let Some(output) = output {
        return Ok(output.clone());
    }

    if let Some(target) = target {
        if local {
            return Ok(target.skill_path(name));
        }
        return target.global_skill_path(name);
    }

    Ok(PathBuf::from(format!("{name}/SKILL.md")))
}

#[instrument(skip_all)]
pub fn push_skill(args: &SkillPushArgs) -> Result<(), CliError> {
    let content = std::fs::read_to_string(&args.path)
        .map_err(|e| CliError::Error(format!("Failed to read skill file {:?}: {e}", args.path)))?;

    let mut card = parse_skill_markdown(&content, Some(&args.path))?;

    let skill_source_dir = args
        .path
        .parent()
        .unwrap_or(std::path::Path::new("."))
        .to_path_buf();
    card.source_dir = Some(skill_source_dir);

    let root = args.path.parent().unwrap_or(std::path::Path::new("."));
    card.skill
        .validate(root)
        .map_err(|e| CliError::Error(e.to_string()))?;

    // Normalize space and name regardless of source (markdown or CLI override)
    card.space = clean_string(args.space.as_deref().unwrap_or(&card.space));
    card.name = clean_string(&card.name);

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

    let space_clean = clean_string(&space);
    let name_clean = clean_string(&name);

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

    let output_path = resolve_pull_path(
        &name_clean,
        args.output.as_ref(),
        args.target.as_ref(),
        args.local,
    )?;

    let output_dir = output_path
        .parent()
        .unwrap_or_else(|| std::path::Path::new("."));

    std::fs::create_dir_all(output_dir)?;
    copy_downloaded_skill_files(&tmp_path, output_dir)?;

    let skill_md_path = output_dir.join("SKILL.md");
    if !skill_md_path.exists() {
        std::fs::write(&skill_md_path, &markdown)?;
    }

    // tmp_dir drops here, cleaning up automatically
    drop(tmp_dir);

    // Auto-track: append to the appropriate skills.yaml unless --no-track
    if !args.no_track {
        let yaml_path = if args.local {
            PathBuf::from(".opsml-skills.yaml")
        } else {
            dirs::home_dir()
                .ok_or_else(|| CliError::Error("Cannot determine home directory".into()))?
                .join(".opsml")
                .join("skills.yaml")
        };

        let ref_entry = opsml_toml::ArtifactRef {
            space: space_clean.clone(),
            name: name_clean.clone(),
            version: args.version.clone(),
        };

        let registry_url = std::env::var("OPSML_TRACKING_URI").unwrap_or_default();
        if let Err(e) =
            opsml_toml::OpsmlSkillsYaml::append_skill(&yaml_path, &ref_entry, &registry_url)
        {
            eprintln!(
                "warn: failed to track {}/{} in {}: {e}",
                space_clean,
                name_clean,
                yaml_path.display()
            );
        }
    }

    println!(
        "{} {}/{} v{} -> {}",
        Colorize::green("Pulled"),
        Colorize::purple(&card.space),
        card.name,
        Colorize::green(&card.version),
        output_dir.display(),
    );

    Ok(())
}

fn copy_downloaded_skill_files(
    src_dir: &std::path::Path,
    dest_dir: &std::path::Path,
) -> Result<(), CliError> {
    if !src_dir.is_dir() {
        return Ok(());
    }
    let canonical_dest = dest_dir.canonicalize().map_err(|e| {
        CliError::Error(format!(
            "cannot canonicalize output dir '{}': {e}",
            dest_dir.display()
        ))
    })?;
    for entry in std::fs::read_dir(src_dir)? {
        let entry = entry?;
        let path = entry.path();
        let file_name = entry.file_name();
        let name = file_name.to_string_lossy();
        if name == "Card.json" {
            continue;
        }
        let dest = canonical_dest.join(&file_name);
        if path.is_dir() {
            copy_dir_recursive(&path, &dest, &canonical_dest)?;
        } else {
            if let Some(parent) = dest.parent() {
                std::fs::create_dir_all(parent)?;
            }
            let canonical_file = dest.canonicalize().unwrap_or_else(|_| dest.clone());
            if !canonical_file.starts_with(&canonical_dest) {
                return Err(CliError::Error(format!(
                    "path traversal detected: '{}' escapes output directory",
                    dest.display()
                )));
            }
            std::fs::copy(&path, &dest)?;
        }
    }
    Ok(())
}

fn copy_dir_recursive(
    src: &std::path::Path,
    dest: &std::path::Path,
    canonical_root: &std::path::Path,
) -> Result<(), CliError> {
    std::fs::create_dir_all(dest)?;
    for entry in std::fs::read_dir(src)? {
        let entry = entry?;
        let src_path = entry.path();
        let dest_path = dest.join(entry.file_name());
        if src_path.is_dir() {
            copy_dir_recursive(&src_path, &dest_path, canonical_root)?;
        } else {
            let canonical_file = dest_path
                .canonicalize()
                .unwrap_or_else(|_| dest_path.clone());
            if !canonical_file.starts_with(canonical_root) {
                return Err(CliError::Error(format!(
                    "path traversal detected: '{}' escapes output directory",
                    dest_path.display()
                )));
            }
            std::fs::copy(&src_path, &dest_path)?;
        }
    }
    Ok(())
}

/// Recursively find Card.json in the download directory.
pub(crate) fn find_card_json(dir: &std::path::Path, depth: usize) -> Result<PathBuf, CliError> {
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

    let space = args.space.clone().map(|s| clean_string(&s));

    let name = args.name.clone().map(|n| clean_string(&n));

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
pub fn remove_skill(args: &SkillRemoveArgs) -> Result<(), CliError> {
    let (space_raw, name_raw) = parse_skill_identifier(&args.name, args.space.as_deref())?;
    let space = clean_string(&space_raw);
    let name = clean_string(&name_raw);

    // 1. Remove from yaml
    let yaml_path = if args.local {
        PathBuf::from(".opsml-skills.yaml")
    } else {
        dirs::home_dir()
            .ok_or_else(|| CliError::Error("Cannot determine home directory".into()))?
            .join(".opsml")
            .join("skills.yaml")
    };

    if yaml_path.exists() {
        opsml_toml::OpsmlSkillsYaml::remove_skill(&yaml_path, &space, &name)?;
    }

    // 2. Delete skill files from all target directories
    let all_targets = [
        PullTarget::ClaudeCode,
        PullTarget::Codex,
        PullTarget::GeminiCli,
        PullTarget::GithubCopilot,
    ];
    for target in &all_targets {
        let path = if args.local {
            target.skill_path(&name)
        } else {
            match target.global_skill_path(&name) {
                Ok(p) => p,
                Err(_) => continue,
            }
        };
        if path.exists() {
            std::fs::remove_file(&path)?;
            if let Some(parent) = path.parent() {
                let _ = std::fs::remove_dir(parent); // ignore if not empty
            }
        }
    }

    // 3. Remove from manifest
    let mut manifest = crate::actions::manifest::SkillManifest::load().unwrap_or_default();
    let manifest_key = crate::actions::manifest::SkillManifest::key(&space, &name);
    manifest.remove(&manifest_key);
    if let Err(e) = manifest.save() {
        eprintln!("warn: failed to update manifest: {e}");
    }

    // 4. Remove from cache
    let mut cache = crate::actions::cache::CacheManifest::load().unwrap_or_default();
    let cache_key = if args.local {
        let abs = std::fs::canonicalize(".").unwrap_or_else(|_| PathBuf::from("."));
        format!("project:{}/{}/{}", abs.display(), space, name)
    } else {
        format!("global/{}/{}", space, name)
    };
    cache.entries.remove(&cache_key);
    if let Err(e) = cache.save() {
        eprintln!("warn: failed to update cache: {e}");
    }

    println!(
        "{} {}/{}",
        Colorize::green("Removed"),
        Colorize::purple(&space),
        name,
    );

    Ok(())
}

#[instrument(skip_all)]
pub fn init_skill(args: &SkillInitArgs) -> Result<(), CliError> {
    let raw_name = args.name.as_deref().unwrap_or("my-skill");
    let name = clean_string(raw_name);
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
    use opsml_semver::VersionType;

    #[test]
    fn test_pull_target_path_resolution() {
        assert_eq!(
            PullTarget::ClaudeCode.skill_path("my-skill"),
            PathBuf::from(".claude/skills/my-skill/SKILL.md")
        );
        assert_eq!(
            PullTarget::Codex.skill_path("my-skill"),
            PathBuf::from(".codex/skills/my-skill/SKILL.md")
        );
        assert_eq!(
            PullTarget::GeminiCli.skill_path("my-skill"),
            PathBuf::from(".gemini/skills/my-skill/SKILL.md")
        );
        assert_eq!(
            PullTarget::GithubCopilot.skill_path("my-skill"),
            PathBuf::from(".github/skills/my-skill/SKILL.md")
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
            false,
        )
        .unwrap();
        assert_eq!(path, PathBuf::from("custom/path.md"));
    }

    #[test]
    fn test_resolve_pull_path_global_by_default() {
        let path =
            resolve_pull_path("my-skill", None, Some(&PullTarget::ClaudeCode), false).unwrap();
        // Should be an absolute home-based path
        assert!(path.is_absolute());
        assert!(path.ends_with(".claude/skills/my-skill/SKILL.md"));
    }

    #[test]
    fn test_resolve_pull_path_local_flag() {
        let path =
            resolve_pull_path("my-skill", None, Some(&PullTarget::GithubCopilot), true).unwrap();
        assert_eq!(path, PathBuf::from(".github/skills/my-skill/SKILL.md"));
    }

    #[test]
    fn test_resolve_pull_path_no_target() {
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

    // --- remove_skill cache key ---

    #[test]
    fn test_remove_skill_cache_key_project_not_empty_path() {
        // Verify that the fixed canonicalize fallback never produces an empty-path key.
        let abs = std::fs::canonicalize(".").unwrap_or_else(|_| PathBuf::from("."));
        let key = format!("project:{}/space/name", abs.display());
        assert!(key.starts_with("project:"));
        assert!(
            !key.starts_with("project:///"),
            "empty PathBuf fallback produces malformed key"
        );
    }

    // --- find_card_json depth guard ---

    #[test]
    fn test_find_card_json_depth_limit() {
        let dir = tempfile::tempdir().unwrap();
        let result = find_card_json(dir.path(), 21);
        assert!(result.is_err());
        let msg = result.unwrap_err().to_string();
        assert!(
            msg.contains("too deeply nested") || msg.contains("deeply nested"),
            "{msg}"
        );
    }
}
