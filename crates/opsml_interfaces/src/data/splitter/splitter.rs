use std::collections::HashMap;

use pyo3::exceptions::PyValueError;
use pyo3::types::{PyFloat, PyInt, PyString};
use pyo3::PyResult;
use pyo3::{prelude::*, IntoPyObjectExt};
use serde::{Deserialize, Serialize};

#[pyclass(eq)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum ColValType {
    String(String),
    Float(f64),
    Int(i64),
    Timestamp(String),
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
    inequality: Option<String>,
}

#[pymethods]
impl ColumnSplit {
    #[new]
    #[pyo3(signature = (column_value, column_name, column_type, inequality=None))]
    pub fn new(
        column_value: &Bound<'_, PyAny>,
        column_name: String,
        column_type: ColType,
        inequality: Option<String>,
    ) -> PyResult<Self> {
        let mut col_val = None;
        let mut ineq = None;

        if !PyAnyMethods::is_none(column_value) {
            col_val = match column_type {
                ColType::Timestamp => {
                    // column_value must be an isoformat string
                    if column_value.is_instance_of::<PyString>() {
                        Some(ColValType::Timestamp(column_value.extract().unwrap()))
                    } else {
                        return Err(PyValueError::new_err("Invalid timestamp"));
                    }
                }
                ColType::Builtin => {
                    if column_value.is_instance_of::<PyString>() {
                        Some(ColValType::String(column_value.extract().unwrap()))
                    } else if column_value.is_instance_of::<PyFloat>() {
                        Some(ColValType::Float(column_value.extract().unwrap()))
                    } else if column_value.is_instance_of::<PyInt>() {
                        Some(ColValType::Int(column_value.extract().unwrap()))
                    } else {
                        return Err(PyValueError::new_err("Invalid value"));
                    }
                }
            };
        };

        if let Some(inequality) = inequality {
            // strip whitespace
            ineq = Some(inequality.trim().to_string());
        }

        Ok(ColumnSplit {
            column_name,
            column_value: col_val.unwrap(),
            column_type,
            inequality: ineq,
        })
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
}

#[pyclass]
struct DataSplit {
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
    fn new(
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
}

#[pyclass]
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

pub struct PolarsColumnSplitter {
    label: String,
    column_split: ColumnSplit,
    dependent_vars: Option<Vec<String>>,
}

impl PolarsColumnSplitter {
    pub fn new(
        label: String,
        column_split: ColumnSplit,
        dependent_vars: Option<Vec<String>>,
    ) -> Self {
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
        let polars_dataframe = polars.getattr("DataFrame")?;
        if !data.is_instance(&polars_dataframe)? {
            return Err(PyValueError::new_err("data is not a polars DataFrame"));
        }

        let mut data_map = HashMap::new();
        let column_name = &self.column_split.column_name;
        let value = &self.column_split.column_value.to_py_object(py);

        let filtered_data = match &self.column_split.inequality {
            None => data.call_method1(
                "filter",
                (polars
                    .call_method1("col", (column_name,))?
                    .call_method1("eq", (value,))?,),
            )?,
            Some(ineq) if ineq == ">" => data.call_method1(
                "filter",
                (polars
                    .call_method1("col", (column_name,))?
                    .call_method1("gt", (value,))?,),
            )?,
            Some(ineq) if ineq == ">=" => data.call_method1(
                "filter",
                (polars
                    .call_method1("col", (column_name,))?
                    .call_method1("ge", (value,))?,),
            )?,
            Some(ineq) if ineq == "<" => data.call_method1(
                "filter",
                (polars
                    .call_method1("col", (column_name,))?
                    .call_method1("lt", (value,))?,),
            )?,
            Some(_) => data.call_method1(
                "filter",
                (polars
                    .call_method1("col", (column_name,))?
                    .call_method1("le", (value,))?,),
            )?,
        };

        if let Some(dependent_vars) = &self.dependent_vars {
            let columns: Vec<String> = filtered_data.getattr("columns")?.extract()?;
            let x_cols = remove_diff(&columns, dependent_vars);

            data_map.insert(
                self.label.clone(),
                Data {
                    x: filtered_data
                        .call_method1("select", (x_cols,))
                        .unwrap()
                        .into(),
                    y: filtered_data
                        .call_method1("select", (dependent_vars,))
                        .unwrap()
                        .into(),
                },
            );

            return Ok(data_map);
        } else {
            data_map.insert(
                self.label.clone(),
                Data {
                    x: filtered_data.into(),
                    // pyany none
                    y: py.None().into(),
                },
            );

            return Ok(data_map);
        }
    }
}
