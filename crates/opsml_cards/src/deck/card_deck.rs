use crate::error::CardError;
use crate::traits::OpsmlCard;
use crate::utils::BaseArgs;
use crate::{DataCard, ExperimentCard, ModelCard, PromptCard};
use chrono::{DateTime, Utc};
use opsml_interfaces::{DataLoadKwargs, ModelLoadKwargs};
use opsml_types::contracts::CardEntry;
use opsml_types::CommonKwargs;
use opsml_types::{
    contracts::{CardDeckClientRecord, CardRecord},
    RegistryType, SaveName, Suffix,
};
use opsml_utils::{extract_py_attr, PyHelperFuncs};
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
use std::path::{Path, PathBuf};
use tracing::{debug, error, instrument};

type PyBoundAny<'py> = Bound<'py, PyAny>;
type OptionalPyBound<'py> = Option<PyBoundAny<'py>>;
type ExtractedKwargs<'py> = (OptionalPyBound<'py>, OptionalPyBound<'py>);

#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
pub struct Card {
    #[pyo3(get, set)]
    pub space: String,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub version: String,

    #[pyo3(get, set)]
    pub uid: String,

    #[pyo3(get, set)]
    pub registry_type: RegistryType,

    #[pyo3(get, set)]
    pub alias: String,
}

#[pymethods]
impl Card {
    #[new]
    #[pyo3(signature = (alias, registry_type=None, space=None, name=None, version=None, uid=None, card=None))]
    pub fn new(
        alias: String,
        registry_type: Option<RegistryType>,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
        card: Option<Bound<'_, PyAny>>,
    ) -> Result<Self, CardError> {
        // if card is not None, then set the registry_type and alias
        if let Some(card) = card {
            let registry_type = extract_py_attr::<RegistryType>(&card, "registry_type")?;

            let uid = extract_py_attr::<Option<String>>(&card, "uid")?
                .ok_or_else(|| CardError::MissingAttributeError("uid".to_string()))?;

            let name = extract_py_attr::<Option<String>>(&card, "name")?
                .ok_or_else(|| CardError::MissingAttributeError("name".to_string()))?;

            let space = extract_py_attr::<Option<String>>(&card, "space")?
                .ok_or_else(|| CardError::MissingAttributeError("space".to_string()))?;

            let version = extract_py_attr::<Option<String>>(&card, "version")?
                .ok_or_else(|| CardError::MissingAttributeError("version".to_string()))?;

            return Ok(Card {
                space,
                name,
                version,
                uid,
                registry_type,
                alias,
            });
        }

        // if registry is none, raise error
        let registry_type = match registry_type {
            Some(registry_type) => registry_type,
            None => {
                error!("Registry type is required unless a registered card is provided");
                return Err(CardError::MissingRegistryTypeError);
            }
        };

        // check that at least space/name  or uid is provided
        let has_space_or_name = space.is_some() || name.is_some();
        let has_uid = uid.is_some();

        if !has_space_or_name && !has_uid {
            error!("Either space/name or uid must be provided");
            return Err(CardError::MissingCardDeckArgsError);
        }

        Ok(Card {
            space: space
                .map(String::from)
                .unwrap_or_else(|| CommonKwargs::Undefined.to_string()),
            name: name
                .map(String::from)
                .unwrap_or_else(|| CommonKwargs::Undefined.to_string()),
            version: version
                .map(String::from)
                .unwrap_or_else(|| CommonKwargs::Undefined.to_string()),
            uid: uid
                .map(String::from)
                .unwrap_or_else(|| CommonKwargs::Undefined.to_string()),
            registry_type,
            alias,
        })
    }
}

impl Card {
    pub fn rust_new(
        alias: String,
        registry_type: RegistryType,
        space: String,
        name: String,
        version: Option<String>,
    ) -> Card {
        Card {
            space,
            name,
            version: version.unwrap_or_else(|| CommonKwargs::Undefined.to_string()),
            uid: CommonKwargs::Undefined.to_string(),
            registry_type,
            alias,
        }
    }
}

#[pyclass]
struct CardListIter {
    inner: std::vec::IntoIter<Card>,
}

#[pymethods]
impl CardListIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<Card> {
        slf.inner.next()
    }
}
/// CardList holds a list of cards for the CardDeck
///
/// # Implementation
/// * Implements `__iter__`, `__len__`, and `__getitem__` for Python list compatibility
/// * Implements `IntoIterator` for Rust iterator compatibility
///
/// # Attributes
/// * `cards`: A vector of `Card` objects
#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
pub struct CardList {
    #[pyo3(get)]
    pub cards: Vec<Card>,
}

#[pymethods]
impl CardList {
    fn __iter__(slf: PyRef<'_, Self>) -> Result<Py<CardListIter>, CardError> {
        let iter = CardListIter {
            inner: slf.cards.clone().into_iter(),
        };
        Ok(Py::new(slf.py(), iter)?)
    }

    pub fn __len__(&self) -> usize {
        self.cards.len()
    }

    pub fn __getitem__(&self, index: usize) -> Result<Card, CardError> {
        if index >= self.cards.len() {
            return Err(CardError::IndexOutOfBoundsError(index));
        }
        Ok(self.cards[index].clone())
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

impl CardList {
    pub fn new_rs(cards: Vec<Card>) -> CardList {
        CardList { cards }
    }
    pub fn to_card_entries(&self) -> Vec<CardEntry> {
        self.cards
            .iter()
            .map(|card| CardEntry {
                alias: card.alias.clone(),
                version: card.version.clone(),
                uid: card.uid.clone(),
                registry_type: card.registry_type.clone(),
            })
            .collect()
    }
}

impl<'a> IntoIterator for &'a CardList {
    type Item = &'a Card;
    type IntoIter = std::slice::Iter<'a, Card>;

    fn into_iter(self) -> Self::IntoIter {
        self.cards.iter()
    }
}

/// CardDeck is a collection of cards that can be used to create a card deck and load in one call
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

    #[pyo3(get)]
    pub cards: CardList,

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

    #[pyo3(get, set)]
    pub experimentcard_uid: Option<String>,
}

#[pymethods]
impl CardDeck {
    #[new]
    #[pyo3(signature = (space, name,  cards, version=None))]
    pub fn new(
        space: &str,
        name: &str,
        cards: Vec<Card>, // can be Vec<Card> or Vec<ModelCard, DataCard, etc.>
        version: Option<&str>,
    ) -> Result<Self, CardError> {
        let registry_type = RegistryType::Deck;
        let base_args =
            BaseArgs::create_args(Some(name), Some(space), version, None, &registry_type)?;

        Ok(CardDeck {
            space: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            created_at: Utc::now(),
            cards: CardList { cards },
            opsml_version: opsml_version::version(),
            card_objs: HashMap::new(),
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            is_card: true,
            registry_type,
            experimentcard_uid: None,
        })
    }

    #[setter]
    pub fn set_cards(&mut self, cards: Vec<Card>) {
        self.cards = CardList { cards };
    }

    /// Load the cards in the card deck
    ///
    /// # Arguments
    /// * `py` - Python interpreter state
    /// * `load_kwargs` - Optional map of alias to kwargs containing load arguments (DataLoadKwargs, ModelLoadKwargs)
    ///
    #[instrument(skip_all)]
    #[pyo3(signature = (load_kwargs=None))]
    pub fn load<'py>(
        &mut self,
        py: Python<'py>,
        load_kwargs: Option<HashMap<String, Bound<'_, PyAny>>>,
    ) -> Result<(), CardError> {
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
                    let kwargs = load_kwargs
                        .as_ref()
                        .and_then(|kwargs| kwargs.get(alias))
                        .map(|kwargs| kwargs.extract::<ModelLoadKwargs>())
                        .transpose()?;

                    bound.call_method1("load", (Option::<PathBuf>::None, kwargs))?;
                }
                _ => {}
            }
        }
        Ok(())
    }

    #[pyo3(signature = (path))]
    pub fn save(&self, path: PathBuf) -> Result<(), CardError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(self, &card_save_path)?;

        Ok(())
    }

    #[staticmethod]
    #[pyo3(signature = (json_string))]
    pub fn model_validate_json(json_string: String) -> Result<CardDeck, CardError> {
        Ok(serde_json::from_str(&json_string).inspect_err(|e| {
            error!("Failed to validate json: {}", e);
        })?)
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
            cards: self.cards.to_card_entries(),
            opsml_version: self.opsml_version.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
        };

        Ok(CardRecord::Deck(record))
    }

    /// enable __getitem__ for CardDeck alias calls
    pub fn __getitem__<'py>(
        &self,
        py: Python<'py>,
        key: &str,
    ) -> Result<Bound<'py, PyAny>, CardError> {
        match self.card_objs.get(key) {
            Some(value) => Ok(value.clone_ref(py).into_bound(py)),
            None => Err(CardError::CardDeckKeyError(key.to_string())),
        }
    }

    /// Downloads artifacts for all cards in the card deck.
    ///
    /// # Arguments
    /// * `py` - Python interpreter state
    /// * `path` - Optional path to save the artifacts. If not provided, defaults to "card_deck".
    /// Path follows the format: `card_deck/{name}-{version}/{alias}`.
    ///
    /// # Returns
    /// Returns `Result<()>` indicating success or failure.
    ///
    /// # Errors
    /// Will return `Result::Err` if:
    /// - The path cannot be created or written to.
    /// - The artifacts cannot be downloaded.
    #[pyo3(signature = (path=None))]
    pub fn download_artifacts(
        &mut self,
        py: Python,
        path: Option<PathBuf>,
    ) -> Result<(), CardError> {
        let base_path = path.unwrap_or_else(|| PathBuf::from("card_deck"));

        // delete the path if it exists
        if base_path.exists() {
            std::fs::remove_dir_all(&base_path).inspect_err(|e| {
                error!("Failed to remove directory: {}", e);
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
    /// * `path` - Path to the card deck files. This should be the top-level directory and will be
    /// appended with the "{name}-{version} directory containing the card deck files". Defaults to "card_deck".
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
    /// Returns `Result<CardDeck>` containing the loaded card deck or an error
    ///
    /// # Errors
    /// Will return `Result::Err` if:
    /// - Card deck JSON file cannot be read
    /// - Individual card files cannot be loaded
    /// - Invalid kwargs are provided
    #[staticmethod]
    #[pyo3(signature = (path=None, load_kwargs=None))]
    pub fn from_path(
        py: Python,
        path: Option<PathBuf>,
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<CardDeck, CardError> {
        let path = path.unwrap_or_else(|| PathBuf::from(SaveName::CardDeck));

        // check path exists
        if !path.exists() {
            error!("Path does not exist: {:?}", path);
            return Err(CardError::PathDoesNotExistError(
                path.to_string_lossy().to_string(),
            ));
        }

        let mut card_deck = Self::load_card_deck_json(&path)?;

        for card in &card_deck.cards {
            let card_obj = Self::load_card(py, &path, card, load_kwargs)?;
            card_deck.card_objs.insert(card.alias.clone(), card_obj);
        }

        Ok(card_deck)
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

impl CardDeck {
    fn load_card(
        py: Python,
        base_path: &Path,
        card: &Card,
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<PyObject, CardError> {
        let card_path = base_path.join(&card.alias);

        let (interface, load_kwargs) = Self::extract_kwargs(py, load_kwargs, &card.alias)
            .inspect_err(|e| {
                error!("Failed to extract kwargs: {}", e);
            })?;

        let card_json = Self::read_card_json(&card_path)?;

        let card_obj = match card.registry_type {
            RegistryType::Data => {
                Self::load_data_card(py, &card_json, card_path, interface, load_kwargs)?
            }
            RegistryType::Model => {
                Self::load_model_card(py, &card_json, card_path, interface, load_kwargs)?
            }
            RegistryType::Experiment => Self::load_experiment_card(&card_json)?,
            RegistryType::Prompt => Self::load_prompt_card(&card_json)?,
            _ => {
                error!("Unsupported registry type: {:?}", card.registry_type);
                return Err(CardError::UnsupportedRegistryTypeError(
                    card.registry_type.clone(),
                ));
            }
        };

        Ok(card_obj)
    }
    pub fn load_card_deck_json(path: &Path) -> Result<CardDeck, CardError> {
        let card_deck_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        let json_string = std::fs::read_to_string(card_deck_path).inspect_err(|e| {
            error!("Failed to read file: {}", e);
        })?;
        Self::model_validate_json(json_string)
    }

    fn extract_kwargs<'py>(
        py: Python<'py>,
        kwargs: Option<&Bound<'py, PyDict>>,
        alias: &str,
    ) -> Result<ExtractedKwargs<'py>, CardError> {
        let card_kwargs = kwargs
            .and_then(|kwargs| kwargs.get_item(alias).ok())
            .and_then(|bound| match bound {
                Some(b) => b.downcast::<PyDict>().ok().cloned(),
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

    fn read_card_json(card_path: &Path) -> Result<String, CardError> {
        Ok(std::fs::read_to_string(
            card_path.join(SaveName::Card).with_extension(Suffix::Json),
        )?)
    }

    fn load_data_card(
        py: Python,
        card_json: &str,
        card_path: PathBuf,
        interface: Option<Bound<'_, PyAny>>,
        load_kwargs: Option<Bound<'_, PyAny>>,
    ) -> Result<PyObject, CardError> {
        let mut card_obj =
            DataCard::model_validate_json(py, card_json.to_string(), interface.as_ref())?;
        let kwargs = load_kwargs.and_then(|kwargs| kwargs.extract::<DataLoadKwargs>().ok());

        card_obj
            .load(py, Some(card_path), kwargs)
            .inspect_err(|e| {
                error!("Failed to load card: {}", e);
            })?;

        Ok(card_obj.into_py_any(py).inspect_err(|e| {
            error!("Failed to convert card to PyAny: {}", e);
        })?)
    }

    fn load_model_card(
        py: Python,
        card_json: &str,
        card_path: PathBuf,
        interface: Option<Bound<'_, PyAny>>,
        load_kwargs: Option<Bound<'_, PyAny>>,
    ) -> Result<PyObject, CardError> {
        let mut card_obj =
            ModelCard::model_validate_json(py, card_json.to_string(), interface.as_ref())?;
        let kwargs = load_kwargs.and_then(|kwargs| kwargs.extract::<ModelLoadKwargs>().ok());

        card_obj
            .load(py, Some(card_path), kwargs)
            .inspect_err(|e| {
                error!("Failed to load card: {}", e);
            })?;

        Ok(card_obj.into_py_any(py).inspect_err(|e| {
            error!("Failed to convert card to PyAny: {}", e);
        })?)
    }

    fn load_experiment_card(card_json: &str) -> Result<PyObject, CardError> {
        let card_obj = ExperimentCard::model_validate_json(card_json.to_string())?;
        Python::with_gil(|py| Ok(card_obj.into_py_any(py)?))
    }

    fn load_prompt_card(card_json: &str) -> Result<PyObject, CardError> {
        let card_obj = PromptCard::model_validate_json(card_json.to_string())?;
        Python::with_gil(|py| Ok(card_obj.into_py_any(py)?))
    }
}

impl CardDeck {
    /// Helper function for creating CardDeck from within Rust. Used in the CLI lock command.
    pub fn rust_new(
        space: String,
        name: String,
        cards: Vec<Card>, // can be Vec<Card> or Vec<ModelCard, DataCard, etc.>
        version: Option<&str>,
    ) -> Result<CardDeck, CardError> {
        let registry_type = RegistryType::Deck;
        let base_args =
            BaseArgs::create_args(Some(&name), Some(&space), version, None, &registry_type)?;

        Ok(CardDeck {
            space: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            created_at: Utc::now(),
            cards: CardList::new_rs(cards),
            opsml_version: opsml_version::version(),
            card_objs: HashMap::new(),
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            is_card: true,
            registry_type,
            experimentcard_uid: None,
        })
    }

    /// Helper method for getting a card by alias
    ///
    /// # Arguments
    /// * `alias` - The alias of the card to retrieve
    ///
    /// # Returns
    /// Returns a `Result<Card, CardError>` containing the card if found, or an error if not found
    pub fn get_card(&self, alias: &str) -> Result<Card, CardError> {
        self.cards
            .cards
            .iter()
            .find(|card| card.alias == alias)
            .cloned()
            .ok_or_else(|| CardError::AliasNotFoundInDeckError)
    }
}

// generic trait for compatibility and use in rust-based card functions
impl OpsmlCard for CardDeck {
    fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        self.get_registry_card()
    }

    fn get_version(&self) -> String {
        self.version.clone()
    }

    fn registry_type(&self) -> &RegistryType {
        &self.registry_type
    }

    fn set_space(&mut self, space: String) {
        self.space = space;
    }

    fn is_card(&self) -> bool {
        self.is_card
    }

    fn set_name(&mut self, name: String) {
        self.name = name;
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

    fn save(&self, path: PathBuf) -> Result<(), CardError> {
        self.save(path)
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
        state.serialize_field("experimentcard_uid", &self.experimentcard_uid)?;
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
            ExperimentcardUid,
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
                let mut experimentcard_uid = None;

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
                        Field::ExperimentcardUid => {
                            experimentcard_uid = Some(map.next_value()?);
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
                let experimentcard_uid = experimentcard_uid.unwrap_or(None);

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
                    experimentcard_uid,
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
            "experimentcard_uid",
        ];
        deserializer.deserialize_struct("CardDeck", FIELDS, CardDeckVisitor)
    }
}
