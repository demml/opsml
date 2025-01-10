use crate::model::ModelInterfaceSaveMetadata;
use opsml_error::error::OpsmlError;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

//#[pyclass]
//#[derive(Debug, Serialize, Deserialize, Clone)]
//pub enum ModelSaveMetadata {
//    Base(ModelDataInterfaceSaveMetadata),
//}
//
//#[pymethods]
//impl ModelSaveMetadata {
//    #[new]
//    #[pyo3(signature = (save_args))]
//    pub fn new(save_args: &Bound<'_, PyAny>) -> PyResult<Self> {
//        if save_args.is_instance_of::<ModelDataInterfaceSaveMetadata>() {
//            let args: ModelDataInterfaceSaveMetadata = save_args.extract().map_err(|e| {
//                OpsmlError::new_err(format!("Failed to extract ModelInterfaceArgs: {}", e))
//            })?;
//            Ok(ModelSaveMetadata::Base(args))
//        } else {
//            Err(OpsmlError::new_err("Invalid ModelInterfaceArgs type"))
//        }
//    }
//
//    pub fn type_name(&self) -> &str {
//        match self {
//            ModelSaveMetadata::Base(_) => "Base",
//        }
//    }
//}
