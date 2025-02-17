use crate::data::{
    generate_feature_schema, DataInterface, DataInterfaceMetadata, DataInterfaceSaveMetadata,
    DataLoadKwargs, DataSaveKwargs, SqlLogic,
};
use crate::types::FeatureSchema;
use opsml_error::OpsmlError;
use opsml_types::{DataInterfaceType, DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use scouter_client::DataProfile;
use std::collections::HashMap;
use std::path::Path;
use std::path::PathBuf;

#[pyclass(extends=DataInterface, subclass)]
#[derive(Debug)]
pub struct PandasData {
    #[pyo3(get)]
    pub data: Option<PyObject>,
}

#[pymethods]
impl PandasData {
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
                let pandas = py.import("pandas")?.getattr("DataFrame")?;

                // check if data is a numpy array
                if data.is_instance(&pandas).unwrap() {
                    Some(data.into_py_any(py)?)
                } else {
                    return Err(OpsmlError::new_err("Data must be a pandas dataframe"));
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

        data_interface.data_type = DataType::Pandas;
        data_interface.interface_type = DataInterfaceType::Pandas;

        Ok((PandasData { data }, data_interface))
    }

    #[setter]
    pub fn set_data(&mut self, data: &Bound<'_, PyAny>) -> PyResult<()> {
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
                Err(OpsmlError::new_err("Data must be a pandas DataFrame"))
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
        ))
    }

    #[pyo3(signature = (path, load_kwargs=None))]
    pub fn load_data(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        load_kwargs: Option<DataLoadKwargs>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Parquet);
        let load_kwargs = load_kwargs.unwrap_or_default();
        let pandas = PyModule::import(py, "pandas")?;

        // Load the data using polars
        let data = pandas.call_method("read_parquet", (load_path,), load_kwargs.data_kwargs(py))?;

        self_.set_data(&data)?;

        Ok(())
    }
}

impl PandasData {
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

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Parquet);
        let full_save_path = path.join(&save_path);

        let _ = &self
            .data
            .as_ref()
            .unwrap()
            .call_method(py, "to_parquet", (full_save_path,), kwargs)
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        Ok(save_path)
    }

    pub fn create_feature_schema(&mut self, py: Python) -> PyResult<FeatureSchema> {
        // Create and insert the feature
        let feature_map =
            generate_feature_schema(self.data.as_ref().unwrap().bind(py), &DataType::Pandas)?;

        Ok(feature_map)
    }

    pub fn from_path(
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PyObject> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Parquet);

        let pandas = PyModule::import(py, "pandas")?;

        // Load the data using polars
        let data = pandas.call_method("read_parquet", (load_path,), kwargs)?;

        let interface = PandasData::new(py, Some(&data), None, None, None, None, None)?;

        let bound = Py::new(py, interface)?.as_any().clone_ref(py);

        Ok(bound)
    }
}
