use super::error::SubAgentError;
use crate::BaseArgs;
use crate::error::CardError;
use crate::traits::{OpsmlCard, ProfileExt};
use chrono::{DateTime, Utc};
use opsml_agent_cli::AgentCliFramework;
use opsml_types::contracts::subagent::SubAgentSpec;
use opsml_types::contracts::{CardRecord, SubAgentCardClientRecord};
use opsml_types::{RegistryType, SaveName, Suffix};
use opsml_utils::PyHelperFuncs;
use opsml_utils::get_utc_datetime;
use scouter_client::ProfileRequest;
use serde::{Deserialize, Serialize, de::DeserializeOwned};
use sha2::{Digest, Sha256};
use std::path::PathBuf;
use tracing::instrument;

/// Parse a SubAgent markdown file (YAML frontmatter + markdown body) into a SubAgentCard.
#[instrument(skip_all)]
pub fn parse_subagent_markdown(content: &str) -> Result<SubAgentCard, SubAgentError> {
    // Normalize Windows line endings so the delimiter search works cross-platform.
    let content = content.replace("\r\n", "\n");
    let content = content.as_str();

    // Extract YAML frontmatter between --- delimiters
    let after_open = content
        .strip_prefix("---\n")
        .ok_or_else(|| SubAgentError::Error("Missing opening ---".to_string()))?;

    let close_pos = after_open
        .find("\n---\n")
        .ok_or_else(|| SubAgentError::Error("Missing closing ---".to_string()))?;

    let yaml_str = &after_open[..close_pos];
    let body = after_open[close_pos + 5..].to_string();

    let mut spec: SubAgentSpec = serde_yaml::from_str(yaml_str)?;

    // Validate name: must be non-empty and contain only alphanumeric, '-', or '_'.
    if spec.name.is_empty()
        || !spec
            .name
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_')
    {
        return Err(SubAgentError::Error(format!(
            "Invalid agent name '{}': must be non-empty and contain only [a-zA-Z0-9_-]",
            spec.name
        )));
    }

    spec.system_prompt = if body.is_empty() { None } else { Some(body) };

    let name = spec.name.clone();
    SubAgentCard::new_rs(spec, Some("opsml"), Some(&name), None, None)
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct SubAgentCard {
    pub spec: SubAgentSpec,

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
}

impl SubAgentCard {
    pub fn new_rs(
        spec: SubAgentSpec,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        tags: Option<Vec<String>>,
    ) -> Result<Self, SubAgentError> {
        let registry_type = RegistryType::SubAgent;
        let base_args = BaseArgs::create_args(name, space, version, None, &registry_type)
            .map_err(|e| SubAgentError::Error(e.to_string()))?;

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
        })
    }

    pub fn get_registry_card(&self) -> Result<CardRecord, SubAgentError> {
        let compatible_clis = self
            .spec
            .compatible_clis
            .iter()
            .map(|c| c.to_string())
            .collect();

        let record = SubAgentCardClientRecord {
            uid: self.uid.clone(),
            created_at: self.created_at,
            app_env: self.app_env.clone(),
            space: self.space.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            tags: self.tags.clone(),
            compatible_clis,
            description: Some(self.spec.description.clone()),
            content_hash: Some(self.calculate_content_hash()?),
            opsml_version: self.opsml_version.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            download_count: 0,
        };

        Ok(CardRecord::SubAgent(record))
    }

    pub fn calculate_content_hash(&self) -> Result<Vec<u8>, SubAgentError> {
        let mut hasher = Sha256::new();
        let canonical = serde_json::to_vec(&self.spec)?;
        hasher.update(&canonical);
        Ok(hasher.finalize().to_vec())
    }

    pub fn to_markdown(&self) -> Result<String, SubAgentError> {
        use serde::Serialize;

        #[derive(Debug, Clone, Serialize)]
        #[serde(rename_all = "camelCase")]
        struct OpsmlFrontmatter<'a> {
            name: &'a str,
            description: &'a str,
            #[serde(skip_serializing_if = "Option::is_none")]
            model: Option<&'a str>,
            #[serde(skip_serializing_if = "<[_]>::is_empty")]
            tools: &'a [String],
            #[serde(skip_serializing_if = "<[_]>::is_empty")]
            disallowed_tools: &'a [String],
            #[serde(skip_serializing_if = "<[_]>::is_empty")]
            skills: &'a [String],
            #[serde(skip_serializing_if = "Option::is_none")]
            max_turns: Option<u32>,
            #[serde(skip_serializing_if = "Vec::is_empty")]
            compatible_clis: Vec<String>,
        }

        let fm = OpsmlFrontmatter {
            name: &self.spec.name,
            description: &self.spec.description,
            model: self.spec.model.as_deref(),
            tools: &self.spec.tools,
            disallowed_tools: &self.spec.disallowed_tools,
            skills: &self.spec.skills,
            max_turns: self.spec.max_turns,
            compatible_clis: self
                .spec
                .compatible_clis
                .iter()
                .map(|c| c.to_string())
                .collect(),
        };

        let yaml = serde_yaml::to_string(&fm)?;
        let yaml = yaml.trim_start_matches("---\n");
        let body = self.spec.system_prompt.as_deref().unwrap_or("");

        Ok(format!("---\n{yaml}---\n{body}"))
    }

    pub fn install(
        &self,
        framework: &dyn AgentCliFramework,
        global: bool,
    ) -> Result<PathBuf, SubAgentError> {
        let content = framework
            .serialize_agent(&self.spec)
            .map_err(|e| SubAgentError::Error(e.to_string()))?;
        let dir = framework
            .agent_dir(global)
            .map_err(|e| SubAgentError::Error(e.to_string()))?;
        std::fs::create_dir_all(&dir)?;

        let fname = framework.agent_file_name(&self.spec.name);
        if fname.contains("..") || fname.contains('/') || fname.contains(std::path::MAIN_SEPARATOR)
        {
            return Err(SubAgentError::Error(format!(
                "Invalid agent filename: {fname}"
            )));
        }
        let file_path = dir.join(&fname);

        std::fs::write(&file_path, content)?;
        Ok(file_path)
    }

    pub fn save_card(&mut self, path: PathBuf) -> Result<(), SubAgentError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(self, card_save_path.as_path())?;
        Ok(())
    }

    pub fn model_validate_json(json_string: String) -> Result<SubAgentCard, SubAgentError> {
        Ok(serde_json::from_str(&json_string)?)
    }

    pub fn from_path(path: PathBuf) -> Result<Self, SubAgentError> {
        deserialize_from_path(path)
    }
}

fn deserialize_from_path<T: DeserializeOwned>(path: PathBuf) -> Result<T, SubAgentError> {
    let ext = path
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or_default();
    let content = std::fs::read_to_string(&path)?;
    match ext {
        "json" => Ok(serde_json::from_str(&content)?),
        other => Err(SubAgentError::Error(format!(
            "Unsupported file extension for SubAgentCard deserialization: .{other}"
        ))),
    }
}

impl OpsmlCard for SubAgentCard {
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

impl ProfileExt for SubAgentCard {
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
    use opsml_agent_cli::{
        AgentCliFramework, ClaudeCodeFramework, CodexFramework, CopilotFramework,
        GeminiCliFramework,
    };
    use opsml_types::contracts::CompatibleTool;

    fn make_spec() -> SubAgentSpec {
        SubAgentSpec {
            name: "test-agent".to_string(),
            description: "A test agent".to_string(),
            system_prompt: Some("Do the thing.".to_string()),
            model: Some("claude-sonnet-4-6".to_string()),
            tools: vec!["Read".to_string(), "Grep".to_string()],
            disallowed_tools: vec!["Bash".to_string()],
            max_turns: Some(5),
            compatible_clis: vec![CompatibleTool::ClaudeCode, CompatibleTool::Codex],
            ..Default::default()
        }
    }

    #[test]
    fn test_subagent_card_new_rs() {
        let spec = make_spec();
        let card = SubAgentCard::new_rs(
            spec,
            Some("test-space"),
            Some("test-agent"),
            None,
            Some(vec!["tag1".to_string()]),
        )
        .unwrap();

        assert_eq!(card.name, "test-agent");
        assert_eq!(card.space, "test-space");
        assert_eq!(card.version, "0.0.0");
        assert_eq!(card.tags, vec!["tag1"]);
        assert!(card.is_card);
        assert_eq!(card.registry_type, RegistryType::SubAgent);
    }

    #[test]
    fn test_subagent_card_json_roundtrip() {
        let spec = make_spec();
        let card =
            SubAgentCard::new_rs(spec, Some("test-space"), Some("test-agent"), None, None).unwrap();

        let json = serde_json::to_string(&card).unwrap();
        let restored = SubAgentCard::model_validate_json(json).unwrap();

        assert_eq!(restored.name, card.name);
        assert_eq!(restored.spec.description, card.spec.description);
        assert_eq!(restored.spec.system_prompt, card.spec.system_prompt);
    }

    #[test]
    fn test_subagent_card_get_registry_card() {
        let spec = make_spec();
        let card =
            SubAgentCard::new_rs(spec, Some("test-space"), Some("test-agent"), None, None).unwrap();

        let record = card.get_registry_card().unwrap();
        match record {
            CardRecord::SubAgent(r) => {
                assert_eq!(r.name, "test-agent");
                assert_eq!(r.space, "test-space");
                assert!(r.content_hash.is_some());
                assert!(!r.content_hash.unwrap().is_empty());
            }
            _ => panic!("expected CardRecord::SubAgent"),
        }
    }

    #[test]
    fn test_content_hash_stability() {
        let spec = make_spec();
        let card1 = SubAgentCard::new_rs(spec.clone(), Some("s"), Some("a"), None, None).unwrap();
        let card2 = SubAgentCard::new_rs(spec, Some("s"), Some("a"), None, None).unwrap();

        assert_eq!(
            card1.calculate_content_hash().unwrap(),
            card2.calculate_content_hash().unwrap()
        );
    }

    #[test]
    fn test_markdown_roundtrip() {
        let spec = make_spec();
        let card =
            SubAgentCard::new_rs(spec, Some("test-space"), Some("test-agent"), None, None).unwrap();

        let md = card.to_markdown().unwrap();
        assert!(md.contains("test-agent"));
        assert!(md.contains("A test agent"));
        assert!(md.contains("Do the thing."));

        let restored = parse_subagent_markdown(&md).unwrap();
        assert_eq!(restored.spec.name, card.spec.name);
        assert_eq!(restored.spec.description, card.spec.description);
        assert_eq!(restored.spec.compatible_clis, card.spec.compatible_clis);
    }

    #[test]
    fn test_claude_code_framework_serialize() {
        let spec = make_spec();
        let output = ClaudeCodeFramework.serialize_agent(&spec).unwrap();

        assert!(output.starts_with("---\n"));
        assert!(output.contains("maxTurns: 5"));
        assert!(output.contains("test-agent"));
        // compatible_clis must NOT appear in Claude Code output
        assert!(!output.contains("compatible_clis"));
        assert!(!output.contains("compatibleClis"));
    }

    #[test]
    fn test_gemini_cli_framework_serialize() {
        let spec = make_spec();
        let output = GeminiCliFramework.serialize_agent(&spec).unwrap();

        assert!(output.starts_with("---\n"));
        assert!(output.contains("name: test-agent"));
        assert!(output.contains("description:"));
        // compatible_clis must NOT appear in Gemini output
        assert!(!output.contains("compatible_clis"));
    }

    #[test]
    fn test_codex_framework_serialize() {
        let spec = make_spec();
        let output = CodexFramework.serialize_agent(&spec).unwrap();

        // TOML format, not YAML
        assert!(!output.starts_with("---"));
        assert!(output.contains("name = \"test-agent\""));
        assert!(output.contains("developer_instructions"));
        // mcp_servers section absent when spec.mcp_servers is empty
        assert!(!output.contains("mcp_servers"));
    }

    #[test]
    fn test_codex_framework_serialize_with_mcp_servers() {
        let mut spec = make_spec();
        spec.mcp_servers.insert(
            "my-server".to_string(),
            serde_json::json!({"command": "npx", "args": ["-y", "my-mcp-server"]}),
        );
        spec.sandbox_mode = Some("workspace-write".to_string());
        let output = CodexFramework.serialize_agent(&spec).unwrap();

        assert!(output.contains("[mcp_servers.my-server]"));
        assert!(output.contains("command = \"npx\""));
        assert!(output.contains("sandbox_mode = \"workspace-write\""));
    }

    #[test]
    fn test_copilot_framework_serialize() {
        let spec = make_spec();
        let output = CopilotFramework.serialize_agent(&spec).unwrap();
        let filename = CopilotFramework.agent_file_name(&spec.name);

        assert!(output.starts_with("---\n"));
        assert!(output.contains("name: test-agent"));
        assert!(output.contains("description:"));
        assert!(output.contains("instructions:"));
        assert!(filename.ends_with(".agent.md"));
    }

    #[test]
    fn test_copilot_file_extension() {
        assert_eq!(
            CopilotFramework.agent_file_name("my-agent"),
            "my-agent.agent.md"
        );
    }

    #[test]
    fn test_install_creates_file() {
        let spec = make_spec();
        let card =
            SubAgentCard::new_rs(spec, Some("test-space"), Some("test-agent"), None, None).unwrap();

        let tmp = tempfile::tempdir().unwrap();

        struct TestFramework(PathBuf);
        impl opsml_agent_cli::AgentCliFramework for TestFramework {
            fn name(&self) -> &'static str {
                "test"
            }
            fn skill_path(&self, name: &str) -> PathBuf {
                PathBuf::from(format!("{name}/SKILL.md"))
            }
            fn global_skill_path(
                &self,
                name: &str,
            ) -> Result<PathBuf, opsml_agent_cli::FrameworkError> {
                Ok(self.skill_path(name))
            }
            fn agent_dir(&self, _global: bool) -> Result<PathBuf, opsml_agent_cli::FrameworkError> {
                Ok(self.0.clone())
            }
            fn agent_file_name(&self, name: &str) -> String {
                format!("{name}.md")
            }
            fn serialize_agent(
                &self,
                spec: &SubAgentSpec,
            ) -> Result<String, opsml_agent_cli::FrameworkError> {
                opsml_agent_cli::ClaudeCodeFramework.serialize_agent(spec)
            }
            fn command_dir(&self, _global: bool) -> PathBuf {
                PathBuf::from(".commands")
            }
            fn mcp_config_path(&self) -> PathBuf {
                PathBuf::from(".mcp.json")
            }
            fn merge_mcp_entry(
                &self,
                _name: &str,
                _entry: serde_json::Value,
            ) -> Result<(), opsml_agent_cli::FrameworkError> {
                Ok(())
            }
            fn install_hook(
                &self,
                _name: &str,
                _script_path: &std::path::Path,
                _events: &[opsml_types::contracts::tool::HookEvent],
                _matcher: Option<&serde_json::Value>,
                _global: bool,
            ) -> Result<(), opsml_agent_cli::FrameworkError> {
                Ok(())
            }
        }

        let framework = TestFramework(tmp.path().to_path_buf());
        let path = card.install(&framework, false).unwrap();

        assert!(path.exists());
        let content = std::fs::read_to_string(&path).unwrap();
        assert!(content.contains("test-agent"));
    }

    #[test]
    fn test_parse_markdown_missing_delimiter() {
        let no_delims = "name: test\ndescription: test\n";
        assert!(parse_subagent_markdown(no_delims).is_err());
    }

    #[test]
    fn test_parse_markdown_crlf_line_endings() {
        // A valid markdown with Windows-style CRLF should parse successfully.
        let crlf = "---\r\nname: my-agent\r\ndescription: test\r\n---\r\nDo something.\r\n";
        let card = parse_subagent_markdown(crlf).unwrap();
        assert_eq!(card.spec.name, "my-agent");
        assert!(card.spec.system_prompt.is_some());
    }

    #[test]
    fn test_parse_markdown_invalid_name_rejected() {
        let bad_name = "---\nname: \"../../evil\"\ndescription: test\n---\n";
        assert!(parse_subagent_markdown(bad_name).is_err());
    }

    #[test]
    fn test_from_path_roundtrip() {
        let spec = make_spec();
        let mut card =
            SubAgentCard::new_rs(spec, Some("test-space"), Some("test-agent"), None, None).unwrap();

        let tmp = tempfile::tempdir().unwrap();
        card.save_card(tmp.path().to_path_buf()).unwrap();

        let json_path = tmp.path().join("Card.json");
        let loaded = SubAgentCard::from_path(json_path).unwrap();

        assert_eq!(loaded.name, card.name);
        assert_eq!(loaded.spec.description, card.spec.description);
        assert_eq!(loaded.spec.system_prompt, card.spec.system_prompt);
    }

    #[test]
    fn test_from_path_unsupported_extension() {
        let tmp = tempfile::tempdir().unwrap();
        let yaml_path = tmp.path().join("Card.yaml");
        std::fs::write(&yaml_path, "name: test").unwrap();
        let err = SubAgentCard::from_path(yaml_path).unwrap_err();
        assert!(err.to_string().contains("Unsupported"));
    }

    #[test]
    fn test_to_markdown_system_prompt_not_in_frontmatter() {
        let spec = make_spec();
        let card =
            SubAgentCard::new_rs(spec, Some("test-space"), Some("test-agent"), None, None).unwrap();

        let md = card.to_markdown().unwrap();

        // Extract the YAML frontmatter block between the two --- delimiters.
        let after_open = md.strip_prefix("---\n").unwrap();
        let close = after_open.find("\n---\n").unwrap();
        let frontmatter = &after_open[..close];

        assert!(
            !frontmatter.contains("systemPrompt") && !frontmatter.contains("system_prompt"),
            "systemPrompt must not appear in the YAML frontmatter block"
        );
    }

    #[test]
    fn test_content_hash_changes_with_system_prompt() {
        let spec1 = make_spec();
        let mut spec2 = spec1.clone();
        spec2.system_prompt = Some("A completely different prompt.".to_string());

        let card1 = SubAgentCard::new_rs(spec1, Some("s"), Some("a"), None, None).unwrap();
        let card2 = SubAgentCard::new_rs(spec2, Some("s"), Some("a"), None, None).unwrap();

        assert_ne!(
            card1.calculate_content_hash().unwrap(),
            card2.calculate_content_hash().unwrap()
        );
    }
}
