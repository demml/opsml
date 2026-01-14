use crate::base::{DriftProfileMap, ModelSaveKwargs};
use crate::data::{ArrowData, DataInterface, NumpyData, PandasData, PolarsData, TorchData};
use crate::error::{ModelInterfaceError, OnnxError, SampleDataError};
use crate::model::InterfaceDataType;

use opsml_types::{DataType, ModelType, SaveName, Suffix};
use pyo3::types::{PyDict, PyList, PyListMethods, PyTuple, PyTupleMethods};
use pyo3::IntoPyObjectExt;
use pyo3::{prelude::*, types::PySlice};
use std::path::Path;
use std::path::PathBuf;
use tracing::{debug, error, instrument};

#[derive(Default)]
pub struct SaveKwargsResult<'py> {
    pub onnx: Option<Bound<'py, PyDict>>,
    pub model: Option<Bound<'py, PyDict>>,
    pub preprocessor: Option<Bound<'py, PyDict>>,
    pub save_onnx: bool,
}

#[derive(Default, Debug)]
pub enum SampleData {
    Pandas(Py<PyAny>),
    Polars(Py<PyAny>),
    Numpy(Py<PyAny>),
    Arrow(Py<PyAny>),
    Torch(Py<PyAny>),
    List(Py<PyList>),
    Tuple(Py<PyTuple>),
    Dict(Py<PyDict>),
    DMatrix(Py<PyAny>),

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

        if let Ok(xgb) = py.import("xgboost") {
            if let Ok(matrix) = xgb.getattr("DMatrix") {
                if data.is_instance(&matrix).unwrap() {
                    let slice = data.call_method("slice", ([0],), None)?;
                    return Ok(SampleData::DMatrix(slice.into_py_any(py)?));
                }
            }
        }

        Ok(SampleData::None)
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
                Ok(SampleData::Pandas(bound))
            }
            InterfaceDataType::Polars => {
                let interface = PolarsData::new(py, Some(&sliced_data), None, None, None, None)?;
                let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                Ok(SampleData::Polars(bound))
            }
            InterfaceDataType::Numpy => {
                let interface = NumpyData::new(py, Some(&sliced_data), None, None, None, None)?;
                let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                Ok(SampleData::Numpy(bound))
            }
            InterfaceDataType::Arrow => {
                let interface = ArrowData::new(py, Some(&sliced_data), None, None, None, None)?;
                let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                Ok(SampleData::Arrow(bound))
            }
            InterfaceDataType::Torch => {
                let interface = TorchData::new(py, Some(&sliced_data), None, None, None, None)?;
                let bound = Py::new(py, interface)?.as_any().clone_ref(py);
                Ok(SampleData::Numpy(bound))
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
            DataType::Pandas => Self::slice_and_return(data, SampleData::Pandas),
            DataType::Polars => Self::slice_and_return(data, SampleData::Polars),
            DataType::Numpy => Self::slice_and_return(data, SampleData::Numpy),
            DataType::Arrow => Self::slice_and_return(data, SampleData::Arrow),
            DataType::TorchTensor => Self::slice_and_return(data, SampleData::Torch),
            _ => Err(SampleDataError::InvalidDataType),
        }
    }

    fn slice_and_return<F>(data: &Bound<'_, PyAny>, constructor: F) -> Result<Self, SampleDataError>
    where
        F: FnOnce(Py<PyAny>) -> SampleData,
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

        Ok(SampleData::List(py_list.clone().unbind()))
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

        Ok(SampleData::Tuple(tuple))
    }

    fn handle_pydict(data: &Bound<'_, PyAny>) -> Result<Self, SampleDataError> {
        let py = data.py();
        let py_dict = data.cast::<PyDict>()?;

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
            SampleData::DMatrix(_) => DataType::DMatrix,
            SampleData::None => DataType::NotProvided,
        }
    }

    pub fn get_data(&self, py: Python) -> Result<Py<PyAny>, SampleDataError> {
        match self {
            SampleData::Pandas(data) => Ok(data.clone_ref(py)),
            SampleData::Polars(data) => Ok(data.clone_ref(py)),
            SampleData::Numpy(data) => Ok(data.clone_ref(py)),
            SampleData::Arrow(data) => Ok(data.clone_ref(py)),
            SampleData::Torch(data) => Ok(data.clone_ref(py)),
            SampleData::List(data) => Ok(data.into_py_any(py).unwrap()),
            SampleData::Tuple(data) => Ok(data.into_py_any(py).unwrap()),
            SampleData::Dict(data) => Ok(data.into_py_any(py).unwrap()),
            SampleData::DMatrix(data) => Ok(data.clone_ref(py)),
            SampleData::None => Ok(py.None()),
        }
    }

    fn save_binary(
        &self,
        data: &Bound<'_, PyAny>,
        path: &Path,
    ) -> Result<PathBuf, SampleDataError> {
        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Bin);
        let full_save_path = path.join(&save_path);
        data.call_method("save_binary", (full_save_path,), None)?;

        Ok(save_path)
    }

    fn save_interface_data(
        &self,
        data: &Bound<'_, PyAny>,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> Result<PathBuf, SampleDataError> {
        debug!("Saving data to path: {:?} with kwargs: {:?}", path, kwargs);
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
            SampleData::Pandas(data) => Ok(Some(
                self.save_interface_data(data.bind(py), path, kwargs)
                    .inspect_err(|e| {
                        error!("Error saving pandas data: {e}");
                    })?,
            )),
            SampleData::Polars(data) => Ok(Some(
                self.save_interface_data(data.bind(py), path, kwargs)
                    .inspect_err(|e| {
                        error!("Error saving polars data: {e}");
                    })?,
            )),
            SampleData::Numpy(data) => Ok(Some(
                self.save_interface_data(data.bind(py), path, kwargs)
                    .inspect_err(|e| {
                        error!("Error saving numpy data: {e}");
                    })?,
            )),
            SampleData::Arrow(data) => Ok(Some(
                self.save_interface_data(data.bind(py), path, kwargs)
                    .inspect_err(|e| {
                        error!("Error saving arrow data: {e}");
                    })?,
            )),
            SampleData::Torch(data) => Ok(Some(
                self.save_interface_data(data.bind(py), path, kwargs)
                    .inspect_err(|e| {
                        error!("Error saving torch data: {e}");
                    })?,
            )),
            SampleData::List(data) => Ok(Some(save_to_joblib(data.bind(py), path).inspect_err(
                |e| {
                    error!("Error saving list data: {e}");
                },
            )?)),
            SampleData::Tuple(data) => Ok(Some(save_to_joblib(data.bind(py), path).inspect_err(
                |e| {
                    error!("Error saving tuple data: {e}");
                },
            )?)),
            SampleData::Dict(data) => Ok(Some(save_to_joblib(data.bind(py), path).inspect_err(
                |e| {
                    error!("Error saving dict data: {e}");
                },
            )?)),
            SampleData::DMatrix(data) => Ok(Some(
                self.save_binary(data.bind(py), path).inspect_err(|e| {
                    error!("Error saving dmatrix data: {e}");
                })?,
            )),
            SampleData::None => Ok(None),
        }
    }

    // helper method for converting all pandas numeric types to f32
    // primarily used with sklearn pipelines and onnx
    fn convert_pandas_to_f32<'py>(
        &self,
        data: Bound<'py, PyAny>,
    ) -> Result<Bound<'py, PyAny>, SampleDataError> {
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

    pub fn load_data<'py>(
        py: Python<'py>,
        path: &Path,
        data_type: &DataType,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> Result<SampleData, SampleDataError> {
        match data_type {
            DataType::Pandas => {
                Ok(PandasData::from_path(py, path, kwargs).map(SampleData::Pandas)?)
            }
            DataType::Polars => {
                Ok(PolarsData::from_path(py, path, kwargs).map(SampleData::Polars)?)
            }
            DataType::Numpy => Ok(NumpyData::from_path(py, path, kwargs).map(SampleData::Numpy)?),
            DataType::Arrow => Ok(ArrowData::from_path(py, path, kwargs).map(SampleData::Arrow)?),
            DataType::TorchTensor => {
                Ok(TorchData::from_path(py, path, kwargs).map(SampleData::Torch)?)
            }
            DataType::List => {
                let data = load_from_joblib(py, path)?;
                Ok(SampleData::List(data.cast::<PyList>()?.clone().unbind()))
            }
            DataType::Tuple => {
                let data = load_from_joblib(py, path)?;
                Ok(SampleData::Tuple(data.cast::<PyTuple>()?.clone().unbind()))
            }
            DataType::Dict => {
                let data = load_from_joblib(py, path)?;
                Ok(SampleData::Dict(data.cast::<PyDict>()?.clone().unbind()))
            }
            DataType::DMatrix => {
                let data = load_dmatrix(py, path)?;
                Ok(SampleData::DMatrix(data.unbind()))
            }

            _ => Ok(SampleData::None),
        }
    }
}

pub fn extract_drift_profile(
    py_profiles: &Bound<'_, PyAny>,
) -> Result<DriftProfileMap, ModelInterfaceError> {
    let py = py_profiles.py();

    if py_profiles.is_instance_of::<PyDict>() {
        let py_profiles = py_profiles.cast::<PyDict>()?;
        let mut profiles = DriftProfileMap::new();

        for (alias, profile) in py_profiles.iter() {
            // For each profile in the list, get its profile attribute
            let alias = alias.extract::<String>()?;
            profiles.add_profile(py, alias, profile)?;
        }

        Ok(profiles)
    } else {
        Err(ModelInterfaceError::DriftProfileMustBeDictionary)
    }
}

pub trait OnnxExtension {
    fn get_data_for_onnx<'py>(
        &self,
        py: Python<'py>,
        model_type: &ModelType,
    ) -> Result<Bound<'py, PyAny>, OnnxError>;

    fn get_feature_names(&self, _py: Python) -> Result<Vec<String>, OnnxError> {
        Ok(vec![])
    }

    fn is_none(&self) -> bool;
}

impl OnnxExtension for SampleData {
    fn get_data_for_onnx<'py>(
        &self,
        py: Python<'py>,
        model_type: &ModelType,
    ) -> Result<Bound<'py, PyAny>, OnnxError> {
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
            SampleData::DMatrix(data) => Ok({
                // need to convert DMatriz to csr and then numpy array
                let dmatrix = data.bind(py);
                dmatrix.call_method0("get_data")?.call_method0("toarray")?
            }),
            SampleData::None => Ok(py.None().bind(py).clone()),
        }
    }

    fn get_feature_names(&self, py: Python) -> Result<Vec<String>, OnnxError> {
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
            SampleData::DMatrix(_) => Ok(vec![]),
        }
    }

    fn is_none(&self) -> bool {
        matches!(self, SampleData::None)
    }
}

/// Parse the save kwargs from the model save kwargs
pub fn parse_save_kwargs<'py>(
    py: Python<'py>,
    save_kwargs: Option<&ModelSaveKwargs>,
) -> SaveKwargsResult<'py> {
    match save_kwargs {
        Some(kwargs) => SaveKwargsResult {
            onnx: kwargs.onnx_kwargs(py).cloned(),
            model: kwargs.model_kwargs(py).cloned(),
            preprocessor: kwargs.preprocessor_kwargs(py).cloned(),
            save_onnx: kwargs.save_onnx(),
        },
        None => SaveKwargsResult::default(),
    }
}

pub fn save_to_joblib(data: &Bound<'_, PyAny>, path: &Path) -> Result<PathBuf, SampleDataError> {
    let py = data.py();
    let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Joblib);
    let full_save_path = path.join(&save_path);
    let joblib = py.import("joblib")?;
    joblib.call_method1("dump", (data, full_save_path))?;

    Ok(save_path)
}

pub fn load_from_joblib<'py>(
    py: Python<'py>,
    path: &Path,
) -> Result<Bound<'py, PyAny>, SampleDataError> {
    let joblib = py.import("joblib")?;
    let data = joblib.call_method1("load", (path,))?;

    Ok(data)
}

fn load_dmatrix<'py>(py: Python<'py>, path: &Path) -> Result<Bound<'py, PyAny>, SampleDataError> {
    let xgb = py.import("xgboost")?;
    let data = xgb.call_method1("DMatrix", (path,))?;
    Ok(data)
}

pub fn get_class_full_name(class: &Bound<'_, PyAny>) -> Result<String, SampleDataError> {
    let module = class.getattr("__module__")?.str()?.to_string();
    let name = class.getattr("__name__")?.str()?.to_string();
    Ok(format!("{module}.{name}"))
}
