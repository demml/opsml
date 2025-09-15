use crate::error::{PyUtilError, UtilError};
use chrono::Timelike;
use chrono::{DateTime, NaiveDateTime, Utc};
use colored_json::{Color, ColorMode, ColoredFormatter, PrettyFormatter, Styler};
use pyo3::{prelude::*, types::PyAnyMethods};
use regex::Regex;

use pyo3::types::{PyBool, PyDict, PyDictMethods, PyFloat, PyInt, PyList, PyString, PyTuple};
use pyo3::IntoPyObjectExt;
use serde::Serialize;
use serde_json::{json, Value};
use std::path::{Path, PathBuf};
use uuid::Uuid;

const PUNCTUATION: &str = "!\"#$%&'()*+,./:;<=>?@[\\]^`{|}~";
const NAME_SPACE_PATTERN: &str = r"^[a-z0-9]+(?:[-a-z0-9]+)*/[-a-z0-9]+$";

/// Clean a string by removing punctuation and converting to lowercase
///
/// # Arguments
/// * `input` - A string slice that holds the input string
///
/// # Returns
///
/// A `Result` containing the cleaned string or a `UtilError`
///
/// # Errors
///
/// This function will return an error if:
/// - The regex pattern cannot be created.
pub fn clean_string(input: &str) -> Result<String, UtilError> {
    let pattern = format!("[{}]", regex::escape(PUNCTUATION));
    let re = Regex::new(&pattern.to_string())?;
    Ok(re
        .replace_all(&input.trim().to_lowercase(), "")
        .to_string()
        .replace('_', "-"))
}

pub fn validate_name_space_pattern(name: &str, space: &str) -> Result<(), UtilError> {
    let space_name = format!("{space}/{name}");

    let re = Regex::new(NAME_SPACE_PATTERN)?;

    if !re.is_match(&space_name) {
        return Err(UtilError::InvalidSpaceNamePattern);
    }

    if name.len() > 53 {
        return Err(UtilError::SpaceNamePatternTooLong);
    }

    Ok(())
}

/// Check if a string is a valid `UUIDv7`
///
/// # Arguments
/// * `uid` - A string slice that holds the UUID
///
/// # Returns
/// * `bool` - A boolean indicating if the UUID is valid
///
/// # Errors
///
/// This function will return an error if:
/// - The UUID string cannot be parsed.
pub fn is_valid_uuidv7(uid: &str) -> Result<bool, UtilError> {
    match Uuid::parse_str(uid) {
        Ok(uuid) => Ok(uuid.get_version_num() == 7),
        Err(_) => Err(UtilError::UuidError),
    }
}

/// Get the current epoch time in microseconds
///
/// # Returns
///
/// An `i64` containing the current epoch time in microseconds
///
/// # Errors
///
/// This function will return an error if:
/// - The current time cannot be retrieved
pub fn get_epoch_time_to_search(max_date: &str) -> Result<i64, UtilError> {
    const YEAR_MONTH_DATE: &str = "%Y-%m-%d";

    // Parse the date string into a  DateTime<Utc>
    let converted_date = NaiveDateTime::parse_from_str(max_date, YEAR_MONTH_DATE)
        .map_err(|_| UtilError::DateError)?;

    // Replace hour, minute, and second to get the max values for the date
    let max_date = converted_date
        .with_hour(23)
        .ok_or(UtilError::DateError)?
        .with_minute(59)
        .ok_or(UtilError::DateError)?
        .with_second(59)
        .ok_or(UtilError::DateError)?;

    // Convert  DateTime<Utc> to timestamp in microseconds
    let timestamp = max_date.and_utc().timestamp() * 1_000_000;

    Ok(timestamp)
}

pub fn get_utc_date() -> String {
    chrono::Utc::now().format("%Y-%m-%d").to_string()
}

pub fn get_utc_timestamp() -> i64 {
    chrono::Utc::now().timestamp()
}

pub fn get_utc_datetime() -> DateTime<Utc> {
    Utc::now() // Returns DateTime<Utc> directly
}

pub fn create_uuid7() -> String {
    Uuid::now_v7().to_string()
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
            Err(e) => format!("Failed to serialize to json: {e}"),
        }
        // serialize the struct to a string
    }

    pub fn __json__<T: Serialize>(object: T) -> String {
        match serde_json::to_string_pretty(&object) {
            Ok(json) => json,
            Err(e) => format!("Failed to serialize to json: {e}"),
        }
    }

    /// Save a struct to a JSON file
    ///
    /// # Arguments
    ///
    /// * `model` - A reference to a struct that implements the `Serialize` trait
    /// * `path` - A reference to a `Path` object that holds the path to the file
    ///
    /// # Returns
    ///
    /// A `Result` containing `()` or a `UtilError`
    ///
    /// # Errors
    ///
    /// This function will return an error if:
    /// - The struct cannot be serialized to a string
    pub fn save_to_json<T>(model: T, path: &Path) -> Result<(), PyUtilError>
    where
        T: Serialize,
    {
        // serialize the struct to a string
        let json =
            serde_json::to_string_pretty(&model).map_err(|_| UtilError::SerializationError)?;

        // ensure .json extension
        let path = path.with_extension("json");

        if !path.exists() {
            // ensure path exists, create if not
            let parent_path = path.parent().ok_or(UtilError::GetParentPathError)?;

            std::fs::create_dir_all(parent_path).map_err(|_| UtilError::CreateDirectoryError)?;
        }

        std::fs::write(path, json).map_err(|_| UtilError::WriteError)?;

        Ok(())
    }
}

pub fn json_to_pyobject<'py>(
    py: Python,
    value: &Value,
    dict: &Bound<'py, PyDict>,
) -> Result<Bound<'py, PyDict>, PyUtilError> {
    match value {
        Value::Object(map) => {
            for (k, v) in map {
                let py_value = match v {
                    Value::Null => py.None(),
                    Value::Bool(b) => b.into_py_any(py)?,
                    Value::Number(n) => {
                        if let Some(i) = n.as_i64() {
                            i.into_py_any(py)?
                        } else if let Some(f) = n.as_f64() {
                            f.into_py_any(py)?
                        } else {
                            return Err(PyUtilError::InvalidNumber);
                        }
                    }
                    Value::String(s) => s.into_py_any(py)?,
                    Value::Array(arr) => {
                        let py_list = PyList::empty(py);
                        for item in arr {
                            let py_item = json_to_pyobject_value(py, item)?;
                            py_list.append(py_item)?;
                        }
                        py_list.into_py_any(py)?
                    }
                    Value::Object(_) => {
                        let nested_dict = PyDict::new(py);
                        json_to_pyobject(py, v, &nested_dict)?;
                        nested_dict.into_py_any(py)?
                    }
                };
                dict.set_item(k, py_value)?;
            }
        }
        _ => return Err(PyUtilError::RootMustBeObjectError),
    }

    Ok(dict.clone())
}

pub fn json_to_pyobject_value(py: Python, value: &Value) -> Result<Py<PyAny>, PyUtilError> {
    Ok(match value {
        Value::Null => py.None(),
        Value::Bool(b) => b.into_py_any(py)?,
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                i.into_py_any(py)?
            } else if let Some(f) = n.as_f64() {
                f.into_py_any(py)?
            } else {
                return Err(PyUtilError::InvalidNumber);
            }
        }
        Value::String(s) => s.into_py_any(py)?,
        Value::Array(arr) => {
            let py_list = PyList::empty(py);
            for item in arr {
                let py_item = json_to_pyobject_value(py, item)?;
                py_list.append(py_item)?;
            }
            py_list.into_py_any(py)?
        }
        Value::Object(_) => {
            let nested_dict = PyDict::new(py);
            json_to_pyobject(py, value, &nested_dict)?;
            nested_dict.into_py_any(py)?
        }
    })
}

pub fn pyobject_to_json(obj: &Bound<'_, PyAny>) -> Result<Value, PyUtilError> {
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
    } else if obj.is_instance_of::<PyTuple>() {
        let tuple = obj.downcast::<PyTuple>()?;
        let mut vec = Vec::new();
        for item in tuple.iter() {
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
        // display "cant show" for unsupported types
        // call obj.str to get the string representation
        // if error, default to "unsupported type"
        let obj_str = match obj.str() {
            Ok(s) => s
                .extract::<String>()
                .unwrap_or_else(|_| "unsupported type".to_string()),
            Err(_) => "unsupported type".to_string(),
        };

        Ok(Value::String(obj_str))
    }
}

/// Converts a UUID string to a byte key
///
/// # Errors
///
/// This function will return an error if:
/// - The UUID string cannot be parsed.
pub fn uid_to_byte_key(uid: &str) -> Result<[u8; 32], UtilError> {
    let mut uid_key = [0u8; 32];
    let parsed_uid = Uuid::parse_str(uid).map_err(|_| UtilError::UuidError)?;

    uid_key[..16].copy_from_slice(parsed_uid.as_bytes());

    Ok(uid_key)
}

/// Creates a temp path
///
/// # Errors
///
/// This function will return an error if:
/// - the temporary directory cannot be created.
pub fn create_tmp_path() -> Result<PathBuf, UtilError> {
    let tmp_dir = tempfile::TempDir::new()?;

    let tmp_path = tmp_dir.keep();

    Ok(tmp_path)
}

/// Unwraps a Python string attribute from a `PyAny` object.
///
/// # Arguments
/// * `obj` - A reference to a `PyAny` object.
/// * `field` - The name of the attribute to unwrap.
///
/// # Returns
///
/// A `Result` containing the unwrapped string or a `UtilError`.
///
/// # Errors
///
/// This function will return an error if:
/// - The attribute cannot be found.
/// - The attribute cannot be extracted as a string.
pub fn unwrap_pystring(obj: &Bound<'_, PyAny>, field: &str) -> Result<String, PyUtilError> {
    Ok(obj.getattr(field)?.extract::<String>()?)
}

/// Checks if python object is an instance of a Pydantic BaseModel
/// # Arguments
/// * `py` - Python interpreter instance
/// * `obj` - Python object to check
/// # Returns
/// * `Ok(bool)` - `true` if the object is a Pydantic model
/// * `Err(TypeError)` - if there was an error importing Pydantic or checking
pub fn is_pydantic_model(py: Python, obj: &Bound<'_, PyAny>) -> Result<bool, PyUtilError> {
    let pydantic = match py.import("pydantic") {
        Ok(module) => module,
        Err(e) => return Err(PyUtilError::FailedToImportPydantic(e.to_string())),
    };
    let basemodel = pydantic.getattr("BaseModel")?;

    // check if context is a pydantic model
    let is_basemodel = obj
        .is_instance(&basemodel)
        .map_err(|e| PyUtilError::FailedToCheckPydanticModel(e.to_string()))?;

    Ok(is_basemodel)
}

#[cfg(test)]
mod tests {
    use crate::clean_string;

    #[test]
    fn test_remove_punctuation() {
        let text = "Hello?";
        let expected = "hello";
        assert_eq!(clean_string(text).unwrap(), expected);

        let text = "Hel#lo?";
        let expected = "hello";
        assert_eq!(clean_string(text).unwrap(), expected);

        let text = "Hello_World!";
        let expected = "hello-world";
        assert_eq!(clean_string(text).unwrap(), expected);
    }

    #[test]
    fn test_name_space_validation() {
        let name = "hello";
        let space = "world";

        assert!(super::validate_name_space_pattern(name, space).is_ok());

        let name = "llllllllllllllllloooooooooooooonnnnnnnnnnnnnnggggggggggggggg";
        let space = "nnnnnnnnnnnnnaaaaaaaaaaaaaaammmmmmmmmmmmmeeeeeeeeeee";

        assert!(super::validate_name_space_pattern(name, space).is_err());
    }
}
