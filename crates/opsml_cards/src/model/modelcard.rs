use crate::error::CardError;
use crate::model::error::interface_error;
use crate::utils::BaseArgs;
use chrono::{DateTime, Utc};
use opsml_crypt::decrypt_directory;
use opsml_interfaces::base::DriftProfileMap;
use opsml_interfaces::{error::ModelInterfaceError, OnnxModel, OnnxSession};
use opsml_interfaces::{
    CatBoostModel, HuggingFaceModel, LightGBMModel, LightningModel, SklearnModel, TorchModel,
    XGBoostModel,
};
use opsml_interfaces::{ModelInterface, TensorFlowModel};
use opsml_interfaces::{ModelInterfaceMetadata, ModelLoadKwargs, ModelSaveKwargs};
use opsml_storage::storage_client;
use opsml_types::contracts::{ArtifactKey, CardRecord, ModelCardClientRecord};
use opsml_types::{
    DataType, ModelInterfaceType, ModelType, RegistryType, SaveName, Suffix, TaskType,
};
use opsml_utils::{create_tmp_path, extract_py_attr, get_utc_datetime, PyHelperFuncs};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::{IntoPyObjectExt, PyObject};
use pyo3::{PyTraverseError, PyVisit};
use serde::{
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
    Deserialize, Deserializer, Serialize, Serializer,
};
use std::fmt;
use std::path::{Path, PathBuf};
use tracing::{debug, error, instrument};

fn interface_from_metadata<'py>(
    py: Python<'py>,
    metadata: &ModelInterfaceMetadata,
) -> Result<Bound<'py, PyAny>, ModelInterfaceError> {
    match metadata.interface_type {
        ModelInterfaceType::Sklearn => SklearnModel::from_metadata(py, metadata),
        ModelInterfaceType::CatBoost => CatBoostModel::from_metadata(py, metadata),
        ModelInterfaceType::LightGBM => LightGBMModel::from_metadata(py, metadata),
        ModelInterfaceType::XGBoost => XGBoostModel::from_metadata(py, metadata),
        ModelInterfaceType::Torch => TorchModel::from_metadata(py, metadata),
        ModelInterfaceType::Lightning => LightningModel::from_metadata(py, metadata),
        ModelInterfaceType::HuggingFace => HuggingFaceModel::from_metadata(py, metadata),
        ModelInterfaceType::TensorFlow => TensorFlowModel::from_metadata(py, metadata),
        ModelInterfaceType::Onnx => OnnxModel::from_metadata(py, metadata),
        _ => Err(ModelInterfaceError::InterfaceTypeNotFoundError),
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ModelCardMetadata {
    #[pyo3(get, set)]
    pub datacard_uid: Option<String>,

    #[pyo3(get, set)]
    pub experimentcard_uid: Option<String>,

    #[pyo3(get, set)]
    pub auditcard_uid: Option<String>,

    pub interface_metadata: ModelInterfaceMetadata,
}

#[pymethods]
impl ModelCardMetadata {
    #[new]
    #[pyo3(signature = (datacard_uid=None, experimentcard_uid=None, auditcard_uid=None))]
    pub fn new(
        datacard_uid: Option<&str>,
        experimentcard_uid: Option<&str>,
        auditcard_uid: Option<&str>,
    ) -> Self {
        Self {
            datacard_uid: datacard_uid.map(|s| s.to_string()),
            experimentcard_uid: experimentcard_uid.map(|s| s.to_string()),
            auditcard_uid: auditcard_uid.map(|s| s.to_string()),
            interface_metadata: ModelInterfaceMetadata::default(),
        }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass]
pub struct ModelCard {
    #[pyo3(get, set)]
    pub interface: Option<PyObject>,

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

    #[pyo3(get, set)]
    pub metadata: ModelCardMetadata,

    #[pyo3(get)]
    pub registry_type: RegistryType,

    #[pyo3(get, set)]
    pub app_env: String,

    #[pyo3(get, set)]
    pub created_at: DateTime<Utc>,

    #[pyo3(get)]
    pub is_card: bool,

    #[pyo3(get)]
    pub opsml_version: String,

    artifact_key: Option<ArtifactKey>,
}

#[pymethods]
impl ModelCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (interface, space=None, name=None, version=None, uid=None, tags=None, datacard_uid=None, metadata=None))]
    pub fn new(
        py: Python,
        interface: &Bound<'_, PyAny>,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
        tags: Option<&Bound<'_, PyList>>,
        datacard_uid: Option<&str>,
        metadata: Option<ModelCardMetadata>,
    ) -> Result<Self, CardError> {
        let registry_type = RegistryType::Model;
        let tags = match tags {
            None => Vec::new(),
            Some(t) => t.extract::<Vec<String>>()?,
        };

        let base_args = BaseArgs::create_args(name, space, version, uid, &registry_type)?;

        if interface.is_instance_of::<ModelInterface>() {
            //
        } else {
            return Err(CardError::CustomError(interface_error()));
        }

        let interface_type = extract_py_attr::<ModelInterfaceType>(interface, "interface_type")?;
        let data_type = extract_py_attr::<DataType>(interface, "data_type")?;
        let model_type = extract_py_attr::<ModelType>(interface, "model_type")?;
        let task_type = extract_py_attr::<TaskType>(interface, "task_type")?;

        let mut metadata = metadata.unwrap_or_default();

        // if metadata.datacard_uid is None, set it to datacard_uid
        if metadata.datacard_uid.is_none() {
            metadata.datacard_uid = datacard_uid.map(|s| s.to_string());
        }

        metadata.interface_metadata.interface_type = interface_type;
        metadata.interface_metadata.data_type = data_type;
        metadata.interface_metadata.model_type = model_type;
        metadata.interface_metadata.task_type = task_type;

        Ok(Self {
            interface: Some(interface.into_py_any(py)?),
            space: base_args.0,
            name: base_args.1,
            version: base_args.2,
            uid: base_args.3,
            tags,
            metadata,
            registry_type,
            artifact_key: None,
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            created_at: get_utc_datetime(),
            is_card: true,
            opsml_version: opsml_version::version(),
        })
    }

    #[getter]
    pub fn get_onnx_session<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Option<Bound<'py, OnnxSession>>, CardError> {
        if let Some(interface) = self.interface.as_ref() {
            let session = interface.bind(py).getattr("onnx_session")?;

            if session.is_none() {
                Ok(None)
            } else {
                let session = session.downcast::<OnnxSession>()?;
                Ok(Some(session.clone()))
            }
        } else {
            Ok(None)
        }
    }

    #[getter]
    pub fn datacard_uid(&self) -> Option<&str> {
        self.metadata.datacard_uid.as_deref()
    }

    #[setter]
    pub fn set_datacard_uid(&mut self, datacard_uid: Option<String>) {
        self.metadata.datacard_uid = datacard_uid.map(|s| s.to_string());
    }

    #[getter]
    pub fn experimentcard_uid(&self) -> Option<&str> {
        self.metadata.experimentcard_uid.as_deref()
    }

    #[setter]
    pub fn set_experimentcard_uid(&mut self, experimentcard_uid: Option<String>) {
        self.metadata.experimentcard_uid = experimentcard_uid.map(|s| s.to_string());
    }

    #[getter]
    pub fn auditcard_uid(&self) -> Option<&str> {
        self.metadata.auditcard_uid.as_deref()
    }

    #[setter]
    pub fn set_auditcard_uid(&mut self, auditcard_uid: Option<String>) {
        self.metadata.auditcard_uid = auditcard_uid.map(|s| s.to_string());
    }

    #[setter]
    pub fn set_interface(&mut self, interface: &Bound<'_, PyAny>) -> Result<(), CardError> {
        if interface.is_instance_of::<ModelInterface>() {
            self.interface = Some(interface.into_py_any(interface.py())?);
            Ok(())
        } else {
            Err(CardError::MustBeModelInterfaceError)
        }
    }

    #[getter]
    pub fn interface<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyAny>> {
        self.interface.as_ref().map(|i| i.bind(py).clone())
    }

    #[getter]
    pub fn drift_profile<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Bound<'py, DriftProfileMap>, CardError> {
        if let Some(interface) = self.interface.as_ref() {
            let drift_profiles = interface.bind(py).getattr("drift_profile")?;
            Ok(drift_profiles.downcast::<DriftProfileMap>()?.clone())
        } else {
            Err(CardError::InterfaceNotFoundError)
        }
    }

    pub fn add_tags(&mut self, tags: Vec<String>) {
        self.tags.extend(tags);
    }

    #[pyo3(signature = (path, save_kwargs=None))]
    pub fn save(
        &mut self,
        py: Python,
        path: PathBuf,
        save_kwargs: Option<ModelSaveKwargs>,
    ) -> Result<(), CardError> {
        // save model interface
        // if option raise error
        let model = self
            .interface
            .as_ref()
            .ok_or_else(|| CardError::InterfaceNotFoundError)?;

        // scouter integration: update drift config args
        self.update_drift_config_args(py)?;

        let metadata = model
            .bind(py)
            .call_method("save", (path.clone(), save_kwargs), None)
            .inspect_err(|e| {
                error!("Failed to save model interface: {e}");
            })?;

        // extract into ModelInterfaceMetadata
        let interface_metadata = metadata
            .extract::<ModelInterfaceMetadata>()
            .inspect_err(|e| {
                error!("Failed to extract metadata: {e}");
            })?;

        // update metadata
        self.metadata.interface_metadata = interface_metadata;

        // save modelcard
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(&self, &card_save_path)?;

        Ok(())
    }

    #[pyo3(signature = (path=None, load_kwargs=None))]
    #[allow(clippy::too_many_arguments)]
    #[instrument(skip_all)]
    pub fn load(
        &mut self,
        py: Python,
        path: Option<PathBuf>,
        load_kwargs: Option<ModelLoadKwargs>,
    ) -> Result<(), CardError> {
        debug!("Loading model: {:?}", path);
        let path = if let Some(p) = path {
            p
        } else {
            let tmp_path = create_tmp_path()?;
            // download assets
            self.download_all_artifacts(&tmp_path)?;
            tmp_path
        };

        let save_metadata = self
            .metadata
            .interface_metadata
            .save_metadata
            .clone()
            .into_bound_py_any(py)?;

        // load model interface

        let interface = self.interface.as_ref().unwrap().bind(py);

        interface.call_method("load", (path, save_metadata, load_kwargs), None)?;

        Ok(())
    }

    /// Staticmethod for loading a ModelCard from a path.
    /// This is typically used within the context of APIs, where a
    /// use may download a model's artifacts before starting the API.
    /// This helper allows a user to load the ModelCard from a path during API startup.
    /// # Arguments
    /// * `py` - The Python interpreter instance.
    /// * `path` - The path to the model card directory.
    /// * `load_kwargs` - Optional keyword arguments for loading the model.
    /// * `interface` - Optional interface for the model. Used with Custom interfaces
    #[staticmethod]
    #[pyo3(signature = (path, load_kwargs=None, interface=None))]
    pub fn load_from_path<'py>(
        py: Python<'py>,
        path: PathBuf,
        load_kwargs: Option<ModelLoadKwargs>,
        interface: Option<&Bound<'py, PyAny>>,
    ) -> Result<Self, CardError> {
        // Load the Card json first in order to get it's metadata
        let card_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        let json_string = std::fs::read_to_string(&card_path).inspect_err(|e| {
            error!("Failed to read card json: {e}");
        })?;

        let mut card =
            ModelCard::model_validate_json(py, json_string, interface).inspect_err(|e| {
                error!("Failed to validate ModelCard: {e}");
            })?;

        card.load(py, Some(path), load_kwargs)?;

        Ok(card)
    }

    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (path=None))]
    pub fn download_artifacts(&mut self, path: Option<PathBuf>) -> Result<(), CardError> {
        let path = path.unwrap_or_else(|| PathBuf::from("card_artifacts"));
        self.download_all_artifacts(&path)?;
        Ok(())
    }

    pub fn model_dump_json(&self) -> String {
        serde_json::to_string(self).unwrap()
    }

    #[staticmethod]
    #[pyo3(signature = (json_string, interface=None))]
    pub fn model_validate_json(
        py: Python,
        json_string: String,
        interface: Option<&Bound<'_, PyAny>>,
    ) -> Result<ModelCard, CardError> {
        let mut card: ModelCard = serde_json::from_str(&json_string).inspect_err(|e| {
            error!("Failed to validate json: {e}");
        })?;

        card.load_interface(py, interface)?;

        Ok(card)
    }

    /// Helper function to get the drift profile path from the metadata.
    /// This function will return an error if the no drift profile map is found or
    /// if the alias is not found in the map.
    ///
    /// # Arguments
    /// * `alias` - The alias of the drift profile to get the path for.
    ///
    /// # Returns
    /// * `Result<PathBuf, CardError>` - The path to the drift profile.
    pub fn drift_profile_path(&self, alias: &str) -> Result<PathBuf, CardError> {
        // Use as_ref() to avoid unwrapping the Option
        let map = self
            .metadata
            .interface_metadata
            .save_metadata
            .drift_profile_uri_map
            .as_ref()
            .ok_or(CardError::DriftProfileNotFoundError)?;

        // Get the profile directly without checking contains_key first
        map.get(alias)
            .ok_or(CardError::DriftProfileNotFoundError)
            // Use clone only at the final return point
            .map(|profile| profile.uri.clone())
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        if let Some(ref interface) = self.interface {
            visit.call(interface)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.interface = None;
    }

    pub fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        let record = ModelCardClientRecord {
            app_env: self.app_env.clone(),
            created_at: self.created_at,
            space: self.space.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            uid: self.uid.clone(),
            tags: self.tags.clone(),
            datacard_uid: self.metadata.datacard_uid.clone(),
            data_type: self.metadata.interface_metadata.data_type.to_string(),
            model_type: self.metadata.interface_metadata.model_type.to_string(),
            experimentcard_uid: self.metadata.experimentcard_uid.clone(),
            auditcard_uid: self.metadata.auditcard_uid.clone(),
            interface_type: self.metadata.interface_metadata.interface_type.to_string(),
            task_type: self.metadata.interface_metadata.task_type.to_string(),
            opsml_version: self.opsml_version.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
        };

        Ok(CardRecord::Model(record))
    }

    pub fn save_card(&self, path: PathBuf) -> Result<(), CardError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(self, &card_save_path)?;

        Ok(())
    }

    /// Get the model from the interface if available.
    /// This will result in an error if the interface is not set and
    /// the model is not available.
    #[getter]
    pub fn model<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, CardError> {
        if let Some(interface) = self.interface.as_ref() {
            // get property "model" from interface
            let model = interface.bind(py).getattr("model")?;

            // check if model is None
            if model.is_none() {
                Err(CardError::ModelNotSetError)
            // return model
            } else {
                Ok(model)
            }
        } else {
            Err(CardError::InterfaceNotFoundError)
        }
    }
}

impl ModelCard {
    pub fn set_artifact_key(&mut self, key: ArtifactKey) {
        self.artifact_key = Some(key);
    }
    fn update_drift_config_args(&self, py: Python) -> Result<(), CardError> {
        let interface = self.interface.as_ref().unwrap().bind(py);
        let drift_profiles = interface.getattr("drift_profile")?;
        // downcast to list
        let drift_profiles = drift_profiles.downcast::<DriftProfileMap>()?;

        // if drift_profiles is empty, return
        if drift_profiles.call_method0("is_empty")?.extract::<bool>()? {
            Ok(())
        } else {
            // set new config args from card and update all profiles
            let config_args = PyDict::new(py);
            config_args.set_item("name", &self.name)?;
            config_args.set_item("space", &self.space)?;
            config_args.set_item("version", &self.version)?;

            drift_profiles.call_method1("update_config_args", (&config_args,))?;

            Ok(())
        }
    }

    fn load_interface(
        &mut self,
        py: Python,
        interface: Option<&Bound<'_, PyAny>>,
    ) -> Result<(), CardError> {
        if let Some(interface) = interface {
            // this for custom interfaces (uninstantiated)

            let interface = interface
                .call_method1("from_metadata", (self.metadata.interface_metadata.clone(),))?;

            self.set_interface(&interface)
        } else {
            // match interface type
            let interface = interface_from_metadata(py, &self.metadata.interface_metadata)?;
            self.set_interface(&interface)
        }
    }
}

impl Serialize for ModelCard {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("ModelCard", 11)?;

        // set session to none
        state.serialize_field("name", &self.name)?;
        state.serialize_field("space", &self.space)?;
        state.serialize_field("version", &self.version)?;
        state.serialize_field("uid", &self.uid)?;
        state.serialize_field("tags", &self.tags)?;
        state.serialize_field("metadata", &self.metadata)?;
        state.serialize_field("registry_type", &self.registry_type)?;
        state.serialize_field("created_at", &self.created_at)?;
        state.serialize_field("app_env", &self.app_env)?;
        state.serialize_field("is_card", &self.is_card)?;
        state.serialize_field("opsml_version", &self.opsml_version)?;
        state.end()
    }
}

impl FromPyObject<'_> for ModelCard {
    fn extract_bound(ob: &Bound<'_, PyAny>) -> PyResult<Self> {
        let interface = ob.getattr("interface")?;
        let name = ob.getattr("name")?.extract()?;
        let space = ob.getattr("space")?.extract()?;

        let version = ob.getattr("version")?.extract()?;
        let uid = ob.getattr("uid")?.extract()?;
        let tags = ob.getattr("tags")?.extract()?;
        let metadata = ob.getattr("metadata")?.extract()?;
        let registry_type = ob.getattr("registry_type")?.extract()?;
        let created_at = ob.getattr("created_at")?.extract()?;
        let app_env = ob.getattr("app_env")?.extract()?;
        let opsml_version = ob.getattr("opsml_version")?.extract()?;

        Ok(ModelCard {
            interface: Some(interface.into()),
            name,
            space,
            version,
            uid,
            tags,
            metadata,
            registry_type,
            artifact_key: None,
            app_env,
            created_at,
            is_card: true,
            opsml_version,
        })
    }
}

impl<'de> Deserialize<'de> for ModelCard {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(field_identifier, rename_all = "snake_case")]
        enum Field {
            Interface,
            Name,
            Space,
            Version,
            Uid,
            Tags,
            Metadata,
            RegistryType,
            AppEnv,
            CreatedAt,
            IsCard,
            OpsmlVersion,
        }

        struct ModelCardVisitor;

        impl<'de> Visitor<'de> for ModelCardVisitor {
            type Value = ModelCard;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("struct ModelCard")
            }

            fn visit_map<V>(self, mut map: V) -> Result<ModelCard, V::Error>
            where
                V: MapAccess<'de>,
            {
                let mut interface = None;
                let mut name = None;
                let mut space = None;
                let mut version = None;
                let mut uid = None;
                let mut tags = None;
                let mut metadata = None;
                let mut registry_type = None;
                let mut app_env = None;
                let mut created_at = None;
                let mut is_card = None;
                let mut opsml_version = None;

                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Interface => {
                            let _interface: Option<serde_json::Value> = map.next_value()?;
                            interface = None; // Default to None always (pyobject)
                        }
                        Field::Name => {
                            name = Some(map.next_value()?);
                        }
                        Field::Space => {
                            space = Some(map.next_value()?);
                        }

                        Field::Version => {
                            version = Some(map.next_value()?);
                        }
                        Field::Uid => {
                            uid = Some(map.next_value()?);
                        }
                        Field::Tags => {
                            tags = Some(map.next_value()?);
                        }
                        Field::Metadata => {
                            metadata = Some(map.next_value()?);
                        }
                        Field::RegistryType => {
                            registry_type = Some(map.next_value()?);
                        }
                        Field::AppEnv => {
                            app_env = Some(map.next_value()?);
                        }
                        Field::CreatedAt => {
                            created_at = Some(map.next_value()?);
                        }
                        Field::IsCard => {
                            is_card = Some(map.next_value()?);
                        }
                        Field::OpsmlVersion => {
                            opsml_version = Some(map.next_value()?);
                        }
                    }
                }

                let name = name.ok_or_else(|| de::Error::missing_field("name"))?;
                let space = space.ok_or_else(|| de::Error::missing_field("space"))?;
                let version = version.ok_or_else(|| de::Error::missing_field("version"))?;
                let uid = uid.ok_or_else(|| de::Error::missing_field("uid"))?;
                let tags = tags.ok_or_else(|| de::Error::missing_field("tags"))?;
                let metadata = metadata.ok_or_else(|| de::Error::missing_field("metadata"))?;
                let registry_type =
                    registry_type.ok_or_else(|| de::Error::missing_field("registry_type"))?;
                let app_env = app_env.ok_or_else(|| de::Error::missing_field("app_env"))?;
                let created_at =
                    created_at.ok_or_else(|| de::Error::missing_field("created_at"))?;
                let is_card = is_card.ok_or_else(|| de::Error::missing_field("is_card"))?;
                let opsml_version =
                    opsml_version.ok_or_else(|| de::Error::missing_field("opsml_version"))?;

                Ok(ModelCard {
                    interface,
                    name,
                    space,
                    version,
                    uid,
                    tags,
                    metadata,
                    registry_type,
                    artifact_key: None,
                    app_env,
                    created_at,
                    is_card,
                    opsml_version,
                })
            }
        }

        const FIELDS: &[&str] = &[
            "interface",
            "name",
            "space",
            "version",
            "uid",
            "tags",
            "metadata",
            "registry_type",
            "app_env",
            "created_at",
            "is_card",
            "opsml_version",
        ];
        deserializer.deserialize_struct("ModelCard", FIELDS, ModelCardVisitor)
    }
}

impl ModelCard {
    fn get_decryption_key(&self) -> Result<Vec<u8>, CardError> {
        if self.artifact_key.is_none() {
            Err(CardError::DecryptionKeyNotFoundError)
        } else {
            Ok(self.artifact_key.as_ref().unwrap().get_decrypt_key()?)
        }
    }
    fn download_all_artifacts(&mut self, lpath: &Path) -> Result<(), CardError> {
        let decrypt_key = self.get_decryption_key()?;
        let uri = self.artifact_key.as_ref().unwrap().storage_path();

        storage_client()?.get(lpath, &uri, true)?;

        decrypt_directory(lpath, &decrypt_key)?;

        Ok(())
    }
}
