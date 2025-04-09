use opsml_error::PyProjectTomlError;
use opsml_types::RegistryType;
use serde::{de::IntoDeserializer, de::SeqAccess, Deserialize, Deserializer, Serialize};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::str::FromStr;

#[derive(Debug, Serialize, Deserialize)]
pub struct DefaultConfig {
    pub space: Option<String>,
    pub name: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CardConfig {
    #[serde(rename = "type")]
    pub space: Option<String>,
    pub name: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DeckCard {
    pub alias: String,
    pub space: Option<String>,
    pub name: String,
    pub version: Option<String>,
    #[serde(rename = "type")]
    pub card_type: RegistryType,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DeckConfig {
    pub create: bool,
    pub name: String,
    pub space: String,
    pub version: Option<String>,
    pub cards: Vec<DeckCard>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OpsmlTool {
    /// Default argument that will apply to all cards
    ///
    /// # Example
    /// [tool.opsml.default]
    /// space = "opsml"
    /// name = "opsml"
    default: Option<DefaultConfig>,

    /// Registry specific arguments
    ///
    /// # Example
    /// [tool.opsml.registry]
    /// data = { space = "opsml", name = "opsml" }
    /// model = { space = "opsml", name = "opsml" }
    /// experiment = { space = "opsml", name = "opsml" }
    registry: Option<HashMap<RegistryType, CardConfig>>,

    /// CardDeck configuration
    ///
    /// # Example
    /// [tool.opsml.deck]
    /// create = true
    /// name = "opsml"
    /// space = "opsml"
    /// version = "1"
    /// cards = [
    ///    {alias="data", space = "opsml", name = "opsml", version="1", type="data"},
    ///    {alias="model", space = "opsml", name = "opsml", version="1", type="model"},
    /// ]
    deck: Option<DeckConfig>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub struct PyProjectToml {
    pub tool: Option<OpsmlTool>,
}

impl PyProjectToml {
    pub fn new() -> Self {
        PyProjectToml {
            tool: Some(OpsmlTool {
                default: None,
                registry: None,
                deck: None,
            }),
        }
    }

    pub fn from_str(content: &str) -> Result<Self, PyProjectTomlError> {
        let pyproject: toml_edit::Document =
            toml_edit::Document::from_str(content).map_err(PyProjectTomlError::ParseError)?;

        let pyproject = PyProjectToml::deserialize(pyproject.into_deserializer())
            .map_err(PyProjectTomlError::TomlSchema)?;

        Ok(pyproject)
    }
}

//pub fn from_string(content: &str) -> Result<Self, PyProjectTomlError> {
//    let pyproject: toml_edit::ImDocument<_> =
//        toml_edit::ImDocument::from_str(&content).map_err(PyProjectTomlError::ParseError)?;
//
//    let pyproject = PyProjectToml::deserialize(pyproject.into_deserializer())
//        .map_err(PyProjectTomlError::TomlSchema)?;
//}
