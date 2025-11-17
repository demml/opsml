use crate::error::CardError;
use crate::utils::BaseArgs;
use chrono::{DateTime, Utc};
use opsml_crypt::decrypt_directory;
use opsml_interfaces::data::{
    ArrowData, DataInterface, DataInterfaceMetadata, DataLoadKwargs, DataSaveKwargs, NumpyData,
    PandasData, PolarsData, SqlData, TorchData,
};
use opsml_interfaces::FeatureSchema;
use opsml_storage::storage_client;
use opsml_types::contracts::{ArtifactKey, CardRecord, DataCardClientRecord};
use opsml_types::interfaces::types::DataInterfaceType;
use opsml_types::{DataType, RegistryType, SaveName, Suffix};
use opsml_utils::{create_tmp_path, extract_py_attr, get_utc_datetime, PyHelperFuncs};
use pyo3::types::PyList;
use pyo3::{prelude::*, IntoPyObjectExt};
use pyo3::{PyTraverseError, PyVisit};
use serde::{
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
    Deserialize, Deserializer, Serialize, Serializer,
};
use std::path::{Path, PathBuf};
use tracing::error;

fn interface_from_metadata<'py>(
    py: Python<'py>,
    metadata: &DataInterfaceMetadata,
) -> Result<Bound<'py, PyAny>, CardError> {
    match metadata.interface_type {
        DataInterfaceType::Arrow => Ok(ArrowData::from_metadata(py, metadata)?),
        DataInterfaceType::Pandas => Ok(PandasData::from_metadata(py, metadata)?),
        DataInterfaceType::Numpy => Ok(NumpyData::from_metadata(py, metadata)?),
        DataInterfaceType::Polars => Ok(PolarsData::from_metadata(py, metadata)?),
        DataInterfaceType::Torch => Ok(TorchData::from_metadata(py, metadata)?),
        DataInterfaceType::Sql => Ok(SqlData::from_metadata(py, metadata)?),

        _ => {
            error!("Interface type not found");
            Err(CardError::InterfaceNotFoundError)
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DataCardMetadata {
    #[pyo3(get, set)]
    pub schema: FeatureSchema,

    #[pyo3(get, set)]
    pub experimentcard_uid: Option<String>,

    #[pyo3(get, set)]
    pub auditcard_uid: Option<String>,

    pub interface_metadata: DataInterfaceMetadata,
}

#[pyclass]
pub struct DataCard {
    #[pyo3(get, set)]
    pub interface: Option<Py<PyAny>>,

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
    pub metadata: DataCardMetadata,

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
impl DataCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (interface, space=None, name=None, version=None, uid=None, tags=None, metadata=None))]
    pub fn new(
        interface: &Bound<'_, PyAny>,
        space: Option<&str>,
        name: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
        tags: Option<&Bound<'_, PyList>>,
        metadata: Option<DataCardMetadata>,
    ) -> Result<Self, CardError> {
        let registry_type = RegistryType::Data;
        let tags = match tags {
            None => Vec::new(),
            Some(t) => t.extract::<Vec<String>>()?,
        };

        let base_args = BaseArgs::create_args(name, space, version, uid, &registry_type)?;

        let py = interface.py();

        if interface.is_instance_of::<DataInterface>() {
            //
        } else {
            return Err(CardError::MustBeDataInterfaceError);
        }

        let interface_type = extract_py_attr::<DataInterfaceType>(interface, "interface_type")?;
        let data_type = extract_py_attr::<DataType>(interface, "data_type")?;

        let mut metadata = metadata.unwrap_or_default();
        metadata.interface_metadata.interface_type = interface_type;
        metadata.interface_metadata.data_type = data_type;

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

    #[setter]
    pub fn set_interface(&mut self, interface: &Bound<'_, PyAny>) -> Result<(), CardError> {
        if interface.is_instance_of::<DataInterface>() {
            self.interface = Some(interface.into_py_any(interface.py())?);
            Ok(())
        } else {
            Err(CardError::MustBeDataInterfaceError)
        }
    }

    #[getter]
    pub fn interface<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyAny>> {
        self.interface.as_ref().map(|i| i.bind(py).clone())
    }

    pub fn add_tags(&mut self, tags: Vec<String>) {
        self.tags.extend(tags);
    }

    #[getter]
    pub fn experimentcard_uid(&self) -> Option<&str> {
        self.metadata.experimentcard_uid.as_deref()
    }

    #[setter]
    pub fn set_experimentcard_uid(&mut self, experimentcard_uid: Option<String>) {
        self.metadata.experimentcard_uid = experimentcard_uid.map(|s| s.to_string());
    }

    #[pyo3(signature = (path, save_kwargs=None))]
    pub fn save(
        &mut self,
        py: Python,
        path: PathBuf,
        save_kwargs: Option<DataSaveKwargs>,
    ) -> Result<(), CardError> {
        // if option raise error
        let data = self
            .interface
            .as_ref()
            .ok_or_else(|| CardError::InterfaceNotFoundError)?;

        // call save on interface
        let metadata = data
            .call_method(py, "save", (&path, save_kwargs), None)?
            .extract::<DataInterfaceMetadata>(py)?;

        // update metadata
        self.metadata.interface_metadata = metadata;

        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(&self, &card_save_path)?;

        Ok(())
    }

    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (path=None))]
    pub fn download_artifacts(&mut self, path: Option<PathBuf>) -> Result<(), CardError> {
        let path = path.unwrap_or_else(|| PathBuf::from("card_artifacts"));
        self.download_all_artifacts(&path)?;
        Ok(())
    }

    #[pyo3(signature = (path=None, load_kwargs=None))]
    #[allow(clippy::too_many_arguments)]
    pub fn load(
        &mut self,
        py: Python,
        path: Option<PathBuf>,
        load_kwargs: Option<DataLoadKwargs>,
    ) -> Result<(), CardError> {
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

        // load data interface
        self.interface.as_ref().unwrap().bind(py).call_method(
            "load",
            (path, save_metadata, load_kwargs),
            None,
        )?;

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
    ) -> Result<DataCard, CardError> {
        let mut card: DataCard = serde_json::from_str(&json_string).inspect_err(|e| {
            error!("Failed to validate json: {}", e);
        })?;

        card.load_interface(py, interface)?;

        Ok(card)
    }

    pub fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        let record = DataCardClientRecord {
            created_at: self.created_at,
            app_env: self.app_env.clone(),
            space: self.space.clone(),
            name: self.name.clone(),
            version: self.version.clone(),
            uid: self.uid.clone(),
            tags: self.tags.clone(),
            data_type: self.metadata.interface_metadata.data_type.to_string(),
            experimentcard_uid: self.metadata.experimentcard_uid.clone(),
            auditcard_uid: self.metadata.auditcard_uid.clone(),
            interface_type: self.metadata.interface_metadata.interface_type.to_string(),
            opsml_version: self.opsml_version.clone(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
        };

        Ok(CardRecord::Data(record))
    }

    pub fn save_card(&self, path: PathBuf) -> Result<(), CardError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(self, &card_save_path)?;

        Ok(())
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

    /// Get the model from the interface if available.
    /// This will result in an error if the interface is not set and
    /// the model is not available.
    #[getter]
    pub fn data<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, CardError> {
        if let Some(interface) = self.interface.as_ref() {
            // get property "model" from interface
            let data = interface.bind(py).getattr("data")?;

            // check if model is None
            if data.is_none() {
                Err(CardError::DataNotSetError)
            // return model
            } else {
                Ok(data)
            }
        } else {
            Err(CardError::InterfaceNotFoundError)
        }
    }

    /// Create a data profile using the interface's method.
    pub fn create_data_profile(&self, py: Python) -> Result<(), CardError> {
        let interface = self
            .interface
            .as_ref()
            .ok_or_else(|| CardError::InterfaceNotFoundError)?;

        interface.bind(py).call_method0("create_data_profile")?;

        Ok(())
    }

    pub fn split_data<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, CardError> {
        let interface = self
            .interface
            .as_ref()
            .ok_or_else(|| CardError::InterfaceNotFoundError)?;

        Ok(interface.bind(py).call_method0("split_data")?)
    }
}

impl DataCard {
    pub fn set_artifact_key(&mut self, key: ArtifactKey) {
        self.artifact_key = Some(key);
    }

    fn load_interface(
        &mut self,
        py: Python,
        interface: Option<&Bound<'_, PyAny>>,
    ) -> Result<(), CardError> {
        if let Some(interface) = interface {
            let interface = interface
                .call_method1("from_metadata", (self.metadata.interface_metadata.clone(),))?;

            self.set_interface(&interface)
        } else {
            // match interface type
            let interface = interface_from_metadata(py, &self.metadata.interface_metadata)?;
            self.set_interface(&interface)
        }
    }

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

impl Serialize for DataCard {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("DataCard", 10)?;

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

impl<'de> Deserialize<'de> for DataCard {
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

        struct DataCardVisitor;

        impl<'de> Visitor<'de> for DataCardVisitor {
            type Value = DataCard;

            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("struct DataCard")
            }

            fn visit_map<V>(self, mut map: V) -> Result<DataCard, V::Error>
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
                            interface = None; // Default to None always (Py<PyAny>)
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

                Ok(DataCard {
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
        deserializer.deserialize_struct("DataCard", FIELDS, DataCardVisitor)
    }
}

impl FromPyObject<'_> for DataCard {
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

        Ok(DataCard {
            interface: Some(interface.unbind()),
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
