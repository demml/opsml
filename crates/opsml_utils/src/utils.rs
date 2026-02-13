use crate::error::UtilError;
use chrono::Timelike;
use chrono::{DateTime, NaiveDateTime, Utc};
use colored_json::{Color, ColorMode, ColoredFormatter, PrettyFormatter, Styler};
use pyo3::types::{PyBool, PyDict, PyFloat, PyInt, PyList, PyString, PyTuple};
use pyo3::{prelude::*, types::PyAnyMethods};
use regex::Regex;
use serde::Serialize;
use serde_json::{Value, json};
use std::path::{Path, PathBuf};
use tracing::debug;
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
    pub fn save_to_json<T>(model: T, path: &Path) -> Result<(), UtilError>
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
pub fn unwrap_pystring(obj: &Bound<'_, PyAny>, field: &str) -> Result<String, UtilError> {
    Ok(obj.getattr(field)?.extract::<String>()?)
}

/// Recursively converts Python objects to JSON-compatible values
/// Handles ndarrays and other non-serializable types by converting to lists or strings
fn pyobject_to_json_value(_py: Python, obj: &Bound<'_, PyAny>) -> Result<Value, UtilError> {
    if obj.is_none() {
        return Ok(Value::Null);
    }

    if obj.is_instance_of::<PyBool>() {
        return Ok(json!(obj.extract::<bool>()?));
    }

    if obj.is_instance_of::<PyInt>() {
        return Ok(json!(obj.extract::<i64>()?));
    }

    if obj.is_instance_of::<PyFloat>() {
        return Ok(json!(obj.extract::<f64>()?));
    }

    if obj.is_instance_of::<PyString>() {
        return Ok(json!(obj.extract::<String>()?));
    }

    if obj.is_instance_of::<PyList>() || obj.is_instance_of::<PyTuple>() {
        let list = obj.extract::<Vec<Bound<'_, PyAny>>>()?;
        let values: Result<Vec<Value>, _> = list
            .iter()
            .map(|item| pyobject_to_json_value(_py, item))
            .collect();
        return Ok(Value::Array(values?));
    }

    if obj.is_instance_of::<PyDict>() {
        let dict = obj.cast::<PyDict>()?;
        let mut map = serde_json::Map::new();

        for (key, value) in dict.iter() {
            let key_str = if key.is_instance_of::<PyString>() {
                key.extract::<String>()?
            } else {
                key.str()?.extract::<String>()?
            };

            map.insert(key_str, pyobject_to_json_value(_py, &value)?);
        }

        return Ok(Value::Object(map));
    }

    // Handle numpy arrays
    if (obj.hasattr("__array__")? || obj.hasattr("tolist")?)
        && let Ok(py_list) = obj.call_method0("tolist")
    {
        return pyobject_to_json_value(_py, &py_list);
    }

    // Handle pandas Series/DataFrame
    if obj.hasattr("to_dict")?
        && let Ok(py_dict) = obj.call_method0("to_dict")
    {
        return pyobject_to_json_value(_py, &py_dict);
    }

    // Fallback: convert to string representation
    debug!(
        "Converting non-serializable type {} to string",
        obj.get_type().name()?
    );
    Ok(json!(obj.str()?.extract::<String>()?))
}

/// Converts a PyDict to a JSON Value, handling numpy arrays and other non-serializable types
pub fn pydict_to_json_value(py: Python, dict: &Bound<'_, PyDict>) -> Result<Value, UtilError> {
    let mut map = serde_json::Map::new();

    for (key, value) in dict.iter() {
        let key_str = if key.is_instance_of::<PyString>() {
            key.extract::<String>()?
        } else {
            key.str()?.extract::<String>()?
        };

        map.insert(key_str, pyobject_to_json_value(py, &value)?);
    }

    Ok(Value::Object(map))
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
