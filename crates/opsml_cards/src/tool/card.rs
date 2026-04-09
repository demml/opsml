use super::error::ToolError;
use crate::BaseArgs;
use crate::error::CardError;
use crate::traits::{OpsmlCard, ProfileExt};
use chrono::{DateTime, Utc};
use opsml_types::contracts::tool::{
    ApiCallConfig, HookEvent, ShellScriptConfig, ToolSpec, ToolType,
};
use opsml_types::contracts::{CardRecord, ToolCardClientRecord};
use opsml_types::{RegistryType, SaveName, Suffix};
use opsml_utils::PyHelperFuncs;
use opsml_utils::get_utc_datetime;
use scouter_client::ProfileRequest;
use serde::{Deserialize, Serialize, de::DeserializeOwned};
use sha2::{Digest, Sha256};
use std::path::PathBuf;
use tracing::instrument;

/// Parse a ToolCard markdown file (YAML frontmatter + markdown body) into a ToolCard.
#[instrument(skip_all)]
pub fn parse_tool_markdown(content: &str) -> Result<ToolCard, ToolError> {
    // Normalize Windows line endings.
    let content = content.replace("\r\n", "\n");
    let content = content.as_str();

    // Extract YAML frontmatter between --- delimiters
    let after_open = content
        .strip_prefix("---\n")
        .ok_or_else(|| ToolError::Error("Missing opening ---".to_string()))?;

    let close_pos = after_open
        .find("\n---\n")
        .ok_or_else(|| ToolError::Error("Missing closing ---".to_string()))?;

    let yaml_str = &after_open[..close_pos];
    let body = after_open[close_pos + 5..].to_string();

    let spec: ToolSpec = serde_yaml::from_str(yaml_str)?;

    // Validate name: must be non-empty and contain only alphanumeric, '-', or '_'.
    if spec.name.is_empty()
        || !spec
            .name
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_')
    {
        return Err(ToolError::Error(format!(
            "Invalid tool name '{}': must be non-empty and contain only [a-zA-Z0-9_-]",
            spec.name
        )));
    }

    if let Some(m) = &spec.hook_matcher {
        super::installer::validate_hook_matcher(m)?;
    }

    let body_opt = if body.is_empty() { None } else { Some(body) };
    let name = spec.name.clone();

    let mut card = ToolCard::new_rs(spec, Some("opsml"), Some(&name), None, None)?;
    card.body = body_opt;
    Ok(card)
}

/// Validate a shell script body before writing to disk.
/// Enforces a 1 MB size limit and requires a shebang from the allowlist.
fn validate_script_body(body: &str, tool_name: &str) -> Result<(), ToolError> {
    const MAX_BYTES: usize = 1024 * 1024;
    const ALLOWED_SHEBANGS: &[&str] = &[
        "#!/bin/sh",
        "#!/bin/bash",
        "#!/usr/bin/env bash",
        "#!/usr/bin/env sh",
    ];
    if body.len() > MAX_BYTES {
        return Err(ToolError::Error(format!(
            "script body for '{}' exceeds 1 MB limit",
            tool_name
        )));
    }
    let first_line = body.lines().next().unwrap_or("");
    if !ALLOWED_SHEBANGS.iter().any(|s| first_line.starts_with(s)) {
        return Err(ToolError::Error(format!(
            "script body for '{}' must start with one of: {}",
            tool_name,
            ALLOWED_SHEBANGS.join(", ")
        )));
    }
    Ok(())
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ToolCard {
    pub spec: ToolSpec,

    pub space: String,
    pub name: String,
    pub version: String,
    pub uid: String,
    pub tags: Vec<String>,
    pub app_env: String,
    pub is_card: bool,
    pub opsml_version: String,
    pub created_at: DateTime<Utc>,
    pub registry_type: RegistryType,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub body: Option<String>,
}

impl ToolCard {
    pub fn new_rs(
        spec: ToolSpec,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        tags: Option<Vec<String>>,
    ) -> Result<Self, ToolError> {
        let registry_type = RegistryType::Tool;
        let base_args = BaseArgs::create_args(name, space, version, None, &registry_type)
            .map_err(|e| ToolError::Error(e.to_string()))?;

        Ok(Self {
            spec,
            space: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            tags: tags.unwrap_or_default(),
            registry_type,
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            created_at: get_utc_datetime(),
            is_card: true,
            opsml_version: opsml_version::version(),
            body: None,
        })
    }

    pub fn get_registry_card(&self) -> Result<CardRecord, ToolError> {
        let record = ToolCardClientRecord {
            uid: self.uid.clone(),
            created_at: self.created_at,
            app_env: self.app_env.clone(),
            space: self.space.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            tags: self.tags.clone(),
            opsml_version: self.opsml_version.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            tool_type: self.spec.tool_type.to_string(),
            args_schema: self.spec.args_schema.clone(),
            content_hash: Some(self.calculate_content_hash()?),
            download_count: 0,
            description: Some(self.spec.description.clone()),
        };

        Ok(CardRecord::Tool(record))
    }

    pub fn calculate_content_hash(&self) -> Result<Vec<u8>, ToolError> {
        fn sort_json_keys(v: serde_json::Value) -> serde_json::Value {
            match v {
                serde_json::Value::Object(map) => {
                    let sorted: serde_json::Map<String, serde_json::Value> = map
                        .into_iter()
                        .map(|(k, v)| (k, sort_json_keys(v)))
                        .collect::<std::collections::BTreeMap<_, _>>()
                        .into_iter()
                        .collect();
                    serde_json::Value::Object(sorted)
                }
                serde_json::Value::Array(arr) => {
                    serde_json::Value::Array(arr.into_iter().map(sort_json_keys).collect())
                }
                other => other,
            }
        }

        let mut hasher = Sha256::new();
        let spec_value = serde_json::to_value(&self.spec)?;
        let canonical = serde_json::to_vec(&sort_json_keys(spec_value))?;
        hasher.update(&canonical);
        if let Some(body) = &self.body {
            hasher.update(body.as_bytes());
        }
        Ok(hasher.finalize().to_vec())
    }

    pub fn to_markdown(&self) -> Result<String, ToolError> {
        #[derive(Debug, Clone, Serialize)]
        #[serde(rename_all = "camelCase")]
        struct ToolFrontmatter<'a> {
            name: &'a str,
            description: &'a str,
            tool_type: String,
            #[serde(skip_serializing_if = "Option::is_none")]
            args_schema: Option<&'a serde_json::Value>,
            #[serde(skip_serializing_if = "Option::is_none")]
            output_schema: Option<&'a serde_json::Value>,
            #[serde(skip_serializing_if = "Option::is_none")]
            script_config: Option<&'a ShellScriptConfig>,
            #[serde(skip_serializing_if = "Option::is_none")]
            api_config: Option<&'a ApiCallConfig>,
            #[serde(skip_serializing_if = "Option::is_none")]
            mcp_server_name: Option<&'a str>,
            #[serde(skip_serializing_if = "<[_]>::is_empty")]
            allowed_tools: &'a [String],
            requires_approval: bool,
            #[serde(skip_serializing_if = "<[_]>::is_empty")]
            hook_events: &'a [HookEvent],
            #[serde(skip_serializing_if = "Option::is_none")]
            hook_matcher: Option<&'a serde_json::Value>,
        }

        let sanitized_api_config = self
            .spec
            .api_config
            .as_ref()
            .map(|c| c.sanitize_for_response());
        let fm = ToolFrontmatter {
            name: &self.spec.name,
            description: &self.spec.description,
            tool_type: self.spec.tool_type.to_string(),
            args_schema: self.spec.args_schema.as_ref(),
            output_schema: self.spec.output_schema.as_ref(),
            script_config: self.spec.script_config.as_ref(),
            api_config: sanitized_api_config.as_ref(),
            mcp_server_name: self.spec.mcp_server_name.as_deref(),
            allowed_tools: &self.spec.allowed_tools,
            requires_approval: self.spec.requires_approval,
            hook_events: &self.spec.hook_events,
            hook_matcher: self.spec.hook_matcher.as_ref(),
        };

        let yaml = serde_yaml::to_string(&fm)?;
        let yaml = yaml.trim_start_matches("---\n");
        let body = self.body.as_deref().unwrap_or("");

        Ok(format!("---\n{yaml}---\n{body}"))
    }

    pub fn pull_artifacts(
        &self,
        install_dir: PathBuf,
        hook_installer: Option<&dyn super::installer::HookInstaller>,
        global: bool,
        expected_hash: Option<&[u8]>,
    ) -> Result<PathBuf, ToolError> {
        if self.name.is_empty()
            || !self
                .name
                .chars()
                .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_')
        {
            return Err(ToolError::Error(format!(
                "Invalid tool name '{}': must be non-empty and contain only [a-zA-Z0-9_-]",
                self.name
            )));
        }
        std::fs::create_dir_all(&install_dir)?;
        #[cfg(unix)]
        let install_dir = install_dir.canonicalize()?;
        if matches!(self.spec.tool_type, ToolType::ShellScript | ToolType::Hook)
            && self.body.is_none()
        {
            return Err(ToolError::Error(format!(
                "{} tool '{}' has no body; cannot install",
                self.spec.tool_type, self.name
            )));
        }

        // Verify content hash before writing any script to disk.
        if matches!(self.spec.tool_type, ToolType::ShellScript | ToolType::Hook)
            && let Some(expected) = expected_hash
        {
            let actual = self.calculate_content_hash()?;
            if actual != expected {
                return Err(ToolError::Error(format!(
                    "Content hash mismatch for '{}': registry record does not match received body. Refusing to install.",
                    self.name
                )));
            }
        }

        let body_content = self.body.as_deref().unwrap_or("");

        // Validate script body content (size + shebang) before writing.
        if matches!(self.spec.tool_type, ToolType::ShellScript | ToolType::Hook) {
            validate_script_body(body_content, &self.name)?;
        }

        match &self.spec.tool_type {
            ToolType::ShellScript => {
                let path = install_dir.join(format!("{}.sh", self.name));
                std::fs::write(&path, body_content)?;
                #[cfg(unix)]
                {
                    use std::os::unix::fs::PermissionsExt;
                    let mut perms = std::fs::metadata(&path)?.permissions();
                    perms.set_mode(0o700);
                    std::fs::set_permissions(&path, perms)?;
                }
                Ok(path)
            }
            ToolType::SlashCommand => {
                #[derive(Serialize)]
                struct SlashFrontmatter<'a> {
                    description: &'a str,
                    #[serde(rename = "allowed-tools", skip_serializing_if = "<[_]>::is_empty")]
                    allowed_tools: &'a [String],
                }

                let fm = SlashFrontmatter {
                    description: &self.spec.description,
                    allowed_tools: &self.spec.allowed_tools,
                };
                let yaml = serde_yaml::to_string(&fm)?;
                let yaml = yaml.trim_start_matches("---\n");
                let content = format!("---\n{yaml}---\n{body_content}");

                let path = install_dir.join(format!("{}.md", self.name));
                std::fs::write(&path, content)?;
                Ok(path)
            }
            ToolType::McpServer => {
                let path = install_dir.join(format!("{}-mcp.json", self.name));
                let json_content = serde_json::to_string_pretty(&self.spec)?;
                std::fs::write(&path, json_content)?;
                Ok(path)
            }
            ToolType::ApiCall => {
                let path = install_dir.join(format!("{}-api.yaml", self.name));
                let yaml_content = serde_yaml::to_string(&self.spec)?;
                std::fs::write(&path, yaml_content)?;
                Ok(path)
            }
            ToolType::Hook => {
                let hook_dir = install_dir.join(".opsml/hooks");
                std::fs::create_dir_all(&hook_dir)?;
                let path = hook_dir.join(format!("{}.sh", self.name));
                std::fs::write(&path, body_content)?;
                #[cfg(unix)]
                {
                    use std::os::unix::fs::PermissionsExt;
                    let mut perms = std::fs::metadata(&path)?.permissions();
                    perms.set_mode(0o700);
                    std::fs::set_permissions(&path, perms)?;
                }
                let relative_path = std::env::current_dir()
                    .ok()
                    .and_then(|cwd| path.strip_prefix(&cwd).ok().map(|p| p.to_path_buf()))
                    .unwrap_or_else(|| {
                        tracing::warn!(
                            "Could not make hook path relative to CWD; registering absolute path: {}",
                            path.display()
                        );
                        path.clone()
                    });
                if let Some(installer) = hook_installer {
                    installer.install_hook(
                        &self.name,
                        &relative_path,
                        &self.spec.hook_events,
                        self.spec.hook_matcher.as_ref(),
                        global,
                    )?;
                }
                Ok(path)
            }
            ToolType::InternalFunction | ToolType::Custom(_) => {
                let path = install_dir.join(format!("{}-spec.yaml", self.name));
                let yaml_content = serde_yaml::to_string(&self.spec)?;
                std::fs::write(&path, yaml_content)?;
                Ok(path)
            }
        }
    }

    pub fn save_card(&mut self, path: PathBuf) -> Result<(), ToolError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(self, card_save_path.as_path())?;
        Ok(())
    }

    pub fn model_validate_json(json_string: String) -> Result<ToolCard, ToolError> {
        Ok(serde_json::from_str(&json_string)?)
    }

    pub fn from_path(path: PathBuf) -> Result<Self, ToolError> {
        deserialize_from_path(path)
    }
}

fn deserialize_from_path<T: DeserializeOwned>(path: PathBuf) -> Result<T, ToolError> {
    let ext = path
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or_default();
    let content = std::fs::read_to_string(&path)?;
    match ext {
        "json" => Ok(serde_json::from_str(&content)?),
        other => Err(ToolError::Error(format!(
            "Unsupported file extension for ToolCard deserialization: .{other}"
        ))),
    }
}

impl OpsmlCard for ToolCard {
    fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        self.get_registry_card().map_err(CardError::from)
    }

    fn get_version(&self) -> String {
        self.version.clone()
    }

    fn set_name(&mut self, name: String) {
        self.name = name;
    }

    fn set_space(&mut self, space: String) {
        self.space = space;
    }

    fn set_version(&mut self, version: String) {
        self.version = version;
    }

    fn set_uid(&mut self, uid: String) {
        self.uid = uid;
    }

    fn set_created_at(&mut self, created_at: DateTime<Utc>) {
        self.created_at = created_at;
    }

    fn set_app_env(&mut self, app_env: String) {
        self.app_env = app_env;
    }

    fn is_card(&self) -> bool {
        self.is_card
    }

    fn save(&mut self, path: PathBuf) -> Result<(), CardError> {
        self.save_card(path).map_err(CardError::from)
    }

    fn registry_type(&self) -> &RegistryType {
        &self.registry_type
    }

    fn update_drift_config_args(&mut self) -> Result<(), CardError> {
        Ok(())
    }

    fn set_profile_uid(&mut self, _profile_uid: String) -> Result<(), CardError> {
        Ok(())
    }
}

impl ProfileExt for ToolCard {
    fn get_profile_request(&self) -> Result<ProfileRequest, CardError> {
        Err(CardError::DriftProfileNotFoundError)
    }

    fn has_profile(&self) -> bool {
        false
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use opsml_types::contracts::tool::{ApiCallConfig, HookEvent, ShellScriptConfig};

    fn make_spec() -> ToolSpec {
        ToolSpec {
            name: "my-tool".to_string(),
            description: "A generic tool".to_string(),
            tool_type: ToolType::ShellScript,
            ..Default::default()
        }
    }

    fn make_shell_spec() -> ToolSpec {
        ToolSpec {
            name: "my-tool".to_string(),
            description: "A shell script tool".to_string(),
            tool_type: ToolType::ShellScript,
            script_config: Some(ShellScriptConfig {
                script: Some("echo hello".to_string()),
                shell: Some("/bin/bash".to_string()),
            }),
            ..Default::default()
        }
    }

    fn make_slash_spec() -> ToolSpec {
        ToolSpec {
            name: "my-slash".to_string(),
            description: "A slash command".to_string(),
            tool_type: ToolType::SlashCommand,
            allowed_tools: vec!["Read".to_string(), "Grep".to_string()],
            ..Default::default()
        }
    }

    fn make_mcp_spec() -> ToolSpec {
        ToolSpec {
            name: "my-mcp".to_string(),
            description: "An MCP server tool".to_string(),
            tool_type: ToolType::McpServer,
            mcp_server_name: Some("my-mcp-server".to_string()),
            ..Default::default()
        }
    }

    fn make_api_spec() -> ToolSpec {
        ToolSpec {
            name: "my-api".to_string(),
            description: "An API call tool".to_string(),
            tool_type: ToolType::ApiCall,
            api_config: Some(ApiCallConfig {
                url: "https://example.com".to_string(),
                ..Default::default()
            }),
            ..Default::default()
        }
    }

    #[test]
    fn test_tool_card_new_rs() {
        let spec = make_shell_spec();
        let card = ToolCard::new_rs(
            spec,
            Some("test-space"),
            Some("my-tool"),
            None,
            Some(vec!["tag1".to_string()]),
        )
        .unwrap();

        assert_eq!(card.name, "my-tool");
        assert_eq!(card.space, "test-space");
        assert_eq!(card.version, "0.0.0");
        assert_eq!(card.tags, vec!["tag1"]);
        assert!(card.is_card);
        assert_eq!(card.registry_type, RegistryType::Tool);
    }

    #[test]
    fn test_tool_card_json_roundtrip() {
        let spec = make_shell_spec();
        let card = ToolCard::new_rs(spec, Some("test-space"), Some("my-tool"), None, None).unwrap();

        let json = serde_json::to_string(&card).unwrap();
        let restored = ToolCard::model_validate_json(json).unwrap();

        assert_eq!(restored.name, card.name);
        assert_eq!(restored.spec.description, card.spec.description);
        assert_eq!(restored.body, card.body);
    }

    #[test]
    fn test_tool_card_get_registry_card() {
        let spec = make_shell_spec();
        let card = ToolCard::new_rs(spec, Some("test-space"), Some("my-tool"), None, None).unwrap();

        let record = card.get_registry_card().unwrap();
        match record {
            CardRecord::Tool(r) => {
                assert_eq!(r.name, "my-tool");
                assert_eq!(r.space, "test-space");
                assert_eq!(r.tool_type, "ShellScript");
                assert!(r.content_hash.is_some());
                assert!(!r.content_hash.unwrap().is_empty());
            }
            _ => panic!("expected CardRecord::Tool"),
        }
    }

    #[test]
    fn test_content_hash_stability() {
        let spec = make_shell_spec();
        let card1 = ToolCard::new_rs(spec.clone(), Some("s"), Some("my-tool"), None, None).unwrap();
        let card2 = ToolCard::new_rs(spec, Some("s"), Some("my-tool"), None, None).unwrap();

        assert_eq!(
            card1.calculate_content_hash().unwrap(),
            card2.calculate_content_hash().unwrap()
        );
    }

    #[test]
    fn test_content_hash_changes_with_spec() {
        let spec1 = make_shell_spec();
        let mut spec2 = spec1.clone();
        spec2.description = "A completely different description".to_string();

        let card1 = ToolCard::new_rs(spec1, Some("s"), Some("my-tool"), None, None).unwrap();
        let card2 = ToolCard::new_rs(spec2, Some("s"), Some("my-tool"), None, None).unwrap();

        assert_ne!(
            card1.calculate_content_hash().unwrap(),
            card2.calculate_content_hash().unwrap()
        );
    }

    #[test]
    fn test_parse_markdown_shell_script() {
        let md = "---\nname: my-tool\ndescription: A shell script\ntoolType: ShellScript\nrequiresApproval: false\n---\necho hello\n";
        let card = parse_tool_markdown(md).unwrap();
        assert_eq!(card.spec.name, "my-tool");
        assert_eq!(card.spec.tool_type, ToolType::ShellScript);
        assert_eq!(card.body, Some("echo hello\n".to_string()));
    }

    #[test]
    fn test_parse_markdown_slash_command() {
        let md = "---\nname: my-slash\ndescription: A slash command\ntoolType: SlashCommand\nrequiresApproval: false\n---\nDo the thing.\n";
        let card = parse_tool_markdown(md).unwrap();
        assert_eq!(card.spec.tool_type, ToolType::SlashCommand);
        assert_eq!(card.body, Some("Do the thing.\n".to_string()));
    }

    #[test]
    fn test_parse_markdown_missing_delimiter() {
        let no_delims = "name: my-tool\ndescription: test\n";
        assert!(parse_tool_markdown(no_delims).is_err());
    }

    #[test]
    fn test_parse_markdown_crlf() {
        let crlf = "---\r\nname: my-tool\r\ndescription: test\r\ntoolType: ShellScript\r\nrequiresApproval: false\r\n---\r\nDo something.\r\n";
        let card = parse_tool_markdown(crlf).unwrap();
        assert_eq!(card.spec.name, "my-tool");
        assert!(card.body.is_some());
    }

    #[test]
    fn test_parse_markdown_invalid_name() {
        let bad_name = "---\nname: \"../../evil\"\ndescription: test\ntoolType: ShellScript\nrequiresApproval: false\n---\n";
        assert!(parse_tool_markdown(bad_name).is_err());
    }

    #[test]
    fn test_pull_artifacts_shell_script() {
        let tmp = tempfile::tempdir().unwrap();
        let spec = make_shell_spec();
        let mut card =
            ToolCard::new_rs(spec, Some("test-space"), Some("my-tool"), None, None).unwrap();
        card.body = Some("#!/bin/bash\necho hello\n".to_string());

        let path = card
            .pull_artifacts(tmp.path().to_path_buf(), None, false, None)
            .unwrap();
        assert!(path.exists());
        assert!(path.to_str().unwrap().ends_with(".sh"));
        let content = std::fs::read_to_string(&path).unwrap();
        assert!(content.contains("echo hello"));
    }

    #[test]
    fn test_pull_artifacts_slash_command() {
        let tmp = tempfile::tempdir().unwrap();
        let spec = make_slash_spec();
        let mut card =
            ToolCard::new_rs(spec, Some("test-space"), Some("my-slash"), None, None).unwrap();
        card.body = Some("Run the linter.\n".to_string());

        let path = card
            .pull_artifacts(tmp.path().to_path_buf(), None, false, None)
            .unwrap();
        assert!(path.exists());
        assert!(path.to_str().unwrap().ends_with(".md"));
        let content = std::fs::read_to_string(&path).unwrap();
        assert!(content.contains("allowed-tools"));
        assert!(content.contains("Read"));
        assert!(content.contains("Run the linter."));
    }

    #[test]
    fn test_pull_artifacts_mcp_server() {
        let tmp = tempfile::tempdir().unwrap();
        let spec = make_mcp_spec();
        let card = ToolCard::new_rs(spec, Some("test-space"), Some("my-mcp"), None, None).unwrap();

        let path = card
            .pull_artifacts(tmp.path().to_path_buf(), None, false, None)
            .unwrap();
        assert!(path.exists());
        assert!(path.to_str().unwrap().ends_with("-mcp.json"));
    }

    #[test]
    fn test_pull_artifacts_api_call() {
        let tmp = tempfile::tempdir().unwrap();
        let spec = make_api_spec();
        let card = ToolCard::new_rs(spec, Some("test-space"), Some("my-api"), None, None).unwrap();

        let path = card
            .pull_artifacts(tmp.path().to_path_buf(), None, false, None)
            .unwrap();
        assert!(path.exists());
        assert!(path.to_str().unwrap().ends_with("-api.yaml"));
    }

    #[test]
    fn test_merge_mcp_entry_idempotent() {
        use crate::tool::installer::{ClaudeCodeInstaller, McpConfigInstaller};

        let tmp = tempfile::tempdir().unwrap();
        let orig_dir = std::env::current_dir().unwrap();
        std::env::set_current_dir(tmp.path()).unwrap();

        let installer = ClaudeCodeInstaller;
        let entry = serde_json::json!({
            "command": "npx",
            "args": ["-y", "my-mcp-server"]
        });

        installer
            .merge_mcp_entry("my-server", entry.clone())
            .unwrap();
        installer.merge_mcp_entry("my-server", entry).unwrap();

        let content = std::fs::read_to_string(installer.mcp_config_path()).unwrap();
        let parsed: serde_json::Value = serde_json::from_str(&content).unwrap();
        let mcp_servers = parsed["mcpServers"].as_object().unwrap();

        assert_eq!(mcp_servers.len(), 1);
        assert!(mcp_servers.contains_key("my-server"));

        std::env::set_current_dir(orig_dir).unwrap();
    }

    #[test]
    fn test_to_markdown_body_not_in_frontmatter() {
        let spec = make_spec();
        let mut card =
            ToolCard::new_rs(spec, Some("test-space"), Some("my-tool"), None, None).unwrap();
        card.body = Some("Run the linter.".to_string());

        let md = card.to_markdown().unwrap();

        let after_open = md.strip_prefix("---\n").unwrap();
        let close = after_open.find("\n---\n").unwrap();
        let frontmatter = &after_open[..close];

        assert!(
            !frontmatter.contains("body"),
            "body must not appear in the YAML frontmatter block"
        );
        assert!(
            md.contains("Run the linter."),
            "body must appear in the markdown body section"
        );
    }

    #[test]
    fn test_pull_artifacts_internal_function() {
        let tmp = tempfile::tempdir().unwrap();
        let spec = ToolSpec {
            name: "my-func".to_string(),
            description: "An internal function".to_string(),
            tool_type: ToolType::InternalFunction,
            ..Default::default()
        };
        let card = ToolCard::new_rs(spec, Some("s"), Some("my-func"), None, None).unwrap();
        let output = card
            .pull_artifacts(tmp.path().to_path_buf(), None, false, None)
            .unwrap();
        assert!(output.exists());
        assert!(output.to_string_lossy().ends_with("-spec.yaml"));
    }

    #[test]
    fn test_pull_artifacts_custom() {
        let tmp = tempfile::tempdir().unwrap();
        let spec = ToolSpec {
            name: "my-custom".to_string(),
            description: "Custom tool".to_string(),
            tool_type: ToolType::Custom("my-custom-type".to_string()),
            ..Default::default()
        };
        let card = ToolCard::new_rs(spec, Some("s"), Some("my-custom"), None, None).unwrap();
        let output = card
            .pull_artifacts(tmp.path().to_path_buf(), None, false, None)
            .unwrap();
        assert!(output.exists());
        assert!(output.to_string_lossy().ends_with("-spec.yaml"));
    }

    #[test]
    fn test_from_path_roundtrip() {
        let spec = make_shell_spec();
        let mut card =
            ToolCard::new_rs(spec, Some("test-space"), Some("my-tool"), None, None).unwrap();
        card.body = Some("echo hello".to_string());

        let tmp = tempfile::tempdir().unwrap();
        card.save_card(tmp.path().to_path_buf()).unwrap();

        let json_path = tmp.path().join("Card.json");
        let loaded = ToolCard::from_path(json_path).unwrap();

        assert_eq!(loaded.name, card.name);
        assert_eq!(loaded.spec.description, card.spec.description);
        assert_eq!(loaded.body, card.body);
    }

    #[test]
    fn test_pull_hook_writes_script_and_sets_executable() {
        let tmp = tempfile::tempdir().unwrap();
        let spec = ToolSpec {
            name: "my-hook".to_string(),
            description: "A hook".to_string(),
            tool_type: ToolType::Hook,
            hook_events: vec![HookEvent::PostToolUse],
            ..Default::default()
        };
        let mut card = ToolCard::new_rs(spec, Some("s"), Some("my-hook"), None, None).unwrap();
        card.body = Some("#!/bin/bash\necho hook\n".to_string());

        let path = card
            .pull_artifacts(tmp.path().to_path_buf(), None, false, None)
            .unwrap();
        assert!(path.exists());
        assert!(path.to_string_lossy().ends_with(".sh"));

        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let perms = std::fs::metadata(&path).unwrap().permissions();
            assert_eq!(perms.mode() & 0o777, 0o700);
        }
    }

    #[test]
    fn test_pull_hook_no_installer_still_writes_script() {
        let tmp = tempfile::tempdir().unwrap();
        let spec = ToolSpec {
            name: "no-installer".to_string(),
            description: "Hook without installer".to_string(),
            tool_type: ToolType::Hook,
            ..Default::default()
        };
        let mut card = ToolCard::new_rs(spec, Some("s"), Some("no-installer"), None, None).unwrap();
        card.body = Some("#!/bin/bash\necho no-installer\n".to_string());
        let path = card
            .pull_artifacts(tmp.path().to_path_buf(), None, false, None)
            .unwrap();
        assert!(path.exists());
    }

    // --- Cross-installer hook tests ---

    fn with_hook_tempdir<F: FnOnce(&std::path::Path)>(f: F) {
        let tmp = tempfile::tempdir().unwrap();
        let _guard = crate::tool::test_util::CWD_LOCK
            .lock()
            .unwrap_or_else(|e| e.into_inner());
        let orig = std::env::current_dir().unwrap();
        std::env::set_current_dir(tmp.path()).unwrap();
        f(tmp.path());
        std::env::set_current_dir(orig).unwrap();
    }

    fn make_hook_card(name: &str) -> ToolCard {
        let spec = ToolSpec {
            name: name.to_string(),
            description: "test hook".to_string(),
            tool_type: ToolType::Hook,
            hook_events: vec![HookEvent::PostToolUse],
            hook_matcher: Some(serde_json::json!({"tool": "Write"})),
            ..Default::default()
        };
        let mut card = ToolCard::new_rs(spec, Some("s"), Some(name), None, None).unwrap();
        card.body = Some(format!("#!/bin/bash\necho {name}\n"));
        card
    }

    #[test]
    fn test_pull_hook_with_claude_installer() {
        use crate::tool::installer::ClaudeCodeInstaller;
        with_hook_tempdir(|tmp| {
            let card = make_hook_card("my-hook");
            let installer = ClaudeCodeInstaller;
            let path = card
                .pull_artifacts(tmp.to_path_buf(), Some(&installer), false, None)
                .unwrap();
            assert!(path.exists(), "script must be written");

            let settings: serde_json::Value = serde_json::from_str(
                &std::fs::read_to_string(tmp.join(".claude/settings.json")).unwrap(),
            )
            .unwrap();
            let arr = settings["hooks"]["PostToolUse"].as_array().unwrap();
            assert_eq!(arr.len(), 1);
            assert_eq!(
                arr[0]["hooks"][0]["command"], ".opsml/hooks/my-hook.sh",
                "Claude Code command path"
            );
        });
    }

    #[test]
    fn test_pull_hook_custom_output_dir_config_path_correct() {
        use crate::tool::installer::ClaudeCodeInstaller;
        let cwd_tmp = tempfile::tempdir().unwrap();
        let install_tmp = tempfile::tempdir().unwrap();

        let _guard = crate::tool::test_util::CWD_LOCK
            .lock()
            .unwrap_or_else(|e| e.into_inner());
        let orig = std::env::current_dir().unwrap();
        std::env::set_current_dir(cwd_tmp.path()).unwrap();

        let card = make_hook_card("my-hook");
        let installer = ClaudeCodeInstaller;
        let path = card
            .pull_artifacts(
                install_tmp.path().to_path_buf(),
                Some(&installer),
                false,
                None,
            )
            .unwrap();
        assert!(path.exists(), "script must be written at install_dir");

        let settings: serde_json::Value = serde_json::from_str(
            &std::fs::read_to_string(cwd_tmp.path().join(".claude/settings.json")).unwrap(),
        )
        .unwrap();
        let arr = settings["hooks"]["PostToolUse"].as_array().unwrap();
        assert_eq!(arr.len(), 1);

        let command = arr[0]["hooks"][0]["command"].as_str().unwrap();
        let script_path = std::path::Path::new(command);
        // The command must resolve to the actual script location from CWD
        let resolved = if script_path.is_absolute() {
            script_path.to_path_buf()
        } else {
            cwd_tmp.path().join(script_path)
        };
        assert!(
            resolved.exists(),
            "command path '{command}' must resolve to an existing file from CWD, but it doesn't"
        );

        std::env::set_current_dir(orig).unwrap();
    }

    #[test]
    fn test_pull_hook_with_gemini_installer() {
        use crate::tool::installer::GeminiCliInstaller;
        with_hook_tempdir(|tmp| {
            let card = make_hook_card("my-hook");
            let installer = GeminiCliInstaller;
            let path = card
                .pull_artifacts(tmp.to_path_buf(), Some(&installer), false, None)
                .unwrap();
            assert!(path.exists(), "script must be written");

            let settings: serde_json::Value = serde_json::from_str(
                &std::fs::read_to_string(tmp.join(".gemini/settings.json")).unwrap(),
            )
            .unwrap();
            let arr = settings["hooks"]["post_tool_use"].as_array().unwrap();
            assert_eq!(arr.len(), 1);
            assert_eq!(
                arr[0]["script"], ".opsml/hooks/my-hook.sh",
                "Gemini script path"
            );
        });
    }

    #[test]
    fn test_pull_hook_with_codex_installer() {
        use crate::tool::installer::CodexInstaller;
        with_hook_tempdir(|tmp| {
            let card = make_hook_card("my-hook");
            let installer = CodexInstaller;
            let path = card
                .pull_artifacts(tmp.to_path_buf(), Some(&installer), false, None)
                .unwrap();
            assert!(path.exists(), "script must be written");

            let config_path = tmp.join(".codex/config.yaml");
            assert!(config_path.exists());
            let parsed: serde_json::Value =
                serde_yaml::from_str(&std::fs::read_to_string(&config_path).unwrap()).unwrap();
            let hooks = parsed["hooks"].as_array().unwrap();
            assert_eq!(hooks.len(), 1);
            assert_eq!(hooks[0]["event"], "post_tool_use");
            assert_eq!(hooks[0]["script"], ".opsml/hooks/my-hook.sh");
        });
    }

    #[test]
    fn test_pull_hook_with_copilot_installer() {
        use crate::tool::installer::CopilotInstaller;
        with_hook_tempdir(|tmp| {
            let card = make_hook_card("my-hook");
            let installer = CopilotInstaller;
            let path = card
                .pull_artifacts(tmp.to_path_buf(), Some(&installer), false, None)
                .unwrap();
            // Copilot writes the script but no config file
            assert!(path.exists(), "script must be written");
            assert!(
                !tmp.join(".claude/settings.json").exists(),
                "no Claude config for Copilot"
            );
            assert!(
                !tmp.join(".gemini/settings.json").exists(),
                "no Gemini config for Copilot"
            );
            assert!(
                !tmp.join(".codex/config.yaml").exists(),
                "no Codex config for Copilot"
            );
        });
    }

    #[test]
    fn test_pull_hook_to_all_installers() {
        use crate::tool::installer::{
            ClaudeCodeInstaller, CodexInstaller, CopilotInstaller, GeminiCliInstaller,
        };
        with_hook_tempdir(|tmp| {
            let card = make_hook_card("multi-hook");

            // Pull to all four targets in sequence (same working dir = same config dir)
            card.pull_artifacts(tmp.to_path_buf(), Some(&ClaudeCodeInstaller), false, None)
                .unwrap();
            card.pull_artifacts(tmp.to_path_buf(), Some(&GeminiCliInstaller), false, None)
                .unwrap();
            card.pull_artifacts(tmp.to_path_buf(), Some(&CodexInstaller), false, None)
                .unwrap();
            card.pull_artifacts(tmp.to_path_buf(), Some(&CopilotInstaller), false, None)
                .unwrap();

            // Script written once (subsequent pulls overwrite same path — that's fine)
            let script = tmp.join(".opsml/hooks/multi-hook.sh");
            assert!(script.exists(), "script must exist after all pulls");

            // Claude Code config
            let claude: serde_json::Value = serde_json::from_str(
                &std::fs::read_to_string(tmp.join(".claude/settings.json")).unwrap(),
            )
            .unwrap();
            assert!(
                claude["hooks"]["PostToolUse"].as_array().is_some(),
                "Claude PostToolUse registered"
            );

            // Gemini config
            let gemini: serde_json::Value = serde_json::from_str(
                &std::fs::read_to_string(tmp.join(".gemini/settings.json")).unwrap(),
            )
            .unwrap();
            assert!(
                gemini["hooks"]["post_tool_use"].as_array().is_some(),
                "Gemini post_tool_use registered"
            );

            // Codex config
            let codex: serde_json::Value = serde_yaml::from_str(
                &std::fs::read_to_string(tmp.join(".codex/config.yaml")).unwrap(),
            )
            .unwrap();
            assert!(
                !codex["hooks"].as_array().unwrap().is_empty(),
                "Codex hooks registered"
            );
        });
    }

    #[test]
    fn test_pull_hook_codex_then_claude() {
        use crate::tool::installer::{ClaudeCodeInstaller, CodexInstaller};
        with_hook_tempdir(|tmp| {
            let card = make_hook_card("cross-hook");

            // Register in Codex first, then Claude — both configs must be independent
            card.pull_artifacts(tmp.to_path_buf(), Some(&CodexInstaller), false, None)
                .unwrap();
            card.pull_artifacts(tmp.to_path_buf(), Some(&ClaudeCodeInstaller), false, None)
                .unwrap();

            let codex: serde_json::Value = serde_yaml::from_str(
                &std::fs::read_to_string(tmp.join(".codex/config.yaml")).unwrap(),
            )
            .unwrap();
            assert_eq!(codex["hooks"].as_array().unwrap().len(), 1);

            let claude: serde_json::Value = serde_json::from_str(
                &std::fs::read_to_string(tmp.join(".claude/settings.json")).unwrap(),
            )
            .unwrap();
            assert!(claude["hooks"]["PostToolUse"].as_array().is_some());
        });
    }

    #[test]
    fn test_pull_hook_claude_then_gemini() {
        use crate::tool::installer::{ClaudeCodeInstaller, GeminiCliInstaller};
        with_hook_tempdir(|tmp| {
            let card = make_hook_card("cross-hook2");

            card.pull_artifacts(tmp.to_path_buf(), Some(&ClaudeCodeInstaller), false, None)
                .unwrap();
            card.pull_artifacts(tmp.to_path_buf(), Some(&GeminiCliInstaller), false, None)
                .unwrap();

            let claude: serde_json::Value = serde_json::from_str(
                &std::fs::read_to_string(tmp.join(".claude/settings.json")).unwrap(),
            )
            .unwrap();
            let arr = claude["hooks"]["PostToolUse"].as_array().unwrap();
            assert_eq!(arr.len(), 1, "Claude must have exactly one hook entry");

            let gemini: serde_json::Value = serde_json::from_str(
                &std::fs::read_to_string(tmp.join(".gemini/settings.json")).unwrap(),
            )
            .unwrap();
            let arr = gemini["hooks"]["post_tool_use"].as_array().unwrap();
            assert_eq!(arr.len(), 1, "Gemini must have exactly one hook entry");
        });
    }

    #[test]
    fn test_parse_markdown_hook() {
        let md = "---\nname: my-hook\ndescription: A hook\ntoolType: Hook\nhookEvents:\n  - PostToolUse\nhookMatcher:\n  tool: Write\n---\n";
        let card = parse_tool_markdown(md).unwrap();
        assert_eq!(card.spec.tool_type, ToolType::Hook);
        assert_eq!(card.spec.hook_events, vec![HookEvent::PostToolUse]);
        assert_eq!(
            card.spec.hook_matcher,
            Some(serde_json::json!({"tool": "Write"}))
        );
    }

    #[test]
    fn test_parse_markdown_mcp_server() {
        let md = "---\nname: my-mcp\ndescription: An MCP server\ntoolType: McpServer\n\
                  mcpServerName: my-server\n---\n";
        let card = parse_tool_markdown(md).unwrap();
        assert_eq!(card.spec.tool_type, ToolType::McpServer);
        assert_eq!(card.spec.mcp_server_name, Some("my-server".to_string()));
    }

    #[test]
    fn test_parse_markdown_api_call() {
        let md = "---\nname: my-api\ndescription: An API call\ntoolType: ApiCall\napiConfig:\n  url: https://example.com\n  method: GET\n---\n";
        let card = parse_tool_markdown(md).unwrap();
        assert_eq!(card.spec.tool_type, ToolType::ApiCall);
        assert_eq!(
            card.spec.api_config.as_ref().unwrap().url,
            "https://example.com"
        );
    }

    #[test]
    fn test_to_markdown_roundtrip_hook() {
        let spec = ToolSpec {
            name: "rt-hook".to_string(),
            description: "roundtrip hook".to_string(),
            tool_type: ToolType::Hook,
            hook_events: vec![HookEvent::PostToolUse],
            hook_matcher: Some(serde_json::json!({"tool": "Write"})),
            ..Default::default()
        };
        let mut card = ToolCard::new_rs(spec, Some("test"), Some("rt-hook"), None, None).unwrap();
        card.body = Some("#!/bin/bash\necho hi\n".to_string());
        let md = card.to_markdown().unwrap();
        let parsed = parse_tool_markdown(&md).unwrap();
        assert_eq!(parsed.spec.tool_type, ToolType::Hook);
        assert_eq!(parsed.spec.hook_events, vec![HookEvent::PostToolUse]);
        assert_eq!(parsed.spec.hook_matcher, card.spec.hook_matcher);
    }

    #[test]
    fn test_to_markdown_roundtrip_mcp_server() {
        let spec = ToolSpec {
            name: "rt-mcp".to_string(),
            description: "roundtrip mcp".to_string(),
            tool_type: ToolType::McpServer,
            mcp_server_name: Some("my-server".to_string()),
            ..Default::default()
        };
        let card = ToolCard::new_rs(spec, Some("test"), Some("rt-mcp"), None, None).unwrap();
        let md = card.to_markdown().unwrap();
        let parsed = parse_tool_markdown(&md).unwrap();
        assert_eq!(parsed.spec.tool_type, ToolType::McpServer);
        assert_eq!(parsed.spec.mcp_server_name, Some("my-server".to_string()));
    }

    #[test]
    fn test_to_markdown_roundtrip_api_call() {
        let spec = ToolSpec {
            name: "rt-api".to_string(),
            description: "roundtrip api".to_string(),
            tool_type: ToolType::ApiCall,
            api_config: Some(ApiCallConfig {
                url: "https://example.com".to_string(),
                method: "POST".to_string(),
                ..Default::default()
            }),
            ..Default::default()
        };
        let card = ToolCard::new_rs(spec, Some("test"), Some("rt-api"), None, None).unwrap();
        let md = card.to_markdown().unwrap();
        let parsed = parse_tool_markdown(&md).unwrap();
        assert_eq!(parsed.spec.tool_type, ToolType::ApiCall);
        assert_eq!(
            parsed.spec.api_config.as_ref().unwrap().url,
            "https://example.com"
        );
    }

    #[test]
    fn test_pull_artifacts_shell_script_no_body_returns_error() {
        let spec = ToolSpec {
            name: "no-body".to_string(),
            description: "test".to_string(),
            tool_type: ToolType::ShellScript,
            ..Default::default()
        };
        let card = ToolCard::new_rs(spec, Some("test"), Some("no-body"), None, None).unwrap();
        let tmp = tempfile::tempdir().unwrap();
        let result = card.pull_artifacts(tmp.path().to_path_buf(), None, false, None);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("no body"));
    }

    #[test]
    fn test_pull_artifacts_hook_no_body_returns_error() {
        let spec = ToolSpec {
            name: "no-body-hook".to_string(),
            description: "test".to_string(),
            tool_type: ToolType::Hook,
            hook_events: vec![HookEvent::PostToolUse],
            ..Default::default()
        };
        let card = ToolCard::new_rs(spec, Some("test"), Some("no-body-hook"), None, None).unwrap();
        let tmp = tempfile::tempdir().unwrap();
        let result = card.pull_artifacts(tmp.path().to_path_buf(), None, false, None);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("no body"));
    }

    #[test]
    fn test_from_path_unsupported_extension() {
        let tmp = tempfile::tempdir().unwrap();
        let yaml_path = tmp.path().join("card.yaml");
        std::fs::write(&yaml_path, "name: test\n").unwrap();
        let result = ToolCard::from_path(yaml_path);
        assert!(result.is_err());
        assert!(
            result
                .unwrap_err()
                .to_string()
                .to_lowercase()
                .contains("unsupported")
        );
    }

    #[test]
    fn test_calculate_content_hash_stable_key_order() {
        let spec1 = ToolSpec {
            name: "hash-test".to_string(),
            description: "test".to_string(),
            tool_type: ToolType::ApiCall,
            args_schema: Some(serde_json::json!({"b": 2, "a": 1})),
            ..Default::default()
        };
        let spec2 = ToolSpec {
            name: "hash-test".to_string(),
            description: "test".to_string(),
            tool_type: ToolType::ApiCall,
            args_schema: Some(serde_json::json!({"a": 1, "b": 2})),
            ..Default::default()
        };
        let card1 = ToolCard::new_rs(spec1, Some("test"), Some("hash-test"), None, None).unwrap();
        let card2 = ToolCard::new_rs(spec2, Some("test"), Some("hash-test"), None, None).unwrap();
        assert_eq!(
            card1.calculate_content_hash().unwrap(),
            card2.calculate_content_hash().unwrap()
        );
    }

    #[test]
    fn test_hook_matcher_roundtrip_hash_stable() {
        // Verify that hook_matcher survives a to_markdown → parse_tool_markdown roundtrip
        // and that content_hash is stable across the roundtrip.
        let spec = ToolSpec {
            name: "stable-hook".to_string(),
            description: "test".to_string(),
            tool_type: ToolType::Hook,
            hook_events: vec![HookEvent::PostToolUse],
            hook_matcher: Some(serde_json::json!({"tool": "Write"})),
            ..Default::default()
        };
        let mut card =
            ToolCard::new_rs(spec, Some("test"), Some("stable-hook"), None, None).unwrap();
        card.body = Some("#!/bin/bash\n".to_string());
        let hash_before = card.calculate_content_hash().unwrap();
        let md = card.to_markdown().unwrap();
        let parsed = parse_tool_markdown(&md).unwrap();
        let hash_after = parsed.calculate_content_hash().unwrap();
        assert_eq!(
            parsed.spec.hook_matcher,
            Some(serde_json::json!({"tool": "Write"}))
        );
        assert_eq!(hash_before, hash_after);
    }

    #[test]
    fn test_parse_tool_markdown_invalid_hook_matcher_is_err() {
        let md = "---\nname: bad-hook\ndescription: test\ntoolType: Hook\nhookEvents:\n  - PostToolUse\nhookMatcher: 42\n---\n#!/bin/bash\n";
        let result = parse_tool_markdown(md);
        assert!(result.is_err(), "expected parse error for hookMatcher: 42");
    }

    #[test]
    fn test_pull_artifacts_hash_mismatch_returns_error() {
        let spec = ToolSpec {
            name: "tampered".to_string(),
            description: "test".to_string(),
            tool_type: ToolType::Hook,
            hook_events: vec![HookEvent::PostToolUse],
            ..Default::default()
        };
        let mut card = ToolCard::new_rs(spec, Some("s"), Some("tampered"), None, None).unwrap();
        card.body = Some("#!/bin/bash\necho legit\n".to_string());

        let wrong_hash = vec![0u8; 32]; // deliberately wrong 32-byte hash
        let tmp = tempfile::tempdir().unwrap();
        let result = card.pull_artifacts(tmp.path().to_path_buf(), None, false, Some(&wrong_hash));
        assert!(result.is_err());
        let msg = result.unwrap_err().to_string();
        assert!(
            msg.contains("hash mismatch") || msg.contains("Content hash"),
            "unexpected error: {msg}"
        );
    }

    #[test]
    fn test_validate_script_body_size_limit() {
        let spec = ToolSpec {
            name: "big-script".to_string(),
            description: "test".to_string(),
            tool_type: ToolType::ShellScript,
            ..Default::default()
        };
        let mut card = ToolCard::new_rs(spec, Some("s"), Some("big-script"), None, None).unwrap();
        // Body just over 1 MB — must fail validation
        let body = format!("#!/bin/bash\n{}", "x".repeat(1024 * 1024));
        card.body = Some(body);
        let tmp = tempfile::tempdir().unwrap();
        let result = card.pull_artifacts(tmp.path().to_path_buf(), None, false, None);
        assert!(result.is_err());
        let msg = result.unwrap_err().to_string();
        assert!(
            msg.contains("1 MB") || msg.contains("exceeds"),
            "unexpected: {msg}"
        );
    }

    #[test]
    fn test_validate_script_body_missing_shebang_is_err() {
        let spec = ToolSpec {
            name: "no-shebang".to_string(),
            description: "test".to_string(),
            tool_type: ToolType::ShellScript,
            ..Default::default()
        };
        let mut card = ToolCard::new_rs(spec, Some("s"), Some("no-shebang"), None, None).unwrap();
        card.body = Some("echo hello\n".to_string());
        let tmp = tempfile::tempdir().unwrap();
        let result = card.pull_artifacts(tmp.path().to_path_buf(), None, false, None);
        assert!(result.is_err());
        let msg = result.unwrap_err().to_string();
        assert!(
            msg.contains("shebang") || msg.contains("#!"),
            "unexpected: {msg}"
        );
    }
}
