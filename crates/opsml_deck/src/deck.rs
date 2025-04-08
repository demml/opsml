use chrono::{DateTime, Utc};
use opsml_error::{CardError, OpsmlError};
use opsml_interfaces::{DataLoadKwargs, ModelLoadKwargs};
use opsml_registry::CardRegistries;
use opsml_types::{
    cards::BaseArgs,
    contracts::{CardDeckClientRecord, CardRecord},
    RegistryType, SaveName, Suffix,
};
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use pyo3::IntoPyObjectExt;
use pyo3::PyTraverseError;
use pyo3::PyVisit;
use serde::{
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
    Deserialize, Deserializer, Serialize, Serializer,
};
use std::collections::HashMap;
use std::path::PathBuf;
use tracing::{debug, error, instrument};

#[pyclass]
pub struct CardKwargs {
    #[pyo3(get)]
    pub interface: Option<PyObject>,
    #[pyo3(get)]
    pub load_kwargs: PyObject,
}

impl CardKwargs {
    pub fn new(
        py: Python,
        interface: Option<PyObject>,
        load_kwargs: Bound<'_, PyAny>,
    ) -> PyResult<Self> {
        // Check that load_kwargs is either ModelLoadKwargs or DataLoadKwargs
        if !load_kwargs.is_instance_of::<ModelLoadKwargs>()
            && !load_kwargs.is_instance_of::<DataLoadKwargs>()
        {
            error!("load_kwargs must be either ModelLoadKwargs or DataLoadKwargs");
            return Err(OpsmlError::new_err(
                "load_kwargs must be either ModelLoadKwargs or DataLoadKwargs",
            ));
        }

        debug!("load_kwargs type: {:?}", load_kwargs.get_type());

        Ok(CardKwargs {
            interface,
            load_kwargs: load_kwargs.into_py_any(py).map_err(|e| {
                error!("Failed to convert load_kwargs to PyObject: {}", e);
                OpsmlError::new_err(e.to_string())
            })?,
        })
    }
}

impl FromPyObject<'_> for CardKwargs {
    fn extract_bound(obj: &Bound<'_, PyAny>) -> PyResult<Self> {
        let interface = obj.getattr("interface")?.extract::<Option<PyObject>>()?;
        let load_kwargs = obj.getattr("load_kwargs")?.extract::<PyObject>()?;
        Ok(CardKwargs {
            interface,
            load_kwargs,
        })
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Card {
    #[pyo3(get, set)]
    pub space: Option<String>,

    #[pyo3(get, set)]
    pub name: Option<String>,

    #[pyo3(get, set)]
    pub version: Option<String>,

    #[pyo3(get, set)]
    pub uid: Option<String>,

    #[pyo3(get, set)]
    pub registry_type: RegistryType,

    #[pyo3(get, set)]
    pub alias: String,
}

/// Helper function to load a card and convert it to PyObject
///
/// # Arguments
///
/// * `py`: Python interpreter
/// * `card_registries`: Card registries
/// * `card`: Card to load
/// * `interface`: Optional interface to use
/// * `load_kwargs`: Optional load kwargs   
///     
fn load_and_extract_card(
    py: Python,
    card_registries: &CardRegistries,
    card: &Card,
    interface: Option<&Bound<'_, PyAny>>,
    load_kwargs: Option<&Bound<'_, PyAny>>,
) -> PyResult<PyObject> {
    let card_obj = match card.registry_type {
        RegistryType::Model => {
            let model_card = card_registries.model.load_card(
                py,
                card.uid.clone(),
                card.space.clone(),
                card.name.clone(),
                card.version.clone(),
                interface,
            )?;

            if let Some(kwargs) = load_kwargs {
                let model_kwargs = kwargs.extract::<ModelLoadKwargs>()?;
                let args = (None::<()>, false, Some(model_kwargs));
                model_card.call_method1("load", args)?;
            }
            model_card
        }
        RegistryType::Data => {
            let data_card = card_registries.data.load_card(
                py,
                card.uid.clone(),
                card.space.clone(),
                card.name.clone(),
                card.version.clone(),
                interface,
            )?;

            if let Some(kwargs) = load_kwargs {
                let data_kwargs = kwargs.extract::<DataLoadKwargs>()?;
                let args = (None::<()>, Some(data_kwargs));
                data_card.call_method1("load", args)?;
            }
            data_card
        }
        RegistryType::Experiment => card_registries.experiment.load_card(
            py,
            card.uid.clone(),
            card.space.clone(),
            card.name.clone(),
            card.version.clone(),
            None,
        )?,
        RegistryType::Prompt => card_registries.prompt.load_card(
            py,
            card.uid.clone(),
            card.space.clone(),
            card.name.clone(),
            card.version.clone(),
            None,
        )?,
        _ => {
            return Err(OpsmlError::new_err(format!(
                "Card type {} not supported",
                card.registry_type
            )))
        }
    };

    card_obj.into_py_any(py).map_err(|e| {
        error!("Failed to convert card to PyObject: {}", e);
        OpsmlError::new_err(e.to_string())
    })
}

/// CardDeck is a collection of cards that can be used to create a card deck and load in one call
///
#[pyclass]
#[derive(Debug)]
pub struct CardDeck {
    #[pyo3(get)]
    pub space: String,

    #[pyo3(get)]
    pub name: String,

    #[pyo3(get)]
    pub version: String,

    #[pyo3(get)]
    pub uid: String,

    #[pyo3(get)]
    pub created_at: DateTime<Utc>,

    #[pyo3(get, set)]
    pub cards: Vec<Card>,

    #[pyo3(get)]
    pub opsml_version: String,

    #[pyo3(get, set)]
    pub app_env: String,

    // this is the holder for the card objects (ModelCard, DataCard, etc.)
    pub card_objs: HashMap<String, PyObject>,
}

#[pymethods]
impl CardDeck {
    #[new]
    #[pyo3(signature = (space, name,  cards, version=None))]
    pub fn new(space: &str, name: &str, cards: Vec<Card>, version: Option<&str>) -> PyResult<Self> {
        let base_args =
            BaseArgs::create_args(Some(name), Some(space), version, None).map_err(|e| {
                error!("Failed to create base args: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;
        Ok(CardDeck {
            space: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            created_at: Utc::now(),
            cards,
            opsml_version: env!("CARGO_PKG_VERSION").to_string(),
            card_objs: HashMap::new(),
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
        })
    }

    /// Load the cards in the card deck
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter state
    /// * `load_kwargs` - Optional map of alias to kwargs containing interface and load arguments
    ///
    #[instrument(skip_all, fields(deck_name = %self.name))]
    pub fn load<'py>(
        &mut self,
        py: Python<'py>,
        load_kwargs: Option<HashMap<String, CardKwargs>>,
    ) -> PyResult<()> {
        debug!("Loading CardDeck: {}", self.name);
        let card_registries = CardRegistries::new()?;

        for card in &self.cards {
            // Skip if already loaded
            if self.card_objs.contains_key(&card.alias) {
                debug!("Card {} already exists in card_objs", card.alias);
                continue;
            }

            // Get kwargs if they exist
            let (interface, load_kwargs) = load_kwargs
                .as_ref()
                .and_then(|kwargs| kwargs.get(&card.alias))
                .map(|card_kwargs| {
                    let interface = card_kwargs
                        .interface
                        .as_ref()
                        .map(|i| i.clone_ref(py).into_bound(py));
                    let load_kwargs = card_kwargs.load_kwargs.clone_ref(py).into_bound(py);
                    (interface, Some(load_kwargs))
                })
                .unwrap_or((None, None));

            // Load and store the card
            let card_obj = load_and_extract_card(
                py,
                &card_registries,
                card,
                interface.as_ref(),
                load_kwargs.as_ref(),
            )?;
            self.card_objs.insert(card.alias.clone(), card_obj);
        }

        Ok(())
    }

    #[pyo3(signature = (path))]
    pub fn save(&mut self, path: PathBuf) -> Result<(), CardError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(self, &card_save_path)?;

        Ok(())
    }

    #[staticmethod]
    #[pyo3(signature = (json_string))]
    pub fn model_validate_json(json_string: String) -> PyResult<CardDeck> {
        serde_json::from_str(&json_string).map_err(|e| {
            error!("Failed to validate json: {}", e);
            OpsmlError::new_err(e.to_string())
        })
    }

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        for card_obj in self.card_objs.values() {
            visit.call(card_obj)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.card_objs.clear();
    }

    pub fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        let record = CardDeckClientRecord {
            created_at: self.created_at,
            app_env: self.app_env.clone(),
            space: self.space.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            uid: self.uid.clone(),
            opsml_version: self.opsml_version.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
        };

        Ok(CardRecord::Deck(record))
    }
}

impl Serialize for CardDeck {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("CardDeck", 8)?;

        // set session to none
        state.serialize_field("space", &self.space)?;
        state.serialize_field("name", &self.name)?;
        state.serialize_field("version", &self.version)?;
        state.serialize_field("uid", &self.uid)?;
        state.serialize_field("created_at", &self.created_at)?;
        state.serialize_field("cards", &self.cards)?;
        state.serialize_field("opsml_version", &self.opsml_version)?;
        state.serialize_field("app_env", &self.app_env)?;
        state.end()
    }
}

impl<'de> Deserialize<'de> for CardDeck {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(field_identifier, rename_all = "snake_case")]
        enum Field {
            Space,
            Name,
            Version,
            Uid,
            CreatedAt,
            OpsmlVersion,
            Cards,
            CardObjs,
            AppEnv,
        }

        struct CardDeckVisitor;

        impl<'de> Visitor<'de> for CardDeckVisitor {
            type Value = CardDeck;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct CardDeck")
            }

            fn visit_map<V>(self, mut map: V) -> Result<CardDeck, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut space = None;
                let mut name = None;
                let mut version = None;
                let mut uid = None;
                let mut created_at = None;
                let mut opsml_version = None;
                let mut cards = None;
                let mut card_objs = None;
                let mut app_env = None;

                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Space => {
                            space = Some(map.next_value()?);
                        }
                        Field::Name => {
                            name = Some(map.next_value()?);
                        }
                        Field::Version => {
                            version = Some(map.next_value()?);
                        }
                        Field::Uid => {
                            uid = Some(map.next_value()?);
                        }

                        Field::CreatedAt => {
                            created_at = Some(map.next_value()?);
                        }

                        Field::OpsmlVersion => {
                            opsml_version = Some(map.next_value()?);
                        }
                        Field::Cards => {
                            cards = Some(map.next_value()?);
                        }
                        Field::CardObjs => {
                            card_objs = None;
                        }
                        Field::AppEnv => {
                            app_env = Some(map.next_value()?);
                        }
                    }
                }

                let space = space.ok_or_else(|| de::Error::missing_field("space"))?;
                let name = name.ok_or_else(|| de::Error::missing_field("name"))?;
                let version = version.ok_or_else(|| de::Error::missing_field("version"))?;
                let uid = uid.ok_or_else(|| de::Error::missing_field("uid"))?;
                let created_at =
                    created_at.ok_or_else(|| de::Error::missing_field("created_at"))?;
                let opsml_version =
                    opsml_version.ok_or_else(|| de::Error::missing_field("opsml_version"))?;
                let cards = cards.ok_or_else(|| de::Error::missing_field("cards"))?;
                let card_objs = card_objs.unwrap_or_else(HashMap::new);
                let app_env = app_env.ok_or_else(|| de::Error::missing_field("app_env"))?;

                Ok(CardDeck {
                    space,
                    name,
                    version,
                    uid,
                    created_at,
                    cards,
                    opsml_version,
                    card_objs,
                    app_env,
                })
            }
        }

        const FIELDS: &[&str] = &[
            "space",
            "name",
            "version",
            "uid",
            "created_at",
            "opsml_version",
            "cards",
            "card_objs",
            "app_env",
        ];
        deserializer.deserialize_struct("CardDeck", FIELDS, CardDeckVisitor)
    }
}
