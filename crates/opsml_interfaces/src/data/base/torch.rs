use crate::data::{
    generate_feature_schema, DataInterface, DataInterfaceMetadata, DataInterfaceSaveMetadata,
    DataLoadKwargs, DataSaveKwargs, SqlLogic,
};
use crate::error::DataInterfaceError;
use crate::types::FeatureSchema;
use opsml_types::{DataInterfaceType, DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::{IntoPyObjectExt, PyTraverseError, PyVisit};
use scouter_client::DataProfile;
use std::collections::HashMap;
use std::path::{Path, PathBuf};

#[pyclass(extends=DataInterface, subclass)]
pub struct TorchData {
    #[pyo3(get)]
    pub data: Option<Py<PyAny>>,

    #[pyo3(get)]
    pub data_type: DataType,
}

#[pymethods]
impl TorchData {
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
                let tensor = py.import("torch")?.getattr("Tensor")?;
                // check if data is a numpy array
                if data.is_instance(&tensor).unwrap() {
                    Some(data.into_py_any(py)?)
                } else {
                    let type_name = data.get_type().name()?;
                    return Err(DataInterfaceError::TorchTypeError(type_name.to_string()));
                }
            }
            None => None,
        };

        let mut data_interface = DataInterface::new(
            py,
            None,
            data_splits,
            dependent_vars,
            sql_logic,
            data_profile,
        )?;

        data_interface.interface_type = DataInterfaceType::Torch;

        Ok((
            TorchData {
                data,
                data_type: DataType::TorchTensor,
            },
            data_interface,
        ))
    }

    #[setter]
    #[allow(clippy::needless_lifetimes)]
    pub fn set_data(&mut self, data: &Bound<'_, PyAny>) -> Result<(), DataInterfaceError> {
        let py = data.py();

        // check if data is None
        if PyAnyMethods::is_none(data) {
            self.data = None;
            Ok(())
        } else {
            // check if data is a numpy array
            // get type name of data
            let tensor = py.import("torch")?.getattr("Tensor")?;

            // check if data is a numpy array
            if data.is_instance(&tensor).unwrap() {
                self.data = Some(data.into_py_any(py)?);
                Ok(())
            } else {
                let type_name = data.get_type().name()?;
                Err(DataInterfaceError::TorchTypeError(type_name.to_string()))
            }
        }
    }

    #[pyo3(signature = (path, save_kwargs=None))]
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
            self_.as_super().dependent_vars.clone(),
            self_.as_super().data_splits.clone(),
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
        let torch = PyModule::import(py, "torch")?;
        let load_kwargs = load_kwargs.unwrap_or_default();

        let data = match self_.as_super().data_type {
            DataType::TorchDataset => {
                // get "torch_dataset from kwargs"
                // return error when kwargs is none
                let kwargs = load_kwargs.data_kwargs(py);
                let kwargs = kwargs.ok_or_else(|| DataInterfaceError::MissingTorchKwargsError)?;

                let torch_dataset = kwargs.get_item("torch_dataset").unwrap();

                if let Some(dataset) = torch_dataset {
                    dataset
                } else {
                    return Err(DataInterfaceError::MissingTorchKwargsError);
                };

                // pop torch_dataset from kwargs
                kwargs.del_item("torch_dataset")?;
                torch.call_method("load", (load_path,), Some(kwargs))?
            }

            _ => torch.call_method("load", (load_path,), load_kwargs.data_kwargs(py))?,
        };

        self_.set_data(&data)?;

        Ok(())
    }

    #[pyo3(signature = (_bin_size=20, _compute_correlations=false))]
    pub fn create_data_profile(
        mut _self_: PyRefMut<'_, Self>,
        _py: Python,
        _bin_size: usize,
        _compute_correlations: bool,
    ) -> Result<DataProfile, DataInterfaceError> {
        Err(DataInterfaceError::DataTypeNotSupportedForProfilingError)
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

impl TorchData {
    pub fn from_metadata<'py>(
        py: Python<'py>,
        metadata: &DataInterfaceMetadata,
    ) -> Result<Bound<'py, PyAny>, DataInterfaceError> {
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

        let data_interface = TorchData {
            data: None,
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
        if self.data.is_none() {
            return Err(DataInterfaceError::MissingDataError);
        }

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Pt);
        let full_save_path = path.join(&save_path);

        let torch = py.import("torch")?;
        let args = (self.data.as_ref().unwrap(), full_save_path);

        match self.data_type {
            DataType::TorchDataset => {
                // get "torch_dataset from kwargs"
                // return error with kwargs is none

                let kwargs = kwargs.ok_or_else(|| DataInterfaceError::MissingTorchKwargsError)?;

                let torch_dataset = kwargs.get_item("torch_dataset").unwrap();

                if let Some(dataset) = torch_dataset {
                    dataset
                } else {
                    return Err(DataInterfaceError::MissingTorchKwargsError);
                };

                // pop torch_dataset from kwargs
                kwargs.del_item("torch_dataset")?;

                torch.call_method("save", args, Some(kwargs))?;
            }
            _ => {
                torch.call_method("save", args, kwargs)?;
            }
        }

        // Save the data using joblib

        Ok(save_path)
    }

    pub fn create_feature_schema(
        &mut self,
        py: Python,
    ) -> Result<FeatureSchema, DataInterfaceError> {
        // Create and insert the feature
        let feature_map =
            generate_feature_schema(self.data.as_ref().unwrap().bind(py), &self.data_type)?;

        Ok(feature_map)
    }

    pub fn from_path(
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Py<PyAny>, DataInterfaceError> {
        let numpy = PyModule::import(py, "torch")?;

        // Load the data using numpy
        let data = numpy.call_method("load", (path,), kwargs)?;

        let interface = TorchData::new(py, Some(&data), None, None, None, None)?;

        let bound = Py::new(py, interface)?.as_any().clone_ref(py);

        Ok(bound)
    }
}
