use crate::BaseArgs;
use crate::error::CardError;
use crate::skill::error::SkillError;
use crate::traits::OpsmlCard;
use crate::traits::ProfileExt;
use chrono::{DateTime, Utc};
use opsml_types::contracts::CardRecord;
use opsml_types::contracts::SkillCardClientRecord;
use opsml_types::contracts::agent::AgentSkillStandard;
use opsml_types::contracts::skill::SkillDependency;
use opsml_types::{RegistryType, SaveName, Suffix};
use opsml_utils::PyHelperFuncs;
#[cfg(feature = "python")]
use opsml_utils::depythonize_object_to_value;
use opsml_utils::get_utc_datetime;
#[cfg(feature = "python")]
use pyo3::IntoPyObjectExt;
#[cfg(feature = "python")]
use pyo3::prelude::*;
#[cfg(feature = "python")]
use pythonize;
use scouter_client::ProfileRequest;
use serde::de::DeserializeOwned;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};
use tracing::{error, instrument};
use walkdir::WalkDir;

fn deserialize_from_path<T: DeserializeOwned>(path: PathBuf) -> Result<T, SkillError> {
    let content = std::fs::read_to_string(&path)?;
    let extension = path
        .extension()
        .and_then(|ext| ext.to_str())
        .ok_or_else(|| SkillError::Error(format!("Invalid file path: {:?}", path)))?;
    let item = match extension.to_lowercase().as_str() {
        "json" => serde_json::from_str(&content)?,
        "yaml" | "yml" => serde_yaml::from_str(&content)?,
        _ => {
            return Err(SkillError::Error(format!(
                "Unsupported file extension '{}'. Expected .json, .yaml, or .yml",
                extension
            )));
        }
    };
    Ok(item)
}

fn copy_companion_files(source_dir: &Path, dest_dir: &Path) -> Result<(), SkillError> {
    let canonical_dest = dest_dir
        .canonicalize()
        .map_err(|e| SkillError::Error(format!("cannot canonicalize dest_dir: {e}")))?;
    for entry in WalkDir::new(source_dir).follow_links(false).min_depth(1) {
        let entry = entry.map_err(|e| SkillError::Error(e.to_string()))?;
        // Skip symlinks — following them could exfiltrate files outside the source tree.
        if entry.file_type().is_symlink() {
            continue;
        }
        let rel = entry
            .path()
            .strip_prefix(source_dir)
            .map_err(|e| SkillError::Error(e.to_string()))?;
        let file_name = rel.file_name().and_then(|f| f.to_str()).unwrap_or("");
        if file_name == "SKILL.md" || file_name == "Card.json" {
            continue;
        }
        let dest = canonical_dest.join(rel);
        if entry.file_type().is_dir() {
            std::fs::create_dir_all(&dest)?;
        } else {
            if let Some(parent) = dest.parent() {
                std::fs::create_dir_all(parent)?;
            }
            // Containment check: ensure dest cannot escape dest_dir via path components.
            let canonical_dest_file = dest.canonicalize().unwrap_or_else(|_| dest.clone());
            if !canonical_dest_file.starts_with(&canonical_dest) {
                return Err(SkillError::Error(format!(
                    "path traversal detected: '{}' escapes destination directory",
                    dest.display()
                )));
            }
            std::fs::copy(entry.path(), &dest)?;
        }
    }
    Ok(())
}

/// Parse a skill markdown file (YAML frontmatter + markdown body) into a SkillCard.
#[instrument(skip_all)]
pub fn parse_skill_markdown(
    content: &str,
    source_path: Option<&PathBuf>,
) -> Result<SkillCard, SkillError> {
    let skill = AgentSkillStandard::from_markdown(content).map_err(|e| {
        error!("Failed to parse skill markdown {:?}: {e}", source_path);
        SkillError::AgentConfigError(e)
    })?;
    let name = skill.name.clone();
    SkillCard::new_rs(
        skill,
        Some("opsml"),
        Some(&name),
        None,
        None,
        None,
        None,
        None,
    )
}

#[cfg_attr(feature = "python", pyclass(skip_from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct SkillCard {
    pub skill: AgentSkillStandard,
    pub dependencies: Vec<SkillDependency>,
    pub space: String,
    pub name: String,
    pub version: String,
    pub uid: String,
    pub tags: Vec<String>,
    pub input_schema: Option<serde_json::Value>,
    pub compatible_tools: Vec<String>,
    pub app_env: String,
    pub is_card: bool,
    pub opsml_version: String,
    pub created_at: DateTime<Utc>,
    pub registry_type: RegistryType,

    #[serde(skip)]
    pub source_dir: Option<PathBuf>, // CLI-only; not exposed to Python or serialized to the registry.
}

#[cfg(feature = "python")]
#[pymethods]
impl SkillCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (skill, space=None, name=None, version=None, tags=None, compatible_tools=None, dependencies=None, input_schema=None, source_dir=None))]
    pub fn new(
        skill: &Bound<'_, PyAny>,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        tags: Option<Vec<String>>,
        compatible_tools: Option<Vec<String>>,
        dependencies: Option<Vec<SkillDependency>>,
        input_schema: Option<Bound<'_, PyAny>>,
        source_dir: Option<PathBuf>,
    ) -> Result<Self, SkillError> {
        let py = skill.py();
        let skill = skill.extract::<AgentSkillStandard>().inspect_err(|e| {
            error!("Failed to extract AgentSkillStandard: {e}");
        })?;

        let derived_name = skill.name.clone();
        let effective_name = name.or(Some(derived_name.as_str()));
        let input_schema = input_schema
            .map(|schema| depythonize_object_to_value(py, &schema))
            .transpose()?;

        let mut card = Self::new_rs(
            skill,
            space,
            effective_name,
            version,
            tags,
            compatible_tools,
            dependencies,
            input_schema,
        )?;
        card.source_dir = source_dir;
        Ok(card)
    }

    #[getter]
    pub fn skill<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, SkillError> {
        Ok(self.skill.clone().into_bound_py_any(py)?)
    }

    #[setter]
    pub fn set_skill(&mut self, skill: &Bound<'_, PyAny>) -> Result<(), SkillError> {
        self.skill = skill.extract::<AgentSkillStandard>().inspect_err(|e| {
            error!("Failed to extract AgentSkillStandard: {e}");
        })?;
        Ok(())
    }

    #[getter]
    pub fn dependencies<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, SkillError> {
        Ok(self.dependencies.clone().into_bound_py_any(py)?)
    }

    #[setter]
    pub fn set_dependencies(&mut self, dependencies: &Bound<'_, PyAny>) -> Result<(), SkillError> {
        self.dependencies = dependencies
            .extract::<Vec<SkillDependency>>()
            .inspect_err(|e| {
                error!("Failed to extract dependencies: {e}");
            })?;
        Ok(())
    }

    #[getter]
    pub fn input_schema<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Option<Bound<'py, PyAny>>, SkillError> {
        match &self.input_schema {
            Some(schema) => Ok(Some(
                pythonize::pythonize(py, schema).map_err(|e| SkillError::Error(e.to_string()))?,
            )),
            None => Ok(None),
        }
    }

    #[setter]
    pub fn set_input_schema(&mut self, schema: Option<Bound<'_, PyAny>>) -> Result<(), SkillError> {
        self.input_schema = match schema {
            Some(s) => Some(depythonize_object_to_value(s.py(), &s)?),
            None => None,
        };
        Ok(())
    }

    #[getter]
    pub fn space(&self) -> String {
        self.space.clone()
    }
    #[setter]
    pub fn set_space(&mut self, val: String) {
        self.space = val;
    }

    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }
    #[setter]
    pub fn set_name(&mut self, val: String) {
        self.name = val;
    }

    #[getter]
    pub fn version(&self) -> String {
        self.version.clone()
    }
    #[setter]
    pub fn set_version(&mut self, val: String) {
        self.version = val;
    }

    #[getter]
    pub fn uid(&self) -> String {
        self.uid.clone()
    }
    #[setter]
    pub fn set_uid(&mut self, val: String) {
        self.uid = val;
    }

    #[getter]
    pub fn tags(&self) -> Vec<String> {
        self.tags.clone()
    }
    #[setter]
    pub fn set_tags(&mut self, val: Vec<String>) {
        self.tags = val;
    }

    #[getter]
    pub fn compatible_tools(&self) -> Vec<String> {
        self.compatible_tools.clone()
    }
    #[setter]
    pub fn set_compatible_tools(&mut self, val: Vec<String>) {
        self.compatible_tools = val;
    }

    #[getter]
    pub fn app_env(&self) -> String {
        self.app_env.clone()
    }
    #[setter]
    pub fn set_app_env(&mut self, val: String) {
        self.app_env = val;
    }

    #[getter]
    pub fn is_card(&self) -> bool {
        self.is_card
    }

    #[getter]
    pub fn opsml_version(&self) -> String {
        self.opsml_version.clone()
    }

    #[getter]
    pub fn created_at(&self) -> DateTime<Utc> {
        self.created_at
    }
    #[setter]
    pub fn set_created_at(&mut self, val: DateTime<Utc>) {
        self.created_at = val;
    }

    #[getter]
    pub fn registry_type(&self) -> RegistryType {
        self.registry_type.clone()
    }

    #[staticmethod]
    pub fn from_markdown(path: PathBuf) -> Result<Self, SkillError> {
        let content = std::fs::read_to_string(&path)?;
        parse_skill_markdown(&content, Some(&path))
    }

    #[pyo3(name = "to_markdown")]
    pub fn py_to_markdown(&self) -> Result<String, SkillError> {
        self.to_markdown()
    }

    #[pyo3(signature = (path))]
    pub fn save(&mut self, path: PathBuf) -> Result<(), SkillError> {
        self.save_card(path)
    }

    pub fn add_tags(&mut self, tags: Vec<String>) {
        self.tags.extend(tags);
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    #[pyo3(name = "get_registry_card")]
    pub fn get_registry_card_py(&self) -> Result<CardRecord, CardError> {
        let record = self.get_registry_card()?;
        Ok(record)
    }
}

impl SkillCard {
    pub fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        let record = SkillCardClientRecord {
            uid: self.uid.clone(),
            created_at: self.created_at,
            app_env: self.app_env.clone(),
            space: self.space.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            tags: self.tags.clone(),
            compatible_tools: self.compatible_tools.clone(),
            dependencies: self.dependencies.clone(),
            description: self.skill.description.clone().into(),
            license: self.skill.license.clone(),
            content_hash: self.calculate_content_hash()?,
            opsml_version: self.opsml_version.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            download_count: 0,
            input_schema: self.input_schema.clone(),
            body: self.skill.body.clone(),
        };
        Ok(CardRecord::Skill(record))
    }

    pub fn calculate_content_hash(&self) -> Result<Vec<u8>, SkillError> {
        let mut hasher = Sha256::new();
        let canonical = serde_json::to_vec(&self.skill)?;
        hasher.update(&canonical);
        Ok(hasher.finalize().to_vec())
    }

    pub fn model_validate_json(json_string: String) -> Result<SkillCard, SkillError> {
        Ok(serde_json::from_str(&json_string).inspect_err(|e| {
            error!("Failed to validate json: {e}");
        })?)
    }

    pub fn from_path(path: PathBuf) -> Result<Self, SkillError> {
        deserialize_from_path(path)
    }

    pub fn to_markdown(&self) -> Result<String, SkillError> {
        Ok(self.skill.to_markdown()?)
    }

    pub fn save_card(&mut self, path: PathBuf) -> Result<(), SkillError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(&mut *self, card_save_path.as_path())?;

        let skill_md = self
            .skill
            .to_markdown()
            .map_err(|e| SkillError::Error(e.to_string()))?;
        std::fs::write(path.join("SKILL.md"), skill_md)?;

        if let Some(ref source_dir) = self.source_dir.clone() {
            copy_companion_files(source_dir, &path)?;
        } else {
            tracing::debug!(
                "source_dir is None — skipping companion file copy (card was loaded from registry or deserialized without a local path)"
            );
        }
        Ok(())
    }

    #[allow(clippy::too_many_arguments)]
    pub fn new_rs(
        skill: AgentSkillStandard,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        tags: Option<Vec<String>>,
        compatible_tools: Option<Vec<String>>,
        dependencies: Option<Vec<SkillDependency>>,
        input_schema: Option<serde_json::Value>,
    ) -> Result<Self, SkillError> {
        let registry_type = RegistryType::Skill;
        let base_args = BaseArgs::create_args(name, space, version, None, &registry_type)?;

        Ok(Self {
            skill,
            space: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3, // will be set when saving to registry
            tags: tags.unwrap_or_default(),
            compatible_tools: compatible_tools.unwrap_or_default(),
            dependencies: dependencies.unwrap_or_default(),
            input_schema,
            registry_type,
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            created_at: get_utc_datetime(),
            is_card: true,
            opsml_version: opsml_version::version(),
            source_dir: None,
        })
    }
}

impl OpsmlCard for SkillCard {
    fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        self.get_registry_card()
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
        Ok(self.save_card(path)?)
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

impl ProfileExt for SkillCard {
    fn get_profile_request(&self) -> Result<ProfileRequest, CardError> {
        Err(CardError::DriftProfileNotFoundError)
    }

    fn has_profile(&self) -> bool {
        false
    }
}

#[cfg(all(test, feature = "python"))]
mod tests {
    use super::*;

    fn make_skill() -> AgentSkillStandard {
        AgentSkillStandard {
            name: "my-skill".to_string(),
            description: "A test skill".to_string(),
            license: Some("MIT".to_string()),
            compatibility: None,
            metadata: None,
            allowed_tools: None,
            skills_path: None,
            body: Some("Do the thing.".to_string()),
        }
    }

    #[test]
    fn test_skillcard_new_rs() {
        let skill = make_skill();
        let card = SkillCard::new_rs(
            skill,
            Some("test-space"),
            Some("my-skill"),
            None,
            Some(vec!["tag1".to_string()]),
            Some(vec!["claude-code".to_string()]),
            None,
            None,
        )
        .unwrap();

        assert_eq!(card.name, "my-skill");
        assert_eq!(card.space, "test-space");
        assert_eq!(card.version, "0.0.0");
        assert_eq!(card.tags, vec!["tag1"]);
        assert_eq!(card.compatible_tools, vec!["claude-code"]);
        assert!(card.is_card);
        assert_eq!(card.registry_type, RegistryType::Skill);
    }

    #[test]
    fn test_skillcard_json_roundtrip() {
        let skill = make_skill();
        let card = SkillCard::new_rs(
            skill,
            Some("test-space"),
            Some("my-skill"),
            None,
            None,
            None,
            None,
            None,
        )
        .unwrap();

        let json = serde_json::to_string(&card).unwrap();
        let restored = SkillCard::model_validate_json(json).unwrap();

        assert_eq!(restored.name, card.name);
        assert_eq!(restored.space, card.space);
        assert_eq!(restored.version, card.version);
        assert_eq!(restored.skill.description, card.skill.description);
        assert_eq!(restored.skill.body, card.skill.body);
        assert!(restored.is_card);
    }

    #[test]
    fn test_skillcard_get_registry_card() {
        let skill = make_skill();
        let card = SkillCard::new_rs(
            skill,
            Some("test-space"),
            Some("my-skill"),
            None,
            Some(vec!["ml".to_string()]),
            Some(vec!["codex".to_string()]),
            None,
            Some(
                serde_json::json!({"type": "object", "properties": {"input": {"type": "string"}}}),
            ),
        )
        .unwrap();

        let record = card.get_registry_card().unwrap();
        match record {
            CardRecord::Skill(r) => {
                assert_eq!(r.name, "my-skill");
                assert_eq!(r.space, "test-space");
                assert_eq!(r.compatible_tools, vec!["codex"]);
                assert_eq!(r.tags, vec!["ml"]);
                assert!(r.input_schema.is_some());
                assert!(!r.content_hash.is_empty());
            }
            _ => panic!("expected CardRecord::Skill"),
        }
    }

    #[test]
    fn test_skillcard_content_hash_deterministic() {
        let skill = make_skill();
        let card = SkillCard::new_rs(
            skill.clone(),
            Some("s"),
            Some("my-skill"),
            None,
            None,
            None,
            None,
            None,
        )
        .unwrap();
        let card2 = SkillCard::new_rs(
            skill,
            Some("s"),
            Some("my-skill"),
            None,
            None,
            None,
            None,
            None,
        )
        .unwrap();

        assert_eq!(
            card.calculate_content_hash().unwrap(),
            card2.calculate_content_hash().unwrap()
        );
    }

    #[test]
    fn test_skillcard_content_hash_changes_with_body() {
        let mut skill1 = make_skill();
        skill1.body = Some("body A".to_string());
        let mut skill2 = make_skill();
        skill2.body = Some("body B".to_string());

        let card1 = SkillCard::new_rs(
            skill1,
            Some("s"),
            Some("my-skill"),
            None,
            None,
            None,
            None,
            None,
        )
        .unwrap();
        let card2 = SkillCard::new_rs(
            skill2,
            Some("s"),
            Some("my-skill"),
            None,
            None,
            None,
            None,
            None,
        )
        .unwrap();

        assert_ne!(
            card1.calculate_content_hash().unwrap(),
            card2.calculate_content_hash().unwrap()
        );
    }

    #[test]
    fn test_skillcard_input_schema_parsing() {
        let skill = make_skill();
        let card = SkillCard::new_rs(
            skill,
            Some("s"),
            Some("my-skill"),
            None,
            None,
            None,
            None,
            Some(
                serde_json::json!({"type": "object", "properties": {"input": {"type": "string"}}}),
            ),
        )
        .unwrap();

        let record = card.get_registry_card().unwrap();
        if let CardRecord::Skill(r) = record {
            let schema = r.input_schema.unwrap();
            assert_eq!(schema["type"], "object");
        } else {
            panic!("expected CardRecord::Skill");
        }
    }

    #[test]
    fn test_skillcard_markdown_roundtrip() {
        let skill = AgentSkillStandard {
            name: "roundtrip-skill".to_string(),
            description: "Roundtrip test".to_string(),
            license: Some("Apache-2.0".to_string()),
            compatibility: None,
            metadata: None,
            allowed_tools: Some(vec!["Bash".to_string()]),
            skills_path: None,
            body: Some("# Instructions\n\nDo the thing.\n".to_string()),
        };

        let card = SkillCard::new_rs(
            skill,
            Some("test-space"),
            Some("roundtrip-skill"),
            None,
            None,
            None,
            None,
            None,
        )
        .unwrap();

        let md = card.to_markdown().unwrap();
        assert!(md.contains("roundtrip-skill"));
        assert!(md.contains("Roundtrip test"));
        assert!(md.contains("Do the thing."));

        // Round-trip via AgentSkillStandard::from_markdown
        let restored = AgentSkillStandard::from_markdown(&md).unwrap();
        assert_eq!(restored.name, card.skill.name);
        assert_eq!(restored.description, card.skill.description);
        assert_eq!(restored.license, card.skill.license);
        let body = restored.body.as_deref().unwrap_or("");
        assert!(!body.starts_with("---"));
        assert!(body.contains("Do the thing."));
        assert!(body.trim_start_matches('\n').starts_with("# Instructions"));
    }

    #[test]
    fn test_parse_skill_markdown_invalid_yaml() {
        let bad = "---\n: invalid: yaml: {{\n---\nbody";
        assert!(matches!(
            parse_skill_markdown(bad, None),
            Err(SkillError::AgentConfigError(_))
        ));
    }

    #[test]
    fn test_parse_skill_markdown_missing_delimiter() {
        let no_delims = "name: my-skill\ndescription: test\n";
        assert!(matches!(
            parse_skill_markdown(no_delims, None),
            Err(SkillError::AgentConfigError(_))
        ));
    }

    #[test]
    fn test_skillcard_content_hash_no_body() {
        let mut skill = make_skill();
        skill.body = None;
        let card = SkillCard::new_rs(
            skill.clone(),
            Some("s"),
            Some("my-skill"),
            None,
            None,
            None,
            None,
            None,
        )
        .unwrap();
        let card2 = SkillCard::new_rs(
            skill,
            Some("s"),
            Some("my-skill"),
            None,
            None,
            None,
            None,
            None,
        )
        .unwrap();
        let h1 = card.calculate_content_hash().unwrap();
        let h2 = card2.calculate_content_hash().unwrap();
        assert!(!h1.is_empty());
        assert_eq!(h1, h2);
    }

    #[test]
    fn test_skillcard_to_markdown_body_not_in_frontmatter() {
        let skill = AgentSkillStandard {
            name: "fm-test".to_string(),
            description: "Frontmatter body exclusion test".to_string(),
            license: None,
            compatibility: None,
            metadata: None,
            allowed_tools: None,
            skills_path: None,
            body: Some("# Steps\n\nDo the thing.\n".to_string()),
        };
        let card = SkillCard::new_rs(
            skill,
            Some("s"),
            Some("fm-test"),
            None,
            None,
            None,
            None,
            None,
        )
        .unwrap();

        let md = card.to_markdown().unwrap();
        let restored = AgentSkillStandard::from_markdown(&md).unwrap();

        // body content must NOT appear as a YAML key in the frontmatter
        assert!(
            !md[..md.find("\n---\n# ").unwrap_or(md.len())].contains("body:"),
            "frontmatter should not contain a 'body:' key"
        );
        // body content must appear in the parsed body
        let body = restored.body.as_deref().unwrap_or("");
        assert!(body.contains("Do the thing."));
    }

    #[test]
    fn test_skillcard_to_markdown_no_body() {
        let mut skill = make_skill();
        skill.body = None;
        let card = SkillCard::new_rs(
            skill,
            Some("s"),
            Some("my-skill"),
            None,
            None,
            None,
            None,
            None,
        )
        .unwrap();
        let md = card.to_markdown().unwrap();
        let restored = AgentSkillStandard::from_markdown(&md).unwrap();
        assert_eq!(restored.body.as_deref().unwrap_or(""), "");
    }

    #[test]
    fn test_deserialize_from_path_yaml() {
        let skill = make_skill();
        let card = SkillCard::new_rs(
            skill,
            Some("test-space"),
            Some("my-skill"),
            None,
            None,
            None,
            None,
            None,
        )
        .unwrap();

        let tmp = tempfile::tempdir().unwrap();
        let yaml_path = tmp.path().join("Card.yaml");
        let yaml = serde_yaml::to_string(&card).unwrap();
        std::fs::write(&yaml_path, yaml).unwrap();

        let loaded: SkillCard = deserialize_from_path(yaml_path).unwrap();
        assert_eq!(loaded.name, "my-skill");
        assert_eq!(loaded.space, "test-space");
    }

    #[test]
    fn test_deserialize_from_path_unsupported_extension() {
        let tmp = tempfile::tempdir().unwrap();
        let txt_path = tmp.path().join("Card.txt");
        std::fs::write(&txt_path, "{}").unwrap();

        let result: Result<SkillCard, SkillError> = deserialize_from_path(txt_path);
        assert!(result.is_err());
        let err = result.unwrap_err().to_string();
        assert!(err.contains("Unsupported file extension"));
    }
}
