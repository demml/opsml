use super::error::SubAgentError;
use super::target::SubAgentCliTarget;
use crate::BaseArgs;
use crate::error::CardError;
use crate::traits::{OpsmlCard, ProfileExt};
use chrono::{DateTime, Utc};
use opsml_types::contracts::subagent::SubAgentSpec;
use opsml_types::contracts::{CardRecord, SubAgentCardClientRecord};
use opsml_types::{RegistryType, SaveName, Suffix};
use opsml_utils::PyHelperFuncs;
use opsml_utils::get_utc_datetime;
use scouter_client::ProfileRequest;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::path::PathBuf;
use tracing::instrument;

/// Parse a SubAgent markdown file (YAML frontmatter + markdown body) into a SubAgentCard.
#[instrument(skip_all)]
pub fn parse_subagent_markdown(content: &str) -> Result<SubAgentCard, SubAgentError> {
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
        target: &dyn SubAgentCliTarget,
        global: bool,
    ) -> Result<PathBuf, SubAgentError> {
        let content = target.serialize(&self.spec)?;
        let dir = target.agent_dir(global);
        std::fs::create_dir_all(&dir)?;
        let file_path = dir.join(target.file_name(&self.spec.name));
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
    use crate::subagent::target::{ClaudeCodeTarget, CodexTarget, CopilotTarget, GeminiCliTarget};

    fn make_spec() -> SubAgentSpec {
        SubAgentSpec {
            name: "test-agent".to_string(),
            description: "A test agent".to_string(),
            system_prompt: Some("Do the thing.".to_string()),
            model: Some("claude-sonnet-4-6".to_string()),
            tools: vec!["Read".to_string(), "Grep".to_string()],
            disallowed_tools: vec!["Bash".to_string()],
            max_turns: Some(5),
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
    }

    #[test]
    fn test_claude_code_target_serialize() {
        let spec = make_spec();
        let target = ClaudeCodeTarget;
        let output = target.serialize(&spec).unwrap();

        assert!(output.starts_with("---\n"));
        assert!(output.contains("maxTurns: 5"));
        assert!(output.contains("test-agent"));
        // compatible_clis must NOT appear in Claude Code output
        assert!(!output.contains("compatible_clis"));
        assert!(!output.contains("compatibleClis"));
    }

    #[test]
    fn test_gemini_cli_target_serialize() {
        let spec = make_spec();
        let target = GeminiCliTarget;
        let output = target.serialize(&spec).unwrap();

        assert!(output.starts_with("---\n"));
        assert!(output.contains("name: test-agent"));
        assert!(output.contains("description:"));
    }

    #[test]
    fn test_codex_target_serialize() {
        let spec = make_spec();
        let target = CodexTarget;
        let output = target.serialize(&spec).unwrap();

        // TOML format, not YAML
        assert!(!output.starts_with("---"));
        assert!(output.contains("name = \"test-agent\""));
        assert!(output.contains("mcp_servers"));
        // developer_instructions must be last field (TOML serialization order)
        let dev_instr_pos = output.find("developer_instructions").unwrap();
        let mcp_pos = output.find("mcp_servers").unwrap();
        assert!(dev_instr_pos > mcp_pos);
    }

    #[test]
    fn test_copilot_target_serialize() {
        let spec = make_spec();
        let target = CopilotTarget;
        let output = target.serialize(&spec).unwrap();
        let filename = target.file_name(&spec.name);

        assert!(output.starts_with("---\n"));
        assert!(output.contains("name: test-agent"));
        assert!(filename.ends_with(".agent.md"));
    }

    #[test]
    fn test_copilot_file_extension() {
        let target = CopilotTarget;
        assert_eq!(target.file_name("my-agent"), "my-agent.agent.md");
    }

    #[test]
    fn test_install_creates_file() {
        let spec = make_spec();
        let card =
            SubAgentCard::new_rs(spec, Some("test-space"), Some("test-agent"), None, None).unwrap();

        let tmp = tempfile::tempdir().unwrap();
        // Override directory by using a custom target
        struct TestTarget(PathBuf);
        impl SubAgentCliTarget for TestTarget {
            fn serialize(&self, spec: &SubAgentSpec) -> Result<String, SubAgentError> {
                ClaudeCodeTarget.serialize(spec)
            }
            fn file_name(&self, name: &str) -> String {
                format!("{name}.md")
            }
            fn agent_dir(&self, _global: bool) -> PathBuf {
                self.0.clone()
            }
        }

        let test_target = TestTarget(tmp.path().to_path_buf());
        let path = card.install(&test_target, false).unwrap();

        assert!(path.exists());
        let content = std::fs::read_to_string(&path).unwrap();
        assert!(content.contains("test-agent"));
    }

    #[test]
    fn test_parse_markdown_missing_delimiter() {
        let no_delims = "name: test\ndescription: test\n";
        assert!(parse_subagent_markdown(no_delims).is_err());
    }
}
