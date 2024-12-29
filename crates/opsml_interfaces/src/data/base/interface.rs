use crate::data::{self, Data, DataSplit, DataSplits, DataSplitter, DependentVars, SqlLogic};
use crate::types::{Feature, FeatureMap};
use opsml_error::error::OpsmlError;
use opsml_types::{DataType, SaveName, Suffix};
use opsml_utils::FileUtils;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyAnyMethods, PyList};
use pyo3::IntoPyObjectExt;
use std::collections::HashMap;
use std::path::PathBuf;

// TODO add opsml_logging and save_data method

#[pyclass(subclass)]
pub struct DataInterface {
    data: PyObject,

    #[pyo3(get, set)]
    data_splits: DataSplits,

    #[pyo3(get, set)]
    dependent_vars: DependentVars,

    #[pyo3(get, set)]
    feature_map: FeatureMap,

    #[pyo3(get, set)]
    sql_logic: SqlLogic,
}

#[pymethods]
impl DataInterface {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (data=None, data_splits=None, dependent_vars=None, feature_map=None, sql_logic=None))]
    fn new(
        py: Python,
        data: Option<&Bound<'_, PyAny>>, // data can be any pyobject
        data_splits: Option<&Bound<'_, PyAny>>, //
        dependent_vars: Option<&Bound<'_, PyAny>>,
        feature_map: Option<FeatureMap>,
        sql_logic: Option<SqlLogic>,
    ) -> PyResult<Self> {
        // define data splits
        let splits: DataSplits = {
            if let Some(data_splits) = data_splits {
                // check if data_splits is either Vec<DataSplit> or DataSplits
                if data_splits.is_instance_of::<DataSplits>() {
                    data_splits.extract::<DataSplits>()?
                } else if data_splits.is_instance_of::<PyList>() {
                    // pylist should be list of DataSplit
                    DataSplits::new(data_splits.extract::<Vec<DataSplit>>()?)
                } else {
                    DataSplits::default()
                }
            } else {
                DataSplits::default()
            }
        };

        // define dependent vars
        let depen_vars: DependentVars = {
            if let Some(dependent_vars) = dependent_vars {
                // check if dependent_vars is either DependentVars or Vec<String>, Vec<usize> or DependentVars
                if dependent_vars.is_instance_of::<DependentVars>() {
                    dependent_vars.extract::<DependentVars>()?
                } else if dependent_vars.is_instance_of::<PyList>() {
                    // pylist should be list of string or list of int
                    if dependent_vars.extract::<Vec<String>>().is_ok() {
                        let column_names = dependent_vars.extract::<Vec<String>>()?;
                        DependentVars::new(Some(column_names), None)
                    } else if dependent_vars.extract::<Vec<usize>>().is_ok() {
                        let column_indices = dependent_vars.extract::<Vec<usize>>()?;
                        DependentVars::new(None, Some(column_indices))
                    } else {
                        DependentVars::default()
                    }
                } else {
                    DependentVars::default()
                }
            } else {
                DependentVars::default()
            }
        };

        let feature_map = feature_map.unwrap_or_default();
        let sql_logic = sql_logic.unwrap_or_default();

        let data = match data {
            Some(data) => data.into_py_any(py)?,
            None => py.None(),
        };
        Ok(DataInterface {
            data,
            data_splits: splits,
            dependent_vars: depen_vars,
            feature_map,
            sql_logic,
        })
    }

    #[getter]
    pub fn data(&mut self) -> &PyObject {
        &self.data
    }

    #[setter]
    pub fn set_data(&mut self, data: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = data.py();

        // check if data is None
        if PyAnyMethods::is_none(data) {
            self.data = py.None();
            return Ok(());
        } else {
            self.data = data.into_py_any(py)?;
        };

        Ok(())
    }
    pub fn save_data(&mut self, py: Python, path: PathBuf) -> PyResult<()> {
        // check if data is None
        if self.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        let save_path = path.join(SaveName::Data).with_extension(Suffix::Joblib);

        let joblib = py.import("joblib")?;

        // Save the data using joblib
        joblib.call_method1("dump", (&self.data, save_path))?;

        // Get the class name of self.data
        let name: String = self
            .data
            .getattr(py, "__class__")?
            .getattr(py, "__name__")?
            .extract(py)?;

        // Create and insert the feature
        let mut features = HashMap::new();
        features.insert("features".to_string(), Feature::new(name, vec![1], None));
        self.feature_map = features;

        Ok(())
    }

    pub fn load_data(&mut self, py: Python, path: PathBuf) -> PyResult<()> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Joblib);
        let joblib = py.import("joblib")?;

        // Load the data using joblib
        self.data = joblib.call_method1("load", (load_path,))?.into();

        Ok(())
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
        self.sql_logic.add_sql_logic(name, query, filepath)?;

        Ok(())
    }

    pub fn split_data(&mut self, py: Python) -> PyResult<HashMap<String, Data>> {
        // check if data is None
        if self.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        if self.data_splits.is_empty() {
            return Err(OpsmlError::new_err(
                "No data splits detected in interface for splitting",
            ));
        }

        let dependent_vars = self.dependent_vars.clone();
        let splits = self
            .data_splits
            .iter()
            .map(|split| {
                let data = DataSplitter::split_data(
                    split,
                    self.data.bind(py),
                    &self.data_type(),
                    dependent_vars.clone(),
                )
                .expect("Failed to split data");
                (split.label.clone(), data)
            })
            .collect::<HashMap<String, Data>>();

        Ok(splits)
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
