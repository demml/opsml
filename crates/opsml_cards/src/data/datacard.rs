use crate::BaseArgs;
use opsml_error::error::OpsmlError;
use opsml_interfaces::data::DataInterfaceSaveMetadata;
use opsml_interfaces::FeatureSchema;
use opsml_types::{
    cards::{CardTable, CardType},
    DataType, InterfaceType,
};
use pyo3::types::{PyDict, PyList};
use pyo3::{prelude::*, IntoPyObjectExt};
use pyo3::{PyTraverseError, PyVisit};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tracing::error;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DataCardMetadata {
    #[pyo3(get, set)]
    pub data_type: DataType,

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
    #[pyo3(signature = (data_type, schema=FeatureSchema::default(), runcard_uid=None, pipelinecard_uid=None, auditcard_uid=None))]
    pub fn new(
        data_type: DataType,
        schema: FeatureSchema,
        runcard_uid: Option<String>,
        pipelinecard_uid: Option<String>,
        auditcard_uid: Option<String>,
    ) -> Self {
        Self {
            data_type,
            schema,
            runcard_uid,
            pipelinecard_uid,
            auditcard_uid,
        }
    }
}

#[pyclass]
#[derive(Debug)]
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
            data_type,
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
        })
    }

    #[getter]
    pub fn uri(&self) -> PathBuf {
        let uri = format!(
            "{}/{}/{}/v{}",
            CardTable::Data,
            self.repository,
            self.name,
            self.version
        );

        PathBuf::from(uri)
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
        })
    }
}
