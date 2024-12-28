use crate::data::DataSplit;
use crate::types::Feature;
use opsml_error::error::OpsmlError;
use opsml_types::DataType;
use opsml_utils::FileUtils;
use pyo3::prelude::*;
use pyo3::IntoPyObjectExt;
use std::collections::HashMap;
use std::path::PathBuf;


// TODO add opsml_logging and save_data method

#[pyclass(subclass)]
pub struct DataInterface {
    #[pyo3(get, set)]
    data: Option<PyObject>,

    #[pyo3(get, set)]
    data_splits: Vec<DataSplit>,

    #[pyo3(get, set)]
    dependent_vars: Vec<String>,

    #[pyo3(get, set)]
    feature_map: HashMap<String, Feature>,

    #[pyo3(get, set)]
    sql_logic: HashMap<String, String>,
}

#[pymethods]
impl DataInterface {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (data=None, data_splits=None, dependent_vars=None, feature_map=None, sql_logic=None))]
    fn new(
        data: Option<&Bound<'_, PyAny>>,
        data_splits: Option<Vec<DataSplit>>,
        dependent_vars: Option<Vec<String>>,
        feature_map: Option<HashMap<String, Feature>>,
        sql_logic: Option<HashMap<String, String>>,
    ) -> PyResult<Self> {
        let data_splits = data_splits.unwrap_or_default();
        let dependent_vars = dependent_vars.unwrap_or_default();
        let feature_map = feature_map.unwrap_or_default();
        let sql_logic = DataInterface::extract_sql_logic(sql_logic.unwrap_or_default())?;

        Ok(DataInterface {
            data: data.map(|d| {
                d.into_py_any(d.py())
                    .map_err(|e| OpsmlError::new_err(e.to_string()))
                    .unwrap()
            }),
            data_splits,
            dependent_vars,
            feature_map,
            sql_logic,
        })
    }

    pub fn save_data(&self, path: PathBuf) -> PyResult<()> {
        // if data is not present, return OK
        if self.data.is_none() {
            tr
            return Ok(());
        }
    }

    #[getter]
    pub fn data_type(&self) -> DataType {
        DataType::Base
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
            self.sql_logic.insert(name, query);
        } else {
            let query = FileUtils::open_file(&filepath)?;
            self.sql_logic.insert(name, query);
        }

        Ok(())
    }
}

impl DataInterface {
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
