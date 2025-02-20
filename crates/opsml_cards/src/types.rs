use opsml_error::error::CardError;
use opsml_interfaces::{FeatureSchema, OnnxSchema};
use opsml_types::*;
use opsml_utils::{clean_string, validate_name_repository_pattern, FileUtils, PyHelperFuncs};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;
use walkdir::WalkDir;

#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Default)]
pub struct Description {
    #[pyo3(get, set)]
    pub summary: Option<String>,

    #[pyo3(get, set)]
    pub sample_code: Option<String>,

    #[pyo3(get, set)]
    pub notes: Option<String>,
}

#[pymethods]
impl Description {
    #[new]
    #[pyo3(signature = (summary=None, sample_code=None, notes=None))]
    fn new(
        summary: Option<String>,
        sample_code: Option<String>,
        notes: Option<String>,
    ) -> PyResult<Self> {
        // check if summary is some and if it is a file path. If .md file, read the file. IF not, return string
        let extracted_summary = match summary {
            Some(summary) => {
                if summary.ends_with(".md") {
                    let filepath = FileUtils::open_file(&summary)?;
                    Some(filepath)
                } else {
                    Some(summary)
                }
            }
            None => None,
        };

        let extracted_sample_code = match sample_code {
            Some(sample_code) => {
                if sample_code.ends_with(".md") {
                    let filepath = FileUtils::open_file(&sample_code)?;
                    Some(filepath)
                } else {
                    Some(sample_code)
                }
            }
            None => None,
        };

        Ok(Description {
            summary: extracted_summary,
            sample_code: extracted_sample_code,
            notes,
        })
    }
    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }
}

impl Description {
    pub fn find_filepath(filepath: &str) -> Result<String, CardError> {
        // get file name of path
        let path = std::path::Path::new(&filepath)
            .file_name()
            .unwrap()
            .to_str()
            .unwrap();

        let current_dir = std::env::current_dir().map_err(|e| CardError::Error(e.to_string()))?;
        // recursively search for file in current directory
        for entry in WalkDir::new(current_dir) {
            let entry = entry.map_err(|e| CardError::Error(e.to_string()))?;
            if entry.file_type().is_file() && entry.file_name().to_string_lossy() == path {
                // open the file and read it to a string
                let file = std::fs::read_to_string(entry.path())
                    .map_err(|e| CardError::Error(e.to_string()))?;

                return Ok(file);
            }
        }
        // raise error if file not found
        let msg = format!("File not found: {}", filepath);
        Err(CardError::Error(msg))
    }
}

#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Default)]
pub struct DataSchema {
    #[pyo3(get, set)]
    pub data_type: String,

    #[pyo3(get, set)]
    pub input_features: Option<FeatureSchema>,

    #[pyo3(get, set)]
    pub output_features: Option<FeatureSchema>,

    #[pyo3(get, set)]
    pub onnx_schema: Option<OnnxSchema>,
}

#[pymethods]
impl DataSchema {
    #[new]
    #[pyo3(signature = (data_type, input_features=None, output_features=None, onnx_schema=None))]
    fn new(
        data_type: String,
        input_features: Option<FeatureSchema>,
        output_features: Option<FeatureSchema>,
        onnx_schema: Option<OnnxSchema>,
    ) -> Self {
        DataSchema {
            data_type,
            input_features,
            output_features,
            onnx_schema,
        }
    }
    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }
}

#[derive(Debug, Serialize, Deserialize)]
#[pyclass]
pub struct CardInfo {
    #[pyo3(get)]
    pub name: Option<String>,

    #[pyo3(get)]
    pub repository: Option<String>,

    #[pyo3(get)]
    pub uid: Option<String>,

    #[pyo3(get)]
    pub version: Option<String>,

    #[pyo3(get)]
    pub tags: Option<Vec<String>>,
}

#[pymethods]
impl CardInfo {
    #[new]
    #[pyo3(signature = (name=None, repository=None, uid=None, version=None, tags=None))]
    pub fn new(
        name: Option<String>,
        repository: Option<String>,

        uid: Option<String>,
        version: Option<String>,
        tags: Option<Vec<String>>,
    ) -> Self {
        Self {
            name,
            repository,
            uid,
            version,
            tags,
        }
    }
    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }

    pub fn set_env(&self) {
        // if check name, repo. If any is set, set environment variable
        // if name is set, set OPSML_RUNTIME_NAME
        // if repository is set, set OPSML_RUNTIME_REPOSITORY

        if let Some(name) = &self.name {
            std::env::set_var("OPSML_RUNTIME_NAME", name);
        }

        if let Some(repo) = &self.repository {
            std::env::set_var("OPSML_RUNTIME_REPOSITORY", repo);
        }
    }

    // primarily used for checking and testing. Do not write .pyi file for this method
    pub fn get_vars(&self) -> HashMap<String, String> {
        // check if OPSML_RUNTIME_NAME, OPSML_RUNTIME_REPOSITORY are set
        // Print out the values if they are set

        let name = std::env::var("OPSML_RUNTIME_NAME").unwrap_or_default();
        let repo = std::env::var("OPSML_RUNTIME_REPOSITORY").unwrap_or_default();

        // print
        let mut map = HashMap::new();
        map.insert("OPSML_RUNTIME_NAME".to_string(), name);
        map.insert("OPSML_RUNTIME_REPOSITORY".to_string(), repo);

        map
    }
}

impl CardInfo {
    pub fn get_value_by_name(&self, name: &str) -> &Option<String> {
        match name {
            "name" => &self.name,
            "repository" => &self.repository,

            "uid" => &self.uid,
            "version" => &self.version,
            _ => &None,
        }
    }
}

impl FromPyObject<'_> for CardInfo {
    fn extract_bound(ob: &Bound<'_, PyAny>) -> PyResult<Self> {
        let name = ob.getattr("name").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let repository = ob.getattr("repository").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let version = ob.getattr("version").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let uid = ob.getattr("uid").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<String>()?))
            }
        })?;

        let tags = ob.getattr("tags").and_then(|item| {
            if item.is_none() {
                Ok(None)
            } else {
                Ok(Some(item.extract::<Vec<String>>()?))
            }
        })?;

        Ok(CardInfo {
            name,
            repository,

            uid,
            version,
            tags,
        })
    }
}

pub type BaseArgsResult = (String, String, String, String);

pub struct BaseArgs {}

impl BaseArgs {
    pub fn create_args(
        name: Option<&str>,
        repository: Option<&str>,
        version: Option<&str>,
        uid: Option<&str>,
    ) -> Result<BaseArgsResult, CardError> {
        let name = clean_string(&Self::get_value("NAME", name)?)?;
        let repository = clean_string(&Self::get_value("REPOSITORY", repository)?)?;

        let version = version.map_or(CommonKwargs::BaseVersion.to_string(), |v| v.to_string());
        let uid = uid.map_or(CommonKwargs::Undefined.to_string(), |v| v.to_string());

        validate_name_repository_pattern(&name, &repository)?;

        Ok((repository, name, version, uid))
    }

    fn get_value(key: &str, value: Option<&str>) -> Result<String, CardError> {
        let env_key = format!("OPSML_RUNTIME_{}", key.to_uppercase());
        let env_val = env::var(&env_key).ok();

        value
            .as_ref()
            .map(|s| s.to_string())
            .or(env_val)
            .ok_or_else(|| CardError::Error(format!("{} not provided", key)))
    }
}
