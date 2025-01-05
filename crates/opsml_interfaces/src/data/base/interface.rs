use crate::data::{Data, DataSplit, DataSplits, DependentVars, InterfaceSaveMetadata, SqlLogic};
use crate::types::{Feature, FeatureMap};
use opsml_error::error::OpsmlError;
use opsml_types::{DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::types::{PyAny, PyAnyMethods, PyList};
use pyo3::IntoPyObjectExt;
use std::collections::HashMap;
use std::path::PathBuf;

//TODO: add data_profile

#[pyclass(subclass)]
pub struct DataInterface {
    #[pyo3(get)]
    pub data: PyObject,

    #[pyo3(get)]
    pub data_splits: DataSplits,

    #[pyo3(get)]
    pub dependent_vars: DependentVars,

    #[pyo3(get, set)]
    pub feature_map: FeatureMap,

    #[pyo3(get, set)]
    pub sql_logic: SqlLogic,

    #[pyo3(get)]
    pub data_type: DataType,
}

#[pymethods]
impl DataInterface {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (data=None, data_splits=None, dependent_vars=None, feature_map=None, sql_logic=None))]
    pub fn new<'py>(
        py: Python,
        data: Option<&Bound<'py, PyAny>>, // data can be any pyobject
        data_splits: Option<&Bound<'py, PyAny>>, //
        dependent_vars: Option<&Bound<'py, PyAny>>,
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
            data_type: DataType::Base,
        })
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

    #[setter]
    pub fn set_data_splits(&mut self, data_splits: &Bound<'_, PyAny>) -> PyResult<()> {
        // check if data_splits is None
        if PyAnyMethods::is_none(data_splits) {
            self.data_splits = DataSplits::default();
            return Ok(());
        }

        // check if data_splits is either Vec<DataSplit> or DataSplits
        if data_splits.is_instance_of::<DataSplits>() {
            self.data_splits = data_splits.extract::<DataSplits>()?;
        } else if data_splits.is_instance_of::<PyList>() {
            // pylist should be list of DataSplit
            self.data_splits = DataSplits::new(data_splits.extract::<Vec<DataSplit>>()?);
        } else {
            self.data_splits = DataSplits::default();
        }

        Ok(())
    }

    #[setter]
    pub fn set_dependent_vars(&mut self, dependent_vars: &Bound<'_, PyAny>) -> PyResult<()> {
        // check if dependent_vars is None
        if PyAnyMethods::is_none(dependent_vars) {
            self.dependent_vars = DependentVars::default();
            return Ok(());
        }

        // check if dependent_vars is either DependentVars or Vec<String>, Vec<usize> or DependentVars
        if dependent_vars.is_instance_of::<DependentVars>() {
            self.dependent_vars = dependent_vars.extract::<DependentVars>()?;
        } else if dependent_vars.is_instance_of::<PyList>() {
            // pylist should be list of string or list of int
            if dependent_vars.extract::<Vec<String>>().is_ok() {
                let column_names = dependent_vars.extract::<Vec<String>>()?;
                self.dependent_vars = DependentVars::new(Some(column_names), None);
            } else if dependent_vars.extract::<Vec<usize>>().is_ok() {
                let column_indices = dependent_vars.extract::<Vec<usize>>()?;
                self.dependent_vars = DependentVars::new(None, Some(column_indices));
            } else {
                self.dependent_vars = DependentVars::default();
            }
        } else {
            self.dependent_vars = DependentVars::default();
        }

        Ok(())
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save_data(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<InterfaceSaveMetadata> {
        // check if data is None
        if self.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Joblib);
        let full_save_path = path.join(&save_path);
        let joblib = py.import("joblib")?;

        // Save the data using joblib
        joblib.call_method("dump", (&self.data, full_save_path), kwargs)?;

        // Get the class name of self.data
        let name: String = self
            .data
            .getattr(py, "__class__")?
            .getattr(py, "__name__")?
            .extract(py)?;

        // Create and insert the feature
        let mut features = HashMap::new();
        features.insert("features".to_string(), Feature::new(name, vec![1], None));
        self.feature_map = FeatureMap::new(Some(features));

        Ok(InterfaceSaveMetadata {
            data_type: self.data_type.clone(),
            feature_map: self.feature_map.clone(),
            data_save_path: save_path,
            data_profile_save_path: None,
        })
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn load_data<'py>(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Joblib);
        let joblib = py.import("joblib")?;

        // Load the data using joblib
        self.data = joblib.call_method("load", (load_path,), kwargs)?.into();

        Ok(())
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

        self.data_splits
            .split_data(self.data.bind(py), &self.data_type, &dependent_vars)
    }
}
