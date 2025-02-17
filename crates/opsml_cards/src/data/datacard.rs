use crate::BaseArgs;
use opsml_error::error::{CardError, OpsmlError};
use opsml_interfaces::data::DataInterfaceSaveMetadata;
use opsml_interfaces::FeatureSchema;
use opsml_storage::FileSystemStorage;
use opsml_types::contracts::{ArtifactKey, Card, DataCardClientRecord};
use opsml_types::interfaces::types::DataInterfaceType;
use opsml_types::{
    cards::{CardTable, CardType},
    DataType, InterfaceType,
};
use pyo3::types::{PyDict, PyList};
use pyo3::{prelude::*, IntoPyObjectExt};
use pyo3::{PyTraverseError, PyVisit};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use tracing::error;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DataCardMetadata {
    #[pyo3(get, set)]
    pub schema: FeatureSchema,

    #[pyo3(get, set)]
    pub runcard_uid: Option<String>,

    #[pyo3(get, set)]
    pub pipelinecard_uid: Option<String>,

    #[pyo3(get, set)]
    pub auditcard_uid: Option<String>,
}

#[pymethods]
impl DataCardMetadata {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = ( schema=FeatureSchema::default(), runcard_uid=None, pipelinecard_uid=None, auditcard_uid=None))]
    pub fn new(
        schema: FeatureSchema,
        runcard_uid: Option<String>,
        pipelinecard_uid: Option<String>,
        auditcard_uid: Option<String>,
    ) -> Self {
        Self {
            schema,
            runcard_uid,
            pipelinecard_uid,
            auditcard_uid,
        }
    }
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

    #[pyo3(get, set)]
    pub uid: String,

    #[pyo3(get, set)]
    pub tags: Vec<String>,

    #[pyo3(get, set)]
    pub metadata: DataCardMetadata,

    #[pyo3(get)]
    pub card_type: CardType,

    #[pyo3(get)]
    pub data_type: DataType,

    pub rt: Option<Arc<tokio::runtime::Runtime>>,

    pub fs: Option<Arc<Mutex<FileSystemStorage>>>,

    pub artifact_key: Option<ArtifactKey>,
}

#[pymethods]
impl DataCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (interface, repository=None, name=None, contact=None, version=None, uid=None, tags=None, metadata=None))]
    pub fn new(
        interface: &Bound<'_, PyAny>,
        repository: Option<&str>,
        name: Option<&str>,
        contact: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
        tags: Option<&Bound<'_, PyList>>,
        metadata: Option<DataCardMetadata>,
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
        let interface_type = interface
            .getattr("interface_type")?
            .extract::<InterfaceType>()
            .map_err(|e| {
                OpsmlError::new_err(
                    format!("Invalid type passed to interface. Ensure class is a subclass of DataInterface. Error: {}", e)
                )
            })?;

        let data_type = interface
            .getattr("data_type")?
            .extract::<DataType>()
            .map_err(|e| {
                OpsmlError::new_err(format!(
                    "Error parsing data_type from interface. Error: {}",
                    e
                ))
            })?;

        if interface_type != InterfaceType::Data {
            return Err(OpsmlError::new_err(
                "Invalid type passed to interface. Ensure class is a subclass of DataInterface",
            ));
        }

        let metadata = metadata.unwrap_or(DataCardMetadata::new(
            FeatureSchema::default(),
            None,
            None,
            None,
        ));

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
            metadata,
            card_type: CardType::Data,
            data_type,
            rt: None,
            fs: None,
            artifact_key: None,
        })
    }

    pub fn add_tags(&mut self, tags: Vec<String>) {
        self.tags.extend(tags);
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save(
        &self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<DataInterfaceSaveMetadata> {
        let args = (path,);

        // if option raise error
        let data = self.interface.as_ref().ok_or_else(|| {
            OpsmlError::new_err(
                "Interface not found. Ensure DataCard has been initialized correctly",
            )
        })?;

        // call save on interface
        let metadata = data
            .call_method(py, "save", args, kwargs)
            .map_err(|e| {
                OpsmlError::new_err(format!("Error calling save method on interface: {}", e))
            })?
            .extract::<DataInterfaceSaveMetadata>(py)
            .map_err(|e| {
                OpsmlError::new_err(format!("Error extracting metadata from interface: {}", e))
            })?;

        Ok(metadata)
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
    pub fn get_registry_card(&self) -> Result<Card, CardError> {
        let record = DataCardClientRecord {
            created_at: None,
            app_env: None,
            repository: self.repository.clone(),
            name: self.name.clone(),
            contact: self.contact.clone(),
            version: self.version.clone(),
            uid: self.uid.clone(),
            tags: self.tags.clone(),
            data_type: self.data_type.to_string(),
            runcard_uid: self.metadata.runcard_uid.clone(),
            pipelinecard_uid: self.metadata.pipelinecard_uid.clone(),
            auditcard_uid: self.metadata.auditcard_uid.clone(),
            interface_type: DataInterfaceType::Arrow.to_string(),
            username: std::env::var("OPSML_USERNAME").unwrap_or_else(|_| "guest".to_string()),
        };

        Ok(Card::Data(record))
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
        let card_type = ob.getattr("card_type")?.extract()?;
        let data_type = ob.getattr("data_type")?.extract()?;

        Ok(DataCard {
            interface: Some(interface.unbind()),
            name,
            repository,
            contact,
            version,
            uid,
            tags,
            metadata,
            card_type,
            data_type,
        })
    }
}
