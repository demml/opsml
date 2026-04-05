use super::error::ToolError;
use crate::BaseArgs;
use crate::error::CardError;
use crate::traits::{OpsmlCard, ProfileExt};
use chrono::{DateTime, Utc};
use opsml_types::contracts::tool::{ToolSpec, ToolType};
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

    let body_opt = if body.is_empty() { None } else { Some(body) };
    let name = spec.name.clone();

    let mut card = ToolCard::new_rs(spec, Some("opsml"), Some(&name), None, None)?;
    card.body = body_opt;
    Ok(card)
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
        let mut hasher = Sha256::new();
        let canonical = serde_json::to_vec(&self.spec)?;
        hasher.update(&canonical);
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
            script_config: Option<&'a opsml_types::contracts::tool::ShellScriptConfig>,
            #[serde(skip_serializing_if = "Option::is_none")]
            api_config: Option<&'a opsml_types::contracts::tool::ApiCallConfig>,
            #[serde(skip_serializing_if = "Option::is_none")]
            mcp_server_name: Option<&'a str>,
            #[serde(skip_serializing_if = "<[_]>::is_empty")]
            allowed_tools: &'a [String],
            requires_approval: bool,
        }

        let fm = ToolFrontmatter {
            name: &self.spec.name,
            description: &self.spec.description,
            tool_type: self.spec.tool_type.to_string(),
            args_schema: self.spec.args_schema.as_ref(),
            output_schema: self.spec.output_schema.as_ref(),
            script_config: self.spec.script_config.as_ref(),
            api_config: self.spec.api_config.as_ref(),
            mcp_server_name: self.spec.mcp_server_name.as_deref(),
            allowed_tools: &self.spec.allowed_tools,
            requires_approval: self.spec.requires_approval,
        };

        let yaml = serde_yaml::to_string(&fm)?;
        let yaml = yaml.trim_start_matches("---\n");
        let body = self.body.as_deref().unwrap_or("");

        Ok(format!("---\n{yaml}---\n{body}"))
    }

    pub fn pull_artifacts(&self, install_dir: PathBuf) -> Result<PathBuf, ToolError> {
        std::fs::create_dir_all(&install_dir)?;
        let body_content = self.body.as_deref().unwrap_or("");

        match &self.spec.tool_type {
            ToolType::ShellScript => {
                let path = install_dir.join(format!("{}.sh", self.name));
                std::fs::write(&path, body_content)?;
                #[cfg(unix)]
                {
                    use std::os::unix::fs::PermissionsExt;
                    let mut perms = std::fs::metadata(&path)?.permissions();
                    perms.set_mode(0o755);
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
    use opsml_types::contracts::tool::{ApiCallConfig, ShellScriptConfig};

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
        let card =
            ToolCard::new_rs(spec, Some("test-space"), Some("my-tool"), None, None).unwrap();

        let json = serde_json::to_string(&card).unwrap();
        let restored = ToolCard::model_validate_json(json).unwrap();

        assert_eq!(restored.name, card.name);
        assert_eq!(restored.spec.description, card.spec.description);
        assert_eq!(restored.body, card.body);
    }

    #[test]
    fn test_tool_card_get_registry_card() {
        let spec = make_shell_spec();
        let card =
            ToolCard::new_rs(spec, Some("test-space"), Some("my-tool"), None, None).unwrap();

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

        let path = card.pull_artifacts(tmp.path().to_path_buf()).unwrap();
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

        let path = card.pull_artifacts(tmp.path().to_path_buf()).unwrap();
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
        let card =
            ToolCard::new_rs(spec, Some("test-space"), Some("my-mcp"), None, None).unwrap();

        let path = card.pull_artifacts(tmp.path().to_path_buf()).unwrap();
        assert!(path.exists());
        assert!(path.to_str().unwrap().ends_with("-mcp.json"));
    }

    #[test]
    fn test_pull_artifacts_api_call() {
        let tmp = tempfile::tempdir().unwrap();
        let spec = make_api_spec();
        let card =
            ToolCard::new_rs(spec, Some("test-space"), Some("my-api"), None, None).unwrap();

        let path = card.pull_artifacts(tmp.path().to_path_buf()).unwrap();
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

        installer.merge_mcp_entry("my-server", entry.clone()).unwrap();
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
        let output = card.pull_artifacts(tmp.path().to_path_buf()).unwrap();
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
        let output = card.pull_artifacts(tmp.path().to_path_buf()).unwrap();
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
}
