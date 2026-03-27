use crate::BaseArgs;
use crate::error::CardError;
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
use serde::de::DeserializeOwned;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::path::PathBuf;
use tracing::{error, instrument};

fn deserialize_from_path<T: DeserializeOwned>(path: PathBuf) -> Result<T, CardError> {
    let content = std::fs::read_to_string(&path)?;
    let extension = path
        .extension()
        .and_then(|ext| ext.to_str())
        .ok_or_else(|| CardError::Error(format!("Invalid file path: {:?}", path)))?;
    let item = match extension.to_lowercase().as_str() {
        "json" => serde_json::from_str(&content)?,
        "yaml" | "yml" => serde_yaml::from_str(&content)?,
        _ => {
            return Err(CardError::Error(format!(
                "Unsupported file extension '{}'. Expected .json, .yaml, or .yml",
                extension
            )));
        }
    };
    Ok(item)
}

/// Helper function to split frontmatter and body from markdown content
/// Returns None if frontmatter delimiters are not found
/// Assumes frontmatter is delimited by `---` on its own line, and body starts after closing `---`
fn split_frontmatter(content: &str) -> Option<(&str, &str)> {
    let content = content.trim_start();
    let rest = content.strip_prefix("---")?;
    // accept `---\n` or `---\r\n`
    let rest = rest
        .strip_prefix('\n')
        .or_else(|| rest.strip_prefix("\r\n"))?;
    let end = rest.find("\n---").or_else(|| rest.find("\r\n---"))?;
    let frontmatter = &rest[..end];
    let after_delim = &rest[end..];
    // skip past the closing `---` line
    let body_start = after_delim
        .find('\n')
        .map(|i| i + 1)
        .unwrap_or(after_delim.len());
    let body = &after_delim[body_start..];
    Some((frontmatter, body))
}

/// Parse a skill markdown file (YAML frontmatter + markdown body).
///
/// The file format is:
/// ```
/// ---
/// <yaml frontmatter matching AgentSkillStandard fields>
/// ---
/// <markdown body>
/// ```
#[instrument(skip_all)]
pub fn parse_skill_markdown(
    content: &str,
    source_path: Option<&PathBuf>,
) -> Result<SkillCard, CardError> {
    let (frontmatter, body) = split_frontmatter(content).ok_or_else(|| {
        CardError::Error(format!(
            "Skill markdown {:?} is missing YAML frontmatter delimiters (---)",
            source_path
        ))
    })?;

    let mut skill: AgentSkillStandard = serde_yaml::from_str(frontmatter)
        .map_err(CardError::SerdeYamlError)
        .inspect_err(|e| error!("Failed to parse skill frontmatter: {e}"))?;

    skill.body = Some(body.to_string());

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
    ) -> Result<Self, CardError> {
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
    pub fn skill<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, CardError> {
        Ok(self.skill.clone().into_bound_py_any(py)?)
    }

    #[setter]
    pub fn set_skill(&mut self, skill: &Bound<'_, PyAny>) -> Result<(), CardError> {
        self.skill = skill.extract::<AgentSkillStandard>().inspect_err(|e| {
            error!("Failed to extract AgentSkillStandard: {e}");
        })?;
        Ok(())
    }

    #[getter]
    pub fn dependecies<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, CardError> {
        Ok(self.dependencies.clone().into_bound_py_any(py)?)
    }

    #[setter]
    pub fn set_dependencies(&mut self, dependencies: &Bound<'_, PyAny>) -> Result<(), CardError> {
        self.dependencies = dependencies
            .extract::<Vec<SkillDependency>>()
            .inspect_err(|e| {
                error!("Failed to extract dependencies: {e}");
            })?;
        Ok(())
    }

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
        };

        Ok(CardRecord::Skill(record))
    }

    pub fn calculate_content_hash(&self) -> Result<Vec<u8>, CardError> {
        let mut hasher = Sha256::new();
        hasher.update(self.skill.name.as_bytes());
        hasher.update(self.skill.description.as_bytes());
        if let Some(body) = &self.skill.body {
            hasher.update(body.as_bytes());
        }
        Ok(hasher.finalize().to_vec())
    }

    #[staticmethod]
    pub fn from_markdown(path: PathBuf) -> Result<Self, CardError> {
        let content = std::fs::read_to_string(&path)?;
        parse_skill_markdown(&content, Some(&path))
    }

    pub fn to_markdown(&self) -> Result<String, CardError> {
        let mut frontmatter =
            serde_yaml::to_string(&self.skill).map_err(|e| CardError::SerdeYamlError(e))?;

        // serde_yaml serializes with trailing newline; trim and wrap in delimiters
        frontmatter = frontmatter.trim_end().to_string();

        let body = self.skill.body.as_deref().unwrap_or("");
        Ok(format!("---\n{frontmatter}\n---\n{body}"))
    }

    #[pyo3(signature = (path), name = "save")]
    pub fn save_card(&mut self, path: PathBuf) -> Result<(), CardError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(&self, &card_save_path)?;
        Ok(())
    }

    #[staticmethod]
    pub fn model_validate_json(json_string: String) -> Result<SkillCard, CardError> {
        Ok(serde_json::from_str(&json_string).inspect_err(|e| {
            error!("Failed to validate json: {e}");
        })?)
    }

    #[staticmethod]
    pub fn from_path(path: PathBuf) -> Result<Self, CardError> {
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
    ) -> Result<Self, CardError> {
        let registry_type = RegistryType::Skill;
        let base_args = BaseArgs::create_args(name, space, version, None, &registry_type)?;

        Ok(Self {
            skill,
            space: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
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
    fn test_skillcard_default() {
        let card = super::SkillCard::default();
        assert_eq!(card.space, "");
        assert_eq!(card.name, "");
        assert_eq!(card.version, "");
        assert_eq!(card.uid, "");
        assert!(card.tags.is_empty());
        assert!(card.compatible_tools.is_empty());

        assert_eq!(card.app_env, "");
        assert_eq!(card.is_card, false);
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
}
