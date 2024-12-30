use opsml_error::OpsmlError;
use opsml_utils::{FileUtils, PyHelperFuncs};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct DependentVars {
    #[pyo3(get, set)]
    pub column_names: Vec<String>,

    #[pyo3(get, set)]
    pub column_indices: Vec<usize>,

    pub is_idx: bool,
}

#[pymethods]
impl DependentVars {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (column_names=None, column_indices=None))]
    pub fn new(column_names: Option<Vec<String>>, column_indices: Option<Vec<usize>>) -> Self {
        let column_names = column_names.unwrap_or_default();
        let column_indices = column_indices.unwrap_or_default();

        let is_idx = !column_indices.is_empty();

        DependentVars {
            column_names,
            column_indices,
            is_idx,
        }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

impl DependentVars {
    pub fn get_column_indices(&self) -> Vec<usize> {
        self.column_indices.clone()
    }

    pub fn column_empty(&self) -> bool {
        self.column_names.is_empty()
    }

    pub fn idx_empty(&self) -> bool {
        self.column_indices.is_empty()
    }
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct SqlLogic {
    #[pyo3(get, set)]
    pub queries: HashMap<String, String>,
}

#[pymethods]
impl SqlLogic {
    #[new]
    #[pyo3(signature = (queries=None))]
    pub fn new(queries: Option<HashMap<String, String>>) -> PyResult<Self> {
        Ok(SqlLogic {
            queries: SqlLogic::extract_sql_logic(queries.unwrap_or_default())?,
        })
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    #[pyo3(signature = (name, query=None, filepath=None))]
    pub fn add_sql_logic(
        &mut self,
        name: String,
        query: Option<String>,
        filepath: Option<String>,
    ) -> PyResult<()> {
        let query = query.unwrap_or_default();
        let filepath = filepath.unwrap_or_default();

        if !query.is_empty() && !filepath.is_empty() {
            return Err(OpsmlError::new_err(
                "Only one of query or filename can be provided",
            ));
        }

        if !query.is_empty() {
            self.queries.insert(name, query);
        } else {
            let query = FileUtils::open_file(&filepath)?;
            self.queries.insert(name, query);
        }

        Ok(())
    }

    pub fn __getitem__(&self, key: &str) -> PyResult<String> {
        match self.queries.get(key) {
            Some(query) => Ok(query.clone()),
            None => Err(OpsmlError::new_err("Key not found")),
        }
    }
}

impl SqlLogic {
    fn extract_sql_logic(sql_logic: HashMap<String, String>) -> PyResult<HashMap<String, String>> {
        // check if sql logic is present
        if sql_logic.is_empty() {
            return Ok(sql_logic);
        }

        // get the sql logic
        let sql_logic = sql_logic
            .iter()
            .map(|(key, value)| {
                if value.contains(".sql") {
                    let sql = FileUtils::open_file(value)?;
                    Ok((key.clone(), sql))
                } else {
                    Ok((key.clone(), value.clone()))
                }
            })
            .collect::<PyResult<HashMap<String, String>>>()?;

        Ok(sql_logic)
    }
}
