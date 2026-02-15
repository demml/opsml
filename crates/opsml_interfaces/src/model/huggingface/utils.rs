use crate::base::{OnnxExtension, get_class_full_name, load_from_joblib, save_to_joblib};
use crate::data::{ArrowData, DataInterface, NumpyData, PandasData, PolarsData, TorchData};
use crate::error::{OnnxError, SampleDataError};
use crate::model::InterfaceDataType;
use opsml_types::{DataType, ModelType};
use pyo3::IntoPyObjectExt;
use pyo3::types::{PyDict, PyList, PyListMethods, PyTuple, PyTupleMethods};
use pyo3::{
    prelude::*,
    types::{PySlice, PyString},
};

use std::path::Path;
use std::path::PathBuf;

use tracing::{error, instrument};

#[derive(Default, Debug)]
pub enum HuggingFaceSampleData {
    Pandas(Py<PyAny>),
    Polars(Py<PyAny>),
    Numpy(Py<PyAny>),
    Arrow(Py<PyAny>),
    Torch(Py<PyAny>),
    List(Py<PyList>),
    Tuple(Py<PyTuple>),
    Dict(Py<PyDict>),
    Str(Py<PyString>),

    #[default]
    None,
}

impl HuggingFaceSampleData {
    /// Create a new HuggingFaceSampleData object
    ///
    /// # Arguments
    ///
    /// * `data` - The data to create the HuggingFaceSampleData object from
    ///
    /// # Returns
    ///
    pub fn new(data: &Bound<'_, PyAny>) -> Result<Self, SampleDataError> {
        let py = data.py();
        let transformers = py.import("transformers")?;

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

        if data.is_instance_of::<PyString>() {
            return Ok(HuggingFaceSampleData::Str(
                data.cast::<PyString>()?.clone().unbind(),
            ));
        }

        if data.is_instance(&transformers.getattr("BatchEncoding")?)?
            || data.is_instance(&transformers.getattr("BatchFeature")?)?
        {
            return Self::handle_batch_data(data);
        }

        Ok(HuggingFaceSampleData::None)
    }

    fn match_interface_type(
        py: Python,
        interface_type: &InterfaceDataType,
        data: &Bound<'_, PyAny>,
    ) -> Result<Self, SampleDataError> {
        let slice = PySlice::new(py, 0, 1, 1);
        let sliced_data = data.get_item(slice)?;

        match interface_type {
            InterfaceDataType::Pandas => {
                let interface = PandasData::new(py, Some(&sliced_data), None, None, None, None)?;
                let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                Ok(HuggingFaceSampleData::Pandas(bound))
            }
            InterfaceDataType::Polars => {
                let interface = PolarsData::new(py, Some(&sliced_data), None, None, None, None)?;
                let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                Ok(HuggingFaceSampleData::Polars(bound))
            }
            InterfaceDataType::Numpy => {
                let interface = NumpyData::new(py, Some(&sliced_data), None, None, None, None)?;
                let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                Ok(HuggingFaceSampleData::Numpy(bound))
            }
            InterfaceDataType::Arrow => {
                let interface = ArrowData::new(py, Some(&sliced_data), None, None, None, None)?;
                let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                Ok(HuggingFaceSampleData::Arrow(bound))
            }
            InterfaceDataType::Torch => {
                let interface = TorchData::new(py, Some(&sliced_data), None, None, None, None)?;
                let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                Ok(HuggingFaceSampleData::Numpy(bound))
            }
        }
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
            DataType::Pandas => Self::slice_and_return(data, HuggingFaceSampleData::Pandas),
            DataType::Polars => Self::slice_and_return(data, HuggingFaceSampleData::Polars),
            DataType::Numpy => Self::slice_and_return(data, HuggingFaceSampleData::Numpy),
            DataType::Arrow => Self::slice_and_return(data, HuggingFaceSampleData::Arrow),
            DataType::TorchTensor => Self::slice_and_return(data, HuggingFaceSampleData::Torch),
            _ => Err(SampleDataError::InvalidDataType),
        }
    }

    fn slice_and_return<F>(data: &Bound<'_, PyAny>, constructor: F) -> Result<Self, SampleDataError>
    where
        F: FnOnce(Py<PyAny>) -> HuggingFaceSampleData,
    {
        let py = data.py();
        let slice = PySlice::new(py, 0, 1, 1);
        let sliced_data = data.getattr("data")?.get_item(slice)?;
        data.setattr("data", sliced_data)?;
        Ok(constructor(data.clone().unbind()))
    }

    fn handle_pylist(data: &Bound<'_, PyAny>) -> Result<Self, SampleDataError> {
        let py = data.py();
        let py_list = data.cast::<PyList>()?;

        for (idx, item) in py_list.iter().enumerate() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = item.get_item(&slice)?;
            py_list.set_item(idx, sliced_item)?;
        }

        Ok(HuggingFaceSampleData::List(py_list.clone().unbind()))
    }

    fn handle_pytuple(data: &Bound<'_, PyAny>) -> Result<Self, SampleDataError> {
        let py = data.py();

        // convert data from PyTuple to PyList
        let py_list = PyList::new(py, data.cast::<PyTuple>()?.iter())?;

        for (idx, item) in py_list.iter().enumerate() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = item.get_item(&slice)?;
            py_list.set_item(idx, sliced_item)?;
        }

        let tuple = PyTuple::new(py, py_list.iter())?.unbind();

        Ok(HuggingFaceSampleData::Tuple(tuple))
    }

    fn handle_pydict(data: &Bound<'_, PyAny>) -> Result<Self, SampleDataError> {
        let py = data.py();
        let py_dict = data.cast::<PyDict>()?;

        for (k, v) in py_dict.iter() {
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = v.get_item(slice)?;
            py_dict.set_item(k, sliced_item)?;
        }

        Ok(HuggingFaceSampleData::Dict(py_dict.clone().unbind()))
    }

    fn handle_batch_data(data: &Bound<'_, PyAny>) -> Result<Self, SampleDataError> {
        let py = data.py();
        let py_dict = PyDict::new(py);

        for item in data.call_method0("items")?.try_iter()? {
            let (k, v): (Bound<'_, PyAny>, Bound<'_, PyAny>) = item?.extract()?;
            let slice = PySlice::new(py, 0, 1, 1);
            let sliced_item = v.get_item(slice)?;
            py_dict.set_item(k, sliced_item)?;
        }
        // items is dict_items object

        Ok(HuggingFaceSampleData::Dict(py_dict.clone().unbind()))
    }

    pub fn get_data_type(&self) -> DataType {
        match self {
            HuggingFaceSampleData::Pandas(_) => DataType::Pandas,
            HuggingFaceSampleData::Polars(_) => DataType::Polars,
            HuggingFaceSampleData::Numpy(_) => DataType::Numpy,
            HuggingFaceSampleData::Arrow(_) => DataType::Arrow,
            HuggingFaceSampleData::List(_) => DataType::List,
            HuggingFaceSampleData::Tuple(_) => DataType::Tuple,
            HuggingFaceSampleData::Dict(_) => DataType::Dict,
            HuggingFaceSampleData::Torch(_) => DataType::TorchTensor,
            HuggingFaceSampleData::Str(_) => DataType::Str,
            HuggingFaceSampleData::None => DataType::NotProvided,
        }
    }

    pub fn get_data(&self, py: Python) -> Result<Py<PyAny>, SampleDataError> {
        match self {
            HuggingFaceSampleData::Pandas(data) => Ok(data.clone_ref(py)),
            HuggingFaceSampleData::Polars(data) => Ok(data.clone_ref(py)),
            HuggingFaceSampleData::Numpy(data) => Ok(data.clone_ref(py)),
            HuggingFaceSampleData::Arrow(data) => Ok(data.clone_ref(py)),
            HuggingFaceSampleData::Torch(data) => Ok(data.clone_ref(py)),
            HuggingFaceSampleData::List(data) => Ok(data.into_py_any(py).unwrap()),
            HuggingFaceSampleData::Tuple(data) => Ok(data.into_py_any(py).unwrap()),
            HuggingFaceSampleData::Dict(data) => Ok(data.into_py_any(py).unwrap()),
            HuggingFaceSampleData::Str(data) => Ok(data.into_py_any(py).unwrap()),
            HuggingFaceSampleData::None => Ok(py.None()),
        }
    }

    fn save_interface_data(
        &self,
        data: &Bound<'_, PyAny>,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<PathBuf, SampleDataError> {
        let metadata = data.call_method("save", (path,), kwargs)?;

        // convert pyany to pathbuf
        let save_path = metadata
            .getattr("save_metadata")?
            .getattr("data_uri")?
            .extract::<PathBuf>()?;

        Ok(save_path)
    }

    #[instrument(skip_all)]
    pub fn save_data(
        &self,
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<Option<PathBuf>, SampleDataError> {
        match self {
            HuggingFaceSampleData::Pandas(data) => Ok(Some(
                self.save_interface_data(data.bind(py), path, kwargs)
                    .inspect_err(|e| {
                        error!("Error saving pandas data: {e}");
                    })?,
            )),
            HuggingFaceSampleData::Polars(data) => Ok(Some(
                self.save_interface_data(data.bind(py), path, kwargs)
                    .inspect_err(|e| {
                        error!("Error saving polars data: {e}");
                    })?,
            )),
            HuggingFaceSampleData::Numpy(data) => Ok(Some(
                self.save_interface_data(data.bind(py), path, kwargs)
                    .inspect_err(|e| {
                        error!("Error saving numpy data: {e}");
                    })?,
            )),
            HuggingFaceSampleData::Arrow(data) => Ok(Some(
                self.save_interface_data(data.bind(py), path, kwargs)
                    .inspect_err(|e| {
                        error!("Error saving arrow data: {e}");
                    })?,
            )),
            HuggingFaceSampleData::Torch(data) => Ok(Some(
                self.save_interface_data(data.bind(py), path, kwargs)
                    .inspect_err(|e| {
                        error!("Error saving torch data: {e}");
                    })?,
            )),
            HuggingFaceSampleData::List(data) => Ok(Some(
                save_to_joblib(data.bind(py), path).inspect_err(|e| {
                    error!("Error saving list data: {e}");
                })?,
            )),
            HuggingFaceSampleData::Tuple(data) => Ok(Some(
                save_to_joblib(data.bind(py), path).inspect_err(|e| {
                    error!("Error saving tuple data: {e}");
                })?,
            )),
            HuggingFaceSampleData::Dict(data) => Ok(Some(
                save_to_joblib(data.bind(py), path).inspect_err(|e| {
                    error!("Error saving dict data: {e}");
                })?,
            )),

            HuggingFaceSampleData::Str(data) => Ok(Some(
                save_to_joblib(data.bind(py), path).inspect_err(|e| {
                    error!("Error saving string data: {e}");
                })?,
            )),

            HuggingFaceSampleData::None => Ok(None),
        }
    }

    pub fn load_data<'py>(
        py: Python<'py>,
        path: &Path,
        data_type: &DataType,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> Result<HuggingFaceSampleData, SampleDataError> {
        match data_type {
            DataType::Pandas => Ok(HuggingFaceSampleData::Pandas(PandasData::from_path(
                py, path, kwargs,
            )?)),
            DataType::Polars => Ok(HuggingFaceSampleData::Polars(PolarsData::from_path(
                py, path, kwargs,
            )?)),
            DataType::Numpy => Ok(HuggingFaceSampleData::Numpy(NumpyData::from_path(
                py, path, kwargs,
            )?)),
            DataType::Arrow => Ok(HuggingFaceSampleData::Arrow(ArrowData::from_path(
                py, path, kwargs,
            )?)),
            DataType::TorchTensor => Ok(HuggingFaceSampleData::Torch(TorchData::from_path(
                py, path, kwargs,
            )?)),
            DataType::List => {
                let data = load_from_joblib(py, path)?;
                Ok(HuggingFaceSampleData::List(
                    data.cast::<PyList>()?.clone().unbind(),
                ))
            }
            DataType::Tuple => {
                let data = load_from_joblib(py, path)?;
                Ok(HuggingFaceSampleData::Tuple(
                    data.cast::<PyTuple>()?.clone().unbind(),
                ))
            }
            DataType::Dict => {
                let data = load_from_joblib(py, path)?;
                Ok(HuggingFaceSampleData::Dict(
                    data.cast::<PyDict>()?.clone().unbind(),
                ))
            }

            DataType::Str => {
                let data = load_from_joblib(py, path)?;
                Ok(HuggingFaceSampleData::Str(
                    data.cast::<PyString>()?.clone().unbind(),
                ))
            }

            _ => Ok(HuggingFaceSampleData::None),
        }
    }
}

impl OnnxExtension for HuggingFaceSampleData {
    fn get_data_for_onnx<'py>(
        &self,
        py: Python<'py>,
        _model_type: &ModelType,
    ) -> Result<Bound<'py, PyAny>, OnnxError> {
        Ok(py.None().bind(py).clone())
    }

    fn get_feature_names(&self, _py: Python) -> Result<Vec<String>, OnnxError> {
        Ok(vec![])
    }

    fn is_none(&self) -> bool {
        matches!(self, HuggingFaceSampleData::None)
    }
}
