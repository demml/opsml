use crate::{BaseArgs, CardInfo, Description};
use opsml_error::error::OpsmlError;
use opsml_interfaces::data::DataInterfaceSaveMetadata;
use opsml_interfaces::FeatureSchema;
use opsml_types::{
    cards::{CardTable, CardType},
    DataType, InterfaceType,
};
use pyo3::types::PyDict;
use pyo3::{prelude::*, IntoPyObjectExt};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DataCardMetadata {
    #[pyo3(get, set)]
    pub data_type: DataType,

    #[pyo3(get, set)]
    pub description: Description,

    #[pyo3(get, set)]
    pub feature_map: FeatureSchema,

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
    #[pyo3(signature = (data_type, description=None, feature_map=None, runcard_uid=None, pipelinecard_uid=None, auditcard_uid=None))]
    pub fn new(
        data_type: DataType,
        description: Option<Description>,
        feature_map: Option<FeatureSchema>,
        runcard_uid: Option<String>,
        pipelinecard_uid: Option<String>,
        auditcard_uid: Option<String>,
    ) -> Self {
        Self {
            data_type,
            description: description.unwrap_or_default(),
            feature_map: feature_map.unwrap_or_default(),
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
    pub interface: PyObject,

    #[pyo3(get, set)]
    pub name: String,

    #[pyo3(get, set)]
    pub repository: String,

    #[pyo3(get, set)]
    pub contact: String,

    #[pyo3(get, set)]
    pub version: String,

    #[pyo3(get, set)]
    pub uid: String,

    #[pyo3(get, set)]
    pub tags: HashMap<String, String>,

    #[pyo3(get, set)]
    pub metadata: DataCardMetadata,

    #[pyo3(get)]
    pub card_type: CardType,
}

#[pymethods]
impl DataCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (interface, name=None, repository=None, contact=None, version=None, uid=None, info=None, tags=None, metadata=None))]
    pub fn new(
        interface: &Bound<'_, PyAny>,
        name: Option<String>,
        repository: Option<String>,
        contact: Option<String>,
        version: Option<String>,
        uid: Option<String>,
        info: Option<CardInfo>,
        tags: Option<HashMap<String, String>>,
        metadata: Option<DataCardMetadata>,
    ) -> PyResult<Self> {
        let base_args = BaseArgs::new(
            name,
            repository,
            contact,
            version,
            uid,
            info,
            tags.unwrap_or_default(),
        )?;

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
            data_type, None, None, None, None, None,
        ));

        Ok(Self {
            interface: interface
                .into_py_any(py)
                .map_err(|e| OpsmlError::new_err(e.to_string()))?,
            name: base_args.name,
            repository: base_args.repository,
            contact: base_args.contact,
            version: base_args.version,
            uid: base_args.uid,
            tags: base_args.tags,
            metadata,
            card_type: CardType::Data,
        })
    }

    #[getter]
    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardTable::Data,
            self.repository,
            self.name,
            self.version
        )
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save(
        &self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<DataInterfaceSaveMetadata> {
        let args = (path,);

        // call save on interface
        let metadata = self
            .interface
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
            interface: interface.into(),
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
