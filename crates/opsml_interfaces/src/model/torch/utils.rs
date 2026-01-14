use crate::data::{DataInterface, TorchData};
use crate::error::{OnnxError, SampleDataError};
use crate::model::{
    base::{get_class_full_name, load_from_joblib, save_to_joblib, OnnxExtension},
    InterfaceDataType,
};
use opsml_types::{DataType, ModelType};
use pyo3::types::{PyDict, PyList, PyListMethods, PyTuple, PyTupleMethods};
use pyo3::IntoPyObjectExt;
use pyo3::{prelude::*, types::PySlice};
use std::path::Path;
use std::path::PathBuf;

#[derive(Default, Debug)]
pub enum TorchSampleData {
    Torch(Py<PyAny>),
    List(Py<PyList>),
    Tuple(Py<PyTuple>),
    Dict(Py<PyDict>),
    DataSet(Py<PyAny>),

    #[default]
    None,
}

impl TorchSampleData {
    /// Create a new TorchSampleData object from the given data
    ///
    /// Overview:
    ///     1. Check if the data is a DataInterface object
    ///         - If it is, slice the data and return the object
    ///     2. Check if the data is a supported interface type
    ///         - If it is, slice the data and coerce into the appropriate interface
    ///     3. Check if the data is a list
    ///         - If it is, slice the data and return the object
    ///     4. Check if the data is a tuple
    ///         - If it is, slice the data and return the object
    ///     5. Check if the data is a dictionary
    ///         - If it is, slice each item in the dictionary and return the object
    ///
    /// # Arguments
    ///
    /// * `data` - The data to create the SampleData object from
    ///
    /// # Returns
    ///
    pub fn new(data: &Bound<'_, PyAny>) -> Result<Self, SampleDataError> {
        let py = data.py();

        if data.is_instance_of::<DataInterface>() {
            return Self::handle_data_interface(data);
        }

        if let Some(interface) = Self::get_interface_for_sample(data)? {
            return Ok(interface);
        }

        if data.is_instance_of::<PyList>() {
            return Self::handle_pylist(data);
        }

        if data.is_instance_of::<PyTuple>() {
            return Self::handle_pytuple(data);
        }

        if data.is_instance_of::<PyDict>() {
            return Self::handle_pydict(data);
        }

        let torch_dataset = py
            .import("torch")?
            .getattr("utils")?
            .getattr("data")?
            .getattr("Dataset")?;

        if data.is_instance(&torch_dataset)? {
            return Self::handle_dataset(data);
        }

        Ok(TorchSampleData::None)
    }

    fn handle_pylist(data: &Bound<'_, PyAny>) -> Result<Self, SampleDataError> {
        let py = data.py();
        let py_list = data.cast::<PyList>()?;
        let torch_tensor = py.import("torch")?.getattr("Tensor")?;

        for (idx, item) in py_list.iter().enumerate() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = item.get_item(&slice)?;

            // Check if the item is a torch tensor
            let is_tensor = sliced_item.is_instance(&torch_tensor)?;

            if !is_tensor {
                Err(SampleDataError::TorchDataTypeError)?;
            }

            py_list.set_item(idx, sliced_item)?;
        }

        Ok(TorchSampleData::List(py_list.clone().unbind()))
    }

    fn handle_pytuple(data: &Bound<'_, PyAny>) -> Result<Self, SampleDataError> {
        let py = data.py();
        let torch_tensor = py.import("torch")?.getattr("Tensor")?;

        // convert data from PyTuple to PyList
        let py_list = PyList::new(py, data.cast::<PyTuple>()?.iter())?;

        for (idx, item) in py_list.iter().enumerate() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = item.get_item(&slice)?;

            let is_tensor = sliced_item.is_instance(&torch_tensor)?;

            if !is_tensor {
                Err(SampleDataError::TorchDataTypeError)?;
            }

            py_list.set_item(idx, sliced_item)?;
        }

        let tuple = PyTuple::new(py, py_list.iter())?.unbind();

        Ok(TorchSampleData::Tuple(tuple))
    }

    fn handle_pydict(data: &Bound<'_, PyAny>) -> Result<Self, SampleDataError> {
        let py = data.py();
        let py_dict = data.cast::<PyDict>()?;
        let torch_tensor = py.import("torch")?.getattr("Tensor")?;

        for (k, v) in py_dict.iter() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = v.get_item(slice)?;

            let is_tensor = sliced_item.is_instance(&torch_tensor)?;

            if !is_tensor {
                Err(SampleDataError::TorchDataTypeError)?;
            }

            py_dict.set_item(k, sliced_item)?;
        }

        Ok(TorchSampleData::Dict(py_dict.clone().unbind()))
    }

    fn handle_dataset(data: &Bound<'_, PyAny>) -> Result<Self, SampleDataError> {
        let samples = data.call_method1("__getitem__", (0,))?;

        Ok(TorchSampleData::DataSet(samples.unbind()))
    }

    fn slice_and_return<F>(data: &Bound<'_, PyAny>, constructor: F) -> Result<Self, SampleDataError>
    where
        F: FnOnce(Py<PyAny>) -> TorchSampleData,
    {
        let py = data.py();
        let slice = PySlice::new(py, 0, 1, 1);
        let sliced_data = data.getattr("data")?.get_item(slice)?;
        data.setattr("data", sliced_data)?;
        Ok(constructor(data.clone().unbind()))
    }

    fn get_interface_for_sample(data: &Bound<'_, PyAny>) -> Result<Option<Self>, SampleDataError> {
        let py = data.py();
        let class = data.getattr("__class__")?;
        let full_class_name = get_class_full_name(&class)?;

        if let Ok(interface_type) = InterfaceDataType::from_module_name(&full_class_name) {
            return Self::match_interface_type(py, &interface_type, data).map(Some);
        }

        Ok(None)
    }

    fn handle_data_interface(data: &Bound<'_, PyAny>) -> Result<Self, SampleDataError> {
        let data_type = data.getattr("data_type")?.extract::<DataType>()?;

        match data_type {
            DataType::TorchTensor => Self::slice_and_return(data, TorchSampleData::Torch),
            _ => Err(SampleDataError::DataTypeError),
        }
    }

    fn match_interface_type(
        py: Python,
        interface_type: &InterfaceDataType,
        data: &Bound<'_, PyAny>,
    ) -> Result<Self, SampleDataError> {
        let slice = PySlice::new(py, 0, 1, 1);
        let sliced_data = data.get_item(slice)?;

        match interface_type {
            InterfaceDataType::Torch => {
                let interface = TorchData::new(py, Some(&sliced_data), None, None, None, None)?;
                let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                Ok(TorchSampleData::Torch(bound))
            }

            _ => Err(SampleDataError::DataTypeError),
        }
    }

    pub fn save_data(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Option<PathBuf>, SampleDataError> {
        match self {
            TorchSampleData::Torch(data) => {
                let bound = data.bind(py);
                let save_path = bound.call_method("save", (path,), kwargs)?;
                // convert pyany to pathbuf
                let save_path = save_path.extract::<PathBuf>()?;
                Ok(Some(save_path))
            }

            TorchSampleData::List(data) => Ok(Some(save_to_joblib(data.bind(py), path)?)),
            TorchSampleData::Tuple(data) => Ok(Some(save_to_joblib(data.bind(py), path)?)),
            TorchSampleData::Dict(data) => Ok(Some(save_to_joblib(data.bind(py), path)?)),
            TorchSampleData::DataSet(data) => Ok(Some(save_to_joblib(data.bind(py), path)?)),
            TorchSampleData::None => Ok(None),
        }
    }

    pub fn load_data<'py>(
        py: Python<'py>,
        path: &Path,
        data_type: &DataType,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> Result<TorchSampleData, SampleDataError> {
        match data_type {
            DataType::TorchTensor => {
                Ok(TorchData::from_path(py, path, kwargs).map(TorchSampleData::Torch)?)
            }

            DataType::List => {
                let data = load_from_joblib(py, path)?;
                Ok(TorchSampleData::List(
                    data.cast::<PyList>()?.clone().unbind(),
                ))
            }

            DataType::Tuple => {
                let data = load_from_joblib(py, path)?;
                Ok(TorchSampleData::Tuple(
                    data.cast::<PyTuple>()?.clone().unbind(),
                ))
            }
            DataType::Dict => {
                let data = load_from_joblib(py, path)?;
                Ok(TorchSampleData::Dict(
                    data.cast::<PyDict>()?.clone().unbind(),
                ))
            }

            DataType::TorchDataset => {
                let data = load_from_joblib(py, path)?;
                Ok(TorchSampleData::DataSet(data.clone().unbind()))
            }

            _ => Err(SampleDataError::DataTypeError),
        }
    }

    pub fn get_data_type(&self) -> DataType {
        match self {
            TorchSampleData::Torch(_) => DataType::TorchTensor,
            TorchSampleData::List(_) => DataType::List,
            TorchSampleData::Tuple(_) => DataType::Tuple,
            TorchSampleData::Dict(_) => DataType::Dict,
            TorchSampleData::DataSet(_) => DataType::TorchDataset,
            TorchSampleData::None => DataType::NotProvided,
        }
    }

    pub fn get_data(&self, py: Python) -> Result<Py<PyAny>, SampleDataError> {
        match self {
            TorchSampleData::Torch(data) => Ok(data.into_py_any(py).unwrap()),
            TorchSampleData::List(data) => Ok(data.into_py_any(py).unwrap()),
            TorchSampleData::Tuple(data) => Ok(data.into_py_any(py).unwrap()),
            TorchSampleData::Dict(data) => Ok(data.into_py_any(py).unwrap()),
            TorchSampleData::DataSet(data) => Ok(data.into_py_any(py).unwrap()),
            TorchSampleData::None => Ok(py.None()),
        }
    }
}

impl OnnxExtension for TorchSampleData {
    fn get_data_for_onnx<'py>(
        &self,
        py: Python<'py>,
        _model_type: &ModelType,
    ) -> Result<Bound<'py, PyAny>, OnnxError> {
        match self {
            TorchSampleData::Torch(data) => Ok(data.bind(py).getattr("data")?),
            TorchSampleData::List(data) => Ok({
                let data = data.bind(py);
                // convert list to tuple
                PyTuple::new(py, data.iter())?.into_any()
            }),
            TorchSampleData::Tuple(data) => Ok(data.into_bound_py_any(py).unwrap()),
            TorchSampleData::Dict(data) => Ok({
                let data = data.bind(py);

                // collect all values from dict into a list
                let dict_value_list = PyList::new(py, data.values())?;

                PyTuple::new(py, dict_value_list.iter())?.into_any()
            }),
            TorchSampleData::DataSet(data) => Ok(data.into_bound_py_any(py).unwrap()),
            TorchSampleData::None => Ok(py.None().into_bound_py_any(py).unwrap()),
        }
    }

    fn is_none(&self) -> bool {
        matches!(self, TorchSampleData::None)
    }
}
