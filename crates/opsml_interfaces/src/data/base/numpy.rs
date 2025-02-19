use crate::data::Data;

use crate::data::{
    check_data_splits, check_dependent_vars, generate_feature_schema, DataInterface,
    DataInterfaceMetadata, DataInterfaceSaveMetadata, DataLoadKwargs, DataSaveKwargs, DataSplit,
    DataSplits, DependentVars, SqlLogic,
};
use crate::types::FeatureSchema;
use opsml_error::OpsmlError;
use opsml_types::{DataInterfaceType, DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::{IntoPyObjectExt, PyTraverseError, PyVisit};
use scouter_client::{DataProfile, DataProfiler};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

#[pyclass(extends=DataInterface, subclass)]
#[derive(Debug)]
pub struct NumpyData {
    #[pyo3(get)]
    pub data: Option<PyObject>,

    #[pyo3(get)]
    pub data_splits: DataSplits,

    #[pyo3(get)]
    pub dependent_vars: DependentVars,

    #[pyo3(get)]
    pub data_type: DataType,
}

#[pymethods]
impl NumpyData {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (data=None, data_splits=None, dependent_vars=None, feature_map=None, sql_logic=None, data_profile=None))]
    pub fn new<'py>(
        py: Python,
        data: Option<&Bound<'py, PyAny>>, // data can be any pyobject
        data_splits: Option<&Bound<'py, PyAny>>, //
        dependent_vars: Option<&Bound<'py, PyAny>>,
        feature_map: Option<FeatureSchema>,
        sql_logic: Option<SqlLogic>,
        data_profile: Option<DataProfile>,
    ) -> PyResult<(Self, DataInterface)> {
        // check if data is a numpy array
        let data = match data {
            Some(data) => {
                // check if data is a numpy array
                // get type name of data
                let numpy = py.import("numpy")?.getattr("ndarray")?;
                // check if data is a numpy array
                if data.is_instance(&numpy).unwrap() {
                    Some(data.into_py_any(py)?)
                } else {
                    return Err(OpsmlError::new_err("Data must be a numpy array"));
                }
            }
            None => None,
        };

        let mut data_interface =
            DataInterface::new(py, None, None, None, feature_map, sql_logic, data_profile)?;

        let data_type = DataType::Numpy;
        let data_splits: DataSplits = check_data_splits(data_splits)?;
        let dependent_vars: DependentVars = check_dependent_vars(dependent_vars)?;

        data_interface.interface_type = DataInterfaceType::Numpy;

        Ok((
            NumpyData {
                data,
                data_splits,
                dependent_vars,
                data_type,
            },
            data_interface,
        ))
    }

    #[setter]
    #[allow(clippy::needless_lifetimes)]
    pub fn set_data(&mut self, data: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = data.py();

        // check if data is None
        if PyAnyMethods::is_none(data) {
            self.data = None;
            Ok(())
        } else {
            // check if data is a numpy array
            // get type name of data
            let numpy = py.import("numpy")?.getattr("ndarray")?;

            // check if data is a numpy array
            if data.is_instance(&numpy).unwrap() {
                self.data = Some(data.into_py_any(py)?);
                Ok(())
            } else {
                Err(OpsmlError::new_err("Data must be a numpy array"))
            }
        }
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

    #[pyo3(signature = (path, save_kwargs=None))]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        save_kwargs: Option<DataSaveKwargs>,
    ) -> PyResult<DataInterfaceMetadata> {
        let data_kwargs = save_kwargs
            .as_ref()
            .and_then(|args| args.data_kwargs(py))
            .cloned();

        self_.as_super().schema = self_.create_feature_schema(py)?;
        let sql_uri = self_.as_super().save_sql(path.clone())?;
        let data_profile_uri = if self_.as_super().data_profile.is_none() {
            None
        } else {
            Some(self_.as_super().save_data_profile(&path)?)
        };
        let data_uri = self_.save_data(py, path.clone(), data_kwargs.as_ref())?;

        let save_metadata =
            DataInterfaceSaveMetadata::new(data_uri, sql_uri, data_profile_uri, None, save_kwargs);

        Ok(DataInterfaceMetadata::new(
            save_metadata,
            self_.as_super().schema.clone(),
            HashMap::new(),
            self_.as_super().sql_logic.clone(),
            self_.as_super().interface_type.clone(),
            self_.dependent_vars.clone(),
            self_.data_splits.clone(),
            self_.data_type.clone(),
        ))
    }

    #[pyo3(signature = (path, load_kwargs=None))]
    pub fn load(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        load_kwargs: Option<DataLoadKwargs>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Numpy);
        let load_kwargs = load_kwargs.unwrap_or_default();

        let numpy = PyModule::import(py, "numpy")?;

        // Load the data using numpy
        let data = numpy.call_method("load", (load_path,), load_kwargs.data_kwargs(py))?;

        self_.set_data(&data)?;

        Ok(())
    }

    pub fn split_data(&mut self, py: Python) -> PyResult<HashMap<String, Data>> {
        // check if data is None
        if self.data.is_none() {
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

        self.data_splits.split_data(
            self.data.as_ref().unwrap().bind(py),
            &self.data_type,
            &dependent_vars,
        )
    }

    #[pyo3(signature = (bin_size=20, compute_correlations=false))]
    pub fn create_data_profile(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        bin_size: Option<usize>,
        compute_correlations: Option<bool>,
    ) -> PyResult<DataProfile> {
        let mut profiler = DataProfiler::new();

        // get ScouterDataType from opsml DataType

        let data_type = match self_.as_super().data_type {
            DataType::Numpy => Some(&scouter_client::DataType::Numpy),
            DataType::Pandas => Some(&scouter_client::DataType::Pandas),
            DataType::Polars => Some(&scouter_client::DataType::Polars),
            DataType::Arrow => Some(&scouter_client::DataType::Arrow),
            _ => Err(OpsmlError::new_err("Data type not supported for profiling"))?,
        };

        let profile = profiler.create_data_profile(
            py,
            self_.data.as_ref().unwrap().bind(py),
            data_type,
            bin_size,
            compute_correlations,
        )?;

        self_.as_super().data_profile = Some(profile.clone());

        Ok(profile)
    }

    fn __traverse__(&self, visit: PyVisit) -> Result<(), PyTraverseError> {
        if let Some(ref data) = self.data {
            visit.call(data)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.data = None;
    }
}

impl NumpyData {
    pub fn from_metadata<'py>(
        py: Python<'py>,
        metadata: &DataInterfaceMetadata,
    ) -> PyResult<Bound<'py, PyAny>> {
        let interface = DataInterface {
            data_type: metadata.data_type.clone(),
            interface_type: metadata.interface_type.clone(),
            schema: metadata.schema.clone(),
            dependent_vars: DependentVars::default(),
            data_splits: DataSplits::default(),
            sql_logic: metadata.sql_logic.clone(),
            data_profile: None,
            data: None,
        };

        let data_interface = NumpyData {
            data: None,
            data_splits: metadata.data_splits.clone(),
            dependent_vars: metadata.dependent_vars.clone(),
            data_type: metadata.data_type.clone(),
        };

        Ok(Py::new(py, (data_interface, interface))?.into_bound_py_any(py)?)
    }

    pub fn save_data(
        &self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        if self.data.is_none() {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Numpy);
        let full_save_path = path.join(&save_path);

        let numpy = py.import("numpy")?;
        let args = (full_save_path, self.data.as_ref().unwrap());

        // Save the data using joblib
        numpy
            .call_method("save", args, kwargs)
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        Ok(save_path)
    }

    pub fn create_feature_schema(&mut self, py: Python) -> PyResult<FeatureSchema> {
        // Create and insert the feature
        let feature_map =
            generate_feature_schema(self.data.as_ref().unwrap().bind(py), &DataType::Numpy)?;

        Ok(feature_map)
    }

    pub fn from_path(
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PyObject> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Numpy);

        let numpy = PyModule::import(py, "numpy")?;

        // Load the data using numpy
        let data = numpy.call_method("load", (load_path,), kwargs)?;

        let interface = NumpyData::new(py, Some(&data), None, None, None, None, None)?;

        let bound = Py::new(py, interface)?.as_any().clone_ref(py);

        Ok(bound)
    }
}
