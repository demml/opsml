use crate::data::{
    check_data_splits, check_dependent_vars, generate_feature_schema, Data, DataInterface,
    DataInterfaceMetadata, DataInterfaceSaveMetadata, DataLoadKwargs, DataSaveKwargs, DataSplit,
    DataSplits, DependentVars, SqlLogic,
};
use crate::error::DataInterfaceError;
use crate::types::FeatureSchema;
use opsml_types::{DataInterfaceType, DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::{IntoPyObjectExt, PyTraverseError, PyVisit};
use scouter_client::{DataProfile, DataProfiler};
use std::collections::HashMap;
use std::path::Path;
use std::path::PathBuf;
use tracing::instrument;

#[pyclass(extends=DataInterface, subclass)]
#[derive(Debug)]
pub struct PandasData {
    #[pyo3(get)]
    pub data: Option<Py<PyAny>>,

    #[pyo3(get)]
    pub data_splits: DataSplits,

    #[pyo3(get)]
    pub dependent_vars: DependentVars,

    #[pyo3(get)]
    pub data_type: DataType,
}

#[pymethods]
impl PandasData {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (data=None, data_splits=None, dependent_vars=None, sql_logic=None, data_profile=None))]
    pub fn new<'py>(
        py: Python,
        data: Option<&Bound<'py, PyAny>>, // data can be any pyobject
        data_splits: Option<&Bound<'py, PyAny>>, //
        dependent_vars: Option<&Bound<'py, PyAny>>,
        sql_logic: Option<SqlLogic>,
        data_profile: Option<DataProfile>,
    ) -> Result<(Self, DataInterface), DataInterfaceError> {
        // check if data is a numpy array
        let data = match data {
            Some(data) => {
                // check if data is a numpy array
                // get type name of data
                let pandas = py.import("pandas")?.getattr("DataFrame")?;

                // check if data is a numpy array
                if data.is_instance(&pandas).unwrap() {
                    Some(data.into_py_any(py)?)
                } else {
                    let type_name = data.get_type().name()?;
                    return Err(DataInterfaceError::PandasTypeError(type_name.to_string()));
                }
            }
            None => None,
        };

        let mut data_interface = DataInterface::new(py, None, None, None, sql_logic, data_profile)?;

        let data_type = DataType::Pandas;
        let data_splits: DataSplits = check_data_splits(data_splits)?;
        let dependent_vars: DependentVars = check_dependent_vars(dependent_vars)?;

        data_interface.interface_type = DataInterfaceType::Pandas;

        Ok((
            PandasData {
                data,
                data_splits,
                dependent_vars,
                data_type,
            },
            data_interface,
        ))
    }

    #[setter]
    pub fn set_data(&mut self, data: &Bound<'_, PyAny>) -> Result<(), DataInterfaceError> {
        let py = data.py();

        // check if data is None
        if PyAnyMethods::is_none(data) {
            self.data = None;
            Ok(())
        } else {
            // check if data is a numpy array
            // get type name of data
            let pandas = py.import("pandas")?.getattr("DataFrame")?;

            // check if data is a numpy array
            if data.is_instance(&pandas).unwrap() {
                self.data = Some(data.into_py_any(py)?);
                Ok(())
            } else {
                let type_name = data.get_type().name()?;
                Err(DataInterfaceError::PandasTypeError(type_name.to_string()))
            }
        }
    }

    #[setter]
    pub fn set_data_splits(
        &mut self,
        data_splits: &Bound<'_, PyAny>,
    ) -> Result<(), DataInterfaceError> {
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
    pub fn set_dependent_vars(
        &mut self,
        dependent_vars: &Bound<'_, PyAny>,
    ) -> Result<(), DataInterfaceError> {
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

    pub fn split_data(&mut self, py: Python) -> Result<HashMap<String, Data>, DataInterfaceError> {
        // check if data is None
        if self.data.is_none() {
            return Err(DataInterfaceError::MissingDataError);
        }

        if self.data_splits.is_empty() {
            return Err(DataInterfaceError::MissingDataSplitsError);
        }

        let dependent_vars = self.dependent_vars.clone();

        self.data_splits.split_data(
            self.data.as_ref().unwrap().bind(py),
            &self.data_type,
            &dependent_vars,
        )
    }

    #[pyo3(signature = (path, save_kwargs=None))]
    #[instrument(skip_all)]
    pub fn save(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        save_kwargs: Option<DataSaveKwargs>,
    ) -> Result<DataInterfaceMetadata, DataInterfaceError> {
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

    #[pyo3(signature = (path, metadata, load_kwargs=None))]
    pub fn load(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Option<DataLoadKwargs>,
    ) -> Result<(), DataInterfaceError> {
        let load_path = path.join(metadata.data_uri);
        let load_kwargs = load_kwargs.unwrap_or_default();
        let pandas = PyModule::import(py, "pandas")?;

        // Load the data using polars
        let data = pandas.call_method("read_parquet", (load_path,), load_kwargs.data_kwargs(py))?;

        self_.set_data(&data)?;

        Ok(())
    }

    #[pyo3(signature = (bin_size=20, compute_correlations=false))]
    pub fn create_data_profile(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        bin_size: usize,
        compute_correlations: bool,
    ) -> Result<DataProfile, DataInterfaceError> {
        let mut profiler = DataProfiler::new();

        // get ScouterDataType from opsml DataType

        let data_type = match self_.data_type {
            DataType::Numpy => Some(&scouter_client::DataType::Numpy),
            DataType::Pandas => Some(&scouter_client::DataType::Pandas),
            DataType::Polars => Some(&scouter_client::DataType::Polars),
            DataType::Arrow => Some(&scouter_client::DataType::Arrow),
            _ => Err(DataInterfaceError::DataTypeNotSupportedForProfilingError)?,
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

impl PandasData {
    pub fn from_metadata<'py>(
        py: Python<'py>,
        metadata: &DataInterfaceMetadata,
    ) -> Result<Bound<'py, PyAny>, DataInterfaceError> {
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

        let data_interface = PandasData {
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
    ) -> Result<PathBuf, DataInterfaceError> {
        // check if data is None
        if self.data.is_none() {
            return Err(DataInterfaceError::MissingDataError);
        }

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Parquet);
        let full_save_path = path.join(&save_path);

        let _ = &self.data.as_ref().unwrap().call_method(
            py,
            "to_parquet",
            (full_save_path,),
            kwargs,
        )?;

        Ok(save_path)
    }

    pub fn create_feature_schema(
        &mut self,
        py: Python,
    ) -> Result<FeatureSchema, DataInterfaceError> {
        // Create and insert the feature
        let feature_map =
            generate_feature_schema(self.data.as_ref().unwrap().bind(py), &DataType::Pandas)?;

        Ok(feature_map)
    }

    pub fn from_path(
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Py<PyAny>, DataInterfaceError> {
        let pandas = PyModule::import(py, "pandas")?;

        // Load the data using polars
        let data = pandas.call_method("read_parquet", (path,), kwargs)?;

        let interface = PandasData::new(py, Some(&data), None, None, None, None)?;

        let bound = Py::new(py, interface)?.as_any().clone_ref(py);

        Ok(bound)
    }
}
