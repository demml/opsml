use crate::error::CardError;
use crate::traits::OpsmlCard;
use crate::utils::BaseArgs;
use crate::{DataCard, ExperimentCard, ModelCard, PromptCard};
use chrono::{DateTime, Utc};
use opsml_interfaces::{DataLoadKwargs, ModelLoadKwargs};
use opsml_service::ServiceSpec;
use opsml_types::contracts::{CardEntry, ServiceConfig};
use opsml_types::CommonKwargs;
use opsml_types::{
    contracts::{
        CardRecord, DeploymentConfig, ServiceCardClientRecord, ServiceMetadata, ServiceType,
    },
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

#[derive(PartialEq, Debug, Clone)]
#[pyclass(eq)]
pub struct ServiceInfo {
    pub space: String,
    pub name: String,
    pub version: String,
}

impl ServiceInfo {
    pub fn update(
        &mut self,
        space: String,
        name: String,
        version: String,
    ) -> Result<(), CardError> {
        self.space = space;
        self.name = name;
        self.version = version;
        Ok(())
    }
}

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
            return Err(CardError::MissingServiceCardArgsError);
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
/// CardList holds a list of cards for the ServiceCard
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

impl CardList {
    pub fn iter(&self) -> std::slice::Iter<'_, Card> {
        self.cards.iter()
    }
}

/// ServiceCard is a collection of cards that can be associated and loaded in one call
/// aka a ServiceCard. We use ServiceCard for consistency with developing "Applications".
#[pyclass]
#[derive(Debug)]
pub struct ServiceCard {
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
    pub card_objs: HashMap<String, Py<PyAny>>,

    #[pyo3(get, set)]
    pub experimentcard_uid: Option<String>,

    #[pyo3(get)]
    pub service_type: ServiceType,

    pub metadata: Option<ServiceMetadata>,

    pub deploy: Option<Vec<DeploymentConfig>>,

    pub service_config: Option<ServiceConfig>,
}

#[pymethods]
impl ServiceCard {
    /// Create a new ServiceCard from the provided arguments
    /// # Arguments
    /// * `space` - The space of the service
    /// * `name` - The name of the service
    /// * `cards` - A list of cards to include in the service
    /// * `version` - The version of the service (optional)
    #[new]
    #[pyo3(signature = (space, name,  cards, version=None, service_type=None, load_spec=false))]
    pub fn new(
        space: &str,
        name: &str,
        cards: Vec<Card>, // can be Vec<Card> or Vec<ModelCard, DataCard, etc.>
        version: Option<&str>,
        service_type: Option<ServiceType>,
        load_spec: bool, // whether to load the spec from the service card
    ) -> Result<Self, CardError> {
        let registry_type = RegistryType::Service;
        let base_args =
            BaseArgs::create_args(Some(name), Some(space), version, None, &registry_type)?;

        let spec = if load_spec {
            ServiceSpec::from_env()?
        } else {
            ServiceSpec::new_empty(
                &base_args.0,
                &base_args.1,
                service_type.unwrap_or(ServiceType::Api),
            )?
        };

        Ok(ServiceCard {
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
            service_type: spec.service_type,
            metadata: spec.metadata,
            deploy: spec.deploy,
            service_config: spec.service,
        })
    }

    #[setter]
    pub fn set_cards(&mut self, cards: Vec<Card>) {
        self.cards = CardList { cards };
    }

    /// Load the cards in the
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
        debug!("Loading ServiceCard: {}", self.name);

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
    pub fn model_validate_json(json_string: String) -> Result<ServiceCard, CardError> {
        Ok(serde_json::from_str(&json_string).inspect_err(|e| {
            error!("Failed to validate json: {e}");
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

    /// Get the registry card for the service card
    pub fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        let record = ServiceCardClientRecord {
            created_at: self.created_at,
            app_env: self.app_env.clone(),
            space: self.space.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            uid: self.uid.clone(),
            cards: self.cards.to_card_entries(),
            opsml_version: self.opsml_version.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
            service_type: self.service_type.to_string(),
            metadata: self.metadata.clone(),
            deployment: self.deploy.clone(),
            service_config: self.service_config.clone(),
        };

        Ok(CardRecord::Service(record))
    }

    /// enable __getitem__ for ServiceCard alias calls
    pub fn __getitem__<'py>(
        &self,
        py: Python<'py>,
        key: &str,
    ) -> Result<Bound<'py, PyAny>, CardError> {
        match self.card_objs.get(key) {
            Some(value) => Ok(value.clone_ref(py).into_bound(py)),
            None => Err(CardError::ServiceCardKeyError(key.to_string())),
        }
    }

    /// Downloads artifacts for all cards in the service card.
    ///
    /// # Arguments
    /// * `py` - Python interpreter state
    /// * `path` - Optional path to save the artifacts. If not provided, defaults to "service".
    /// Path follows the format: `service/{name}-{version}/{alias}`.
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
        let base_path = path.unwrap_or_else(|| PathBuf::from("service"));

        // delete the path if it exists
        if base_path.exists() {
            std::fs::remove_dir_all(&base_path).inspect_err(|e| {
                error!("Failed to remove directory: {e}");
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

        // save ServiceCard to path
        self.save(base_path)?;

        Ok(())
    }

    /// Loads a service card and its associated cards from a filesystem path.
    ///
    /// # Process
    /// 1. Loads the service card JSON file
    /// 2. For each card in the service:
    ///    - Loads the card's JSON file
    ///    - Extracts any provided load kwargs
    ///    - Loads the card object with kwargs if provided
    ///    - Loads artifacts for data/model cards
    ///    - Returns the loaded card object
    /// 3. Loads all card objects into the service
    /// 4. Returns the complete service card
    ///
    /// # Arguments
    /// * `py` - Python interpreter state
    /// * `path` - Path to the service card files. This should be the top-level directory and will be
    /// appended with the "{name}-{version} directory containing the service card files". Defaults to "service".
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
    /// Returns `Result<ServiceCard>` containing the loaded service card or an error
    ///
    /// # Errors
    /// Will return `Result::Err` if:
    /// - Card service JSON file cannot be read
    /// - Individual card files cannot be loaded
    /// - Invalid kwargs are provided
    #[staticmethod]
    #[pyo3(signature = (path=None, load_kwargs=None))]
    pub fn from_path(
        py: Python,
        path: Option<PathBuf>,
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<ServiceCard, CardError> {
        let path = path.unwrap_or_else(|| PathBuf::from(SaveName::ServiceCard));

        let service = Self::from_path_rs(py, &path, load_kwargs)?;
        Ok(service)
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    /// Helper for getting space, name and version
    /// associated with the service
    pub fn service_info(&self) -> ServiceInfo {
        ServiceInfo {
            space: self.space.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
        }
    }
}

impl ServiceCard {
    #[instrument(skip_all)]
    pub fn from_path_rs(
        py: Python,
        path: &Path,
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<ServiceCard, CardError> {
        debug!("Loading from path: {:?}", path);
        // check path exists
        if !path.exists() {
            error!("Path does not exist: {:?}", path);
            return Err(CardError::PathDoesNotExistError(
                path.to_string_lossy().to_string(),
            ));
        }

        debug!("Loading service JSON from path: {:?}", path);
        let mut service = Self::load_service_json(path)?;

        debug!("Loading cards");
        for card in &service.cards {
            let card_obj = Self::load_card(py, path, card, load_kwargs)?;
            service.card_objs.insert(card.alias.clone(), card_obj);
        }

        Ok(service)
    }

    #[instrument(skip_all)]
    fn load_card(
        py: Python,
        base_path: &Path,
        card: &Card,
        load_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Py<PyAny>, CardError> {
        let card_path = base_path.join(&card.alias);

        let (interface, load_kwargs) = Self::extract_kwargs(py, load_kwargs, &card.alias)
            .inspect_err(|e| {
                error!("Failed to extract kwargs: {e}");
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
    pub fn load_service_json(path: &Path) -> Result<ServiceCard, CardError> {
        let service_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        let json_string = std::fs::read_to_string(service_path).inspect_err(|e| {
            error!("Failed to read file: {e}");
        })?;
        Self::model_validate_json(json_string)
    }

    fn extract_kwargs<'py>(
        py: Python<'py>,
        kwargs: Option<&Bound<'py, PyDict>>,
        alias: &str,
    ) -> Result<ExtractedKwargs<'py>, CardError> {
        debug!("Extracting kwargs for alias: {}", alias);
        debug!("Provided kwargs: {:?}", kwargs);
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
    ) -> Result<Py<PyAny>, CardError> {
        let mut card_obj =
            DataCard::model_validate_json(py, card_json.to_string(), interface.as_ref())?;
        let kwargs = load_kwargs.and_then(|kwargs| kwargs.extract::<DataLoadKwargs>().ok());

        card_obj
            .load(py, Some(card_path), kwargs)
            .inspect_err(|e| {
                error!("Failed to load card: {e}");
            })?;

        Ok(card_obj.into_py_any(py).inspect_err(|e| {
            error!("Failed to convert card to PyAny: {e}");
        })?)
    }

    #[instrument(skip_all)]
    fn load_model_card(
        py: Python,
        card_json: &str,
        card_path: PathBuf,
        interface: Option<Bound<'_, PyAny>>,
        load_kwargs: Option<Bound<'_, PyAny>>,
    ) -> Result<Py<PyAny>, CardError> {
        let mut card_obj =
            ModelCard::model_validate_json(py, card_json.to_string(), interface.as_ref())?;
        let kwargs = load_kwargs.and_then(|kwargs| kwargs.extract::<ModelLoadKwargs>().ok());

        card_obj
            .load(py, Some(card_path), kwargs)
            .inspect_err(|e| {
                error!("Failed to load card: {e}");
            })?;

        Ok(card_obj.into_py_any(py).inspect_err(|e| {
            error!("Failed to convert card to PyAny: {e}");
        })?)
    }

    fn load_experiment_card(card_json: &str) -> Result<Py<PyAny>, CardError> {
        let card_obj = ExperimentCard::model_validate_json(card_json.to_string())?;
        Python::attach(|py| Ok(card_obj.into_py_any(py)?))
    }

    #[instrument(skip_all)]
    fn load_prompt_card(card_json: &str) -> Result<Py<PyAny>, CardError> {
        debug!("Loading prompt card from JSON");
        let card_obj = PromptCard::model_validate_json(card_json.to_string())?;
        Python::attach(|py| Ok(card_obj.into_py_any(py)?))
    }
}

impl ServiceCard {
    /// Helper function for creating ServiceCard from within Rust. Used in the CLI lock command.
    pub fn rust_new(
        space: String,
        name: String,
        cards: Vec<Card>, // can be Vec<Card> or Vec<ModelCard, DataCard, etc.>
        spec: &ServiceSpec,
    ) -> Result<ServiceCard, CardError> {
        let registry_type = RegistryType::Service;
        let base_args = BaseArgs::create_args(
            Some(&name),
            Some(&space),
            spec.service.version.as_deref(),
            None,
            &registry_type,
        )?;

        Ok(ServiceCard {
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
            service_type: spec.service_type.clone(),
            metadata: spec.metadata.clone(),
            deploy: spec.deploy.clone(),
            service_config: spec.service.clone(),
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
impl OpsmlCard for ServiceCard {
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

impl Serialize for ServiceCard {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("ServiceCard", 10)?;

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
        state.serialize_field("service_type", &self.service_type)?;
        state.serialize_field("metadata", &self.metadata)?;
        state.serialize_field("deploy", &self.deploy)?;
        state.end()
    }
}

impl<'de> Deserialize<'de> for ServiceCard {
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
            ServiceType,
            Metadata,
            Deploy,
        }

        struct ServiceCardVisitor;

        impl<'de> Visitor<'de> for ServiceCardVisitor {
            type Value = ServiceCard;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct ServiceCard")
            }

            fn visit_map<V>(self, mut map: V) -> Result<ServiceCard, V::Error>
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
                let mut service_type = None;
                let mut metadata = None;
                let mut deploy = None;

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
                        Field::ServiceType => {
                            service_type = Some(map.next_value()?);
                        }
                        Field::Metadata => {
                            metadata = Some(map.next_value()?);
                        }
                        Field::Deploy => {
                            deploy = Some(map.next_value()?);
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
                let registry_type = registry_type.unwrap_or(RegistryType::Service);
                let experimentcard_uid = experimentcard_uid.unwrap_or(None);
                let service_type = service_type.unwrap_or(ServiceType::Api);
                let metadata = metadata.unwrap_or(None);
                let deploy = deploy.unwrap_or(None);

                Ok(ServiceCard {
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
                    service_type,
                    metadata,
                    deploy,
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
            "service_type",
            "metadata",
            "deploy",
        ];
        deserializer.deserialize_struct("ServiceCard", FIELDS, ServiceCardVisitor)
    }
}
