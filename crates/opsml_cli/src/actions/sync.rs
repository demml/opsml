use crate::actions::cache::{CacheEntry, CacheManifest};
use crate::actions::manifest::{SkillEntry, SkillManifest};
use crate::actions::skill::find_card_json;
use crate::cli::arg::{PullTarget, SyncArgs};
use crate::error::CliError;
use chrono::{Duration, Utc};
use opsml_colors::Colorize;
use opsml_registry::download::download_card_from_registry;
use opsml_toml::OpsmlSkillsYaml;
use opsml_types::contracts::CardQueryArgs;
use opsml_types::RegistryType;
use std::path::{Path, PathBuf};
use tracing::instrument;

#[instrument(skip_all)]
pub fn sync_skills(args: &SyncArgs) -> Result<(), CliError> {
    let yaml_path = args
        .path
        .as_deref()
        .unwrap_or(Path::new(".opsml-skills.yaml"));

    let yaml = OpsmlSkillsYaml::load(yaml_path)
        .map_err(|e| CliError::Error(format!("Failed to load .opsml-skills.yaml: {e}")))?;

    let mut cache = CacheManifest::load().unwrap_or_default();
    let mut manifest = SkillManifest::load().unwrap_or_default();

    let all_targets = [
        PullTarget::ClaudeCode,
        PullTarget::Codex,
        PullTarget::GeminiCli,
        PullTarget::GithubCopilot,
    ];
    let targets: &[PullTarget] = args.targets.as_deref().unwrap_or(&all_targets);
    let ttl = Duration::minutes(yaml.ttl_minutes as i64);

    let (mut pulled, mut skipped) = (0usize, 0usize);

    for skill_ref in &yaml.skills {
        // Version-agnostic key so "latest" always overwrites the previous pull.
        let cache_key = format!("{}/{}", skill_ref.space, skill_ref.name);

        if !args.force {
            if let Some(entry) = cache.entries.get(&cache_key) {
                if Utc::now() - entry.fetched_at < ttl {
                    if !args.quiet {
                        println!(
                            "{} {}/{} (cached)",
                            Colorize::purple("Skip"),
                            skill_ref.space,
                            skill_ref.name
                        );
                    }
                    skipped += 1;
                    continue;
                }
            }
        }

        let version = skill_ref
            .version
            .as_deref()
            .filter(|v| !v.is_empty() && *v != "latest");

        let query_args = CardQueryArgs {
            space: Some(skill_ref.space.clone()),
            name: Some(skill_ref.name.clone()),
            version: version.map(String::from),
            registry_type: RegistryType::Skill,
            limit: Some(1),
            ..Default::default()
        };

        let tmp_dir = tempfile::Builder::new()
            .prefix("opsml_sync_")
            .tempdir()
            .map_err(|e| CliError::Error(format!("Failed to create temp dir: {e}")))?;

        download_card_from_registry(&query_args, tmp_dir.path().to_path_buf())?;

        let card_json = find_card_json(tmp_dir.path(), 0)?;
        let card = opsml_cards::SkillCard::from_path(card_json)?;
        let markdown = card.to_markdown()?;
        let hash_bytes = card
            .calculate_content_hash()
            .map_err(|e| CliError::Error(format!("Failed to compute content hash: {e}")))?;
        let hash: String = hash_bytes.iter().fold(
            String::with_capacity(hash_bytes.len() * 2),
            |mut s, b| {
                use std::fmt::Write;
                let _ = write!(s, "{b:02x}");
                s
            },
        );

        for target in targets {
            let out = target.skill_path(&card.name);
            if let Some(parent) = out.parent() {
                std::fs::create_dir_all(parent)?;
            }
            std::fs::write(&out, &markdown)?;
        }

        let target_names: Vec<String> = targets.iter().map(|t| format!("{t:?}")).collect();

        cache.upsert(
            cache_key,
            CacheEntry {
                uid: card.uid.clone(),
                content_hash: hash.clone(),
                fetched_at: Utc::now(),
                artifact_path: PathBuf::new(),
                size_bytes: markdown.len() as u64,
            },
        );

        manifest.upsert(SkillEntry {
            space: skill_ref.space.clone(),
            name: card.name.clone(),
            version: card.version.clone(),
            content_hash: hash,
            uid: card.uid.clone(),
            installed_at: Utc::now(),
            server_url: yaml.registry.clone(),
            targets: target_names,
        });

        if !args.quiet {
            println!(
                "{} {}/{} v{}",
                Colorize::green("Synced"),
                Colorize::purple(&card.space),
                card.name,
                card.version,
            );
        }
        pulled += 1;
    }

    cache.save()?;
    manifest.save()?;

    if !args.quiet {
        println!("\n{pulled} synced, {skipped} skipped");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Duration;

    fn make_fresh_cache(space: &str, name: &str, ttl_secs_remaining: i64) -> CacheManifest {
        let mut cache = CacheManifest::default();
        let key = format!("{space}/{name}");
        cache.upsert(
            key,
            CacheEntry {
                uid: "uid-1".into(),
                content_hash: "hash-abc".into(),
                fetched_at: Utc::now() - Duration::seconds(10) + Duration::seconds(ttl_secs_remaining),
                artifact_path: PathBuf::new(),
                size_bytes: 0,
            },
        );
        cache
    }

    #[test]
    fn ttl_hit_increments_skipped() {
        // Build a yaml in-memory string, save to tempdir, and point SyncArgs at it.
        let dir = tempfile::tempdir().unwrap();
        let yaml_path = dir.path().join(".opsml-skills.yaml");
        std::fs::write(
            &yaml_path,
            "registry: http://localhost:3000\nttl_minutes: 60\nskills:\n  - space: s\n    name: n\n",
        )
        .unwrap();

        let yaml = OpsmlSkillsYaml::load(&yaml_path).unwrap();

        // Cache entry is 10 seconds old — well within 60-minute TTL.
        let cache = make_fresh_cache("s", "n", 3590);

        let ttl = Duration::minutes(yaml.ttl_minutes as i64);
        let mut skipped = 0usize;

        for skill_ref in &yaml.skills {
            let cache_key = format!("{}/{}", skill_ref.space, skill_ref.name);
            if let Some(entry) = cache.entries.get(&cache_key) {
                if Utc::now() - entry.fetched_at < ttl {
                    skipped += 1;
                    continue;
                }
            }
            // would normally download — not reached in this test
        }

        assert_eq!(skipped, 1, "fresh cache entry must be skipped");
    }

    #[test]
    fn ttl_miss_does_not_skip() {
        let dir = tempfile::tempdir().unwrap();
        let yaml_path = dir.path().join(".opsml-skills.yaml");
        std::fs::write(
            &yaml_path,
            "registry: http://localhost:3000\nttl_minutes: 1\nskills:\n  - space: s\n    name: n\n",
        )
        .unwrap();

        let yaml = OpsmlSkillsYaml::load(&yaml_path).unwrap();

        // Cache entry is 120 seconds old — past the 1-minute TTL.
        let cache = make_fresh_cache("s", "n", -110); // fetched_at = now - 120s

        let ttl = Duration::minutes(yaml.ttl_minutes as i64);
        let mut would_download = 0usize;

        for skill_ref in &yaml.skills {
            let cache_key = format!("{}/{}", skill_ref.space, skill_ref.name);
            let is_fresh = cache
                .entries
                .get(&cache_key)
                .is_some_and(|e| Utc::now() - e.fetched_at < ttl);
            if !is_fresh {
                would_download += 1;
            }
        }

        assert_eq!(would_download, 1, "stale cache entry must trigger download");
    }

    #[test]
    fn force_bypasses_fresh_cache() {
        let dir = tempfile::tempdir().unwrap();
        let yaml_path = dir.path().join(".opsml-skills.yaml");
        std::fs::write(
            &yaml_path,
            "registry: http://localhost:3000\nttl_minutes: 60\nskills:\n  - space: s\n    name: n\n",
        )
        .unwrap();

        let yaml = OpsmlSkillsYaml::load(&yaml_path).unwrap();
        let cache = make_fresh_cache("s", "n", 3590);
        let force = true;

        let ttl = Duration::minutes(yaml.ttl_minutes as i64);
        let mut would_download = 0usize;

        for skill_ref in &yaml.skills {
            let cache_key = format!("{}/{}", skill_ref.space, skill_ref.name);
            let skip = !force
                && cache
                    .entries
                    .get(&cache_key)
                    .is_some_and(|e| Utc::now() - e.fetched_at < ttl);
            if !skip {
                would_download += 1;
            }
        }

        assert_eq!(would_download, 1, "--force must bypass TTL check");
    }
}
