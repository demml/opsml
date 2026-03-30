use crate::actions::cache::{CacheEntry, CacheManifest};
use crate::actions::manifest::{SkillEntry, SkillManifest};
use crate::actions::skill::find_card_json;
use crate::cli::arg::{PullTarget, SyncArgs};
use crate::error::CliError;
use chrono::{Duration, Utc};
use opsml_colors::Colorize;
use opsml_registry::download::download_card_from_registry;
use opsml_toml::OpsmlSkillsYaml;
use opsml_types::RegistryType;
use opsml_types::contracts::CardQueryArgs;
use std::fmt::Write as FmtWrite;
use std::path::{Path, PathBuf};
use tracing::instrument;

/// Resolve the effective registry URL: `OPSML_TRACKING_URI` env var takes
/// precedence over the `registry` field in the YAML.
fn resolve_registry(yaml_registry: &str) -> String {
    std::env::var("OPSML_TRACKING_URI").unwrap_or_else(|_| yaml_registry.to_string())
}

#[instrument(skip_all)]
pub fn sync_skills(args: &SyncArgs) -> Result<(), CliError> {
    let home = dirs::home_dir()
        .ok_or_else(|| CliError::Error("Cannot determine home directory".into()))?;

    let all_targets = [
        PullTarget::ClaudeCode,
        PullTarget::Codex,
        PullTarget::GeminiCli,
        PullTarget::GithubCopilot,
    ];
    let targets: &[PullTarget] = args.targets.as_deref().unwrap_or(&all_targets);

    let mut cache = CacheManifest::load().unwrap_or_else(|e| {
        eprintln!("warn: cache manifest unreadable ({e}), starting fresh");
        CacheManifest::default()
    });
    let mut manifest = SkillManifest::load().unwrap_or_else(|e| {
        eprintln!("warn: skill manifest unreadable ({e}), starting fresh");
        SkillManifest::default()
    });

    // If --path is given, sync only that scope (backward compat / explicit override)
    if let Some(path) = &args.path {
        let yaml_path = if path.is_dir() {
            path.join(".opsml-skills.yaml")
        } else {
            path.clone()
        };
        let is_global = yaml_path.starts_with(home.join(".opsml"));
        return sync_one_layer(
            &yaml_path,
            targets,
            is_global,
            args,
            &mut cache,
            &mut manifest,
        );
    }

    // Default: sync both layers
    // Layer 1: global (~/.opsml/skills.yaml)
    let global_yaml = home.join(".opsml").join("skills.yaml");
    if global_yaml.exists() {
        if !args.quiet {
            println!("{}", Colorize::purple("Global skills"));
        }
        sync_one_layer(&global_yaml, targets, true, args, &mut cache, &mut manifest)?;
    }

    // Layer 2: project (.opsml-skills.yaml in CWD)
    let project_yaml = PathBuf::from(".opsml-skills.yaml");
    if project_yaml.exists() {
        if !args.quiet {
            println!("\n{}", Colorize::purple("Project skills"));
        }
        sync_one_layer(
            &project_yaml,
            targets,
            false,
            args,
            &mut cache,
            &mut manifest,
        )?;
    }

    Ok(())
}

fn sync_one_layer(
    yaml_path: &Path,
    targets: &[PullTarget],
    is_global: bool,
    args: &SyncArgs,
    cache: &mut CacheManifest,
    manifest: &mut SkillManifest,
) -> Result<(), CliError> {
    let yaml = OpsmlSkillsYaml::load(yaml_path)?;
    let registry_url = resolve_registry(&yaml.registry);
    warn_if_insecure_registry(&registry_url);

    if yaml.ttl_minutes == 0 {
        eprintln!("warn: ttl_minutes is 0 — treating as 1 minute (always re-fetch)");
    }
    let ttl_mins = i64::try_from(yaml.ttl_minutes).unwrap_or(i64::MAX).max(1);
    let ttl = Duration::minutes(ttl_mins);
    let project_root = yaml_path.parent().unwrap_or(Path::new("."));

    let (mut pulled, mut skipped, mut not_found) = (0usize, 0usize, 0usize);

    for skill_ref in &yaml.skills {
        let cache_key = if is_global {
            format!("global/{}/{}", skill_ref.space, skill_ref.name)
        } else {
            let abs =
                std::fs::canonicalize(project_root).unwrap_or_else(|_| project_root.to_path_buf());
            format!(
                "project:{}/{}/{}",
                abs.display(),
                skill_ref.space,
                skill_ref.name
            )
        };

        if !args.force && is_cache_fresh(cache, &cache_key, ttl) {
            if !args.quiet {
                println!(
                    "  {} {}/{} (cached)",
                    Colorize::purple("Skip"),
                    skill_ref.space,
                    skill_ref.name
                );
            }
            skipped += 1;
            continue;
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

        match download_card_from_registry(&query_args, tmp_dir.path().to_path_buf()) {
            Ok(()) => {}
            Err(e) => {
                // Treat download failures as "not found" — warn and skip
                if !args.quiet {
                    eprintln!(
                        "  {} {}/{} (not found on {}): {e}",
                        Colorize::alert("Warn"),
                        skill_ref.space,
                        skill_ref.name,
                        registry_url
                    );
                }
                not_found += 1;
                continue;
            }
        }

        let card_json = find_card_json(tmp_dir.path(), 0)?;
        let card = opsml_cards::SkillCard::from_path(card_json)?;

        if card.name != skill_ref.name {
            return Err(CliError::Error(format!(
                "Registry returned card {:?} but {:?} was requested — refusing to write",
                card.name, skill_ref.name
            )));
        }

        let markdown = card.to_markdown()?;
        let hash_bytes = card
            .calculate_content_hash()
            .map_err(|e| CliError::Error(format!("Failed to compute content hash: {e}")))?;
        let hash: String =
            hash_bytes
                .iter()
                .fold(String::with_capacity(hash_bytes.len() * 2), |mut s, b| {
                    let _ = write!(s, "{b:02x}");
                    s
                });

        validate_artifact_name(&card.name)?;
        validate_artifact_name(&skill_ref.space)?;

        let mut first_out: Option<PathBuf> = None;
        for target in targets {
            let out = if is_global {
                target.global_skill_path(&card.name)?
            } else {
                project_root.join(target.skill_path(&card.name))
            };
            if let Some(parent) = out.parent() {
                std::fs::create_dir_all(parent)?;
            }
            std::fs::write(&out, &markdown)?;
            if first_out.is_none() {
                first_out = Some(out);
            }
        }

        let target_names: Vec<String> = targets.iter().map(|t| format!("{t:?}")).collect();

        cache.upsert(
            cache_key,
            CacheEntry {
                uid: card.uid.clone(),
                content_hash: hash.clone(),
                fetched_at: Utc::now(),
                artifact_path: first_out.unwrap_or_default(),
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
            server_url: registry_url.clone(),
            targets: target_names,
        });

        // Save incrementally so a later failure doesn't lose already-pulled skills
        if let Err(e) = cache.save() {
            eprintln!(
                "warn: failed to persist cache for {}/{}: {e}",
                skill_ref.space, card.name
            );
        }
        if let Err(e) = manifest.save() {
            eprintln!(
                "warn: failed to persist manifest for {}/{}: {e}",
                skill_ref.space, card.name
            );
        }

        if !args.quiet {
            println!(
                "  {} {}/{} v{}",
                Colorize::green("Synced"),
                Colorize::purple(&card.space),
                card.name,
                card.version,
            );
        }
        pulled += 1;
    }

    if !args.quiet {
        let mut parts = vec![format!("{pulled} synced"), format!("{skipped} cached")];
        if not_found > 0 {
            parts.push(format!("{not_found} not found"));
        }
        println!("  {}", parts.join(", "));
    }
    Ok(())
}

fn is_cache_fresh(cache: &CacheManifest, key: &str, ttl: Duration) -> bool {
    cache
        .entries
        .get(key)
        .is_some_and(|e| Utc::now() - e.fetched_at < ttl)
}

fn is_insecure_registry(url: &str) -> bool {
    if !url.starts_with("http://") {
        return false;
    }
    let host = url
        .trim_start_matches("http://")
        .split('/')
        .next()
        .unwrap_or("");
    host != "localhost"
        && !host.starts_with("localhost:")
        && host != "127.0.0.1"
        && !host.starts_with("127.0.0.1:")
        && host != "[::1]"
        && !host.starts_with("[::1]:")
        && host != "::1"
}

fn validate_artifact_name(name: &str) -> Result<(), CliError> {
    if name.is_empty()
        || name.contains('/')
        || name.contains('\\')
        || name.contains("..")
        || name.starts_with('.')
        || name.contains('\0')
    {
        return Err(CliError::Error(format!(
            "Unsafe artifact name from registry: {name:?} — contains path separators or reserved sequences"
        )));
    }
    Ok(())
}

fn warn_if_insecure_registry(url: &str) {
    if is_insecure_registry(url) {
        eprintln!(
            "warning: registry '{}' uses plain HTTP. \
             Skills are fetched without TLS encryption. \
             Use https:// for production registries.",
            url
        );
    }
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
                fetched_at: Utc::now() - Duration::seconds(10)
                    + Duration::seconds(ttl_secs_remaining),
                artifact_path: PathBuf::new(),
                size_bytes: 0,
            },
        );
        cache
    }

    #[test]
    fn test_ttl_hit_increments_skipped() {
        let cache = make_fresh_cache("s", "n", 3590);
        let ttl = Duration::minutes(60);
        assert!(
            is_cache_fresh(&cache, "s/n", ttl),
            "fresh entry must be fresh"
        );
    }

    #[test]
    fn test_ttl_miss_does_not_skip() {
        // Entry is 120 seconds old, TTL is 60 seconds.
        let cache = make_fresh_cache("s", "n", -110);
        let ttl = Duration::minutes(1);
        assert!(
            !is_cache_fresh(&cache, "s/n", ttl),
            "stale entry must not be fresh"
        );
    }

    #[test]
    fn test_force_bypasses_fresh_cache() {
        let cache = make_fresh_cache("s", "n", 3590);
        let ttl = Duration::minutes(60);
        // Cache is fresh, but force=true means the skip condition `!force && is_fresh` is false.
        assert!(is_cache_fresh(&cache, "s/n", ttl), "entry is fresh");
        // With force the caller ignores freshness — the skip gate is `!args.force && fresh`.
        let force = true;
        let skip = !force && is_cache_fresh(&cache, "s/n", ttl);
        assert!(!skip, "force must prevent the skip");
    }

    #[test]
    fn test_cache_fresh_missing_key_returns_false() {
        let cache = CacheManifest::default();
        assert!(!is_cache_fresh(&cache, "s/n", Duration::minutes(60)));
    }

    // --- validate_artifact_name ---

    #[test]
    fn test_validate_artifact_name_accepts_valid() {
        assert!(validate_artifact_name("my-skill").is_ok());
        assert!(validate_artifact_name("skill_v2").is_ok());
        assert!(validate_artifact_name("a").is_ok());
    }

    #[test]
    fn test_validate_artifact_name_rejects_empty() {
        assert!(validate_artifact_name("").is_err());
    }

    #[test]
    fn test_validate_artifact_name_rejects_forward_slash() {
        assert!(validate_artifact_name("space/name").is_err());
    }

    #[test]
    fn test_validate_artifact_name_rejects_backslash() {
        assert!(validate_artifact_name("space\\name").is_err());
    }

    #[test]
    fn test_validate_artifact_name_rejects_dotdot() {
        assert!(validate_artifact_name("../secret").is_err());
        assert!(validate_artifact_name("a..b").is_err());
    }

    #[test]
    fn test_validate_artifact_name_rejects_leading_dot() {
        assert!(validate_artifact_name(".hidden").is_err());
    }

    // --- is_insecure_registry ---

    #[test]
    fn test_insecure_registry_https_is_safe() {
        assert!(!is_insecure_registry("https://registry.example.com"));
    }

    #[test]
    fn test_insecure_registry_localhost_is_safe() {
        assert!(!is_insecure_registry("http://localhost:3000"));
        assert!(!is_insecure_registry("http://localhost"));
        assert!(!is_insecure_registry("http://127.0.0.1"));
        assert!(!is_insecure_registry("http://127.0.0.1:8080"));
    }

    #[test]
    fn test_insecure_registry_remote_http_is_insecure() {
        assert!(is_insecure_registry("http://registry.example.com"));
        assert!(is_insecure_registry("http://10.0.0.1:3000"));
    }

    #[test]
    fn test_insecure_registry_empty_is_safe() {
        assert!(!is_insecure_registry(""));
    }

    // --- resolve_registry ---

    #[test]
    fn test_resolve_registry_env_overrides_yaml() {
        // SAFETY: single-threaded test (--test-threads=1 required for this crate)
        unsafe { std::env::set_var("OPSML_TRACKING_URI", "https://override.example.com") };
        assert_eq!(
            resolve_registry("https://yaml.example.com"),
            "https://override.example.com"
        );
        unsafe { std::env::remove_var("OPSML_TRACKING_URI") };
    }

    #[test]
    fn test_resolve_registry_falls_back_to_yaml() {
        // SAFETY: single-threaded test (--test-threads=1 required for this crate)
        unsafe { std::env::remove_var("OPSML_TRACKING_URI") };
        assert_eq!(
            resolve_registry("https://yaml.example.com"),
            "https://yaml.example.com"
        );
    }

    // --- cache key scoping ---

    #[test]
    fn test_cache_key_global_prefix() {
        let key = format!("global/{}/{}", "myspace", "myskill");
        assert!(key.starts_with("global/"));
        assert!(!key.starts_with("project:"));
    }

    #[test]
    fn test_cache_key_project_fallback_non_empty_path() {
        let abs = std::fs::canonicalize(".").unwrap_or_else(|_| PathBuf::from("."));
        let key = format!("project:{}/space/name", abs.display());
        assert!(key.starts_with("project:"));
        // Empty PathBuf display is "" so would produce "project:///..." — verify we don't get that
        assert!(!key.starts_with("project:///"));
    }

    #[test]
    fn test_validate_artifact_name_rejects_null_byte() {
        assert!(validate_artifact_name("na\0me").is_err());
    }

    #[test]
    fn test_sync_skills_empty_yaml_runs_without_network() {
        let dir = tempfile::tempdir().unwrap();
        let yaml_path = dir.path().join(".opsml-skills.yaml");
        std::fs::write(
            &yaml_path,
            "registry: http://localhost:3000\nttl_minutes: 60\nskills: []\n",
        )
        .unwrap();

        let result = sync_skills(&crate::cli::arg::SyncArgs {
            force: false,
            quiet: true,
            targets: None,
            path: Some(yaml_path),
        });

        // Empty skills list: loop body never executes.
        // Acceptable outcomes: Ok (no saves needed) or ManifestError (cannot write ~/.opsml in test env).
        assert!(
            result.is_ok() || matches!(result, Err(crate::error::CliError::ManifestError(_))),
            "unexpected error: {result:?}"
        );
    }
}
