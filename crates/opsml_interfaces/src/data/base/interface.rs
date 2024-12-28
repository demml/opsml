use crate::data::DataSplit;
use crate::types::Feature;
use opsml_error::error::OpsmlError;
use pyo3::prelude::*;
use pyo3::IntoPyObjectExt;
use std::collections::HashMap;

#[pyclass(subclass)]
struct DataInterface {
    #[pyo3(get)]
    data: PyObject,

    #[pyo3(get)]
    data_splits: Vec<DataSplit>,

    #[pyo3(get)]
    dependent_vars: Vec<String>,

    #[pyo3(get)]
    feature_map: HashMap<String, Feature>,

    #[pyo3(get)]
    sql_logic: HashMap<String, String>,
}

#[pymethods]
impl DataInterface {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (data, data_splits, dependent_vars, feature_map, sql_logic))]
    fn new(
        data: &Bound<'_, PyAny>,
        data_splits: Vec<DataSplit>,
        dependent_vars: Vec<String>,
        feature_map: HashMap<String, Feature>,
        sql_logic: HashMap<String, String>,
    ) -> PyResult<Self> {
        let py = data.py();

        Ok(DataInterface {
            data: data.into_py_any(py).map_err(|e| OpsmlError::new_err(e))?,
            data_splits,
            dependent_vars,
            feature_map,
            sql_logic,
        })
    }
}
