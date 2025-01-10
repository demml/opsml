use crate::data::{ArrowData, DataInterface, NumpyData, PandasData, PolarsData};
use crate::model::InterfaceDataType;
use opsml_error::OpsmlError;
use opsml_types::DataType;
use pyo3::types::{PyDict, PyList, PyListMethods, PyTuple, PyTupleMethods};
use pyo3::IntoPyObjectExt;
use pyo3::{prelude::*, types::PySlice};

#[derive(Default)]
pub enum SampleData {
    Pandas(PyObject),
    Polars(PyObject),
    Numpy(PyObject),
    Arrow(PyObject),
    List(Py<PyList>),
    Tuple(Py<PyTuple>),
    Dict(Py<PyDict>),

    #[default]
    None,
}

impl SampleData {
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

        Ok(SampleData::None)
    }

    fn get_interface_for_sample(data: &Bound<'_, PyAny>) -> PyResult<Option<Self>> {
        let py = data.py();
        let class = data.getattr("__class__")?;
        let module = class.getattr("__module__")?.str()?.to_string();
        let name = class.getattr("__name__")?.str()?.to_string();
        let full_class_name = format!("{}.{}", module, name);

        let interface_type = InterfaceDataType::from_module_name(&full_class_name).ok();

        if let Some(interface_type) = interface_type {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_data = data.get_item(slice)?;
            match interface_type {
                InterfaceDataType::Pandas => {
                    let interface =
                        PandasData::new(py, Some(&sliced_data), None, None, None, None, None)?;
                    let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                    Ok(Some(SampleData::Pandas(bound)))
                }
                InterfaceDataType::Polars => {
                    let interface =
                        PolarsData::new(py, Some(&sliced_data), None, None, None, None, None)?;
                    let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                    Ok(Some(SampleData::Polars(bound)))
                }
                InterfaceDataType::Numpy => {
                    let interface =
                        NumpyData::new(py, Some(&sliced_data), None, None, None, None, None)?;
                    let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                    Ok(Some(SampleData::Numpy(bound)))
                }
                InterfaceDataType::Arrow => {
                    let interface =
                        ArrowData::new(py, Some(&sliced_data), None, None, None, None, None)?;
                    let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                    Ok(Some(SampleData::Arrow(bound)))
                }
            }
        } else {
            Ok(None)
        }
    }

    fn handle_data_interface(data: &Bound<'_, PyAny>) -> PyResult<Self> {
        let data_type = data.getattr("data_type")?.extract::<DataType>()?;

        match data_type {
            DataType::Pandas => Self::slice_and_return(data, SampleData::Pandas),
            DataType::Polars => Self::slice_and_return(data, SampleData::Polars),
            DataType::Numpy => Self::slice_and_return(data, SampleData::Numpy),
            DataType::Arrow => Self::slice_and_return(data, SampleData::Arrow),
            _ => Err(OpsmlError::new_err("Data type not supported")),
        }
    }

    fn slice_and_return<F>(data: &Bound<'_, PyAny>, constructor: F) -> PyResult<Self>
    where
        F: FnOnce(PyObject) -> SampleData,
    {
        let py = data.py();
        let slice = PySlice::new(py, 0, 1, 1);
        let sliced_data = data.getattr("data")?.get_item(slice)?;
        data.setattr("data", sliced_data)?;
        Ok(constructor(data.clone().unbind()))
    }

    fn handle_pylist(data: &Bound<'_, PyAny>) -> PyResult<Self> {
        let py = data.py();
        let py_list = data.downcast::<PyList>()?;

        for (idx, item) in py_list.iter().enumerate() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = item.get_item(&slice)?;
            py_list.set_item(idx, sliced_item)?;
        }

        Ok(SampleData::List(py_list.clone().unbind()))
    }

    fn handle_pytuple(data: &Bound<'_, PyAny>) -> PyResult<Self> {
        let py = data.py();
        let py_tuple = data.downcast::<PyTuple>()?;

        for (idx, item) in py_tuple.iter().enumerate() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = item.get_item(&slice)?;
            py_tuple.set_item(idx, sliced_item)?;
        }

        Ok(SampleData::Tuple(py_tuple.clone().unbind()))
    }

    fn handle_pydict(data: &Bound<'_, PyAny>) -> PyResult<Self> {
        let py = data.py();
        let py_dict = data.downcast::<PyDict>()?;

        for (k, v) in py_dict.iter() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = v.get_item(slice)?;
            py_dict.set_item(k, sliced_item)?;
        }

        Ok(SampleData::Dict(py_dict.clone().unbind()))
    }

    pub fn get_data_type(&self) -> DataType {
        match self {
            SampleData::Pandas(_) => DataType::Pandas,
            SampleData::Polars(_) => DataType::Polars,
            SampleData::Numpy(_) => DataType::Numpy,
            SampleData::Arrow(_) => DataType::Arrow,
            SampleData::List(_) => DataType::List,
            SampleData::Tuple(_) => DataType::Tuple,
            SampleData::Dict(_) => DataType::Dict,
            SampleData::None => DataType::NotProvided,
        }
    }

    pub fn get_data(&self, py: Python) -> PyResult<PyObject> {
        match self {
            SampleData::Pandas(data) => Ok(data.clone_ref(py)),
            SampleData::Polars(data) => Ok(data.clone_ref(py)),
            SampleData::Numpy(data) => Ok(data.clone_ref(py)),
            SampleData::Arrow(data) => Ok(data.clone_ref(py)),
            SampleData::List(data) => Ok(data.into_py_any(py).unwrap()),
            SampleData::Tuple(data) => Ok(data.into_py_any(py).unwrap()),
            SampleData::Dict(data) => Ok(data.into_py_any(py).unwrap()),
            SampleData::None => Ok(py.None()),
        }
    }
}
