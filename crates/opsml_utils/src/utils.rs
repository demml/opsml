use chrono::{NaiveDateTime, Timelike};
use colored_json::{Color, ColorMode, ColoredFormatter, PrettyFormatter, Styler};
use opsml_error::error::UtilError;
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::{prelude::*, types::PyAnyMethods};
use regex::Regex;

use pyo3::types::{PyBool, PyDict, PyDictMethods, PyFloat, PyInt, PyList, PyString};
use pyo3::IntoPyObjectExt;
use serde::Serialize;
use serde_json::{json, Value};
use std::path::PathBuf;

use uuid::Uuid;

const PUNCTUATION: &str = "!\"#$%&'()*+,./:;<=>?@[\\]^`{|}~";
const NAME_REPOSITORY_PATTERN: &str = r"^[a-z0-9]+(?:[-a-z0-9]+)*/[-a-z0-9]+$";

pub fn clean_string(input: &str) -> String {
    let pattern = format!("[{}]", regex::escape(PUNCTUATION));
    let re = Regex::new(&pattern.to_string()).unwrap();
    re.replace_all(&input.trim().to_lowercase(), "")
        .to_string()
        .replace("_", "-")
}

pub fn validate_name_repository_pattern(name: &str, repository: &str) -> Result<(), UtilError> {
    let name_repo = format!("{}/{}", name, repository);

    let re = Regex::new(NAME_REPOSITORY_PATTERN)
        .map_err(|_| UtilError::Error("Failed to create regex".to_string()))?;

    if !re.is_match(&name_repo) {
        return Err(UtilError::Error(
            "Invalid name/repository pattern".to_string(),
        ));
    }

    if name.len() > 53 {
        return Err(UtilError::Error("Name is too long".to_string()));
    }

    Ok(())
}

/// Check if a string is a valid UUIDv4
///
/// # Arguments
///
/// * `uid` - A string slice that holds the UUID
///
/// # Returns
///
/// * `bool` - A boolean indicating if the UUID is valid
pub fn is_valid_uuid4(uid: &str) -> Result<bool, UtilError> {
    match Uuid::parse_str(uid) {
        Ok(uuid) => Ok(uuid.get_version_num() == 4),
        Err(_) => Err(UtilError::UuidError),
    }
}

pub fn get_epoch_time_to_search(max_date: &str) -> Result<i64, UtilError> {
    const YEAR_MONTH_DATE: &str = "%Y-%m-%d";

    // Parse the date string into a NaiveDateTime
    let converted_date = NaiveDateTime::parse_from_str(max_date, YEAR_MONTH_DATE)
        .map_err(|_| UtilError::DateError)?;

    // Replace hour, minute, and second to get the max values for the date
    let max_date = converted_date
        .with_hour(23)
        .unwrap()
        .with_minute(59)
        .unwrap()
        .with_second(59)
        .unwrap();

    // Convert NaiveDateTime to timestamp in microseconds
    let timestamp = max_date.and_utc().timestamp() * 1_000_000;

    Ok(timestamp)
}

pub fn get_utc_date() -> String {
    chrono::Utc::now().format("%Y-%m-%d").to_string()
}

pub fn get_utc_timestamp() -> i64 {
    chrono::Utc::now().timestamp()
}

pub fn get_utc_datetime() -> NaiveDateTime {
    chrono::Utc::now().naive_utc()
}

pub struct PyHelperFuncs {}

impl PyHelperFuncs {
    pub fn __str__<T: Serialize>(object: T) -> String {
        match ColoredFormatter::with_styler(
            PrettyFormatter::default(),
            Styler {
                key: Color::Rgb(75, 57, 120).foreground(),
                string_value: Color::Rgb(4, 205, 155).foreground(),
                float_value: Color::Rgb(4, 205, 155).foreground(),
                integer_value: Color::Rgb(4, 205, 155).foreground(),
                bool_value: Color::Rgb(4, 205, 155).foreground(),
                nil_value: Color::Rgb(4, 205, 155).foreground(),
                ..Default::default()
            },
        )
        .to_colored_json(&object, ColorMode::On)
        {
            Ok(json) => json,
            Err(e) => format!("Failed to serialize to json: {}", e),
        }
        // serialize the struct to a string
    }

    pub fn __json__<T: Serialize>(object: T) -> String {
        match serde_json::to_string_pretty(&object) {
            Ok(json) => json,
            Err(e) => format!("Failed to serialize to json: {}", e),
        }
    }

    pub fn save_to_json<T>(model: T, mut path: PathBuf) -> Result<(), UtilError>
    where
        T: Serialize,
    {
        // serialize the struct to a string
        let json =
            serde_json::to_string_pretty(&model).map_err(|_| UtilError::SerializationError)?;

        // ensure .json extension
        path.set_extension("json");

        if !path.exists() {
            // ensure path exists, create if not
            let parent_path = path.parent().ok_or(UtilError::GetParentPathError)?;

            std::fs::create_dir_all(parent_path).map_err(|_| UtilError::CreateDirectoryError)?;
        }

        std::fs::write(path, json).map_err(|_| UtilError::WriteError)?;

        Ok(())
    }
}

pub fn json_to_pyobject(py: Python, value: &Value, dict: &Bound<'_, PyDict>) -> PyResult<()> {
    match value {
        Value::Object(map) => {
            for (k, v) in map {
                let py_value = match v {
                    Value::Null => py.None(),
                    Value::Bool(b) => b.into_py_any(py).unwrap(),
                    Value::Number(n) => {
                        if let Some(i) = n.as_i64() {
                            i.into_py_any(py).unwrap()
                        } else if let Some(f) = n.as_f64() {
                            f.into_py_any(py).unwrap()
                        } else {
                            return Err(PyValueError::new_err("Invalid number"));
                        }
                    }
                    Value::String(s) => s.into_py_any(py).unwrap(),
                    Value::Array(arr) => {
                        let py_list = PyList::empty(py);
                        for item in arr {
                            let py_item = json_to_pyobject_value(py, item)?;
                            py_list.append(py_item)?;
                        }
                        py_list.into_py_any(py).unwrap()
                    }
                    Value::Object(_) => {
                        let nested_dict = PyDict::new(py);
                        json_to_pyobject(py, v, &nested_dict)?;
                        nested_dict.into_py_any(py).unwrap()
                    }
                };
                dict.set_item(k, py_value)?;
            }
        }
        _ => return Err(PyValueError::new_err("Root must be an object")),
    }
    Ok(())
}

pub fn json_to_pyobject_value(py: Python, value: &Value) -> PyResult<PyObject> {
    Ok(match value {
        Value::Null => py.None(),
        Value::Bool(b) => b.into_py_any(py).unwrap(),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                i.into_py_any(py).unwrap()
            } else if let Some(f) = n.as_f64() {
                f.into_py_any(py).unwrap()
            } else {
                return Err(PyValueError::new_err("Invalid number"));
            }
        }
        Value::String(s) => s.into_py_any(py).unwrap(),
        Value::Array(arr) => {
            let py_list = PyList::empty(py);
            for item in arr {
                let py_item = json_to_pyobject_value(py, item)?;
                py_list.append(py_item)?;
            }
            py_list.into_py_any(py).unwrap()
        }
        Value::Object(_) => {
            let nested_dict = PyDict::new(py);
            json_to_pyobject(py, value, &nested_dict)?;
            nested_dict.into_py_any(py).unwrap()
        }
    })
}

pub fn pyobject_to_json(obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    if obj.is_instance_of::<PyDict>() {
        let dict = obj.downcast::<PyDict>()?;
        let mut map = serde_json::Map::new();
        for (key, value) in dict.iter() {
            let key_str = key.extract::<String>()?;
            let json_value = pyobject_to_json(&value)?;
            map.insert(key_str, json_value);
        }
        Ok(Value::Object(map))
    } else if obj.is_instance_of::<PyList>() {
        let list = obj.downcast::<PyList>()?;
        let mut vec = Vec::new();
        for item in list.iter() {
            vec.push(pyobject_to_json(&item)?);
        }
        Ok(Value::Array(vec))
    } else if obj.is_instance_of::<PyString>() {
        let s = obj.extract::<String>()?;
        Ok(Value::String(s))
    } else if obj.is_instance_of::<PyFloat>() {
        let f = obj.extract::<f64>()?;
        Ok(json!(f))
    } else if obj.is_instance_of::<PyBool>() {
        let b = obj.extract::<bool>()?;
        Ok(json!(b))
    } else if obj.is_instance_of::<PyInt>() {
        let i = obj.extract::<i64>()?;
        Ok(json!(i))
    } else if obj.is_none() {
        Ok(Value::Null)
    } else {
        Err(PyTypeError::new_err(format!(
            "Unsupported type: {}",
            obj.get_type().name()?
        )))
    }
}

#[cfg(test)]
mod tests {
    use crate::clean_string;

    #[test]
    fn test_remove_punctuation() {
        let text = "Hello?";
        let expected = "hello";
        assert_eq!(clean_string(text), expected);

        let text = "Hel#lo?";
        let expected = "hello";
        assert_eq!(clean_string(text), expected);

        let text = "Hello_World!";
        let expected = "hello-world";
        assert_eq!(clean_string(text), expected);
    }

    #[test]
    fn test_name_repository_validation() {
        let name = "hello";
        let repository = "world";

        assert!(super::validate_name_repository_pattern(name, repository).is_ok());

        let name = "llllllllllllllllloooooooooooooonnnnnnnnnnnnnnggggggggggggggg";
        let repository = "nnnnnnnnnnnnnaaaaaaaaaaaaaaammmmmmmmmmmmmeeeeeeeeeee";

        assert!(super::validate_name_repository_pattern(name, repository).is_err());
    }
}
