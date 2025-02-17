// Tests are in py-opsml/tests/interfaces/data
use crate::data::{
    DataInterface, DataInterfaceMetadata, DataInterfaceSaveMetadata, DataSaveKwargs, SqlLogic,
};
use crate::types::FeatureSchema;
use opsml_error::OpsmlError;
use opsml_types::{DataInterfaceType, DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use scouter_client::DataProfile;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
#[pyclass(extends=DataInterface, subclass)]
#[derive(Debug, Clone)]
pub struct ArrowData {
    #[pyo3(get)]
    pub data: Option<PyObject>,
}

#[pymethods]
impl ArrowData {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (data=None, data_splits=None, dependent_vars=None, schema=None, sql_logic=None, data_profile=None))]
    pub fn new<'py>(
        py: Python,
        data: Option<&Bound<'py, PyAny>>, // data can be any pyobject
        data_splits: Option<&Bound<'py, PyAny>>, //
        dependent_vars: Option<&Bound<'py, PyAny>>,
        schema: Option<FeatureSchema>,
        sql_logic: Option<SqlLogic>,
        data_profile: Option<DataProfile>,
    ) -> PyResult<(Self, DataInterface)> {
        // check if data is a numpy array
        let data = match data {
            Some(data) => {
                // check if data is a numpy array
                // get type name of data
                let pyarrow_table = py.import("pyarrow")?.getattr("Table")?;
                // check if data is a numpy array
                if data.is_instance(&pyarrow_table).unwrap() {
                    data.into_py_any(py)?
                } else {
                    return Err(OpsmlError::new_err("Data must be a pyarrow table"));
                }
            }
            None => None,
        };

        let mut data_interface = DataInterface::new(
            py,
            None,
            data_splits,
            dependent_vars,
            schema,
            sql_logic,
            data_profile,
        )?;

        data_interface.data_type = DataType::Arrow;
        data_interface.data = data;
        data_interface.interface_type = DataInterfaceType::Arrow;

        Ok((ArrowData {}, data_interface))
    }

    #[getter]
    pub fn get_data(self_: PyRef<'_, Self>, py: Python) -> PyObject {
        self_.as_super().data.clone_ref(py)
    }

    #[setter]
    pub fn set_data<'py>(mut self_: PyRefMut<'py, Self>, data: &Bound<'py, PyAny>) -> PyResult<()> {
        let py = data.py();
        let parent = self_.as_super();

        // check if data is None
        if PyAnyMethods::is_none(data) {
            parent.data = py.None();
            Ok(())
        } else {
            // check if data is a numpy array
            // get type name of data
            let pyarrow_table = py.import("pyarrow")?.getattr("Table")?;

            // check if data is a numpy array
            if data.is_instance(&pyarrow_table).unwrap() {
                parent.data = data.into_py_any(py)?;
                Ok(())
            } else {
                Err(OpsmlError::new_err("Data must be a pyarrow table"))
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

        let schema = self_.as_super().create_schema(py)?;
        let sql_uri = self_.as_super().save_sql(path.clone())?;
        let data_profile_uri = if self_.as_super().data_profile.is_none() {
            None
        } else {
            Some(self_.as_super().save_data_profile(&path)?)
        };

        let data_uri = ArrowData::save_data(self_, py, path.clone(), data_kwargs.as_ref())?;

        let save_metadata =
            DataInterfaceSaveMetadata::new(data_uri, sql_uri, data_profile_uri, None, save_kwargs);

        Ok(DataInterfaceMetadata::new(
            save_metadata,
            schema,
            HashMap::new(),
            self_.as_super().sql_logic.clone(),
            self_.as_super().interface_type.clone(),
        ))
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn load_data<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Parquet);

        let parquet = py.import("pyarrow")?.getattr("parquet")?;

        // Load the data using numpy
        let data = parquet.call_method("read_table", (load_path,), kwargs)?;

        self_.as_super().data = data.into();

        Ok(())
    }
}

impl ArrowData {
    pub fn from_path(
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PyObject> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Parquet);

        let parquet = py.import("pyarrow")?.getattr("parquet")?;

        // Load the data using numpy
        let data = parquet.call_method("read_table", (load_path,), kwargs)?;

        let interface = ArrowData::new(py, Some(&data), None, None, None, None, None)?;

        let bound = Py::new(py, interface)?.as_any().clone_ref(py);

        Ok(bound)
    }

    pub fn save_data<'py>(
        &self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<PathBuf> {
        let parent = self_.as_super();
        if parent.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Parquet);
        let full_save_path = path.join(&save_path);

        let parquet = py.import("pyarrow")?.getattr("parquet")?;
        let args = (&parent.data, full_save_path);

        // Save the data using joblib
        parquet
            .call_method("write_table", args, kwargs)
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;
        Ok(save_path)
    }
}
