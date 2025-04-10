use opsml_error::PyProjectTomlError;
use opsml_types::RegistryType;
use serde::{de::IntoDeserializer, Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use std::str::FromStr;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CardAttr {
    pub space: Option<String>,
    pub name: Option<String>,
    pub version: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DeckCard {
    pub alias: String,
    pub space: Option<String>,
    pub name: Option<String>,
    pub version: Option<String>,
    pub uid: Option<String>,
    #[serde(rename = "type")]
    pub card_type: Option<RegistryType>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AppConfig {
    pub create: bool,
    #[serde(rename = "type")]
    pub registry_type: RegistryType,
    pub name: Option<String>,
    pub space: Option<String>,
    pub version: Option<String>,
    pub uid: Option<String>,
    pub cards: Option<Vec<DeckCard>>,
}

//impl DeckConfig {
//    /// Convert the DeckConfig to a CardDeck
//    ///
//    /// # Arguments
//    /// * `self` - The DeckConfig to convert
//    ///
//    /// # Returns
//    /// * `Result<CardDeck, PyProjectTomlError>` - The CardDeck
//    ///
//    /// # Errors
//    /// Will return an error if:
//    /// - Card iteration and conversion fails
//    /// - CardDeck construction fails
//    pub fn to_card_deck(&self) -> Result<CardDeck, PyProjectTomlError> {
//        let cards = self
//            .cards
//            .iter()
//            .map(|card| {
//                opsml_cards::Card::new(
//                    card.alias.clone(),
//                    card.card_type.clone(),
//                    card.space.as_deref(),
//                    card.name.as_deref(),
//                    card.version.as_deref(),
//                    card.uid.as_deref(),
//                    None,
//                )
//            })
//            .collect::<Result<Vec<_>, _>>()
//            .map_err(PyProjectTomlError::MapToCardError)?;
//
//        let deck = CardDeck::new(&self.name, &self.space, cards, self.version.as_deref())
//            .map_err(|e| PyProjectTomlError::ConstructCardDeckError(e))?;
//
//        Ok(deck)
//    }
//}

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

    /// CardDeck configuration
    ///
    /// # Example
    /// [tool.opsml.app]
    /// create = true
    /// name = "opsml"
    /// space = "opsml"
    /// version = "1"
    /// cards = [
    ///    {alias="data", space = "opsml", name = "opsml", version="1", type="data"},
    ///    {alias="model", space = "opsml", name = "opsml", version="1", type="model"},
    /// ]
    app: Option<Vec<AppConfig>>,
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

    /// Get the deck configuration
    pub fn get_apps(&self) -> Option<&Vec<AppConfig>> {
        self.app.as_ref()
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
}

impl PyProjectToml {
    /// Quick access to the OpsmlTools
    pub fn get_tools(&self) -> Option<OpsmlTools> {
        self.tool.as_ref().and_then(|t| t.opsml.clone())
    }

    /// Load the pyproject.toml file from a string
    pub fn from_string(content: &str) -> Result<Self, PyProjectTomlError> {
        let pyproject: toml_edit::ImDocument<_> =
            toml_edit::ImDocument::from_str(content).map_err(PyProjectTomlError::ParseError)?;
        //
        let pyproject = PyProjectToml::deserialize(pyproject.into_deserializer())
            .map_err(PyProjectTomlError::TomlSchema)?;

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
    pub fn load(path: Option<PathBuf>) -> Result<Self, PyProjectTomlError> {
        // get the current directory
        let path = match path {
            Some(p) => p,
            None => std::env::current_dir().map_err(PyProjectTomlError::CurrentDirError)?,
        };

        let path = path
            .canonicalize()
            .map_err(PyProjectTomlError::AbsolutePathError)?;

        // Search parent directories
        let project_path = path
            .ancestors()
            .find(|p| p.join("pyproject.toml").is_file())
            .ok_or(PyProjectTomlError::MissingPyprojectToml)?
            .to_path_buf()
            .join("pyproject.toml");

        let content =
            std::fs::read_to_string(&project_path).map_err(PyProjectTomlError::ReadError)?;

        Self::from_string(&content)
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
    fn test_deck_configuration_load() {
        let content = r#"
            [[tool.opsml.app]]
            create = true
            type = "deck"
            name = "opsml"
            space = "opsml"
            version = "1"
            cards = [
                {alias = "data", space = "opsml", name = "opsml", version = "1", type = "data"},
                {alias = "model", space = "opsml", name = "opsml", version = "1", type = "model"}
            ]
        "#;

        let (_temp_dir, root_dir) = write_toml_to_temp(content).unwrap();

        let pyproject = PyProjectToml::load(Some(root_dir)).unwrap();

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
            .app
            .is_some());

        let tools = pyproject.get_tools().unwrap();
        let app = tools.app.as_ref().unwrap()[0].clone();
        let cards = app.cards.clone().unwrap();
        assert!(app.create);
        assert_eq!(app.name.unwrap(), "opsml");
        assert_eq!(app.space.unwrap(), "opsml");
        assert_eq!(app.version, Some("1".to_string()));
        assert_eq!(cards.len(), 2);
        assert_eq!(cards[0].alias, "data");
        assert_eq!(cards[0].space, Some("opsml".to_string()));
        assert_eq!(cards[0].name, Some("opsml".to_string()));
        assert_eq!(cards[0].version, Some("1".to_string()));
        assert_eq!(cards[0].card_type, Some(RegistryType::Data));
        assert_eq!(cards[1].alias, "model");
        assert_eq!(cards[1].space, Some("opsml".to_string()));
        assert_eq!(cards[1].name, Some("opsml".to_string()));
        assert_eq!(cards[1].version, Some("1".to_string()));
    }

    #[test]
    fn test_default_load() {
        let content = r#"
            [tool.opsml.default]
            name = "name"
            space = "space"
        "#;

        let (_temp_dir, root_dir) = write_toml_to_temp(content).unwrap();

        let pyproject = PyProjectToml::load(Some(root_dir)).unwrap();

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
        let deck = tools.default.as_ref().unwrap();
        assert_eq!(deck.name, Some("name".to_string()));
        assert_eq!(deck.space, Some("space".to_string()));
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

        let pyproject = PyProjectToml::load(Some(root_dir)).unwrap();

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
