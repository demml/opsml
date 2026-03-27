use crate::BaseArgs;
use crate::skill::error::SkillError;
use chrono::{DateTime, Utc};
use opsml_types::contracts::CardRecord;
use opsml_types::contracts::SkillCardClientRecord;
use opsml_types::contracts::agent::AgentSkillStandard;
use opsml_types::contracts::skill::SkillDependency;
use opsml_types::{RegistryType, SaveName, Suffix};
use opsml_utils::PyHelperFuncs;
use opsml_utils::depythonize_object_to_value;
use opsml_utils::get_utc_datetime;
use pyo3::IntoPyObjectExt;
use pyo3::prelude::*;
use pythonize;
use serde::de::DeserializeOwned;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::path::PathBuf;
use tracing::{error, instrument};

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
    SkillCard::new_rs(skill, None, Some(&name), None, None, None, None, None)
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct SkillCard {
    pub skill: AgentSkillStandard,
    pub dependencies: Vec<SkillDependency>,

    #[pyo3(get, set)]
    pub space: String,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub version: String,

    #[pyo3(get, set)]
    pub uid: String,

    #[pyo3(get, set)]
    pub tags: Vec<String>,

    pub input_schema: Option<serde_json::Value>,

    #[pyo3(get, set)]
    pub compatible_tools: Vec<String>,

    #[pyo3(get, set)]
    pub app_env: String,

    #[pyo3(get)]
    pub is_card: bool,

    #[pyo3(get)]
    pub opsml_version: String,

    #[pyo3(get, set)]
    pub created_at: DateTime<Utc>,

    #[pyo3(get)]
    pub registry_type: RegistryType,
}

#[pymethods]
impl SkillCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (skill, space=None, name=None, version=None, tags=None, compatible_tools=None, dependencies=None, input_schema=None))]
    pub fn new(
        skill: &Bound<'_, PyAny>,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        tags: Option<Vec<String>>,
        compatible_tools: Option<Vec<String>>,
        dependencies: Option<Vec<SkillDependency>>,
        input_schema: Option<Bound<'_, PyAny>>,
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

        Self::new_rs(
            skill,
            space,
            effective_name,
            version,
            tags,
            compatible_tools,
            dependencies,
            input_schema,
        )
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

    pub fn get_registry_card(&self) -> Result<CardRecord, SkillError> {
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
        };

        Ok(CardRecord::Skill(record))
    }

    pub fn calculate_content_hash(&self) -> Result<Vec<u8>, SkillError> {
        let mut hasher = Sha256::new();
        let canonical = serde_json::to_vec(&self.skill)?;
        hasher.update(&canonical);
        Ok(hasher.finalize().to_vec())
    }

    #[staticmethod]
    pub fn from_markdown(path: PathBuf) -> Result<Self, SkillError> {
        let content = std::fs::read_to_string(&path)?;
        parse_skill_markdown(&content, Some(&path))
    }

    pub fn to_markdown(&self) -> Result<String, SkillError> {
        Ok(self.skill.to_markdown()?)
    }

    #[pyo3(signature = (path), name = "save")]
    pub fn save_card(&mut self, path: PathBuf) -> Result<(), SkillError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(self, card_save_path.as_path())?;
        Ok(())
    }

    #[staticmethod]
    #[pyo3(signature = (json_string))]
    pub fn model_validate_json(json_string: String) -> Result<SkillCard, SkillError> {
        Ok(serde_json::from_str(&json_string).inspect_err(|e| {
            error!("Failed to validate json: {e}");
        })?)
    }

    #[staticmethod]
    pub fn from_path(path: PathBuf) -> Result<Self, SkillError> {
        deserialize_from_path(path)
    }

    pub fn add_tags(&mut self, tags: Vec<String>) {
        self.tags.extend(tags);
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

impl SkillCard {
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
        })
    }
}

#[cfg(test)]
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
}
