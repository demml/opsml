use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DependentVars {
    #[pyo3(get, set)]
    pub column_names: Vec<String>,

    #[pyo3(get, set)]
    pub column_indices: Vec<usize>,
}

#[pymethods]
impl DependentVars {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (column_names=None, column_indices=None))]
    fn new(column_names: Option<Vec<String>>, column_indices: Option<Vec<usize>>) -> Self {
        let column_names = column_names.unwrap_or_default();
        let column_indices = column_indices.unwrap_or_default();
        DependentVars {
            column_names,
            column_indices,
        }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}
