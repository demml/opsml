use crate::BaseArgs;
use chrono::NaiveDateTime;
use opsml_crypt::decrypt_directory;
use opsml_error::error::{CardError, OpsmlError};
use opsml_interfaces::data::{
    ArrowData, DataInterface, DataInterfaceMetadata, DataLoadKwargs, DataSaveKwargs, NumpyData,
    PandasData, PolarsData, SqlData, TorchData,
};
use opsml_interfaces::FeatureSchema;
use opsml_storage::FileSystemStorage;
use opsml_types::contracts::{ArtifactKey, Card, DataCardClientRecord};
use opsml_types::interfaces::types::DataInterfaceType;
use opsml_types::RegistryType;
use opsml_types::{SaveName, Suffix};
use opsml_utils::{create_tmp_path, get_utc_datetime, PyHelperFuncs};
use pyo3::types::PyList;
use pyo3::{prelude::*, IntoPyObjectExt};
use pyo3::{PyTraverseError, PyVisit};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};
use tracing::error;

use serde::{
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
    Deserialize, Deserializer, Serialize, Serializer,
};

fn interface_from_metadata<'py>(
    py: Python<'py>,
    metadata: &DataInterfaceMetadata,
) -> PyResult<Bound<'py, PyAny>> {
    match metadata.interface_type {
        DataInterfaceType::Arrow => ArrowData::from_metadata(py, metadata),
        DataInterfaceType::Pandas => PandasData::from_metadata(py, metadata),
        DataInterfaceType::Numpy => NumpyData::from_metadata(py, metadata),
        DataInterfaceType::Polars => PolarsData::from_metadata(py, metadata),
        DataInterfaceType::Torch => TorchData::from_metadata(py, metadata),
        DataInterfaceType::Sql => SqlData::from_metadata(py, metadata),

        _ => {
            error!("Interface type not found");
            Err(OpsmlError::new_err("Interface type not found"))
        }
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DataCardMetadata {
    #[pyo3(get, set)]
    pub schema: FeatureSchema,

    #[pyo3(get, set)]
    pub runcard_uid: Option<String>,

    #[pyo3(get, set)]
    pub pipelinecard_uid: Option<String>,

    #[pyo3(get, set)]
    pub auditcard_uid: Option<String>,

    pub interface_metadata: DataInterfaceMetadata,
}

#[pyclass]
pub struct DataCard {
    #[pyo3(get, set)]
    pub interface: Option<PyObject>,

    #[pyo3(get, set)]
    pub repository: String,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub contact: String,

    #[pyo3(get, set)]
    pub version: String,

    #[pyo3(get)]
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
    pub created_at: NaiveDateTime,

    pub rt: Option<Arc<tokio::runtime::Runtime>>,

    pub fs: Option<Arc<Mutex<FileSystemStorage>>>,

    pub artifact_key: Option<ArtifactKey>,
}

#[pymethods]
impl DataCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (interface, repository=None, name=None, contact=None, version=None, uid=None, tags=None))]
    pub fn new(
        interface: &Bound<'_, PyAny>,
        repository: Option<&str>,
        name: Option<&str>,
        contact: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
        tags: Option<&Bound<'_, PyList>>,
    ) -> PyResult<Self> {
        let tags = match tags {
            None => Vec::new(),
            Some(t) => t
                .extract::<Vec<String>>()
                .map_err(|e| OpsmlError::new_err(e.to_string()))?,
        };

        let base_args =
            BaseArgs::create_args(name, repository, contact, version, uid).map_err(|e| {
                error!("Failed to create base args: {}", e);
                OpsmlError::new_err(e.to_string())
            })?;

        let py = interface.py();

        // try and extract data_type from interface
        interface
            .getattr("interface_type")?
            .extract::<DataInterfaceType>()
            .map_err(|e| {
                OpsmlError::new_err(
                    format!("Invalid type passed to interface. Ensure class is a subclass of DataInterface. Error: {}", e)
                )
            })?;

        Ok(Self {
            interface: Some(
                interface
                    .into_py_any(py)
                    .map_err(|e| OpsmlError::new_err(e.to_string()))?,
            ),
            repository: base_args.0,
            name: base_args.1,
            contact: base_args.2,
            version: base_args.3,
            uid: base_args.4,
            tags,
            metadata: DataCardMetadata::default(),
            registry_type: RegistryType::Data,
            rt: None,
            fs: None,
            artifact_key: None,
            app_env: std::env::var("APP_ENV").unwrap_or_else(|_| "dev".to_string()),
            created_at: get_utc_datetime(),
        })
    }

    #[setter]
    pub fn set_interface(&mut self, interface: &Bound<'_, PyAny>) -> PyResult<()> {
        if interface.is_instance_of::<DataInterface>() {
            self.interface = Some(
                interface
                    .into_py_any(interface.py())
                    .map_err(|e| OpsmlError::new_err(e.to_string()))
                    .unwrap(),
            );
            Ok(())
        } else {
            return Err(OpsmlError::new_err(
                "interface must be an instance of ModelInterface",
            ));
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
        save_kwargs: Option<DataSaveKwargs>,
    ) -> Result<(), CardError> {
        // if option raise error
        let data = self.interface.as_ref().ok_or_else(|| {
            OpsmlError::new_err(
                "Interface not found. Ensure DataCard has been initialized correctly",
            )
        })?;

        // call save on interface
        let metadata = data
            .call_method(py, "save", (&path, save_kwargs), None)
            .map_err(|e| {
                OpsmlError::new_err(format!("Error calling save method on interface: {}", e))
            })?
            .extract::<DataInterfaceMetadata>(py)
            .map_err(|e| {
                OpsmlError::new_err(format!("Error extracting metadata from interface: {}", e))
            })?;

        // update metadata
        self.metadata.interface_metadata = metadata;

        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(&self, card_save_path)?;

        Ok(())
    }

    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (path=None))]
    pub fn download_artifacts(&mut self, path: Option<PathBuf>) -> PyResult<()> {
        let path = path.unwrap_or_else(|| PathBuf::from("card_artifacts"));
        self.download_all_artifacts(&path)?;
        Ok(())
    }

    #[pyo3(signature = (load_kwargs=None))]
    #[allow(clippy::too_many_arguments)]
    pub fn load(&mut self, py: Python, load_kwargs: Option<DataLoadKwargs>) -> PyResult<()> {
        let tmp_path = create_tmp_path()?;

        // download assets
        self.download_all_artifacts(&tmp_path)?;

        // load data interface
        self.interface.as_ref().unwrap().bind(py).call_method(
            "load",
            (tmp_path, load_kwargs),
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
    ) -> PyResult<DataCard> {
        let mut card: DataCard = serde_json::from_str(&json_string).map_err(|e| {
            error!("Failed to validate json: {}", e);
            OpsmlError::new_err(e.to_string())
        })?;

        card.load_interface(py, interface)?;

        Ok(card)
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
}

impl DataCard {
    fn load_interface(&mut self, py: Python, interface: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
        if let Some(interface) = interface {
            self.set_interface(interface)
        } else {
            // match interface type
            let interface = interface_from_metadata(py, &self.metadata.interface_metadata)?;
            self.set_interface(&interface)
        }
    }

    pub fn get_registry_card(&self) -> Result<Card, CardError> {
        let record = DataCardClientRecord {
            created_at: self.created_at,
            app_env: self.app_env.clone(),
            repository: self.repository.clone(),
            name: self.name.clone(),
            contact: self.contact.clone(),
            version: self.version.clone(),
            uid: self.uid.clone(),
            tags: self.tags.clone(),
            data_type: self.metadata.interface_metadata.data_type.to_string(),
            runcard_uid: self.metadata.runcard_uid.clone(),
            pipelinecard_uid: self.metadata.pipelinecard_uid.clone(),
            auditcard_uid: self.metadata.auditcard_uid.clone(),
            interface_type: self.metadata.interface_metadata.interface_type.to_string(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
        };

        Ok(Card::Data(record))
    }

    fn get_decryption_key(&self) -> Result<Vec<u8>, CardError> {
        if self.artifact_key.is_none() {
            return Err(CardError::Error("Decryption key not found".to_string()));
        } else {
            Ok(self.artifact_key.as_ref().unwrap().get_decrypt_key()?)
        }
    }

    fn download_all_artifacts(&mut self, lpath: &Path) -> Result<(), CardError> {
        let rt = self.rt.clone().unwrap();
        let fs = self.fs.clone().unwrap();

        let decrypt_key = self.get_decryption_key()?;
        let uri = self.artifact_key.as_ref().unwrap().storage_path();

        rt.block_on(async {
            fs.lock()
                .map_err(|e| CardError::Error(format!("Failed to unlock fs: {}", e)))?
                .get(&lpath, &uri, true)
                .await
                .map_err(|e| CardError::Error(format!("Failed to download artifacts: {}", e)))?;

            Ok::<(), CardError>(())
        })?;

        decrypt_directory(&lpath, &decrypt_key)?;

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
        state.serialize_field("repository", &self.repository)?;
        state.serialize_field("contact", &self.contact)?;
        state.serialize_field("version", &self.version)?;
        state.serialize_field("uid", &self.uid)?;
        state.serialize_field("tags", &self.tags)?;
        state.serialize_field("metadata", &self.metadata)?;
        state.serialize_field("registry_type", &self.registry_type)?;
        state.serialize_field("created_at", &self.created_at)?;
        state.serialize_field("app_env", &self.app_env)?;
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
            Repository,
            Contact,
            Version,
            Uid,
            Tags,
            Metadata,
            RegistryType,
            AppEnv,
            CreatedAt,
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
                let mut repository = None;
                let mut contact = None;
                let mut version = None;
                let mut uid = None;
                let mut tags = None;
                let mut metadata = None;
                let mut registry_type = None;
                let mut app_env = None;
                let mut created_at = None;

                while let Some(key) = map.next_key()? {
                    match key {
                        Field::Interface => {
                            let _interface: Option<serde_json::Value> = map.next_value()?;
                            interface = None; // Default to None always (pyobject)
                        }
                        Field::Name => {
                            name = Some(map.next_value()?);
                        }
                        Field::Repository => {
                            repository = Some(map.next_value()?);
                        }
                        Field::Contact => {
                            contact = Some(map.next_value()?);
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
                    }
                }

                let name = name.ok_or_else(|| de::Error::missing_field("name"))?;
                let repository =
                    repository.ok_or_else(|| de::Error::missing_field("repository"))?;
                let contact = contact.ok_or_else(|| de::Error::missing_field("contact"))?;
                let version = version.ok_or_else(|| de::Error::missing_field("version"))?;
                let uid = uid.ok_or_else(|| de::Error::missing_field("uid"))?;
                let tags = tags.ok_or_else(|| de::Error::missing_field("tags"))?;
                let metadata = metadata.ok_or_else(|| de::Error::missing_field("metadata"))?;
                let registry_type =
                    registry_type.ok_or_else(|| de::Error::missing_field("registry_type"))?;
                let app_env = app_env.ok_or_else(|| de::Error::missing_field("app_env"))?;
                let created_at =
                    created_at.ok_or_else(|| de::Error::missing_field("created_at"))?;

                Ok(DataCard {
                    interface,
                    name,
                    repository,
                    contact,
                    version,
                    uid,
                    tags,
                    metadata,
                    registry_type,
                    rt: None,
                    fs: None,
                    artifact_key: None,
                    app_env,
                    created_at,
                })
            }
        }

        const FIELDS: &[&str] = &[
            "interface",
            "name",
            "repository",
            "contact",
            "version",
            "uid",
            "tags",
            "metadata",
            "registry_type",
            "app_env",
            "created_at",
        ];
        deserializer.deserialize_struct("DataCard", FIELDS, DataCardVisitor)
    }
}

impl FromPyObject<'_> for DataCard {
    fn extract_bound(ob: &Bound<'_, PyAny>) -> PyResult<Self> {
        let interface = ob.getattr("interface")?;
        let name = ob.getattr("name")?.extract()?;
        let repository = ob.getattr("repository")?.extract()?;
        let contact = ob.getattr("contact")?.extract()?;
        let version = ob.getattr("version")?.extract()?;
        let uid = ob.getattr("uid")?.extract()?;
        let tags = ob.getattr("tags")?.extract()?;
        let metadata = ob.getattr("metadata")?.extract()?;
        let registry_type = ob.getattr("registry_type")?.extract()?;
        let created_at = ob.getattr("created_at")?.extract()?;
        let app_env = ob.getattr("app_env")?.extract()?;

        Ok(DataCard {
            interface: Some(interface.unbind()),
            name,
            repository,
            contact,
            version,
            uid,
            tags,
            metadata,
            registry_type,
            rt: None,
            fs: None,
            artifact_key: None,
            app_env,
            created_at,
        })
    }
}
