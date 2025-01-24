use crate::data::schema::torch;
use crate::data::{ArrowData, DataInterface, NumpyData, PandasData, PolarsData, TorchData};
use crate::model::{base::get_class_full_name, InterfaceDataType};
use crate::{ModelType, SaveKwargs};
use opsml_error::OpsmlError;
use opsml_types::{DataType, SaveName, Suffix};
use pyo3::types::{PyDict, PyList, PyListMethods, PyTuple, PyTupleMethods};
use pyo3::IntoPyObjectExt;
use pyo3::{prelude::*, types::PySlice};
use scouter_client::{
    CustomDriftProfile, DriftProfile, DriftType, PsiDriftProfile, SpcDriftProfile,
};
use std::path::Path;
use std::path::PathBuf;
use tracing::{error, span};

#[derive(Default, Debug)]
pub enum TorchSampleData {
    Torch(PyObject),
    List(Py<PyList>),
    Tuple(Py<PyTuple>),
    Dict(Py<PyDict>),
    DataSet(PyObject),

    #[default]
    None,
}

impl TorchSampleData {
    /// Create a new SampleData object
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
    pub fn new(data: &Bound<'_, PyAny>) -> PyResult<Self> {
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

    fn handle_pylist(data: &Bound<'_, PyAny>) -> PyResult<Self> {
        let py = data.py();
        let py_list = data.downcast::<PyList>()?;
        let torch_tensor = py.import("torch")?.getattr("Tensor")?;

        for (idx, item) in py_list.iter().enumerate() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = item.get_item(&slice)?;

            // Check if the item is a torch tensor
            let is_tensor = sliced_item.is_instance(&torch_tensor)?;

            if !is_tensor {
                Err(OpsmlError::new_err("Data must be of type torch tensor"))?;
            }

            py_list.set_item(idx, sliced_item)?;
        }

        Ok(TorchSampleData::List(py_list.clone().unbind()))
    }

    fn handle_pytuple(data: &Bound<'_, PyAny>) -> PyResult<Self> {
        let py = data.py();
        let torch_tensor = py.import("torch")?.getattr("Tensor")?;

        // convert data from PyTuple to PyList
        let py_list = PyList::new(py, data.downcast::<PyTuple>()?.iter())?;

        for (idx, item) in py_list.iter().enumerate() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = item.get_item(&slice)?;

            let is_tensor = sliced_item.is_instance(&torch_tensor)?;

            if !is_tensor {
                Err(OpsmlError::new_err("Data must be of type torch tensor"))?;
            }

            py_list.set_item(idx, sliced_item)?;
        }

        let tuple = PyTuple::new(py, py_list.iter())?.unbind();

        Ok(TorchSampleData::Tuple(tuple))
    }

    fn handle_pydict(data: &Bound<'_, PyAny>) -> PyResult<Self> {
        let py = data.py();
        let py_dict = data.downcast::<PyDict>()?;
        let torch_tensor = py.import("torch")?.getattr("Tensor")?;

        for (k, v) in py_dict.iter() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = v.get_item(slice)?;

            let is_tensor = sliced_item.is_instance(&torch_tensor)?;

            if !is_tensor {
                Err(OpsmlError::new_err("Data must be of type torch tensor"))?;
            }

            py_dict.set_item(k, sliced_item)?;
        }

        Ok(TorchSampleData::Dict(py_dict.clone().unbind()))
    }

    fn handle_dataset(data: &Bound<'_, PyAny>) -> PyResult<Self> {
        let samples = data.call_method1("__getitem__", (0,))?;

        Ok(TorchSampleData::DataSet(samples.unbind()))
    }

    fn slice_and_return<F>(data: &Bound<'_, PyAny>, constructor: F) -> PyResult<Self>
    where
        F: FnOnce(PyObject) -> TorchSampleData,
    {
        let py = data.py();
        let slice = PySlice::new(py, 0, 1, 1);
        let sliced_data = data.getattr("data")?.get_item(slice)?;
        data.setattr("data", sliced_data)?;
        Ok(constructor(data.clone().unbind()))
    }

    fn get_interface_for_sample(data: &Bound<'_, PyAny>) -> PyResult<Option<Self>> {
        let py = data.py();
        let class = data.getattr("__class__")?;
        let full_class_name = get_class_full_name(&class)?;

        if let Ok(interface_type) = InterfaceDataType::from_module_name(&full_class_name) {
            return Self::match_interface_type(py, &interface_type, data).map(Some);
        }

        Ok(None)
    }

    fn handle_data_interface(data: &Bound<'_, PyAny>) -> PyResult<Self> {
        let data_type = data.getattr("data_type")?.extract::<DataType>()?;

        match data_type {
            DataType::TorchTensor => Self::slice_and_return(data, TorchSampleData::Torch),
            _ => Err(OpsmlError::new_err("Data type not supported")),
        }
    }

    fn match_interface_type(
        py: Python,
        interface_type: &InterfaceDataType,
        data: &Bound<'_, PyAny>,
    ) -> PyResult<Self> {
        let slice = PySlice::new(py, 0, 1, 1);
        let sliced_data = data.get_item(slice)?;

        match interface_type {
            InterfaceDataType::Torch => {
                let interface =
                    TorchData::new(py, Some(&sliced_data), None, None, None, None, None)?;
                let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                Ok(TorchSampleData::Torch(bound))
            }

            _ => Err(OpsmlError::new_err("Data type not supported")),
        }
    }
}
