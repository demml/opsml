use opsml_error::error::OpsmlError;
use opsml_types::DataType;
use opsml_utils::PyHelperFuncs;
use pyo3::exceptions::PyValueError;
use pyo3::types::{PyDateTime, PyFloat, PyInt, PyString};
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

// remove elements from a that are in b
fn remove_diff<T: PartialEq + Clone>(a: &Vec<T>, b: &Vec<T>) -> Vec<T> {
    a.iter()
        .filter(|x| !b.contains(x))
        .cloned()
        .collect::<Vec<T>>()
}

fn create_data(
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

#[pyclass]
pub struct PolarsColumnSplitter {
    label: String,
    column_split: ColumnSplit,
    dependent_vars: Vec<String>,
}

#[pymethods]
impl PolarsColumnSplitter {
    #[new]
    #[pyo3(signature = (label, column_split, dependent_vars))]
    pub fn new(label: String, column_split: ColumnSplit, dependent_vars: Vec<String>) -> Self {
        PolarsColumnSplitter {
            label,
            column_split,
            dependent_vars,
        }
    }

    pub fn create_split(&self, data: &Bound<'_, PyAny>) -> PyResult<HashMap<String, Data>> {
        let py = data.py();

        // check if polars dataframe
        let polars = py.import("polars")?;

        let column_name = &self.column_split.column_name;
        let value = &self.column_split.column_value.to_py_object(py);

        let filtered_data = match &self.column_split.inequality {
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

        create_data(&self.label, &self.dependent_vars, &filtered_data)
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

        create_data(&self.label, &self.dependent_vars, &sliced_data)
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

        create_data(&self.label, &self.dependent_vars, &sliced_data)
    }
}

#[pyclass]
pub struct DataSplitter {}

#[pymethods]
impl DataSplitter {
    #[new]
    pub fn new() -> Self {
        DataSplitter {}
    }

    #[staticmethod]
    pub fn split_data(
        split: DataSplit,
        data: &Bound<'_, PyAny>,
        data_type: DataType,
        dependent_vars: Vec<String>,
    ) -> PyResult<HashMap<String, Data>> {
        if split.column_split.is_some() && data_type == DataType::Polars {
            let polars_splitter =
                PolarsColumnSplitter::new(split.label, split.column_split.unwrap(), dependent_vars);
            return polars_splitter.create_split(data);
        };

        if split.indice_split.is_some() && data_type == DataType::Polars {
            let polars_splitter =
                PolarsIndexSplitter::new(split.label, split.indice_split.unwrap(), dependent_vars);
            return polars_splitter.create_split(data);
        };

        if split.start_stop_split.is_some() && data_type == DataType::Polars {
            let polars_splitter = PolarsStartStopSplitter::new(
                split.label,
                split.start_stop_split.unwrap(),
                dependent_vars,
            );
            return polars_splitter.create_split(data);
        };

        Ok(HashMap::new())
    }
}
