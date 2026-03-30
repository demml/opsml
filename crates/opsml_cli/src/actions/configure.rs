use crate::actions::sync::sync_skills;
use crate::cli::arg::{ConfigureArgs, PullTarget, SyncArgs};
use crate::error::CliError;
use opsml_colors::Colorize;
use opsml_toml::OpsmlSkillsYaml;
use std::fmt::Write;
use std::path::{Path, PathBuf};

pub fn configure_cli(args: &ConfigureArgs) -> Result<(), CliError> {
    let home = dirs::home_dir()
        .ok_or_else(|| CliError::Error("Cannot determine home directory".into()))?;
    let opsml_dir = home.join(".opsml");
    std::fs::create_dir_all(&opsml_dir)?;

    // Scaffold ~/.opsml/skills.yaml if missing
    let yaml_path = opsml_dir.join("skills.yaml");
    if !yaml_path.exists() {
        OpsmlSkillsYaml::scaffold(&yaml_path)?;
        println!("{} {}", Colorize::green("Created"), yaml_path.display());
    }

    if args.lazy {
        configure_lazy(args, &opsml_dir, &home)
    } else {
        configure_eager(args)
    }
}

fn configure_eager(args: &ConfigureArgs) -> Result<(), CliError> {
    sync_skills(&SyncArgs {
        force: false,
        quiet: false,
        targets: Some(args.target.to_pull_targets()),
        path: None, // both layers
    })
}

fn configure_lazy(args: &ConfigureArgs, opsml_dir: &Path, home: &Path) -> Result<(), CliError> {
    let hooks_dir = opsml_dir.join("hooks");
    std::fs::create_dir_all(&hooks_dir)?;
    let hook_path = hooks_dir.join("startup.sh");

    let opsml_bin = std::env::current_exe()
        .unwrap_or_else(|_| PathBuf::from("opsml"))
        .to_string_lossy()
        .into_owned();

    let hook_content =
        crate::hooks::STARTUP_SH.replace("__OPSML_BIN__", &shell_single_quote(&opsml_bin));

    std::fs::write(&hook_path, hook_content)?;

    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(&hook_path, std::fs::Permissions::from_mode(0o755))?;
    }

    println!("{} {}", Colorize::green("Created"), hook_path.display());

    // sync with no --path → both layers
    let hook_cmd = format!("{} skill sync --quiet", shell_single_quote(&opsml_bin));
    for target in &args.target.to_pull_targets() {
        register_hook(target, home, &hook_cmd)?;
    }
    Ok(())
}

/// Wraps `s` in POSIX single quotes, escaping any internal single quotes.
/// A path like `/home/john doe/bin/opsml` becomes `'/home/john doe/bin/opsml'`.
/// A path like `/weird'path/opsml` becomes `'/weird'\''path/opsml'`.
fn shell_single_quote(s: &str) -> String {
    format!("'{}'", s.replace('\'', r"'\''"))
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
        let content = std::fs::read_to_string(&path)?;
        serde_json::from_str(&content).map_err(|e| {
            CliError::Error(format!(
                "Cannot parse {}: {e}. Fix or delete it before running configure.",
                path.display()
            ))
        })?
    } else {
        serde_json::json!({})
    };

    let existing = settings["hooks"]["UserPromptSubmit"]
        .as_array()
        .cloned()
        .unwrap_or_default();

    let already_registered = existing.iter().any(|entry| {
        entry["hooks"]
            .as_array()
            .map(|hooks| hooks.iter().any(|h| h["command"] == cmd))
            .unwrap_or(false)
    });

    if !already_registered {
        let mut arr = existing;
        arr.push(serde_json::json!({
            "matcher": "",
            "hooks": [{ "type": "command", "command": cmd }]
        }));
        settings["hooks"]["UserPromptSubmit"] = serde_json::Value::Array(arr);
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        std::fs::write(&path, serde_json::to_string_pretty(&settings)?)?;
        println!("{} {}", Colorize::green("Updated"), path.display());
    }
    Ok(())
}

fn register_codex_hook(base: &Path, cmd: &str) -> Result<(), CliError> {
    append_hook_to_sh(base, ".codex", "startup.sh", cmd)
}

fn register_gemini_hook(base: &Path, cmd: &str) -> Result<(), CliError> {
    let path = base.join(".gemini").join("settings.json");
    let mut settings: serde_json::Value = if path.exists() {
        let content = std::fs::read_to_string(&path)?;
        serde_json::from_str(&content).map_err(|e| {
            CliError::Error(format!(
                "Cannot parse {}: {e}. Fix or delete it before running configure.",
                path.display()
            ))
        })?
    } else {
        serde_json::json!({})
    };
    if settings["startup_hook"].as_str() == Some(cmd) {
        return Ok(());
    }
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
fn append_hook_to_sh(base: &Path, dir: &str, filename: &str, cmd: &str) -> Result<(), CliError> {
    let dir_path = base.join(dir);
    std::fs::create_dir_all(&dir_path)?;
    let path = dir_path.join(filename);
    let existing = if path.exists() {
        std::fs::read_to_string(&path)?
    } else {
        String::new()
    };
    let wrote = if !existing.contains(cmd) {
        let mut content = existing;
        if !content.is_empty() && !content.ends_with('\n') {
            content.push('\n');
        }
        let _ = writeln!(content, "{cmd}");
        std::fs::write(&path, &content)?;
        true
    } else {
        false
    };
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(&path, std::fs::Permissions::from_mode(0o755))?;
    }
    if wrote {
        println!("{} {}", Colorize::green("Updated"), path.display());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cli::arg::ConfigureTarget;
    use tempfile::tempdir;

    #[test]
    fn test_configure_cli_creates_yaml_in_home() {
        let home = tempdir().unwrap();
        let opsml_dir = home.path().join(".opsml");
        std::fs::create_dir_all(&opsml_dir).unwrap();
        let yaml_path = opsml_dir.join("skills.yaml");

        // Test that scaffold creates the file
        OpsmlSkillsYaml::scaffold(&yaml_path).unwrap();
        assert!(yaml_path.exists());
    }

    #[test]
    fn test_configure_cli_does_not_overwrite_existing_yaml() {
        let home = tempdir().unwrap();
        let opsml_dir = home.path().join(".opsml");
        std::fs::create_dir_all(&opsml_dir).unwrap();
        let yaml_path = opsml_dir.join("skills.yaml");
        std::fs::write(&yaml_path, "registry: http://custom.example.com\n").unwrap();

        // scaffold should fail since file exists
        assert!(OpsmlSkillsYaml::scaffold(&yaml_path).is_err());

        let content = std::fs::read_to_string(&yaml_path).unwrap();
        assert!(
            content.contains("custom.example.com"),
            "existing yaml must not be overwritten"
        );
    }

    #[test]
    fn test_register_claude_hook_creates_settings_json() {
        let dir = tempdir().unwrap();
        register_claude_hook(dir.path(), "opsml skill sync --quiet").unwrap();
        let content = std::fs::read_to_string(dir.path().join(".claude/settings.json")).unwrap();
        let v: serde_json::Value = serde_json::from_str(&content).unwrap();
        assert!(v["hooks"]["UserPromptSubmit"].is_array());
    }

    #[test]
    fn test_register_claude_hook_merges_existing_settings() {
        let dir = tempdir().unwrap();
        let settings_dir = dir.path().join(".claude");
        std::fs::create_dir_all(&settings_dir).unwrap();
        std::fs::write(
            settings_dir.join("settings.json"),
            r#"{"some_other_key": true}"#,
        )
        .unwrap();
        register_claude_hook(dir.path(), "opsml skill sync --quiet").unwrap();
        let content = std::fs::read_to_string(settings_dir.join("settings.json")).unwrap();
        let v: serde_json::Value = serde_json::from_str(&content).unwrap();
        assert!(
            v["some_other_key"].as_bool().unwrap(),
            "existing keys must be preserved"
        );
        assert!(v["hooks"]["UserPromptSubmit"].is_array());
    }

    #[test]
    fn test_register_codex_hook_is_idempotent() {
        let dir = tempdir().unwrap();
        let cmd = "opsml skill sync --quiet";
        register_codex_hook(dir.path(), cmd).unwrap();
        register_codex_hook(dir.path(), cmd).unwrap();
        let content = std::fs::read_to_string(dir.path().join(".codex/startup.sh")).unwrap();
        assert_eq!(content.matches(cmd).count(), 1);
    }

    #[test]
    fn test_register_gemini_hook_creates_settings_json() {
        let dir = tempdir().unwrap();
        register_gemini_hook(dir.path(), "opsml skill sync --quiet").unwrap();
        let content = std::fs::read_to_string(dir.path().join(".gemini/settings.json")).unwrap();
        let v: serde_json::Value = serde_json::from_str(&content).unwrap();
        assert!(v["startup_hook"].as_str().is_some());
    }

    #[test]
    fn test_register_github_copilot_hook_creates_startup_sh() {
        let dir = tempdir().unwrap();
        register_github_copilot_hook(dir.path(), "opsml skill sync --quiet").unwrap();
        assert!(dir.path().join(".github/copilot/startup.sh").exists());
    }

    #[test]
    fn test_register_claude_hook_is_idempotent() {
        let dir = tempdir().unwrap();
        let cmd = "opsml skill sync --quiet";
        register_claude_hook(dir.path(), cmd).unwrap();
        register_claude_hook(dir.path(), cmd).unwrap();
        let content = std::fs::read_to_string(dir.path().join(".claude/settings.json")).unwrap();
        let v: serde_json::Value = serde_json::from_str(&content).unwrap();
        assert_eq!(
            v["hooks"]["UserPromptSubmit"].as_array().unwrap().len(),
            1,
            "duplicate registration must produce exactly one entry"
        );
    }

    #[test]
    fn test_register_gemini_hook_is_idempotent() {
        let dir = tempdir().unwrap();
        let cmd = "opsml skill sync --quiet";
        register_gemini_hook(dir.path(), cmd).unwrap();
        register_gemini_hook(dir.path(), cmd).unwrap();
        let content = std::fs::read_to_string(dir.path().join(".gemini/settings.json")).unwrap();
        let v: serde_json::Value = serde_json::from_str(&content).unwrap();
        assert_eq!(v["startup_hook"].as_str(), Some(cmd));
    }

    #[test]
    fn test_configure_lazy_writes_startup_sh_and_hook_without_path_flag() {
        let dir = tempdir().unwrap();
        let opsml_dir = dir.path().join(".opsml");
        let yaml_path = opsml_dir.join("skills.yaml");
        OpsmlSkillsYaml::scaffold(&yaml_path).unwrap();

        let args = ConfigureArgs {
            target: ConfigureTarget::ClaudeCode,
            lazy: true,
        };
        configure_lazy(&args, &opsml_dir, dir.path()).unwrap();

        // startup.sh must exist and must not contain the raw placeholder
        let sh = std::fs::read_to_string(opsml_dir.join("hooks/startup.sh")).unwrap();
        assert!(
            !sh.contains("__OPSML_BIN__"),
            "placeholder must be replaced"
        );
        assert!(
            !sh.contains("__OPSML_SKILLS_YAML__"),
            "placeholder must be replaced"
        );

        // The registered hook command must contain "skill sync --quiet" and must NOT contain "--path"
        let settings = std::fs::read_to_string(dir.path().join(".claude/settings.json")).unwrap();
        assert!(
            settings.contains("skill sync --quiet"),
            "hook must run sync"
        );
        assert!(
            !settings.contains("--path"),
            "hook must not hardcode --path"
        );
    }

    #[test]
    fn test_append_hook_to_sh_adds_newline_when_file_lacks_trailing_newline() {
        let dir = tempdir().unwrap();
        let file = dir.path().join("startup.sh");
        std::fs::write(&file, "existing_cmd").unwrap();
        append_hook_to_sh(dir.path(), ".", "startup.sh", "new_cmd").unwrap();
        let content = std::fs::read_to_string(&file).unwrap();
        assert_eq!(
            content, "existing_cmd\nnew_cmd\n",
            "must insert newline separator when file lacks trailing newline"
        );
    }

    #[test]
    fn test_register_claude_hook_returns_error_on_corrupt_json() {
        let dir = tempdir().unwrap();
        let settings_dir = dir.path().join(".claude");
        std::fs::create_dir_all(&settings_dir).unwrap();
        std::fs::write(settings_dir.join("settings.json"), "not json").unwrap();
        let result = register_claude_hook(dir.path(), "cmd");
        assert!(result.is_err());
        let msg = result.unwrap_err().to_string();
        assert!(
            msg.contains("Fix or delete it"),
            "error must include remediation hint: {msg}"
        );
    }
}
