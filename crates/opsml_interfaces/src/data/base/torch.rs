use crate::data::{DataInterface, DataInterfaceSaveMetadata, SqlLogic};
use crate::types::FeatureSchema;
use opsml_error::OpsmlError;
use opsml_types::{DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use scouter_client::DataProfile;
use std::path::{Path, PathBuf};

#[pyclass(extends=DataInterface, subclass)]
pub struct TorchData {}

#[pymethods]
impl TorchData {
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
                let tensor = py.import("torch")?.getattr("Tensor")?;
                // check if data is a numpy array
                if data.is_instance(&tensor).unwrap() {
                    data.into_py_any(py)?
                } else {
                    return Err(OpsmlError::new_err("Data must be a Torch tensor"));
                }
            }
            None => py.None(),
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

        data_interface.data_type = DataType::TorchTensor;
        data_interface.data = data;

        Ok((TorchData {}, data_interface))
    }

    #[getter]
    pub fn get_data(self_: PyRef<'_, Self>, py: Python) -> PyObject {
        self_.as_super().data.clone_ref(py)
    }

    #[setter]
    #[allow(clippy::needless_lifetimes)]
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
            let tensor = py.import("torch")?.getattr("Tensor")?;

            // check if data is a numpy array
            if data.is_instance(&tensor).unwrap() {
                parent.data = data.into_py_any(py)?;
                Ok(())
            } else {
                Err(OpsmlError::new_err("Data must be a torch tensor"))
            }
        }
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save_data<'py>(
        mut self_: PyRefMut<'py, Self>,
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

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Pt);
        let full_save_path = path.join(&save_path);

        let torch = py.import("torch")?;
        let args = (&parent.data, full_save_path);

        match parent.data_type {
            DataType::TorchDataset => {
                // get "torch_dataset from kwargs"
                // return error with kwargs is none

                let kwargs = kwargs.ok_or_else(|| {
                    OpsmlError::new_err("Torch dataset requires kwargs with torch_dataset")
                })?;

                let torch_dataset = kwargs.get_item("torch_dataset").unwrap();

                if let Some(dataset) = torch_dataset {
                    dataset
                } else {
                    return Err(OpsmlError::new_err(
                        "Torch dataset requires kwargs with torch_dataset",
                    ));
                };

                // pop torch_dataset from kwargs
                kwargs.del_item("torch_dataset")?;

                torch
                    .call_method("save", args, Some(kwargs))
                    .map_err(|e| OpsmlError::new_err(e.to_string()))?;
            }
            _ => {
                torch
                    .call_method("save", args, kwargs)
                    .map_err(|e| OpsmlError::new_err(e.to_string()))?;
            }
        }

        // Save the data using joblib

        Ok(save_path)
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<DataInterfaceSaveMetadata> {
        let feature_map = self_.as_super().create_feature_map(py)?;
        let sql_save_path = self_.as_super().save_sql(path.clone())?;
        let save_path = TorchData::save_data(self_, py, path.clone(), kwargs)?;

        Ok(DataInterfaceSaveMetadata {
            data_type: DataType::TorchTensor,
            feature_map: feature_map.clone(),
            data_save_path: Some(save_path),
            sql_save_path,
            data_profile_save_path: None,
        })
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn load_data<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Pt);

        let torch = PyModule::import(py, "torch")?;

        let data = match self_.as_super().data_type {
            DataType::TorchDataset => {
                // get "torch_dataset from kwargs"
                // return error with kwargs is none

                let kwargs = kwargs.ok_or_else(|| {
                    OpsmlError::new_err("Torch dataset requires kwargs with torch_dataset")
                })?;

                let torch_dataset = kwargs.get_item("torch_dataset").unwrap();

                if let Some(dataset) = torch_dataset {
                    dataset
                } else {
                    return Err(OpsmlError::new_err(
                        "Torch dataset requires kwargs with torch_dataset",
                    ));
                };

                // pop torch_dataset from kwargs
                kwargs.del_item("torch_dataset")?;

                torch.call_method("load", (load_path,), Some(kwargs))?
            }
            _ => torch.call_method("load", (load_path,), kwargs)?,
        };

        self_.as_super().data = data.into();

        Ok(())
    }
}

impl TorchData {
    pub fn from_path(
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PyObject> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Pt);

        let numpy = PyModule::import(py, "torch")?;

        // Load the data using numpy
        let data = numpy.call_method("load", (load_path,), kwargs)?;

        let interface = TorchData::new(py, Some(&data), None, None, None, None, None)?;

        let bound = Py::new(py, interface)?.as_any().clone_ref(py);

        Ok(bound)
    }
}
