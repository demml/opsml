use crate::data::DependentVars;
use crate::error::DataInterfaceError;
use opsml_types::DataType;
use opsml_utils::PyHelperFuncs;
use pyo3::types::PyTuple;
use pyo3::types::{PyDateTime, PyFloat, PyInt, PySlice, PyString};
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
    pub fn to_py_object(&self, py: Python) -> Py<PyAny> {
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
    #[pyo3(signature = (column_name, column_value, column_type=ColType::Builtin, inequality=None))]
    pub fn new(
        column_name: String,
        column_value: &Bound<'_, PyAny>,
        column_type: ColType,
        inequality: Option<&Bound<'_, PyAny>>,
    ) -> Result<Self, DataInterfaceError> {
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
                    PyDateTime::from_timestamp(py, timestamp, None)?;
                    ColValType::Timestamp(timestamp)
                } else {
                    return Err(DataInterfaceError::InvalidTimeStamp);
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
                    return Err(DataInterfaceError::InvalidType);
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
    pub label: String,
    #[pyo3(get, set)]
    pub column_split: Option<ColumnSplit>,
    #[pyo3(get, set)]
    pub start_stop_split: Option<StartStopSplit>,
    #[pyo3(get, set)]
    pub indice_split: Option<IndiceSplit>,
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
    ) -> Result<Self, DataInterfaceError> {
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
            return Err(DataInterfaceError::OnlyOneSplitError);
        }

        // check if at least 1 split type is provided
        if count == 0 {
            return Err(DataInterfaceError::AtLeastOneSplitError);
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
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize, Default)]
pub struct DataSplits {
    #[pyo3(get, set)]
    pub splits: Vec<DataSplit>,
}

#[pymethods]
impl DataSplits {
    #[new]
    pub fn new(splits: Vec<DataSplit>) -> Self {
        DataSplits { splits }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }

    pub fn split_data(
        &self,
        data: &Bound<'_, PyAny>,
        data_type: &DataType,
        dependent_vars: &DependentVars,
    ) -> Result<HashMap<String, Data>, DataInterfaceError> {
        let mut split_data = HashMap::new();

        for split in &self.splits {
            let data = DataSplitter::split_data(split, data, data_type, dependent_vars)?;
            split_data.insert(split.label.clone(), data);
        }

        Ok(split_data)
    }
}

impl DataSplits {
    pub fn is_empty(&self) -> bool {
        self.splits.is_empty()
    }
}

#[pyclass]
#[derive(Debug)]
pub struct Data {
    #[pyo3(get)]
    x: Py<PyAny>,

    #[pyo3(get)]
    y: Py<PyAny>,
}

fn remove_diff<T: PartialEq + Clone>(a: &[T], b: &[T]) -> Vec<T> {
    a.iter()
        .filter(|x| !b.contains(x))
        .cloned()
        .collect::<Vec<T>>()
}

fn create_polars_data(
    dependent_vars: &DependentVars,
    data: &Bound<'_, PyAny>,
) -> Result<Data, DataInterfaceError> {
    let py = data.py();

    if !dependent_vars.column_empty() {
        let columns: Vec<String> = data.getattr("columns")?.extract()?;
        let x_cols = remove_diff(&columns, &dependent_vars.column_names);

        Ok(Data {
            x: data.call_method1("select", (x_cols,)).unwrap().into(),
            y: data
                .call_method1("select", (&dependent_vars.column_names,))
                .unwrap()
                .into(),
        })
    } else {
        Ok(Data {
            x: data.into_py_any(py)?,
            // pyany none
            y: py.None(),
        })
    }
}

fn create_pandas_data(
    dependent_vars: &DependentVars,
    data: &Bound<'_, PyAny>,
) -> Result<Data, DataInterfaceError> {
    let py = data.py();
    if !dependent_vars.column_empty() {
        let columns: Vec<String> = data.getattr("columns")?.extract()?;
        let x_cols = remove_diff(&columns, &dependent_vars.column_names);

        Ok(Data {
            x: data.get_item(x_cols)?.into(),
            y: data.get_item(&dependent_vars.column_names)?.into(),
        })
    } else {
        Ok(Data {
            x: data.into_py_any(py)?,
            // pyany none
            y: py.None(),
        })
    }
}

fn create_pyarrow_data(
    dependent_vars: &DependentVars,
    data: &Bound<'_, PyAny>,
) -> Result<Data, DataInterfaceError> {
    let py = data.py();
    if !dependent_vars.column_empty() {
        let columns: Vec<String> = data.getattr("column_names")?.extract()?;
        let x_cols = remove_diff(&columns, &dependent_vars.column_names);

        Ok(Data {
            x: data.call_method1("select", (x_cols,))?.into(),
            y: data
                .call_method1("select", (&dependent_vars.column_names,))?
                .into(),
        })
    } else if !dependent_vars.idx_empty() {
        let shape = data.getattr("shape")?;
        let shape_tuple = shape.cast::<PyTuple>()?;

        let num_cols = shape_tuple.get_item(1).unwrap().extract::<usize>()?;

        // create range list from 0 to num_cols
        let x_cols: Vec<usize> = (0..num_cols).collect();
        let y_cols = dependent_vars.get_column_indices();

        // remove y_cols from x_cols
        let x_cols = remove_diff(&x_cols, &y_cols);

        Ok(Data {
            x: data.call_method1("select", (x_cols,))?.into(),
            y: data.call_method1("select", (y_cols,))?.into(),
        })
    } else {
        Ok(Data {
            x: data.into_py_any(py)?,
            // pyany none
            y: py.None(),
        })
    }
}

fn create_numpy_data(
    dependent_vars: &DependentVars,
    data: &Bound<'_, PyAny>,
) -> Result<Data, DataInterfaceError> {
    let py = data.py();
    if !dependent_vars.idx_empty() {
        let shape = data.getattr("shape")?;
        let shape_tuple = shape.cast::<PyTuple>()?;

        let num_cols = shape_tuple.get_item(1).unwrap().extract::<usize>()?;

        // create range list from 0 to num_cols
        let x_cols: Vec<usize> = (0..num_cols).collect();
        let y_cols = dependent_vars.get_column_indices();

        // remove y_cols from x_cols
        let x_cols = remove_diff(&x_cols, &y_cols);

        Ok(Data {
            x: data.call_method1("take", (x_cols, 1))?.into(),
            y: data.call_method1("take", (y_cols, 1))?.into(),
        })
    } else {
        Ok(Data {
            x: data.into_py_any(py)?,

            y: py.None(),
        })
    }
}

pub struct PolarsColumnSplitter {}

impl PolarsColumnSplitter {
    pub fn create_split(
        data: &Bound<'_, PyAny>,
        column_split: &ColumnSplit,
        dependent_vars: &DependentVars,
    ) -> Result<Data, DataInterfaceError> {
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

        create_polars_data(dependent_vars, &filtered_data)
    }
}

pub struct PolarsIndexSplitter {}

impl PolarsIndexSplitter {
    pub fn create_split(
        data: &Bound<'_, PyAny>,
        indice_split: &IndiceSplit,
        dependent_vars: &DependentVars,
    ) -> Result<Data, DataInterfaceError> {
        let py = data.py();

        let indices = &indice_split.indices;
        let sliced_data = data.get_item(indices.into_py_any(py).unwrap())?;

        create_polars_data(dependent_vars, &sliced_data)
    }
}

pub struct PolarsStartStopSplitter {}

impl PolarsStartStopSplitter {
    pub fn create_split(
        data: &Bound<'_, PyAny>,
        start_stop_split: &StartStopSplit,
        dependent_vars: &DependentVars,
    ) -> Result<Data, DataInterfaceError> {
        // Slice the DataFrame using the start and stop indices
        let start = &start_stop_split.start;
        let stop = &start_stop_split.stop;
        let slice_len = stop - start;

        let sliced_data = data.call_method1("slice", (start, slice_len))?;

        create_polars_data(dependent_vars, &sliced_data)
    }
}

pub struct PandasColumnSplitter {}

impl PandasColumnSplitter {
    pub fn create_split(
        data: &Bound<'_, PyAny>,
        column_split: &ColumnSplit,
        dependent_vars: &DependentVars,
    ) -> Result<Data, DataInterfaceError> {
        let py = data.py();

        // check if polars dataframe
        let pandas = py.import("pandas")?;

        let column_name = &column_split.column_name;

        // if column type is timestamp, convert to datetime
        let value = match column_split.column_type {
            ColType::Timestamp => {
                let timestamp = column_split.column_value.to_py_object(py);
                pandas
                    .call_method1("Timestamp", (timestamp,))?
                    .into_py_any(py)?
            }
            _ => column_split.column_value.to_py_object(py),
        };

        let filtered_data = match column_split.inequality {
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

        create_pandas_data(dependent_vars, &filtered_data)
    }
}

pub struct PandasIndexSplitter {}

impl PandasIndexSplitter {
    pub fn create_split(
        data: &Bound<'_, PyAny>,
        indice_split: &IndiceSplit,
        dependent_vars: &DependentVars,
    ) -> Result<Data, DataInterfaceError> {
        let py = data.py();

        let indices = &indice_split.indices;

        let sliced_data = data
            .getattr("iloc")?
            .call_method1("__getitem__", (indices.into_py_any(py).unwrap(),))?; // iloc is used to slice the dataframe

        create_pandas_data(dependent_vars, &sliced_data)
    }
}

pub struct PandasStartStopSplitter {}

impl PandasStartStopSplitter {
    pub fn create_split(
        data: &Bound<'_, PyAny>,
        start_stop_split: &StartStopSplit,
        dependent_vars: &DependentVars,
    ) -> Result<Data, DataInterfaceError> {
        // Slice the DataFrame using the start and stop indices
        let py = data.py();
        let start = start_stop_split.start as isize;
        let stop = start_stop_split.stop as isize;
        let slice = PySlice::new(py, start, stop, 1);

        let sliced_data = data.get_item(slice)?;

        create_pandas_data(dependent_vars, &sliced_data)
    }
}

pub struct PyArrowIndexSplitter {}

impl PyArrowIndexSplitter {
    pub fn create_split(
        data: &Bound<'_, PyAny>,
        indice_split: &IndiceSplit,
        dependent_vars: &DependentVars,
    ) -> Result<Data, DataInterfaceError> {
        let py = data.py();

        let indices = &indice_split.indices;
        let sliced_data = data.call_method1("take", (indices.into_py_any(py).unwrap(),))?;

        create_pyarrow_data(dependent_vars, &sliced_data)
    }
}

pub struct PyArrowStartStopSplitter {}

impl PyArrowStartStopSplitter {
    pub fn create_split(
        data: &Bound<'_, PyAny>,
        start_stop_split: &StartStopSplit,
        dependent_vars: &DependentVars,
    ) -> Result<Data, DataInterfaceError> {
        // Slice the DataFrame using the start and stop indices

        let start = &start_stop_split.start;
        let stop = &start_stop_split.stop;
        let slice_len = stop - start;

        let sliced_data = data.call_method1("slice", (start, slice_len))?;

        create_pyarrow_data(dependent_vars, &sliced_data)
    }
}

pub struct NumpyIndexSplitter {}

impl NumpyIndexSplitter {
    pub fn create_split(
        data: &Bound<'_, PyAny>,
        indice_split: &IndiceSplit,
        dependent_vars: &DependentVars,
    ) -> Result<Data, DataInterfaceError> {
        let py = data.py();

        let indices = &indice_split.indices;
        let sliced_data = data.call_method1("__getitem__", (indices.into_py_any(py).unwrap(),))?;

        create_numpy_data(dependent_vars, &sliced_data)
    }
}

pub struct NumpyStartStopSplitter {}

impl NumpyStartStopSplitter {
    pub fn create_split(
        data: &Bound<'_, PyAny>,
        start_stop_split: &StartStopSplit,
        dependent_vars: &DependentVars,
    ) -> Result<Data, DataInterfaceError> {
        // Slice the DataFrame using the start and stop indices
        let py = data.py();
        let start = start_stop_split.start as isize;
        let stop = start_stop_split.stop as isize;
        let slice = PySlice::new(py, start, stop, 1);

        let sliced_data = data.get_item(slice)?;

        create_numpy_data(dependent_vars, &sliced_data)
    }
}

#[pyclass]
pub struct DataSplitter {}

#[pymethods]
impl DataSplitter {
    #[staticmethod]
    #[pyo3(signature = (split, data, data_type, dependent_vars))]
    pub fn split_data(
        split: &DataSplit,
        data: &Bound<'_, PyAny>,
        data_type: &DataType,
        dependent_vars: &DependentVars,
    ) -> Result<Data, DataInterfaceError> {
        if split.column_split.is_some() {
            match data_type {
                DataType::Polars => {
                    return PolarsColumnSplitter::create_split(
                        data,
                        split.column_split.as_ref().unwrap(),
                        dependent_vars,
                    );
                }
                DataType::Pandas => {
                    return PandasColumnSplitter::create_split(
                        data,
                        split.column_split.as_ref().unwrap(),
                        dependent_vars,
                    );
                }
                _ => {}
            }
        };

        if split.indice_split.is_some() {
            match data_type {
                DataType::Polars => {
                    return PolarsIndexSplitter::create_split(
                        data,
                        split.indice_split.as_ref().unwrap(),
                        dependent_vars,
                    );
                }
                DataType::Pandas => {
                    return PandasIndexSplitter::create_split(
                        data,
                        split.indice_split.as_ref().unwrap(),
                        dependent_vars,
                    );
                }
                DataType::Arrow => {
                    return PyArrowIndexSplitter::create_split(
                        data,
                        split.indice_split.as_ref().unwrap(),
                        dependent_vars,
                    );
                }
                DataType::Numpy => {
                    return NumpyIndexSplitter::create_split(
                        data,
                        split.indice_split.as_ref().unwrap(),
                        dependent_vars,
                    );
                }
                _ => {}
            }
        };

        if split.start_stop_split.is_some() {
            match data_type {
                DataType::Polars => {
                    return PolarsStartStopSplitter::create_split(
                        data,
                        split.start_stop_split.as_ref().unwrap(),
                        dependent_vars,
                    );
                }
                DataType::Pandas => {
                    return PandasStartStopSplitter::create_split(
                        data,
                        split.start_stop_split.as_ref().unwrap(),
                        dependent_vars,
                    );
                }
                DataType::Arrow => {
                    return PyArrowStartStopSplitter::create_split(
                        data,
                        split.start_stop_split.as_ref().unwrap(),
                        dependent_vars,
                    );
                }
                DataType::Numpy => {
                    return NumpyStartStopSplitter::create_split(
                        data,
                        split.start_stop_split.as_ref().unwrap(),
                        dependent_vars,
                    );
                }
                _ => {}
            }
        };

        Err(DataInterfaceError::InvalidSplitType)
    }
}
