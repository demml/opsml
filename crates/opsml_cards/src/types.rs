use opsml_error::error::CardError;
use opsml_types::*;
use opsml_utils::{clean_string, validate_name_repository_pattern, FileUtils, PyHelperFuncs};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;
use std::fmt;
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
    ) -> Result<Self, CardError> {
        // check if summary is some and if it is a file path. If .md file, read the file. IF not, return string
        let extracted_summary = match summary {
            Some(summary) => {
                if summary.ends_with(".md") {
                    let filepath = FileUtils::open_file(&summary)
                        .map_err(|e| CardError::Error(e.to_string()))?;
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
                    let filepath = FileUtils::open_file(&sample_code)
                        .map_err(|e| CardError::Error(e.to_string()))?;
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
        Err(CardError::Error("File not found".to_string()))
    }
}

#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
pub struct Feature {
    #[pyo3(get, set)]
    feature_type: String,
    #[pyo3(get, set)]
    shape: Vec<i32>,
    #[pyo3(get, set)]
    extra_args: HashMap<String, String>,
}

#[pymethods]
impl Feature {
    #[new]
    #[pyo3(signature = (feature_type, shape, extra_args=None))]
    fn new(
        feature_type: String,
        shape: Vec<i32>,
        extra_args: Option<HashMap<String, String>>,
    ) -> Self {
        Feature {
            feature_type,
            shape,
            extra_args: extra_args.unwrap_or_default(),
        }
    }

    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Default)]
pub struct OnnxSchema {
    #[pyo3(get, set)]
    pub input_features: HashMap<String, Feature>,

    #[pyo3(get, set)]
    pub output_features: HashMap<String, Feature>,

    #[pyo3(get, set)]
    pub onnx_version: String,
}

#[pymethods]
impl OnnxSchema {
    #[new]
    #[pyo3(signature = (input_features, output_features, onnx_version))]
    fn new(
        input_features: HashMap<String, Feature>,
        output_features: HashMap<String, Feature>,
        onnx_version: String,
    ) -> Self {
        OnnxSchema {
            input_features,
            output_features,
            onnx_version,
        }
    }
    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }
}

#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone, Default)]
pub struct DataSchema {
    #[pyo3(get, set)]
    pub data_type: String,

    #[pyo3(get, set)]
    pub input_features: Option<HashMap<String, Feature>>,

    #[pyo3(get, set)]
    pub output_features: Option<HashMap<String, Feature>>,

    #[pyo3(get, set)]
    pub onnx_schema: Option<OnnxSchema>,
}

#[pymethods]
impl DataSchema {
    #[new]
    #[pyo3(signature = (data_type, input_features=None, output_features=None, onnx_schema=None))]
    fn new(
        data_type: String,
        input_features: Option<HashMap<String, Feature>>,
        output_features: Option<HashMap<String, Feature>>,
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
    pub contact: Option<String>,

    #[pyo3(get)]
    pub uid: Option<String>,

    #[pyo3(get)]
    pub version: Option<String>,

    #[pyo3(get)]
    pub tags: Option<HashMap<String, String>>,
}

#[pymethods]
impl CardInfo {
    #[new]
    #[pyo3(signature = (name=None, repository=None, contact=None, uid=None, version=None, tags=None))]
    pub fn new(
        name: Option<String>,
        repository: Option<String>,
        contact: Option<String>,
        uid: Option<String>,
        version: Option<String>,
        tags: Option<HashMap<String, String>>,
    ) -> Self {
        Self {
            name,
            repository,
            contact,
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
        // if check name, repo and contact. If any is set, set environment variable
        // if name is set, set OPSML_RUNTIME_NAME
        // if repository is set, set OPSML_RUNTIME_REPOSITORY
        // if contact is set, set OPSML_RUNTIME_CONTACT

        if let Some(name) = &self.name {
            std::env::set_var("OPSML_RUNTIME_NAME", name);
        }

        if let Some(repo) = &self.repository {
            std::env::set_var("OPSML_RUNTIME_REPOSITORY", repo);
        }

        if let Some(contact) = &self.contact {
            std::env::set_var("OPSML_RUNTIME_CONTACT", contact);
        }
    }

    // primarily used for checking and testing. Do not write .pyi file for this method
    pub fn get_vars(&self) -> HashMap<String, String> {
        // check if OPSML_RUNTIME_NAME, OPSML_RUNTIME_REPOSITORY, OPSML_RUNTIME_CONTACT are set
        // Print out the values if they are set

        let name = std::env::var("OPSML_RUNTIME_NAME").unwrap_or_default();
        let repo = std::env::var("OPSML_RUNTIME_REPOSITORY").unwrap_or_default();
        let contact = std::env::var("OPSML_RUNTIME_CONTACT").unwrap_or_default();

        // print
        let mut map = HashMap::new();
        map.insert("OPSML_RUNTIME_NAME".to_string(), name);
        map.insert("OPSML_RUNTIME_REPOSITORY".to_string(), repo);
        map.insert("OPSML_RUNTIME_CONTACT".to_string(), contact);

        map
    }
}

impl CardInfo {
    pub fn get_value_by_name(&self, name: &str) -> &Option<String> {
        match name {
            "name" => &self.name,
            "repository" => &self.repository,
            "contact" => &self.contact,
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

        let contact = ob.getattr("contact").and_then(|item| {
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
                Ok(Some(item.extract::<HashMap<String, String>>()?))
            }
        })?;

        Ok(CardInfo {
            name,
            repository,
            contact,
            uid,
            version,
            tags,
        })
    }
}

pub struct BaseArgs {
    pub name: String,
    pub repository: String,
    pub contact: String,
    pub version: String,
    pub uid: String,
    pub tags: HashMap<String, String>,
}

impl BaseArgs {
    pub fn new(
        name: Option<String>,
        repository: Option<String>,
        contact: Option<String>,
        version: Option<String>,
        uid: Option<String>,
        info: Option<CardInfo>,
        tags: HashMap<String, String>,
    ) -> Result<Self, CardError> {
        let name = clean_string(&Self::get_value(
            "NAME",
            &name,
            info.as_ref().map(|i| &i.name),
        )?);
        let repository = clean_string(&Self::get_value(
            "REPOSITORY",
            &repository,
            info.as_ref().map(|i| &i.repository),
        )?);
        let contact = Self::get_value("CONTACT", &contact, info.as_ref().map(|i| &i.contact))?;

        let version = version.unwrap_or_else(|| CommonKwargs::BaseVersion.to_string());
        let uid = uid.unwrap_or_else(|| CommonKwargs::Undefined.to_string());

        validate_name_repository_pattern(&name, &repository)?;

        Ok(Self {
            name,
            repository,
            contact,
            version,
            uid,
            tags,
        })
    }

    fn get_value(
        key: &str,
        value: &Option<String>,
        card_info_value: Option<&Option<String>>,
    ) -> Result<String, CardError> {
        let env_key = format!("OPSML_RUNTIME_{}", key.to_uppercase());
        let env_val = env::var(&env_key).ok();

        value
            .as_ref()
            .or_else(|| card_info_value.and_then(|v| v.as_ref()))
            .or(env_val.as_ref())
            .map(|s| s.to_string())
            .ok_or_else(|| CardError::Error(format!("{} not provided", key)))
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum CardTable {
    Data,
    Model,
    Run,
    Project,
    Audit,
    Pipeline,
    Metrics,
    HardwareMetrics,
    Parameters,
    Users,
}

impl fmt::Display for CardTable {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let table_name = match self {
            CardTable::Data => "opsml_data_registry",
            CardTable::Model => "opsml_model_registry",
            CardTable::Run => "opsml_run_registry",
            CardTable::Project => "opsml_project_registry",
            CardTable::Audit => "opsml_audit_registry",
            CardTable::Pipeline => "opsml_pipeline_registry",
            CardTable::Metrics => "opsml_run_metrics",
            CardTable::HardwareMetrics => "opsml_run_hardware_metrics",
            CardTable::Parameters => "opsml_run_parameters",
            CardTable::Users => "opsml_users",
        };
        write!(f, "{}", table_name)
    }
}

impl CardTable {
    pub fn from_registry_type(registry_type: &RegistryType) -> Self {
        match registry_type {
            RegistryType::Data => CardTable::Data,
            RegistryType::Model => CardTable::Model,
            RegistryType::Run => CardTable::Run,
            RegistryType::Project => CardTable::Project,
            RegistryType::Audit => CardTable::Audit,
            RegistryType::Pipeline => CardTable::Pipeline,
            RegistryType::Metrics => CardTable::Metrics,
            RegistryType::HardwareMetrics => CardTable::HardwareMetrics,
            RegistryType::Parameters => CardTable::Parameters,
            RegistryType::Users => CardTable::Users,
        }
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum CardType {
    Data,
    Model,
    Run,
    Project,
    Audit,
    Pipeline,
}
