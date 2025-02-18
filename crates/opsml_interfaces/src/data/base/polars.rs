use crate::data::{
    generate_feature_schema, DataInterface, DataInterfaceMetadata, DataInterfaceSaveMetadata,
    DataLoadKwargs, DataSaveKwargs, SqlLogic,
};
use crate::types::FeatureSchema;
use opsml_error::OpsmlError;
use opsml_types::{DataInterfaceType, DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::{IntoPyObjectExt, PyTraverseError, PyVisit};
use scouter_client::{DataProfile, DataProfiler};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

#[pyclass(extends=DataInterface, subclass)]
#[derive(Debug)]
pub struct PolarsData {
    #[pyo3(get)]
    pub data: Option<PyObject>,
}

#[pymethods]
impl PolarsData {
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
                // import polars.DataFrame and check if data is a polars.DataFrame
                let polars = PyModule::import(py, "polars")?;
                let polars_data_frame = polars.getattr("DataFrame")?;

                // check if data is a polars.DataFrame
                if data.is_instance(&polars_data_frame).unwrap() {
                    Some(data.into_py_any(py)?)
                } else {
                    return Err(OpsmlError::new_err("Data must be a polars.DataFrame"));
                }
            }
            None => None,
        };

        let mut data_interface = DataInterface::new(
            py,
            None,
            data_splits,
            dependent_vars,
            feature_map,
            sql_logic,
            data_profile,
        )?;

        data_interface.data_type = DataType::Polars;

        data_interface.interface_type = DataInterfaceType::Polars;

        Ok((PolarsData { data }, data_interface))
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
            let polars = py.import("polars")?.getattr("DataFrame")?;

            // check if data is a numpy array
            if data.is_instance(&polars).unwrap() {
                self.data = Some(data.into_py_any(py)?);
                Ok(())
            } else {
                Err(OpsmlError::new_err("Data must be a polars dataframe"))
            }
        }
    }

    #[pyo3(signature = (path, save_kwargs=None))]
    pub fn save(
        mut self_: PyRefMut<'_, Self>,
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
            self_.as_super().dependent_vars.clone(),
            self_.as_super().data_splits.clone(),
            self_.as_super().data_type.clone(),
        ))
    }

    #[pyo3(signature = (path, load_kwargs=None))]
    pub fn load(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        load_kwargs: Option<DataLoadKwargs>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Parquet);
        let load_kwargs = load_kwargs.unwrap_or_default();

        let polars = PyModule::import(py, "polars")?;

        // Load the data using polars
        let data = polars.call_method("read_parquet", (load_path,), load_kwargs.data_kwargs(py))?;

        self_.set_data(&data)?;

        Ok(())
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

impl PolarsData {
    pub fn from_metadata<'py>(
        py: Python<'py>,
        metadata: &DataInterfaceMetadata,
    ) -> PyResult<Bound<'py, PyAny>> {
        let interface = DataInterface {
            data_type: metadata.data_type.clone(),
            interface_type: metadata.interface_type.clone(),
            schema: metadata.schema.clone(),
            dependent_vars: metadata.dependent_vars.clone(),
            data_splits: metadata.data_splits.clone(),
            sql_logic: metadata.sql_logic.clone(),
            data_profile: None,
            data: None,
        };

        let data_interface = PolarsData { data: None };

        Ok(Py::new(py, (data_interface, interface))?.into_bound_py_any(py)?)
    }

    pub fn save_data(
        &self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        // check if data is None

        if self.data.is_none() {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Data).with_extension(Suffix::Parquet);
        let full_save_path = path.join(&save_path);

        let _ = self
            .data
            .as_ref()
            .unwrap()
            .call_method(py, "write_parquet", (full_save_path,), kwargs)
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        Ok(save_path)
    }

    pub fn create_feature_schema(&mut self, py: Python) -> PyResult<FeatureSchema> {
        // Create and insert the feature
        let feature_map =
            generate_feature_schema(self.data.as_ref().unwrap().bind(py), &DataType::Polars)?;

        Ok(feature_map)
    }

    pub fn from_path(
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PyObject> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Parquet);

        let polars = PyModule::import(py, "polars")?;

        // Load the data using polars
        let data = polars.call_method("read_parquet", (load_path,), kwargs)?;

        let interface = PolarsData::new(py, Some(&data), None, None, None, None, None)?;

        let bound = Py::new(py, interface)?.as_any().clone_ref(py);

        Ok(bound)
    }
}
