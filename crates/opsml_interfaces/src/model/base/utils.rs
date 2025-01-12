use crate::data::{ArrowData, DataInterface, NumpyData, PandasData, PolarsData, TorchData};
use crate::model::InterfaceDataType;
use crate::ModelType;
use core::num;
use opsml_error::OpsmlError;
use opsml_types::{DataType, SaveName, Suffix};
use pyo3::types::{PyDict, PyList, PyListMethods, PyTuple, PyTupleMethods};
use pyo3::IntoPyObjectExt;
use pyo3::{prelude::*, types::PySlice};
use std::path::PathBuf;

#[derive(Default)]
pub enum SampleData {
    Pandas(PyObject),
    Polars(PyObject),
    Numpy(PyObject),
    Arrow(PyObject),
    Torch(PyObject),
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
                InterfaceDataType::Torch => {
                    let interface =
                        TorchData::new(py, Some(&sliced_data), None, None, None, None, None)?;
                    let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                    Ok(Some(SampleData::Numpy(bound)))
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
            DataType::TorchTensor => Self::slice_and_return(data, SampleData::Torch),
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

        // convert data from PyTuple to PyList
        let py_list = PyList::new(py, data.downcast::<PyTuple>()?.iter())?;

        for (idx, item) in py_list.iter().enumerate() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = item.get_item(&slice)?;
            py_list.set_item(idx, sliced_item)?;
        }

        let tuple = PyTuple::new(py, py_list.iter())?.unbind();

        Ok(SampleData::Tuple(tuple))
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
            SampleData::Torch(_) => DataType::TorchTensor,
            SampleData::None => DataType::NotProvided,
        }
    }

    pub fn get_data(&self, py: Python) -> PyResult<PyObject> {
        match self {
            SampleData::Pandas(data) => Ok(data.clone_ref(py)),
            SampleData::Polars(data) => Ok(data.clone_ref(py)),
            SampleData::Numpy(data) => Ok(data.clone_ref(py)),
            SampleData::Arrow(data) => Ok(data.clone_ref(py)),
            SampleData::Torch(data) => Ok(data.clone_ref(py)),
            SampleData::List(data) => Ok(data.into_py_any(py).unwrap()),
            SampleData::Tuple(data) => Ok(data.into_py_any(py).unwrap()),
            SampleData::Dict(data) => Ok(data.into_py_any(py).unwrap()),
            SampleData::None => Ok(py.None()),
        }
    }

    fn save_to_joblib(&self, data: &Bound<'_, PyAny>, path: PathBuf) -> PyResult<PathBuf> {
        let py = data.py();
        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Joblib);
        let full_save_path = path.join(&save_path);
        let joblib = py.import("joblib")?;
        joblib.call_method1("dump", (data, full_save_path))?;

        Ok(path)
    }

    fn save_interface_data(&self, data: &Bound<'_, PyAny>, path: PathBuf) -> PyResult<PathBuf> {
        let path = data.call_method1("save_data", (path,))?;
        // convert pyany to pathbuf
        let path = path.extract::<PathBuf>()?;
        Ok(path)
    }

    pub fn save_data(&self, py: Python, path: PathBuf) -> PyResult<Option<PathBuf>> {
        match self {
            SampleData::Pandas(data) => Ok(Some(self.save_interface_data(data.bind(py), path)?)),
            SampleData::Polars(data) => Ok(Some(self.save_interface_data(data.bind(py), path)?)),
            SampleData::Numpy(data) => Ok(Some(self.save_interface_data(data.bind(py), path)?)),
            SampleData::Arrow(data) => Ok(Some(self.save_interface_data(data.bind(py), path)?)),
            SampleData::Torch(data) => Ok(Some(self.save_interface_data(data.bind(py), path)?)),
            SampleData::List(data) => Ok(Some(self.save_to_joblib(data.bind(py), path)?)),
            SampleData::Tuple(data) => Ok(Some(self.save_to_joblib(data.bind(py), path)?)),
            SampleData::Dict(data) => Ok(Some(self.save_to_joblib(data.bind(py), path)?)),
            SampleData::None => Ok(None),
        }
    }

    // helper method for converting all pandas numeric types to f32
    // primarily used with sklearn pipelines and onnx
    fn convert_pandas_to_f32<'py>(&self, data: Bound<'py, PyAny>) -> PyResult<Bound<'py, PyAny>> {
        let py = data.py();
        let npfloat32 = py.import("numpy")?.getattr("float32")?;
        let numeric_cols = data
            .call_method1("select_dtypes", ("number",))?
            .getattr("columns")?
            .extract::<Vec<String>>()?;

        let df_numeric_cols = data.get_item(&numeric_cols)?;
        let df_numeric_cols_float = df_numeric_cols.call_method1("astype", (npfloat32,))?;

        data.set_item(&numeric_cols, df_numeric_cols_float)?;

        Ok(data)
    }

    pub fn get_data_for_onnx<'py>(
        &self,
        py: Python<'py>,
        model_type: &ModelType,
    ) -> PyResult<Bound<'py, PyAny>> {
        match self {
            SampleData::Pandas(data) => Ok({
                let data = data.bind(py).getattr("data")?;
                match model_type {
                    ModelType::SklearnPipeline => self.convert_pandas_to_f32(data)?,
                    _ => {
                        let numpy_data = data.call_method0("to_numpy")?;
                        // convert to float32
                        numpy_data.call_method1("astype", ("float32",))?
                    }
                }
            }),
            SampleData::Polars(data) => Ok({
                let data = data.bind(py).getattr("data")?;
                let converted_data = data.call_method0("to_pandas");
                // if data is err, try converting to numpy
                match converted_data {
                    Ok(converted_data) => match model_type {
                        ModelType::SklearnPipeline => self.convert_pandas_to_f32(converted_data)?,
                        _ => {
                            let numpy_data = data.call_method0("to_numpy")?;
                            // convert to float32
                            numpy_data.call_method1("astype", ("float32",))?
                        }
                    },
                    Err(_) => {
                        let numpy_data = data.call_method0("to_numpy")?;
                        // convert to float32
                        numpy_data.call_method1("astype", ("float32",))?
                    }
                }
            }),
            SampleData::Numpy(data) => Ok(data.bind(py).getattr("data")?),
            SampleData::Arrow(data) => Ok({
                let data = data.bind(py).getattr("data")?;
                let converted_data = data.call_method0("to_pandas");
                // if data is err, try converting to numpy
                match converted_data {
                    Ok(converted_data) => self.convert_pandas_to_f32(converted_data)?,
                    Err(_) => {
                        let numpy_data = data.call_method0("to_numpy")?;
                        // convert to float32
                        numpy_data.call_method1("astype", ("float32",))?
                    }
                }
            }),
            SampleData::Torch(data) => Ok(data.bind(py).getattr("data")?),
            SampleData::List(data) => Ok(data.into_py_any(py).unwrap().bind(py).clone()),
            SampleData::Tuple(data) => Ok(data.into_py_any(py).unwrap().bind(py).clone()),
            SampleData::Dict(data) => Ok(data.into_py_any(py).unwrap().bind(py).clone()),
            SampleData::None => Ok(py.None().bind(py).clone()),
        }
    }

    pub fn get_feature_names(&self, py: Python) -> PyResult<Vec<String>> {
        match self {
            SampleData::Pandas(data) => {
                let data = data.bind(py).getattr("data")?;
                let columns = data.getattr("columns")?;
                let columns = columns.extract::<Vec<String>>()?;
                Ok(columns)
            }
            SampleData::Polars(data) => {
                let data = data.bind(py).getattr("data")?;
                let columns = data.getattr("columns")?;
                let columns = columns.extract::<Vec<String>>()?;
                Ok(columns)
            }
            SampleData::Numpy(_) => Ok(vec![]),
            SampleData::Arrow(data) => {
                let data = data.bind(py).getattr("data")?;
                let columns = data.getattr("column_names")?;
                let columns = columns.extract::<Vec<String>>()?;
                Ok(columns)
            }
            SampleData::Torch(_) => Ok(vec![]),
            SampleData::List(_) => Ok(vec![]),
            SampleData::Tuple(_) => Ok(vec![]),
            SampleData::Dict(_) => Ok(vec![]),
            SampleData::None => Ok(vec![]),
        }
    }
}
