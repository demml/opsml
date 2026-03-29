use crate::actions::sync::sync_skills;
use crate::cli::arg::{ConfigureArgs, PullTarget, SyncArgs};
use crate::error::CliError;
use opsml_colors::Colorize;
use opsml_toml::OpsmlSkillsYaml;
use std::fmt::Write as FmtWrite;
use std::path::Path;

pub fn configure_cli(args: &ConfigureArgs) -> Result<(), CliError> {
    let base = args.path.as_deref().unwrap_or(Path::new("."));

    // Scaffold .opsml-skills.yaml if missing
    let yaml_path = base.join(".opsml-skills.yaml");
    if !yaml_path.exists() {
        OpsmlSkillsYaml::scaffold(&yaml_path)
            .map_err(|e| CliError::Error(format!("Failed to scaffold .opsml-skills.yaml: {e}")))?;
        println!("{} {}", Colorize::green("Created"), yaml_path.display());
    }

    // Idempotent .gitignore update
    append_gitignore(base, ".opsml-cache/")?;

    if args.lazy {
        configure_lazy(args, base)
    } else {
        configure_eager(args, base)
    }
}

fn configure_eager(args: &ConfigureArgs, base: &Path) -> Result<(), CliError> {
    sync_skills(&SyncArgs {
        force: false,
        quiet: false,
        targets: Some(args.target.to_pull_targets()),
        path: Some(base.join(".opsml-skills.yaml")),
    })
}

fn configure_lazy(args: &ConfigureArgs, base: &Path) -> Result<(), CliError> {
    let hooks_dir = base.join(".opsml-cache").join("hooks");
    std::fs::create_dir_all(&hooks_dir)?;
    let hook_path = hooks_dir.join("startup.sh");
    std::fs::write(&hook_path, crate::hooks::STARTUP_SH)?;

    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(&hook_path, std::fs::Permissions::from_mode(0o755))?;
    }

    println!("{} {}", Colorize::green("Created"), hook_path.display());

    let hook_cmd = format!("bash {}", hook_path.display());
    for target in &args.target.to_pull_targets() {
        register_hook(target, base, &hook_cmd)?;
    }
    Ok(())
}

/// Idempotent: appends `entry` to .gitignore only if not already present.
fn append_gitignore(base: &Path, entry: &str) -> Result<(), CliError> {
    let path = base.join(".gitignore");
    let existing = if path.exists() {
        std::fs::read_to_string(&path)?
    } else {
        String::new()
    };
    if existing.lines().any(|l| l.trim() == entry) {
        return Ok(());
    }
    let mut content = existing;
    if !content.is_empty() && !content.ends_with('\n') {
        content.push('\n');
    }
    let _ = writeln!(content, "{entry}");
    std::fs::write(&path, content)?;
    Ok(())
}

fn register_hook(target: &PullTarget, base: &Path, cmd: &str) -> Result<(), CliError> {
    match target {
        PullTarget::ClaudeCode => register_claude_hook(base, cmd),
        PullTarget::Codex => register_codex_hook(base, cmd),
        PullTarget::GeminiCli => register_gemini_hook(base, cmd),
        PullTarget::GithubCopilot => register_github_copilot_hook(base, cmd),
    }
}

fn register_claude_hook(base: &Path, cmd: &str) -> Result<(), CliError> {
    let path = base.join(".claude").join("settings.json");
    let mut settings: serde_json::Value = if path.exists() {
        serde_json::from_str(&std::fs::read_to_string(&path)?)
            .unwrap_or(serde_json::json!({}))
    } else {
        serde_json::json!({})
    };
    settings["hooks"]["UserPromptSubmit"] = serde_json::json!([{
        "matcher": "",
        "hooks": [{ "type": "command", "command": cmd }]
    }]);
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::write(&path, serde_json::to_string_pretty(&settings)?)?;
    println!("{} {}", Colorize::green("Updated"), path.display());
    Ok(())
}

fn register_codex_hook(base: &Path, cmd: &str) -> Result<(), CliError> {
    append_hook_to_sh(base, ".codex", "startup.sh", cmd)
}

fn register_gemini_hook(base: &Path, cmd: &str) -> Result<(), CliError> {
    let path = base.join(".gemini").join("settings.json");
    let mut settings: serde_json::Value = if path.exists() {
        serde_json::from_str(&std::fs::read_to_string(&path)?)
            .unwrap_or(serde_json::json!({}))
    } else {
        serde_json::json!({})
    };
    settings["startup_hook"] = serde_json::Value::String(cmd.to_string());
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::write(&path, serde_json::to_string_pretty(&settings)?)?;
    println!("{} {}", Colorize::green("Updated"), path.display());
    Ok(())
}

fn register_github_copilot_hook(base: &Path, cmd: &str) -> Result<(), CliError> {
    append_hook_to_sh(base, ".github/copilot", "startup.sh", cmd)
}

/// Idempotent append of `cmd` to `{base}/{dir}/{filename}`.
fn append_hook_to_sh(
    base: &Path,
    dir: &str,
    filename: &str,
    cmd: &str,
) -> Result<(), CliError> {
    let dir_path = base.join(dir);
    std::fs::create_dir_all(&dir_path)?;
    let path = dir_path.join(filename);
    let existing = if path.exists() {
        std::fs::read_to_string(&path)?
    } else {
        String::new()
    };
    if !existing.contains(cmd) {
        let mut content = existing;
        if !content.is_empty() && !content.ends_with('\n') {
            content.push('\n');
        }
        let _ = writeln!(content, "{cmd}");
        std::fs::write(&path, &content)?;
    }
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(&path, std::fs::Permissions::from_mode(0o755))?;
    }
    println!("{} {}", Colorize::green("Updated"), path.display());
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn append_gitignore_creates_file() {
        let dir = tempdir().unwrap();
        append_gitignore(dir.path(), ".opsml-cache/").unwrap();
        let content = std::fs::read_to_string(dir.path().join(".gitignore")).unwrap();
        assert!(content.contains(".opsml-cache/"));
    }

    #[test]
    fn append_gitignore_is_idempotent() {
        let dir = tempdir().unwrap();
        append_gitignore(dir.path(), ".opsml-cache/").unwrap();
        append_gitignore(dir.path(), ".opsml-cache/").unwrap();
        let content = std::fs::read_to_string(dir.path().join(".gitignore")).unwrap();
        assert_eq!(content.matches(".opsml-cache/").count(), 1);
    }

    #[test]
    fn append_gitignore_preserves_existing_content() {
        let dir = tempdir().unwrap();
        std::fs::write(dir.path().join(".gitignore"), "target/\n").unwrap();
        append_gitignore(dir.path(), ".opsml-cache/").unwrap();
        let content = std::fs::read_to_string(dir.path().join(".gitignore")).unwrap();
        assert!(content.contains("target/"));
        assert!(content.contains(".opsml-cache/"));
    }

    #[test]
    fn configure_cli_creates_yaml() {
        let dir = tempdir().unwrap();
        let args = ConfigureArgs {
            target: crate::cli::arg::ConfigureTarget::ClaudeCode,
            lazy: true, // use lazy to avoid hitting registry
            path: Some(dir.path().to_path_buf()),
        };
        // will fail at hook writing since we don't have full lazy impl deps here
        // but yaml creation should succeed first
        let _ = configure_cli(&args);
        assert!(
            dir.path().join(".opsml-skills.yaml").exists(),
            ".opsml-skills.yaml must be created"
        );
    }

    #[test]
    fn configure_cli_does_not_overwrite_existing_yaml() {
        let dir = tempdir().unwrap();
        let yaml_path = dir.path().join(".opsml-skills.yaml");
        std::fs::write(&yaml_path, "registry: http://custom.example.com\n").unwrap();
        let args = ConfigureArgs {
            target: crate::cli::arg::ConfigureTarget::ClaudeCode,
            lazy: true,
            path: Some(dir.path().to_path_buf()),
        };
        let _ = configure_cli(&args);
        let content = std::fs::read_to_string(&yaml_path).unwrap();
        assert!(content.contains("custom.example.com"), "existing yaml must not be overwritten");
    }

    #[test]
    fn register_claude_hook_creates_settings_json() {
        let dir = tempdir().unwrap();
        register_claude_hook(dir.path(), "bash .opsml-cache/hooks/startup.sh").unwrap();
        let content = std::fs::read_to_string(dir.path().join(".claude/settings.json")).unwrap();
        let v: serde_json::Value = serde_json::from_str(&content).unwrap();
        assert!(v["hooks"]["UserPromptSubmit"].is_array());
    }

    #[test]
    fn register_claude_hook_merges_existing_settings() {
        let dir = tempdir().unwrap();
        let settings_dir = dir.path().join(".claude");
        std::fs::create_dir_all(&settings_dir).unwrap();
        std::fs::write(
            settings_dir.join("settings.json"),
            r#"{"some_other_key": true}"#,
        )
        .unwrap();
        register_claude_hook(dir.path(), "bash .opsml-cache/hooks/startup.sh").unwrap();
        let content = std::fs::read_to_string(settings_dir.join("settings.json")).unwrap();
        let v: serde_json::Value = serde_json::from_str(&content).unwrap();
        assert!(v["some_other_key"].as_bool().unwrap(), "existing keys must be preserved");
        assert!(v["hooks"]["UserPromptSubmit"].is_array());
    }

    #[test]
    fn register_codex_hook_is_idempotent() {
        let dir = tempdir().unwrap();
        let cmd = "bash .opsml-cache/hooks/startup.sh";
        register_codex_hook(dir.path(), cmd).unwrap();
        register_codex_hook(dir.path(), cmd).unwrap();
        let content = std::fs::read_to_string(dir.path().join(".codex/startup.sh")).unwrap();
        assert_eq!(content.matches(cmd).count(), 1);
    }

    #[test]
    fn register_gemini_hook_creates_settings_json() {
        let dir = tempdir().unwrap();
        register_gemini_hook(dir.path(), "bash .opsml-cache/hooks/startup.sh").unwrap();
        let content =
            std::fs::read_to_string(dir.path().join(".gemini/settings.json")).unwrap();
        let v: serde_json::Value = serde_json::from_str(&content).unwrap();
        assert!(v["startup_hook"].as_str().is_some());
    }

    #[test]
    fn register_github_copilot_hook_creates_startup_sh() {
        let dir = tempdir().unwrap();
        register_github_copilot_hook(dir.path(), "bash .opsml-cache/hooks/startup.sh").unwrap();
        assert!(dir.path().join(".github/copilot/startup.sh").exists());
    }
}
