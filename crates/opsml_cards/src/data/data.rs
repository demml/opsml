use crate::{BaseArgs, CardInfo};
use opsml_error::error::OpsmlError;
use pyo3::{intern, prelude::*, IntoPyObjectExt};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DataCardMetadata {
    #[pyo3(get, set)]
    pub interface_type: String,

    #[pyo3(get, set)]
    pub data_type: String,

    #[pyo3(get, set)]
    pub description: Description,

    #[pyo3(get, set)]
    pub feature_map: HashMap<String, Feature>,

    #[pyo3(get, set)]
    pub runcard_uid: Option<String>,

    #[pyo3(get, set)]
    pub pipelinecard_uid: Option<String>,

    #[pyo3(get, set)]
    pub auditcard_uid: Option<String>,
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
        // check if interface is a model interface (should be a bool)
        let is_interface: bool = interface
            .call_method0("is_interface")
            .and_then(|result| {
                result
                    .extract()
                    .map_err(|e| OpsmlError::new_err(e.to_string()))
            })
            .unwrap_or(false);

        if !is_interface {
            return Err(OpsmlError::new_err(
                "Interface is not a data interface".to_string(),
            ));
        }

        let mut metadata = metadata.unwrap_or_default();

        metadata.interface_type = interface
            .getattr(intern!(py, "interface_type"))
            .unwrap()
            .to_string();

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
            CardSQLTableNames::Data,
            self.repository,
            self.name,
            self.version
        )
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
