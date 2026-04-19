use crate::error::CardError;
use chrono::{DateTime, Utc};
use opsml_types::{RegistryType, SaveName, Suffix};
use opsml_utils::PyHelperFuncs;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tracing::error;

#[cfg(feature = "python")]
use {
    crate::utils::BaseArgs,
    opsml_crypt::decrypt_directory,
    opsml_interfaces::{
        FeatureSchema,
        data::{
            ArrowData, DataInterface, DataInterfaceMetadata, DataLoadKwargs, DataSaveKwargs,
            NumpyData, PandasData, PolarsData, SqlData, TorchData,
        },
    },
    opsml_storage::storage_client,
    opsml_types::{
        DataType,
        contracts::{ArtifactKey, CardRecord, DataCardClientRecord},
        interfaces::types::DataInterfaceType,
    },
    opsml_utils::{create_tmp_path, extract_py_attr, get_utc_datetime},
    pyo3::{IntoPyObjectExt, PyTraverseError, PyVisit, prelude::*},
    std::path::Path,
};

#[cfg(feature = "python")]
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

#[cfg_attr(feature = "python", pyclass(from_py_object))]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DataCardMetadata {
    pub experimentcard_uid: Option<String>,
    pub auditcard_uid: Option<String>,

    #[cfg(feature = "python")]
    #[serde(default)]
    pub schema: FeatureSchema,
    #[cfg(feature = "python")]
    #[serde(default)]
    pub interface_metadata: DataInterfaceMetadata,
}

#[cfg(feature = "python")]
#[pymethods]
impl DataCardMetadata {
    #[getter]
    pub fn schema(&self) -> FeatureSchema {
        self.schema.clone()
    }
    #[setter]
    pub fn set_schema(&mut self, val: FeatureSchema) {
        self.schema = val;
    }

    #[getter]
    pub fn experimentcard_uid(&self) -> Option<String> {
        self.experimentcard_uid.clone()
    }
    #[setter]
    pub fn set_experimentcard_uid(&mut self, val: Option<String>) {
        self.experimentcard_uid = val;
    }

    #[getter]
    pub fn auditcard_uid(&self) -> Option<String> {
        self.auditcard_uid.clone()
    }
    #[setter]
    pub fn set_auditcard_uid(&mut self, val: Option<String>) {
        self.auditcard_uid = val;
    }
}

#[cfg_attr(feature = "python", pyclass(skip_from_py_object))]
#[derive(Debug, Serialize, Deserialize)]
pub struct DataCard {
    pub space: String,
    pub name: String,
    pub version: String,
    pub uid: String,
    pub tags: Vec<String>,
    pub metadata: DataCardMetadata,
    pub registry_type: RegistryType,
    pub app_env: String,
    pub created_at: DateTime<Utc>,
    pub is_card: bool,
    pub opsml_version: String,

    #[cfg(feature = "python")]
    #[serde(skip)]
    pub interface: Option<Py<PyAny>>,

    #[serde(skip)]
    #[cfg(feature = "python")]
    artifact_key: Option<ArtifactKey>,
}

impl DataCard {
    pub fn save_card(&self, path: PathBuf) -> Result<(), CardError> {
        let card_save_path = path.join(SaveName::Card).with_extension(Suffix::Json);
        PyHelperFuncs::save_to_json(self, &card_save_path)?;
        Ok(())
    }

    pub fn model_validate_json(json_string: String) -> Result<DataCard, CardError> {
        serde_json::from_str(&json_string).map_err(|e| {
            error!("Failed to validate json: {}", e);
            CardError::from(e)
        })
    }
}

#[cfg(feature = "python")]
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
        tags: Option<Vec<String>>,
        metadata: Option<DataCardMetadata>,
    ) -> Result<Self, CardError> {
        let registry_type = RegistryType::Data;
        let tags = tags.unwrap_or_default();

        let base_args = BaseArgs::create_args(name, space, version, uid, &registry_type)?;

        let py = interface.py();

        if !interface.is_instance_of::<DataInterface>() {
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

    #[getter]
    pub fn space(&self) -> String {
        self.space.clone()
    }
    #[setter]
    pub fn set_space(&mut self, val: String) {
        self.space = val;
    }

    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }
    #[setter]
    pub fn set_name(&mut self, val: String) {
        self.name = val;
    }

    #[getter]
    pub fn version(&self) -> String {
        self.version.clone()
    }
    #[setter]
    pub fn set_version(&mut self, val: String) {
        self.version = val;
    }

    #[getter]
    pub fn uid(&self) -> String {
        self.uid.clone()
    }
    #[setter]
    pub fn set_uid(&mut self, val: String) {
        self.uid = val;
    }

    #[getter]
    pub fn tags(&self) -> Vec<String> {
        self.tags.clone()
    }
    #[setter]
    pub fn set_tags(&mut self, val: Vec<String>) {
        self.tags = val;
    }

    #[getter]
    pub fn metadata(&self) -> DataCardMetadata {
        self.metadata.clone()
    }
    #[setter]
    pub fn set_metadata(&mut self, val: DataCardMetadata) {
        self.metadata = val;
    }

    #[getter]
    pub fn registry_type(&self) -> RegistryType {
        self.registry_type.clone()
    }

    #[getter]
    pub fn app_env(&self) -> String {
        self.app_env.clone()
    }
    #[setter]
    pub fn set_app_env(&mut self, val: String) {
        self.app_env = val;
    }

    #[getter]
    pub fn created_at(&self) -> DateTime<Utc> {
        self.created_at
    }
    #[setter]
    pub fn set_created_at(&mut self, val: DateTime<Utc>) {
        self.created_at = val;
    }

    #[getter]
    pub fn is_card(&self) -> bool {
        self.is_card
    }

    #[getter]
    pub fn opsml_version(&self) -> String {
        self.opsml_version.clone()
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
        self.metadata.experimentcard_uid = experimentcard_uid;
    }

    #[pyo3(signature = (path, save_kwargs=None))]
    pub fn save(
        &mut self,
        py: Python,
        path: PathBuf,
        save_kwargs: Option<DataSaveKwargs>,
    ) -> Result<(), CardError> {
        let data = self
            .interface
            .as_ref()
            .ok_or(CardError::InterfaceNotFoundError)?;

        let metadata = data
            .call_method(py, "save", (&path, save_kwargs), None)?
            .extract::<DataInterfaceMetadata>(py)?;

        self.metadata.interface_metadata = metadata;
        self.save_card(path)
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
            self.download_all_artifacts(&tmp_path)?;
            tmp_path
        };

        let save_metadata = self
            .metadata
            .interface_metadata
            .save_metadata
            .clone()
            .into_bound_py_any(py)?;

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
    #[pyo3(name = "model_validate_json", signature = (json_string, interface=None))]
    pub fn model_validate_json_py(
        py: Python,
        json_string: String,
        interface: Option<&Bound<'_, PyAny>>,
    ) -> Result<DataCard, CardError> {
        let mut card = DataCard::model_validate_json(json_string)?;
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

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        if let Some(ref interface) = self.interface {
            visit.call(interface)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.interface = None;
    }

    #[getter]
    pub fn data<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, CardError> {
        if let Some(interface) = self.interface.as_ref() {
            let data = interface.bind(py).getattr("data")?;

            if data.is_none() {
                Err(CardError::DataNotSetError)
            } else {
                Ok(data)
            }
        } else {
            Err(CardError::InterfaceNotFoundError)
        }
    }

    #[pyo3(signature = (bin_size=20, compute_correlations=false))]
    pub fn create_data_profile(
        &self,
        py: Python,
        bin_size: usize,
        compute_correlations: bool,
    ) -> Result<(), CardError> {
        let interface = self
            .interface
            .as_ref()
            .ok_or(CardError::InterfaceNotFoundError)?;

        interface
            .bind(py)
            .call_method1("create_data_profile", (bin_size, compute_correlations))?;

        Ok(())
    }

    pub fn split_data<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, CardError> {
        let interface = self
            .interface
            .as_ref()
            .ok_or(CardError::InterfaceNotFoundError)?;

        Ok(interface.bind(py).call_method0("split_data")?)
    }

    #[pyo3(name = "save_card")]
    pub fn save_card_py(&self, path: PathBuf) -> Result<(), CardError> {
        self.save_card(path)
    }
}

#[cfg(feature = "python")]
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
            let interface = interface_from_metadata(py, &self.metadata.interface_metadata)?;
            self.set_interface(&interface)
        }
    }

    #[cfg(feature = "python")]
    fn get_decryption_key(&self) -> Result<Vec<u8>, CardError> {
        if let Some(ref key) = self.artifact_key {
            Ok(key.get_crypt_key()?)
        } else {
            Err(CardError::DecryptionKeyNotFoundError)
        }
    }

    #[cfg(feature = "python")]
    fn download_all_artifacts(&mut self, lpath: &Path) -> Result<(), CardError> {
        let decrypt_key = self.get_decryption_key()?;
        let uri = self.artifact_key.as_ref().unwrap().storage_path();

        storage_client()?.get(lpath, &uri, true)?;

        decrypt_directory(lpath, &decrypt_key)?;

        Ok(())
    }
}

#[cfg(feature = "python")]
impl FromPyObject<'_, '_> for DataCard {
    type Error = PyErr;
    fn extract(ob: Borrowed<'_, '_, PyAny>) -> PyResult<Self> {
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
