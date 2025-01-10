use crate::data::{ArrowData, DataInterface, NumpyData, PandasData, PolarsData};
use opsml_error::{OpsmlError, TypeError};
use opsml_types::DataType;
use pyo3::types::{PyList, PyListMethods, PyTuple, PyTupleMethods};
use pyo3::{prelude::*, types::PySlice};
use serde::{Deserialize, Serialize};

pub struct ListData {
    pub strings: Option<Vec<String>>,
    pub numbers: Option<Vec<i32>>,
    pub floats: Option<Vec<f64>>,
}

impl ListData {
    /// Create a new List object
    pub fn new<'py>(list: &Bound<'py, PyList>) -> PyResult<Self> {
        let list = list.get_item(0).map_err(|e| OpsmlError::new_err(e))?;

        let mut strings = Vec::new();
        let mut numbers = Vec::new();
        let mut floats = Vec::new();

        while let Ok(item) = list.try_iter() {
            if let Ok(string) = item.extract::<String>() {
                strings.push(string);
            } else if let Ok(number) = item.extract::<i32>() {
                numbers.push(number);
            } else if let Ok(float) = item.extract::<f64>() {
                floats.push(float);
            } else {
                return Err(OpsmlError::new_err(
                    "List must contain only strings, numbers, or floats",
                ));
            }
        }

        Ok(ListData {
            strings: Some(strings),
            numbers: Some(numbers),
            floats: Some(floats),
        })
    }
}

pub struct TupleData {
    pub strings: Option<Vec<String>>,
    pub numbers: Option<Vec<i32>>,
    pub floats: Option<Vec<f64>>,
}

impl TupleData {
    /// Create a new Tuple object
    pub fn new<'py>(tuple: &Bound<'py, PyTuple>) -> PyResult<Self> {
        let mut strings = Vec::new();
        let mut numbers = Vec::new();
        let mut floats = Vec::new();

        for item in tuple.iter() {
            if let Ok(string) = item.extract::<String>() {
                strings.push(string);
            } else if let Ok(number) = item.extract::<i32>() {
                numbers.push(number);
            } else if let Ok(float) = item.extract::<f64>() {
                floats.push(float);
            } else {
                return Err(OpsmlError::new_err(
                    "Tuple must contain only strings, numbers, or floats",
                ));
            }
        }

        Ok(TupleData {
            strings: Some(strings),
            numbers: Some(numbers),
            floats: Some(floats),
        })
    }
}

pub struct DictData {
    pub dict: PyObject,
}

pub enum SampleData {
    Pandas(PandasData),
    Polars(PolarsData),
    Numpy(NumpyData),
    Arrow(ArrowData),
    List(ListData),
    Tuple(TupleData),
    Dict(DictData),
}

impl SampleData {
    pub fn new<'py>(data: &Bound<'py, PyAny>) -> PyResult<Self> {
        if data.is_instance_of::<DataInterface>() {
            let data_type = data.getattr("data_type")?.extract::<DataType>()?;
            // match data_type and extract interface
            match data_type {
                DataType::Pandas => {
                    let extracted_data = data.extract::<PandasData>()?;
                    return Ok(SampleData::Pandas(extracted_data));
                }
                DataType::Polars => {
                    let extracted_data = data.extract::<PolarsData>()?;
                    return Ok(SampleData::Polars(extracted_data));
                }
                DataType::Numpy => {
                    let extracted_data = data.extract::<NumpyData>()?;
                    return Ok(SampleData::Numpy(extracted_data));
                }
                DataType::Arrow => {
                    let extracted_data = data.extract::<ArrowData>()?;
                    return Ok(SampleData::Arrow(extracted_data));
                }

                _ => return Err(OpsmlError::new_err("Data type not supported")),
            }
        }
        Err(OpsmlError::new_err("Data type not supported"))
    }
}
