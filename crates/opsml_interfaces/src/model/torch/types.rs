use opsml_error::error::OpsmlError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[pyclass]
#[derive(Debug, Deserialize, Serialize, Clone)]
#[allow(dead_code)]
pub struct TorchOnnxArgs {
    #[pyo3(get)]
    pub input_names: Vec<String>,

    #[pyo3(get)]
    pub output_names: Vec<String>,

    #[pyo3(get)]
    pub dynamic_axes: Option<HashMap<String, HashMap<usize, String>>>,

    #[pyo3(get)]
    pub do_constant_folding: bool,

    #[pyo3(get)]
    pub export_params: bool,

    #[pyo3(get)]
    pub verbose: bool,
}

#[pymethods]
impl TorchOnnxArgs {
    #[new]
    #[pyo3(signature = (input_names, output_names, dynamic_axes=None, do_constant_folding=true, export_params=true, verbose=true))]
    pub fn new(
        input_names: Vec<String>,
        output_names: Vec<String>,
        dynamic_axes: Option<HashMap<String, HashMap<usize, String>>>,
        do_constant_folding: bool,
        export_params: bool,
        verbose: bool,
    ) -> Self {
        TorchOnnxArgs {
            input_names,
            output_names,
            dynamic_axes,
            do_constant_folding,
            export_params,
            verbose,
        }
    }

    pub fn model_dump(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("input_names", self.input_names.clone())
            .map_err(|_| OpsmlError::new_err("Failed to set input_names"))?;
        dict.set_item("output_names", self.output_names.clone())
            .map_err(|_| OpsmlError::new_err("Failed to set output_names"))?;
        dict.set_item("dynamic_axes", self.dynamic_axes.clone())
            .map_err(|_| OpsmlError::new_err("Failed to set dynamic_axes"))?;
        dict.set_item("do_constant_folding", self.do_constant_folding)
            .map_err(|_| OpsmlError::new_err("Failed to set do_constant_folding"))?;
        dict.set_item("export_params", self.export_params)
            .map_err(|_| OpsmlError::new_err("Failed to set export_params"))?;
        dict.set_item("verbose", self.verbose)
            .map_err(|_| OpsmlError::new_err("Failed to set verbose"))?;
        dict.into_py_any(py)
    }
}

#[pyclass]
#[derive(Debug, Deserialize, Serialize, Clone)]
#[allow(dead_code)]
pub struct TorchSaveArgs {
    #[pyo3(get)]
    pub as_state_dict: bool,
}

#[pymethods]
impl TorchSaveArgs {
    #[new]
    #[pyo3(signature = (as_state_dict=false))]
    pub fn new(as_state_dict: Option<bool>) -> Self {
        TorchSaveArgs {
            as_state_dict: as_state_dict.unwrap_or(false),
        }
    }
}
