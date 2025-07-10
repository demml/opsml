use crate::error::PyProjectTomlError;
use opsml_types::RegistryType;
use serde::{de::IntoDeserializer, Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::str::FromStr;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CardAttr {
    pub space: Option<String>,
    pub name: Option<String>,
    pub version: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DriftConfig {
    #[serde(default)]
    pub active: bool,
    #[serde(default)]
    pub deactivate_others: bool,
    pub drift_type: Vec<String>,
}

/// toml equivalent of opsml_cards::ServiceCard Card
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Card {
    pub alias: String,
    pub space: String,
    pub name: String,
    pub version: Option<String>,
    #[serde(rename = "type")]
    pub registry_type: RegistryType,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub drift: Option<DriftConfig>,
}

impl Card {
    /// Validate the card configuration to ensure drift is only used for model cards
    pub fn validate(&self) -> Result<(), PyProjectTomlError> {
        // Only allow drift configuration for model cards
        if self.drift.is_some() && self.registry_type != RegistryType::Model {
            return Err(PyProjectTomlError::InvalidConfiguration);
        }
        Ok(())
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ServiceConfig {
    pub name: String,
    pub space: String,
    pub version: Option<String>,
    pub cards: Option<Vec<Card>>,
    pub write_dir: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct OpsmlTools {
    /// Default argument that will apply to all cards
    ///
    /// # Example
    /// [tool.opsml.default]
    /// space = "opsml"
    /// name = "opsml"
    default: Option<CardAttr>,

    /// Registry specific arguments
    ///
    /// # Example
    /// [tool.opsml.registry]
    /// data = { space = "opsml", name = "opsml" }
    /// model = { space = "opsml", name = "opsml" }
    /// experiment = { space = "opsml", name = "opsml" }
    registry: Option<HashMap<RegistryType, CardAttr>>,

    /// ServiceCard configuration
    ///
    /// # Example
    /// [tool.opsml.service]
    /// name = "opsml"
    /// space = "opsml"
    /// version = "1"
    /// cards = [
    ///    {alias="data", space = "opsml", name = "opsml", version="1", type="data"},
    ///    {alias="model", space = "opsml", name = "opsml", version="1", type="model"},
    /// ]
    service: Option<Vec<ServiceConfig>>,
}

impl OpsmlTools {
    /// Gets a value for a given
    /// This method will return the value for the key if it exists in either
    /// the default or registry specific arguments. Default arguments will
    /// override registry specific arguments.
    ///
    /// # Arguments
    /// * `key` - The key to get the value for
    pub fn get_attribute_key_value(
        &self,
        key: &str,
        registry_type: &RegistryType,
    ) -> Option<String> {
        // get the default value
        let default_value = self.default.as_ref().and_then(|d| match key {
            "space" => d.space.clone(),
            "name" => d.name.clone(),
            "version" => d.version.clone(),
            _ => None,
        });

        // if default value is Some, return it
        if default_value.is_some() {
            return default_value;
        }

        // check the registry specific arguments for the given registry type and key
        let registry_value = self
            .registry
            .as_ref()
            .and_then(|r| r.get(registry_type))
            .and_then(|r| match key {
                "space" => r.space.clone(),
                "name" => r.name.clone(),
                "version" => r.version.clone(),
                _ => None,
            });

        registry_value
    }

    /// Get the registry specific arguments
    pub fn get_registry(&self) -> Option<HashMap<RegistryType, CardAttr>> {
        self.registry.clone()
    }

    /// Get the service configuration
    pub fn get_service(&self) -> Option<&Vec<ServiceConfig>> {
        self.service.as_ref()
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OpsmlTool {
    #[serde(rename = "opsml")]
    pub opsml: Option<OpsmlTools>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub struct PyProjectToml {
    pub tool: Option<OpsmlTool>,

    // skip when deserializing
    #[serde(skip)]
    pub root_path: PathBuf,
}

impl PyProjectToml {
    /// Get the root path of the pyproject.toml file
    /// This is used to ensure lockfiles are created in the same directory as the pyproject.toml file
    pub fn get_root_path(&self) -> PathBuf {
        self.root_path.clone()
    }
}

impl PyProjectToml {
    /// Quick access to the OpsmlTools
    pub fn get_tools(&self) -> Option<OpsmlTools> {
        self.tool.as_ref().and_then(|t| t.opsml.clone())
    }

    /// Load the pyproject.toml file from a string
    pub fn from_string(content: &str) -> Result<Self, PyProjectTomlError> {
        let pyproject: toml_edit::Document<_> =
            toml_edit::Document::from_str(content).map_err(PyProjectTomlError::ParseError)?;

        let pyproject = PyProjectToml::deserialize(pyproject.into_deserializer())
            .map_err(PyProjectTomlError::TomlSchema)?;

        if let Some(tool) = &pyproject.tool {
            if let Some(opsml) = &tool.opsml {
                if let Some(apps) = &opsml.service {
                    for app in apps {
                        if let Some(cards) = &app.cards {
                            for card in cards {
                                card.validate()?;
                            }
                        }
                    }
                }
            }
        }

        Ok(pyproject)
    }

    /// Load the pyproject.toml file from a path
    ///
    /// # Arguments
    /// * `path` - The path to the pyproject.toml file
    ///
    /// # Returns
    /// * `Result<Self, PyProjectTomlError>` - The PyProjectToml
    ///
    /// # Errors
    /// Will return an error if:
    /// * The path is not a file
    /// * The path is not a directory
    /// * The path is not a valid toml file
    pub fn load(path: Option<&Path>, toml_name: Option<&str>) -> Result<Self, PyProjectTomlError> {
        let toml_name = toml_name.unwrap_or("pyproject.toml");
        // get the current directory
        let path = match path {
            Some(p) => p,
            None => &std::env::current_dir().map_err(PyProjectTomlError::CurrentDirError)?,
        };

        let path = path
            .canonicalize()
            .map_err(PyProjectTomlError::AbsolutePathError)?;

        // Search parent directories
        let root_path = path
            .ancestors()
            .find(|p| p.join(toml_name).is_file())
            .ok_or(PyProjectTomlError::MissingPyprojectToml(
                toml_name.to_string(),
            ))?
            .to_path_buf();

        let project_path = root_path.join(toml_name);

        let content =
            std::fs::read_to_string(&project_path).map_err(PyProjectTomlError::ReadError)?;

        let mut toml = Self::from_string(&content)?;

        // set the root path
        toml.root_path = root_path.clone();

        Ok(toml)
    }
}

// tests
#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::io::Write;
    use tempfile::TempDir;

    fn write_toml_to_temp(content: &str) -> Result<(TempDir, PathBuf), Box<dyn std::error::Error>> {
        let temp_dir = TempDir::new()?;
        let file_path = temp_dir.path().join("pyproject.toml");

        let mut file = File::create(&file_path)?;
        file.write_all(content.as_bytes())?;

        // Ensure the file is flushed to disk
        file.flush()?;

        let temp_path = temp_dir.path().to_path_buf();

        // check file exist
        if !file_path.exists() {
            return Err("File not created".into());
        }

        // return temp_dir path
        Ok((temp_dir, temp_path))
    }

    #[test]
    fn test_service_configuration_load() {
        let content = r#"
            [[tool.opsml.service]]
            space = "opsml"
            name = "opsml"
            version = "1"
            
            [[tool.opsml.service.cards]]
            alias = "data"
            space = "space"
            name = "name"
            version = "1"
            type = "data"

            [[tool.opsml.service.cards]]
            alias = "model"
            space = "space"
            name = "name"
            version = "1"
            type = "model"
            drift = { active = true, deactivate_others = false, drift_type = ["custom", "psi"] }

        "#;

        let (_temp_dir, root_dir) = write_toml_to_temp(content).unwrap();

        let pyproject = PyProjectToml::load(Some(&root_dir), None).unwrap();

        // assert tool.opsml is not None
        assert!(pyproject.tool.is_some());
        assert!(pyproject.tool.as_ref().unwrap().opsml.is_some());
        assert!(pyproject
            .tool
            .as_ref()
            .unwrap()
            .opsml
            .as_ref()
            .unwrap()
            .service
            .is_some());

        let tools = pyproject.get_tools().unwrap();
        let app = tools.service.as_ref().unwrap()[0].clone();
        let cards = app.cards.clone().unwrap();
        assert_eq!(app.name, "opsml");
        assert_eq!(app.space, "opsml");
        assert_eq!(app.version, Some("1".to_string()));
        assert_eq!(cards.len(), 2);
        assert_eq!(cards[0].alias, "data");
        assert_eq!(cards[0].space, "space".to_string());
        assert_eq!(cards[0].name, "name".to_string());
        assert_eq!(cards[0].version, Some("1".to_string()));
        assert_eq!(cards[0].registry_type, RegistryType::Data);
        assert_eq!(cards[1].alias, "model");
        assert_eq!(cards[1].space, "space".to_string());
        assert_eq!(cards[1].name, "name".to_string());
        assert_eq!(cards[1].version, Some("1".to_string()));
        assert_eq!(cards[1].registry_type, RegistryType::Model);
        assert!(cards[1].drift.as_ref().unwrap().active);
        assert!(!cards[1].drift.as_ref().unwrap().deactivate_others);
    }

    #[test]
    fn test_default_load() {
        let content = r#"
            [tool.opsml.default]
            name = "name"
            space = "space"

            [[tool.opsml.service]]
            alias = "model"
            space = "space"
            name = "name"
            version = "1"
            type = "model"
            drift = { active = true, deactivate_others = false, drift_type = ["custom", "psi"] }

        "#;

        let (_temp_dir, root_dir) = write_toml_to_temp(content).unwrap();

        let pyproject = PyProjectToml::load(Some(&root_dir), None).unwrap();

        // assert tool.opsml is not None
        assert!(pyproject.tool.is_some());
        assert!(pyproject.tool.as_ref().unwrap().opsml.is_some());
        assert!(pyproject
            .tool
            .as_ref()
            .unwrap()
            .opsml
            .as_ref()
            .unwrap()
            .default
            .is_some());

        let tools = pyproject.get_tools().unwrap();
        let service = tools.default.as_ref().unwrap();
        assert_eq!(service.name, Some("name".to_string()));
        assert_eq!(service.space, Some("space".to_string()));
    }

    #[test]
    fn test_cards_load() {
        let content = r#"
            [tool.opsml.registry]
            data = { space = "space", name = "name" }
            model = { space = "space", name = "name" }
            experiment = { space = "space", name = "name" }
        "#;

        let (_temp_dir, root_dir) = write_toml_to_temp(content).unwrap();

        let pyproject = PyProjectToml::load(Some(&root_dir), None).unwrap();

        // assert tool.opsml is not None
        let tools = pyproject.get_tools().unwrap();
        assert!(tools.registry.is_some());
        let registry = tools.registry.as_ref().unwrap();
        assert_eq!(registry.len(), 3);
        assert_eq!(
            registry.get(&RegistryType::Data).unwrap().space,
            Some("space".to_string())
        );
        assert_eq!(
            registry.get(&RegistryType::Data).unwrap().name,
            Some("name".to_string())
        );
        assert_eq!(
            registry.get(&RegistryType::Model).unwrap().space,
            Some("space".to_string())
        );
        assert_eq!(
            registry.get(&RegistryType::Model).unwrap().name,
            Some("name".to_string())
        );
        assert_eq!(
            registry.get(&RegistryType::Experiment).unwrap().space,
            Some("space".to_string())
        );
        assert_eq!(
            registry.get(&RegistryType::Experiment).unwrap().name,
            Some("name".to_string())
        );
    }
}
