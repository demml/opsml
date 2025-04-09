use crate::{DataCard, ExperimentCard, ModelCard, PromptCard};
use chrono::{DateTime, Utc};
use opsml_error::{CardError, OpsmlError};
use opsml_interfaces::{DataLoadKwargs, ModelLoadKwargs};
use opsml_types::{
    cards::BaseArgs,
    contracts::{CardDeckClientRecord, CardRecord},
    RegistryType, SaveName, Suffix,
};
use opsml_utils::PyHelperFuncs;
use pyo3::IntoPyObjectExt;
use pyo3::PyTraverseError;
use pyo3::PyVisit;
use pyo3::{prelude::*, types::PyDict};
use serde::{
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
    Deserialize, Deserializer, Serialize, Serializer,
};
use std::collections::HashMap;
use std::path::PathBuf;
use tracing::{debug, error, instrument};

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

#[pymethods]
impl Card {
    #[new]
    #[pyo3(signature = (registry_type, alias, space=None, name=None, version=None, uid=None))]
    pub fn new(
        registry_type: RegistryType,
        alias: String,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
    ) -> PyResult<Self> {
        // check that at least space/name  or uid is provided
        let has_space_or_name = space.is_some() || name.is_some();
        let has_uid = uid.is_some();

        if !has_space_or_name && !has_uid {
            error!("Either space/name or uid must be provided");
            return Err(OpsmlError::new_err(
                "Either space/name or uid must be provided",
            ));
        }

        Ok(Card {
            space: space.map(|s| s.to_string()),
            name: name.map(|s| s.to_string()),
            version: version.map(|s| s.to_string()),
            uid: uid.map(|s| s.to_string()),
            registry_type,
            alias,
        })
    }
}

/// CardDeck is a collection of cards that can be used to create a card deck and load in one call
///
#[pyclass]
#[derive(Debug)]
pub struct CardDeck {
    #[pyo3(get, set)]
    pub space: String,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub version: String,

    #[pyo3(get, set)]
    pub uid: String,

    #[pyo3(get, set)]
    pub created_at: DateTime<Utc>,

    #[pyo3(get, set)]
    pub cards: Vec<Card>,

    #[pyo3(get)]
    pub opsml_version: String,

    #[pyo3(get, set)]
    pub app_env: String,

    #[pyo3(get)]
    pub is_card: bool,

    #[pyo3(get)]
    pub registry_type: RegistryType,

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
            is_card: true,
            registry_type: RegistryType::Deck,
        })
    }

    /// Load the cards in the card deck
    ///
    /// # Arguments
    ///
    /// * `py` - Python interpreter state
    /// * `load_kwargs` - Optional map of alias to kwargs containing load arguments (DataLoadKwargs, ModelLoadKwargs)
    ///
    #[instrument(skip_all)]
    #[pyo3(signature = (load_kwargs=None))]
    pub fn load<'py>(
        &mut self,
        py: Python<'py>,
        load_kwargs: Option<HashMap<String, Bound<'_, PyAny>>>,
    ) -> PyResult<()> {
        debug!("Loading CardDeck: {}", self.name);

        // iterate over card_objs and call load (only for datacard and modelcard)
        for (alias, card_obj) in &self.card_objs {
            let bound = card_obj.clone_ref(py).into_bound(py);
            let registry_type = bound.getattr("registry_type")?.extract::<RegistryType>()?;

            match registry_type {
                RegistryType::Data => {
                    let kwargs = load_kwargs
                        .as_ref()
                        .and_then(|kwargs| kwargs.get(alias))
                        .map(|kwargs| kwargs.extract::<DataLoadKwargs>())
                        .transpose()?;

                    bound.call_method1("load", (Option::<PathBuf>::None, kwargs))?;
                }
                RegistryType::Model => {
                    let (load_onnx, kwargs) = match load_kwargs
                        .as_ref()
                        .and_then(|kwargs| kwargs.get(alias))
                        .map(|kwargs| kwargs.extract::<ModelLoadKwargs>())
                        .transpose()?
                    {
                        Some(model_kwargs) => {
                            let load_onnx = model_kwargs.load_onnx;
                            let kwargs = Some(model_kwargs);
                            (load_onnx, kwargs)
                        }
                        None => (false, None),
                    };

                    bound.call_method1("load", (Option::<PathBuf>::None, load_onnx, kwargs))?;
                }
                _ => {}
            }
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

    /// Get the registry card for the card deck
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

    /// enable __getitem__ for CardDeck alias calls
    pub fn __getitem__<'py>(&self, py: Python<'py>, key: &str) -> PyResult<Bound<'py, PyAny>> {
        match self.card_objs.get(key) {
            Some(value) => Ok(value.clone_ref(py).into_bound(py)),
            None => Err(OpsmlError::new_err(format!(
                "KeyError: key '{}' not found in CardDeck",
                key
            ))),
        }
    }

    #[pyo3(signature = (path=None))]
    pub fn download_artifacts(&mut self, py: Python, path: Option<PathBuf>) -> PyResult<()> {
        let base_path = path.unwrap_or_else(|| PathBuf::from(self.name.clone()));

        // delete the path if it exists
        if base_path.exists() {
            std::fs::remove_dir_all(&base_path).map_err(|e| {
                error!("Failed to remove directory: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;
        }

        for (alias, card_obj) in &self.card_objs {
            let bound = card_obj.clone_ref(py).into_bound(py);
            let registry_type = bound.getattr("registry_type")?.extract::<RegistryType>()?;
            let card_path = base_path.join(alias);

            match registry_type {
                RegistryType::Data | RegistryType::Model => {
                    bound.call_method1("download_artifacts", (Some(card_path),))?;
                }
                RegistryType::Experiment => {
                    bound.call_method1("save", (card_path,))?;
                }
                RegistryType::Prompt => {
                    bound.call_method1("save_card", (card_path,))?;
                }
                _ => continue,
            }
        }

        // save CardDeck to path
        self.save(base_path)?;

        Ok(())
    }

    /// Loads a card deck and its associated cards from a filesystem path.
    ///
    /// # Process
    /// 1. Loads the card deck JSON file
    /// 2. For each card in the deck:
    ///    - Loads the card's JSON file
    ///    - Extracts any provided load kwargs
    ///    - Loads the card object with kwargs if provided
    ///    - Loads artifacts for data/model cards
    ///    - Returns the loaded card object
    /// 3. Loads all card objects into the deck
    /// 4. Returns the complete card deck
    ///
    /// # Arguments
    /// * `py` - Python interpreter state
    /// * `path` - Path to the card deck JSON file
    /// * `load_kwargs` - Optional loading arguments for cards
    ///
    /// # Load Kwargs Format
    /// The `load_kwargs` argument should be a nested dictionary with structure:
    /// ```python
    /// {
    ///     "card_alias": {
    ///         "interface": interface_object,
    ///         "load_kwargs": DataLoadKwargs | ModelLoadKwargs
    ///     }
    /// }
    /// ```
    ///
    /// # Returns
    /// Returns `PyResult<CardDeck>` containing the loaded card deck or an error
    ///
    /// # Errors
    /// Will return `PyResult::Err` if:
    /// - Card deck JSON file cannot be read
    /// - Individual card files cannot be loaded
    /// - Invalid kwargs are provided
    #[staticmethod]
    #[pyo3(signature = (path, load_kwargs=None))]
    pub fn load_from_path(
        py: Python,
        path: PathBuf,
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<CardDeck> {
        let mut card_deck = Self::load_card_deck_json(&path)?;

        for card in &card_deck.cards {
            let card_obj = Self::load_card(py, &path, card, load_kwargs)?;
            card_deck.card_objs.insert(card.alias.clone(), card_obj);
        }

        Ok(card_deck)
    }
}

impl CardDeck {
    fn load_card(
        py: Python,
        base_path: &PathBuf,
        card: &Card,
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PyObject> {
        let card_path = base_path.join(&card.alias);

        let (interface, load_kwargs) =
            Self::extract_kwargs(py, load_kwargs, &card.alias).map_err(|e| {
                error!("Failed to extract kwargs: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        let card_json = Self::read_card_json(&card_path)?;
        let json_path = card_path.join(SaveName::Card).with_extension(Suffix::Json);

        let card_obj = match card.registry_type {
            RegistryType::Data => {
                Self::load_data_card(py, &card_json, &json_path, interface, load_kwargs)?
            }
            RegistryType::Model => {
                Self::load_model_card(py, &card_json, &json_path, interface, load_kwargs)?
            }
            RegistryType::Experiment => Self::load_experiment_card(&card_json)?,
            RegistryType::Prompt => Self::load_prompt_card(&card_json)?,
            _ => {
                error!("Unsupported registry type: {:?}", card.registry_type);
                return Err(OpsmlError::new_err(format!(
                    "Unsupported registry type: {:?}",
                    card.registry_type
                )));
            }
        };

        Ok(card_obj)
    }
    fn load_card_deck_json(path: &PathBuf) -> PyResult<CardDeck> {
        let card_deck_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        let json_string = std::fs::read_to_string(card_deck_path).map_err(|e| {
            error!("Failed to read file: {}", e);
            OpsmlError::new_err(e.to_string())
        })?;
        Self::model_validate_json(json_string)
    }

    fn extract_kwargs<'py>(
        py: Python<'py>,
        kwargs: Option<&Bound<'py, PyDict>>,
        alias: &str,
    ) -> PyResult<(Option<Bound<'py, PyAny>>, Option<Bound<'py, PyAny>>)> {
        let card_kwargs = kwargs
            .and_then(|kwargs| kwargs.get_item(alias).ok())
            .and_then(|bound| match bound {
                Some(b) => b.downcast::<PyDict>().ok().map(|dict| dict.clone()),
                None => None,
            });

        match card_kwargs {
            Some(kwargs) => {
                let interface = kwargs
                    .get_item("interface")
                    .ok()
                    .flatten()
                    .map(|bound| bound.into_bound_py_any(py))
                    .transpose()?;

                let load_kwargs = kwargs
                    .get_item("load_kwargs")
                    .ok()
                    .flatten()
                    .map(|bound| bound.into_bound_py_any(py))
                    .transpose()?;

                Ok((interface, load_kwargs))
            }
            None => Ok((None, None)),
        }
    }

    fn read_card_json(card_path: &PathBuf) -> PyResult<String> {
        std::fs::read_to_string(card_path.join(SaveName::Card).with_extension(Suffix::Json))
            .map_err(|e| OpsmlError::new_err(e.to_string()))
    }

    fn load_data_card(
        py: Python,
        card_json: &str,
        card_path: &PathBuf,
        interface: Option<Bound<'_, PyAny>>,
        load_kwargs: Option<Bound<'_, PyAny>>,
    ) -> PyResult<PyObject> {
        let mut card_obj =
            DataCard::model_validate_json(py, card_json.to_string(), interface.as_ref())?;
        let kwargs = load_kwargs.and_then(|kwargs| kwargs.extract::<DataLoadKwargs>().ok());

        card_obj
            .load(py, Some(card_path.clone()), kwargs)
            .map_err(|e| {
                error!("Failed to load card: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        card_obj.into_py_any(py).map_err(|e| {
            error!("Failed to convert card to PyAny: {}", e);
            OpsmlError::new_err(e.to_string())
        })
    }

    fn load_model_card(
        py: Python,
        card_json: &str,
        card_path: &PathBuf,
        interface: Option<Bound<'_, PyAny>>,
        load_kwargs: Option<Bound<'_, PyAny>>,
    ) -> PyResult<PyObject> {
        let mut card_obj =
            ModelCard::model_validate_json(py, card_json.to_string(), interface.as_ref())?;
        let kwargs = load_kwargs.and_then(|kwargs| kwargs.extract::<ModelLoadKwargs>().ok());
        let onnx = kwargs.as_ref().map(|k| k.load_onnx).unwrap_or(false);

        card_obj
            .load(py, Some(card_path.clone()), onnx, kwargs)
            .map_err(|e| {
                error!("Failed to load card: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        card_obj.into_py_any(py).map_err(|e| {
            error!("Failed to convert card to PyAny: {}", e);
            OpsmlError::new_err(e.to_string())
        })
    }

    fn load_experiment_card(card_json: &str) -> PyResult<PyObject> {
        let card_obj = ExperimentCard::model_validate_json(card_json.to_string())?;
        Python::with_gil(|py| {
            card_obj.into_py_any(py).map_err(|e| {
                error!("Failed to convert card to PyAny: {}", e);
                OpsmlError::new_err(e.to_string())
            })
        })
    }

    fn load_prompt_card(card_json: &str) -> PyResult<PyObject> {
        let card_obj = PromptCard::model_validate_json(card_json.to_string())?;
        Python::with_gil(|py| {
            card_obj.into_py_any(py).map_err(|e| {
                error!("Failed to convert card to PyAny: {}", e);
                OpsmlError::new_err(e.to_string())
            })
        })
    }
}

impl Serialize for CardDeck {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("CardDeck", 10)?;

        // set session to none
        state.serialize_field("space", &self.space)?;
        state.serialize_field("name", &self.name)?;
        state.serialize_field("version", &self.version)?;
        state.serialize_field("uid", &self.uid)?;
        state.serialize_field("created_at", &self.created_at)?;
        state.serialize_field("cards", &self.cards)?;
        state.serialize_field("opsml_version", &self.opsml_version)?;
        state.serialize_field("app_env", &self.app_env)?;
        state.serialize_field("is_card", &self.is_card)?;
        state.serialize_field("registry_type", &self.registry_type)?;
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
            IsCard,
            RegistryType,
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
                let mut is_card = None;
                let mut registry_type = None;

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
                        Field::IsCard => {
                            is_card = Some(map.next_value()?);
                        }
                        Field::RegistryType => {
                            registry_type = Some(map.next_value()?);
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
                let is_card = is_card.unwrap_or(true);
                let registry_type = registry_type.unwrap_or(RegistryType::Deck);

                Ok(CardDeck {
                    space,
                    name,
                    version,
                    uid,
                    created_at,
                    cards,
                    opsml_version,
                    card_objs,
                    is_card,
                    app_env,
                    registry_type,
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
            "is_card",
            "registry_type",
        ];
        deserializer.deserialize_struct("CardDeck", FIELDS, CardDeckVisitor)
    }
}
