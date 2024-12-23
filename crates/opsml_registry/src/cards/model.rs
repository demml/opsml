use crate::cards::*;
use opsml_error::error::{CardError, OpsmlError};
use opsml_types::*;
use pyo3::prelude::*;
use pyo3::{intern, IntoPyObjectExt, PyObject};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ModelCardMetadata {
    #[pyo3(get, set)]
    pub interface_type: ModelInterfaceType,

    #[pyo3(get, set)]
    pub description: Description,

    #[pyo3(get, set)]
    pub data_schema: DataSchema,

    #[pyo3(get, set)]
    pub datacard_uid: Option<String>,

    #[pyo3(get, set)]
    pub runcard_uid: Option<String>,

    #[pyo3(get, set)]
    pub pipelinecard_uid: Option<String>,

    #[pyo3(get, set)]
    pub auditcard_uid: Option<String>,
}

#[pyclass]
#[derive(Debug)]
pub struct ModelCard {
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
    pub metadata: ModelCardMetadata,

    #[pyo3(get)]
    pub card_type: CardType,

    #[pyo3(get)]
    pub to_onnx: bool,
}

#[pymethods]
impl ModelCard {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (interface, name=None, repository=None, contact=None, version=None, uid=None, info=None, tags=None, metadata=None, to_onnx=None))]
    pub fn new(
        interface: &Bound<'_, PyAny>,
        name: Option<String>,
        repository: Option<String>,
        contact: Option<String>,
        version: Option<String>,
        uid: Option<String>,
        info: Option<CardInfo>,
        tags: Option<HashMap<String, String>>,
        metadata: Option<ModelCardMetadata>,
        to_onnx: Option<bool>,
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
                "Interface argument is not a model interface".to_string(),
            ));
        }
        let mut metadata = metadata.unwrap_or_default();
        metadata.interface_type = interface
            .getattr(intern!(py, "interface_type"))
            .unwrap()
            .extract()?;

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
            metadata: metadata,
            card_type: CardType::Model,
            to_onnx: to_onnx.unwrap_or(false),
        })
    }

    #[getter]
    pub fn uri(&self) -> String {
        format!(
            "{}/{}/{}/v{}",
            CardSQLTableNames::Model,
            self.repository,
            self.name,
            self.version
        )
    }
}

impl ModelCard {
    pub fn set_uid(&mut self, py: Python, uid: &str) -> Result<(), CardError> {
        self.interface
            .setattr(py, intern!(py, "modelcard_uid"), uid)
            .map_err(|e| CardError::Error(e.to_string()))?;

        self.uid = uid.to_string();

        Ok(())
    }
}

impl FromPyObject<'_> for ModelCard {
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
        let to_onnx = ob.getattr("to_onnx")?.extract()?;

        Ok(ModelCard {
            interface: interface.into(),
            name,
            repository,
            contact,
            version,
            uid,
            tags,
            metadata,
            card_type,
            to_onnx,
        })
    }
}

//impl ModelCard {
//    pub fn serialize(&self) -> Result<(), CardError> {
//        Python::with_gil(|py| {
//            let obj = &self.interface;
//
//            // Create the exclude dictionary
//            let exclude_dict = PyDict::new(py);
//            let exclude_set = PySet::new(
//                py,
//                &[
//                    "model",
//                    "preprocessor",
//                    "sample_data",
//                    "onnx_model",
//                    "feature_extractor",
//                    "tokenizer",
//                    "drift_profile",
//                ],
//            )
//            .map_err(|e| CardError::Error(e.to_string()))?;
//            exclude_dict
//                .set_item("exclude", exclude_set)
//                .map_err(|e| CardError::Error(e.to_string()))?;
//
//            // Call the model_dump method with the exclude argument
//            let result = obj
//                .call_method(py, "model_dump", (), Some(&exclude_dict))
//                .map_err(|e| {
//                    CardError::Error(format!(
//                        "Error calling model_dump method on interface: {}",
//                        e
//                    ))
//                })?;
//
//            // cast to pydict
//            let dumped_interface = result
//                .downcast_bound::<PyDict>(py)
//                .map_err(|e| CardError::Error(e.to_string()))?;
//
//            if let Ok(Some(onnx_args)) = dumped_interface.get_item("onnx_args") {
//                let args = onnx_args
//                    .downcast::<PyDict>()
//                    .map_err(|e| CardError::Error(e.to_string()))?;
//
//                // check if config in args. if it is, pop it
//                if let Ok(Some(_)) = args.get_item("config") {
//                    args.del_item("config")
//                        .map_err(|e| CardError::Error(e.to_string()))?;
//                }
//            }
//
//            println!("{:?}", result); // Print the result for debugging
//
//            Ok(())
//        })
//    }
//}
