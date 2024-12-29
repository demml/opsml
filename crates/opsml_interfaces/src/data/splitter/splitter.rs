use opsml_error::error::OpsmlError;
use opsml_types::DataType;
use opsml_utils::PyHelperFuncs;
use pyo3::exceptions::PyValueError;
use pyo3::types::{PyDateTime, PyFloat, PyInt, PySlice, PyString};
use pyo3::PyResult;
use pyo3::{prelude::*, IntoPyObjectExt};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[pyclass(eq)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum Inequality {
    Equal,
    GreaterThan,
    GreaterThanEqual,
    LesserThan,
    LesserThanEqual,
}

#[pymethods]
impl Inequality {
    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

impl From<&str> for Inequality {
    fn from(s: &str) -> Self {
        match s {
            "==" => Inequality::Equal,
            ">" => Inequality::GreaterThan,
            ">=" => Inequality::GreaterThanEqual,
            "<" => Inequality::LesserThan,
            "<=" => Inequality::LesserThanEqual,
            _ => Inequality::GreaterThan,
        }
    }
}

#[pyclass(eq)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum ColValType {
    String(String),
    Float(f64),
    Int(i64),
    Timestamp(f64),
}

impl ColValType {
    pub fn to_py_object(&self, py: Python) -> PyObject {
        match self {
            ColValType::String(val) => val.into_py_any(py).unwrap(),
            ColValType::Float(val) => val.into_py_any(py).unwrap(),
            ColValType::Int(val) => val.into_py_any(py).unwrap(),
            ColValType::Timestamp(val) => val.into_py_any(py).unwrap(),
        }
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize, Default)]
pub enum ColType {
    #[default]
    Builtin,
    Timestamp,
}

#[pyclass(eq)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct ColumnSplit {
    #[pyo3(get, set)]
    column_name: String,
    #[pyo3(get, set)]
    column_value: ColValType,
    #[pyo3(get, set)]
    column_type: ColType,
    #[pyo3(get, set)]
    inequality: Inequality,
}

#[pymethods]
impl ColumnSplit {
    #[new]
    #[pyo3(signature = (column_name, column_value, column_type, inequality=None))]
    pub fn new(
        column_name: String,
        column_value: &Bound<'_, PyAny>,
        column_type: ColType,
        inequality: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Self> {
        let py = column_value.py();
        let fallback_ineq = PyString::new(py, "==");
        let inequality = inequality.unwrap_or(&fallback_ineq);

        let ineq: Inequality = if let Ok(ineq_str) = inequality.extract::<String>() {
            ineq_str.as_str().into()
        } else if let Ok(ineq_enum) = inequality.extract::<Inequality>() {
            ineq_enum
        } else {
            Inequality::Equal
        };

        let col_val = match column_type {
            ColType::Timestamp => {
                if column_value.is_instance_of::<PyFloat>() {
                    let timestamp: f64 = column_value.extract()?;
                    PyDateTime::from_timestamp(py, timestamp, None).map_err(|e| {
                        OpsmlError::new_err(format!("Failed to convert timestamp: {}", e))
                    })?;
                    ColValType::Timestamp(timestamp)
                } else {
                    return Err(OpsmlError::new_err("Invalid timestamp"));
                }
            }
            ColType::Builtin => {
                if column_value.is_instance_of::<PyString>() {
                    ColValType::String(column_value.extract()?)
                } else if column_value.is_instance_of::<PyFloat>() {
                    ColValType::Float(column_value.extract()?)
                } else if column_value.is_instance_of::<PyInt>() {
                    ColValType::Int(column_value.extract()?)
                } else {
                    return Err(OpsmlError::new_err(
                        "Invalid value type. Supported types are String, Float, Int",
                    ));
                }
            }
        };

        Ok(ColumnSplit {
            column_name,
            column_value: col_val,
            column_type,
            inequality: ineq,
        })
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass(eq)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct StartStopSplit {
    #[pyo3(get, set)]
    start: i64,
    #[pyo3(get, set)]
    stop: i64,
}

#[pymethods]
impl StartStopSplit {
    #[new]
    pub fn new(start: i64, stop: i64) -> Self {
        StartStopSplit { start, stop }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass(eq)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct IndiceSplit {
    #[pyo3(get, set)]
    indices: Vec<i64>,
}

#[pymethods]
impl IndiceSplit {
    #[new]
    pub fn new(indices: Vec<i64>) -> Self {
        IndiceSplit { indices }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct DataSplit {
    #[pyo3(get, set)]
    label: String,
    #[pyo3(get, set)]
    column_split: Option<ColumnSplit>,
    #[pyo3(get, set)]
    start_stop_split: Option<StartStopSplit>,
    #[pyo3(get, set)]
    indice_split: Option<IndiceSplit>,
}

#[pymethods]
impl DataSplit {
    #[new]
    #[pyo3(signature = (label, column_split=None, start_stop_split=None, indice_split=None))]
    pub fn new(
        label: String,
        column_split: Option<ColumnSplit>,
        start_stop_split: Option<StartStopSplit>,
        indice_split: Option<IndiceSplit>,
    ) -> PyResult<Self> {
        // check that only one of the splits is provided
        let mut count = 0;
        if column_split.is_some() {
            count += 1;
        }
        if start_stop_split.is_some() {
            count += 1;
        }
        if indice_split.is_some() {
            count += 1;
        }

        if count > 1 {
            return Err(PyValueError::new_err("Only one split type can be provided"));
        }

        // check if at least 1 split type is provided
        if count == 0 {
            return Err(PyValueError::new_err(
                "At least one split type must be provided",
            ));
        }

        Ok(DataSplit {
            label,
            column_split,
            start_stop_split,
            indice_split,
        })
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass]
#[derive(Debug)]
pub struct Data {
    #[pyo3(get)]
    x: PyObject,

    #[pyo3(get)]
    y: PyObject,
}

fn remove_diff<T: PartialEq + Clone>(a: &Vec<T>, b: &Vec<T>) -> Vec<T> {
    a.iter()
        .filter(|x| !b.contains(x))
        .cloned()
        .collect::<Vec<T>>()
}

fn create_polars_data(
    label: &str,
    dependent_vars: &Vec<String>,
    data: &Bound<'_, PyAny>,
) -> PyResult<HashMap<String, Data>> {
    let py = data.py();
    let mut data_map = HashMap::new();
    if !dependent_vars.is_empty() {
        let columns: Vec<String> = data.getattr("columns")?.extract()?;
        let x_cols = remove_diff(&columns, &dependent_vars);

        data_map.insert(
            label.to_string(),
            Data {
                x: data.call_method1("select", (x_cols,)).unwrap().into(),
                y: data
                    .call_method1("select", (&dependent_vars,))
                    .unwrap()
                    .into(),
            },
        );

        return Ok(data_map);
    } else {
        data_map.insert(
            label.to_string(),
            Data {
                x: data.into_py_any(py)?,
                // pyany none
                y: py.None().into(),
            },
        );

        return Ok(data_map);
    }
}

fn create_pandas_data(
    label: &str,
    dependent_vars: &Vec<String>,
    data: &Bound<'_, PyAny>,
) -> PyResult<HashMap<String, Data>> {
    let py = data.py();
    let mut data_map = HashMap::new();
    if !dependent_vars.is_empty() {
        let columns: Vec<String> = data.getattr("columns")?.extract()?;
        let x_cols = remove_diff(&columns, &dependent_vars);

        data_map.insert(
            label.to_string(),
            Data {
                x: data.get_item(x_cols)?.into(),
                y: data.get_item(&dependent_vars.clone())?.into(),
            },
        );

        return Ok(data_map);
    } else {
        data_map.insert(
            label.to_string(),
            Data {
                x: data.into_py_any(py)?,
                // pyany none
                y: py.None().into(),
            },
        );

        return Ok(data_map);
    }
}

pub struct PolarsColumnSplitter {}

impl PolarsColumnSplitter {
    pub fn create_split(
        data: &Bound<'_, PyAny>,
        label: &str,
        column_split: &ColumnSplit,
        dependent_vars: &Vec<String>,
    ) -> PyResult<HashMap<String, Data>> {
        let py = data.py();

        // check if polars dataframe
        let polars = py.import("polars")?;

        let column_name = &column_split.column_name;
        let value = column_split.column_value.to_py_object(py);

        let filtered_data = match column_split.inequality {
            Inequality::Equal => data.call_method1(
                "filter",
                (polars
                    .call_method1("col", (column_name,))?
                    .call_method1("eq", (value,))?,),
            )?,
            Inequality::GreaterThan => data.call_method1(
                "filter",
                (polars
                    .call_method1("col", (column_name,))?
                    .call_method1("gt", (value,))?,),
            )?,
            Inequality::GreaterThanEqual => data.call_method1(
                "filter",
                (polars
                    .call_method1("col", (column_name,))?
                    .call_method1("ge", (value,))?,),
            )?,
            Inequality::LesserThan => data.call_method1(
                "filter",
                (polars
                    .call_method1("col", (column_name,))?
                    .call_method1("lt", (value,))?,),
            )?,
            Inequality::LesserThanEqual => data.call_method1(
                "filter",
                (polars
                    .call_method1("col", (column_name,))?
                    .call_method1("le", (value,))?,),
            )?,
        };

        create_polars_data(label, &dependent_vars, &filtered_data)
    }
}

#[pyclass]
pub struct PolarsIndexSplitter {
    label: String,
    indice_split: IndiceSplit,
    dependent_vars: Vec<String>,
}

#[pymethods]
impl PolarsIndexSplitter {
    #[new]
    #[pyo3(signature = (label, indice_split, dependent_vars))]
    pub fn new(label: String, indice_split: IndiceSplit, dependent_vars: Vec<String>) -> Self {
        PolarsIndexSplitter {
            label,
            indice_split,
            dependent_vars,
        }
    }

    pub fn create_split(&self, data: &Bound<'_, PyAny>) -> PyResult<HashMap<String, Data>> {
        let py = data.py();

        let indices = self.indice_split.indices.clone().into_py_any(py).unwrap();
        let sliced_data = data.get_item(indices)?;

        create_polars_data(&self.label, &self.dependent_vars, &sliced_data)
    }
}

#[pyclass]
pub struct PolarsStartStopSplitter {
    label: String,
    start_stop_split: StartStopSplit,
    dependent_vars: Vec<String>,
}

#[pymethods]
impl PolarsStartStopSplitter {
    #[new]
    #[pyo3(signature = (label, start_stop_split, dependent_vars))]
    pub fn new(
        label: String,
        start_stop_split: StartStopSplit,
        dependent_vars: Vec<String>,
    ) -> Self {
        PolarsStartStopSplitter {
            label,
            start_stop_split,
            dependent_vars,
        }
    }

    pub fn create_split(&self, data: &Bound<'_, PyAny>) -> PyResult<HashMap<String, Data>> {
        // Slice the DataFrame using the start and stop indices
        let start = self.start_stop_split.start;
        let stop = self.start_stop_split.stop;
        let slice_len = stop - start;

        let sliced_data = data.call_method1("slice", (start, slice_len))?;

        create_polars_data(&self.label, &self.dependent_vars, &sliced_data)
    }
}

#[pyclass]
pub struct PandasColumnSplitter {
    label: String,
    column_split: ColumnSplit,
    dependent_vars: Vec<String>,
}

#[pymethods]
impl PandasColumnSplitter {
    #[new]
    #[pyo3(signature = (label, column_split, dependent_vars))]
    pub fn new(label: String, column_split: ColumnSplit, dependent_vars: Vec<String>) -> Self {
        PandasColumnSplitter {
            label,
            column_split,
            dependent_vars,
        }
    }

    pub fn create_split(&self, data: &Bound<'_, PyAny>) -> PyResult<HashMap<String, Data>> {
        let py = data.py();

        // check if polars dataframe
        let pandas = py.import("pandas")?;

        let column_name = &self.column_split.column_name;

        // if column type is timestamp, convert to datetime
        let value = match &self.column_split.column_type {
            ColType::Timestamp => {
                let timestamp = self.column_split.column_value.to_py_object(py);
                pandas
                    .call_method1("Timestamp", (timestamp,))?
                    .into_py_any(py)?
            }
            _ => self.column_split.column_value.to_py_object(py),
        };

        let filtered_data = match self.column_split.inequality {
            Inequality::Equal => data.call_method1(
                "__getitem__",
                (data.get_item(column_name)?.call_method1("eq", (value,))?,),
            )?,
            Inequality::GreaterThan => data.call_method1(
                "__getitem__",
                (data.get_item(column_name)?.call_method1("gt", (value,))?,),
            )?,
            Inequality::GreaterThanEqual => data.call_method1(
                "__getitem__",
                (data.get_item(column_name)?.call_method1("ge", (value,))?,),
            )?,
            Inequality::LesserThan => data.call_method1(
                "__getitem__",
                (data.get_item(column_name)?.call_method1("lt", (value,))?,),
            )?,
            Inequality::LesserThanEqual => data.call_method1(
                "__getitem__",
                (data.get_item(column_name)?.call_method1("le", (value,))?,),
            )?,
        };

        create_pandas_data(&self.label, &self.dependent_vars, &filtered_data)
    }
}

#[pyclass]
pub struct PandasIndexSplitter {
    label: String,
    indice_split: IndiceSplit,
    dependent_vars: Vec<String>,
}

#[pymethods]
impl PandasIndexSplitter {
    #[new]
    #[pyo3(signature = (label, indice_split, dependent_vars))]
    pub fn new(label: String, indice_split: IndiceSplit, dependent_vars: Vec<String>) -> Self {
        PandasIndexSplitter {
            label,
            indice_split,
            dependent_vars,
        }
    }

    pub fn create_split(&self, data: &Bound<'_, PyAny>) -> PyResult<HashMap<String, Data>> {
        let py = data.py();

        let indices = self.indice_split.indices.clone().into_py_any(py).unwrap();
        let sliced_data = data
            .getattr("iloc")?
            .call_method1("__getitem__", (indices,))?; // iloc is used to slice the dataframe

        create_pandas_data(&self.label, &self.dependent_vars, &sliced_data)
    }
}

#[pyclass]
pub struct PandasStartStopSplitter {
    label: String,
    start_stop_split: StartStopSplit,
    dependent_vars: Vec<String>,
}

#[pymethods]
impl PandasStartStopSplitter {
    #[new]
    #[pyo3(signature = (label, start_stop_split, dependent_vars))]
    pub fn new(
        label: String,
        start_stop_split: StartStopSplit,
        dependent_vars: Vec<String>,
    ) -> Self {
        PandasStartStopSplitter {
            label,
            start_stop_split,
            dependent_vars,
        }
    }

    pub fn create_split(&self, data: &Bound<'_, PyAny>) -> PyResult<HashMap<String, Data>> {
        // Slice the DataFrame using the start and stop indices
        let py = data.py();
        let start = self.start_stop_split.start as isize;
        let stop = self.start_stop_split.stop as isize;
        let slice = PySlice::new(py, start, stop, 1);

        let sliced_data = data.get_item(slice)?;

        create_pandas_data(&self.label, &self.dependent_vars, &sliced_data)
    }
}

#[pyclass]
pub struct PyArrowIndexSplitter {
    label: String,
    indice_split: IndiceSplit,
}

#[pymethods]
impl PyArrowIndexSplitter {
    #[new]
    #[pyo3(signature = (label, indice_split))]
    pub fn new(label: String, indice_split: IndiceSplit) -> Self {
        PyArrowIndexSplitter {
            label,
            indice_split,
        }
    }

    pub fn create_split(&self, data: &Bound<'_, PyAny>) -> PyResult<HashMap<String, Data>> {
        let py = data.py();

        let indices = self.indice_split.indices.clone().into_py_any(py).unwrap();
        let sliced_data = data.call_method1("take", (indices,))?;

        let mut map = HashMap::new();

        map.insert(
            self.label.clone(),
            Data {
                x: sliced_data.into(),
                y: py.None().into(),
            },
        );

        Ok(map)
    }
}

#[pyclass]
pub struct PyArrowStartStopSplitter {
    label: String,
    start_stop_split: StartStopSplit,
}

#[pymethods]
impl PyArrowStartStopSplitter {
    #[new]
    #[pyo3(signature = (label, start_stop_split))]
    pub fn new(label: String, start_stop_split: StartStopSplit) -> Self {
        PyArrowStartStopSplitter {
            label,
            start_stop_split,
        }
    }

    pub fn create_split(&self, data: &Bound<'_, PyAny>) -> PyResult<HashMap<String, Data>> {
        // Slice the DataFrame using the start and stop indices
        let py = data.py();
        let start = self.start_stop_split.start;
        let stop = self.start_stop_split.stop;
        let slice_len = stop - start;

        let sliced_data = data.call_method1("slice", (start, slice_len))?;

        let mut map = HashMap::new();

        map.insert(
            self.label.clone(),
            Data {
                x: sliced_data.into(),
                y: py.None().into(),
            },
        );

        Ok(map)
    }
}

pub struct NumpyIndexSplitter {
    label: String,
    indice_split: IndiceSplit,
}

impl NumpyIndexSplitter {
    pub fn new(label: String, indice_split: IndiceSplit) -> Self {
        NumpyIndexSplitter {
            label,
            indice_split,
        }
    }

    pub fn create_split(&self, data: &Bound<'_, PyAny>) -> PyResult<HashMap<String, Data>> {
        let py = data.py();

        let indices = self.indice_split.indices.clone().into_py_any(py).unwrap();
        let sliced_data = data.call_method1("__getitem__", (indices,))?;

        let mut map = HashMap::new();

        map.insert(
            self.label.clone(),
            Data {
                x: sliced_data.into(),
                y: py.None().into(),
            },
        );

        Ok(map)
    }
}

pub struct NumpyStartStopSplitter {
    label: String,
    start_stop_split: StartStopSplit,
}

impl NumpyStartStopSplitter {
    pub fn new(label: String, start_stop_split: StartStopSplit) -> Self {
        NumpyStartStopSplitter {
            label,
            start_stop_split,
        }
    }

    pub fn create_split(&self, data: &Bound<'_, PyAny>) -> PyResult<HashMap<String, Data>> {
        // Slice the DataFrame using the start and stop indices
        let py = data.py();
        let start = self.start_stop_split.start as isize;
        let stop = self.start_stop_split.stop as isize;
        let slice = PySlice::new(py, start, stop, 1);

        let sliced_data = data.get_item(slice)?;

        let mut map = HashMap::new();

        map.insert(
            self.label.clone(),
            Data {
                x: sliced_data.into(),
                y: py.None().into(),
            },
        );

        Ok(map)
    }
}

#[pyclass]
pub struct DataSplitter {}

#[pymethods]
impl DataSplitter {
    #[staticmethod]
    #[pyo3(signature = (split, data, data_type, dependent_vars=None))]
    pub fn split_data(
        split: &DataSplit,
        data: &Bound<'_, PyAny>,
        data_type: DataType,
        dependent_vars: Option<Vec<String>>,
    ) -> PyResult<HashMap<String, Data>> {
        let dep_vars = dependent_vars.unwrap_or_default();
        if split.column_split.is_some() {
            match data_type {
                DataType::Polars => {
                    return PolarsColumnSplitter::create_split(
                        data,
                        &split.label,
                        &split.column_split.as_ref().unwrap(),
                        &dep_vars,
                    );
                }
                DataType::Pandas => {
                    let pandas_splitter = PandasColumnSplitter::new(
                        split.label,
                        split.column_split.unwrap(),
                        dep_vars,
                    );
                    return pandas_splitter.create_split(data);
                }
                _ => {}
            }
        };

        if split.indice_split.is_some() {
            match data_type {
                DataType::Polars => {
                    let polars_splitter = PolarsIndexSplitter::new(
                        split.label,
                        split.indice_split.unwrap(),
                        dep_vars,
                    );
                    return polars_splitter.create_split(data);
                }
                DataType::Pandas => {
                    let pandas_splitter = PandasIndexSplitter::new(
                        split.label,
                        split.indice_split.unwrap(),
                        dep_vars,
                    );
                    return pandas_splitter.create_split(data);
                }
                DataType::PyArrow => {
                    let pyarrow_splitter =
                        PyArrowIndexSplitter::new(split.label, split.indice_split.unwrap());
                    return pyarrow_splitter.create_split(data);
                }
                DataType::Numpy => {
                    let numpy_splitter =
                        NumpyIndexSplitter::new(split.label, split.indice_split.unwrap());
                    return numpy_splitter.create_split(data);
                }
                _ => {}
            }
        };

        if split.start_stop_split.is_some() {
            match data_type {
                DataType::Polars => {
                    let polars_splitter = PolarsStartStopSplitter::new(
                        split.label,
                        split.start_stop_split.unwrap(),
                        dep_vars,
                    );
                    return polars_splitter.create_split(data);
                }
                DataType::Pandas => {
                    let pandas_splitter = PandasStartStopSplitter::new(
                        split.label,
                        split.start_stop_split.unwrap(),
                        dep_vars,
                    );
                    return pandas_splitter.create_split(data);
                }
                DataType::PyArrow => {
                    let pyarrow_splitter =
                        PyArrowStartStopSplitter::new(split.label, split.start_stop_split.unwrap());
                    return pyarrow_splitter.create_split(data);
                }
                DataType::Numpy => {
                    let numpy_splitter =
                        NumpyStartStopSplitter::new(split.label, split.start_stop_split.unwrap());
                    return numpy_splitter.create_split(data);
                }
                _ => {}
            }
        };

        Ok(HashMap::new())
    }
}
