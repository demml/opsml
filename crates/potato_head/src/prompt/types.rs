use crate::error::PotatoError;
use mime_guess;
use opsml_utils::pyobject_to_json;
use opsml_utils::PyHelperFuncs;
use pyo3::types::PyAnyMethods;
use pyo3::types::PyString;
use pyo3::{prelude::*, IntoPyObjectExt};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashSet;
use std::fmt::Display;
use std::sync::OnceLock;
use tracing::error;
static DOCUMENT_MEDIA_TYPES: OnceLock<HashSet<&'static str>> = OnceLock::new();
use crate::prompt::sanitize::PromptSanitizer;
use crate::SanitizedResult;
use pyo3::types::PyDict;

pub enum Role {
    User,
    Assistant,
    Developer,
}

impl Display for Role {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Role::User => write!(f, "user"),
            Role::Assistant => write!(f, "assistant"),
            Role::Developer => write!(f, "developer"),
        }
    }
}

fn get_document_media_types() -> &'static HashSet<&'static str> {
    DOCUMENT_MEDIA_TYPES.get_or_init(|| {
        let mut set = HashSet::new();
        set.insert("application/pdf");
        set.insert("text/plain");
        set.insert("text/csv");
        set.insert("application/vnd.openxmlformats-officedocument.wordprocessingml.document");
        set.insert("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        set.insert("text/html");
        set.insert("text/markdown");
        set.insert("application/vnd.ms-excel");
        set
    })
}

fn get_audio_media_types() -> &'static HashSet<&'static str> {
    static AUDIO_MEDIA_TYPES: OnceLock<HashSet<&'static str>> = OnceLock::new();
    AUDIO_MEDIA_TYPES.get_or_init(|| {
        let mut set = HashSet::new();
        set.insert("audio/mpeg");
        set.insert("audio/wav");
        set
    })
}

fn get_image_media_types() -> &'static HashSet<&'static str> {
    static IMAGE_MEDIA_TYPES: OnceLock<HashSet<&'static str>> = OnceLock::new();
    IMAGE_MEDIA_TYPES.get_or_init(|| {
        let mut set = HashSet::new();
        set.insert("image/jpeg");
        set.insert("image/png");
        set.insert("image/gif");
        set.insert("image/webp");
        set
    })
}

fn image_format(media_type: &str) -> Result<String, PotatoError> {
    let format = match media_type {
        "image/jpeg" => "jpeg",
        "image/png" => "png",
        "image/gif" => "gif",
        "image/webp" => "webp",
        _ => {
            return Err(PotatoError::Error(format!(
                "Unknown image media type: {}",
                media_type
            )))
        }
    };

    Ok(format.to_string())
}

fn document_format(media_type: &str) -> Result<String, PotatoError> {
    let format = match media_type {
        "application/pdf" => "pdf",
        "text/plain" => "txt",
        "text/csv" => "csv",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document" => "docx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" => "xlsx",
        "text/html" => "html",
        "text/markdown" => "md",
        "application/vnd.ms-excel" => "xls",
        _ => {
            return Err(PotatoError::Error(format!(
                "Unknown document media type: {}",
                media_type
            )))
        }
    };
    Ok(format.to_string())
}

fn guess_type(url: &str) -> Result<String, PotatoError> {
    // fail if mime type is not found
    let mime_type = mime_guess::from_path(url)
        .first()
        .ok_or_else(|| PotatoError::Error(format!("Failed to guess mime type for {}", url)))?;

    Ok(mime_type.to_string())
}

#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AudioUrl {
    #[pyo3(get, set)]
    url: String,
    #[pyo3(get)]
    kind: String,
}

#[pymethods]
impl AudioUrl {
    #[new]
    fn new(url: String) -> PyResult<Self> {
        if !url.ends_with(".mp3") && !url.ends_with(".wav") {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Unknown audio file extension: {}",
                url
            )));
        }
        Ok(Self {
            url,
            kind: "audio-url".to_string(),
        })
    }

    #[getter]
    fn media_type(&self) -> String {
        if self.url.ends_with(".mp3") {
            "audio/mpeg".to_string()
        } else {
            "audio/wav".to_string()
        }
    }
}

#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ImageUrl {
    #[pyo3(get, set)]
    pub url: String,
    #[pyo3(get)]
    pub kind: String,
}

#[pymethods]
impl ImageUrl {
    #[new]
    #[pyo3(signature = (url, kind="image-url"))]
    fn new(url: &str, kind: &str) -> PyResult<Self> {
        if !url.ends_with(".jpg")
            && !url.ends_with(".jpeg")
            && !url.ends_with(".png")
            && !url.ends_with(".gif")
            && !url.ends_with(".webp")
        {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Unknown image file extension: {}",
                url
            )));
        }
        Ok(Self {
            url: url.to_string(),
            kind: kind.to_string(),
        })
    }

    #[getter]
    fn media_type(&self) -> Result<String, PotatoError> {
        if self.url.ends_with(".jpg") || self.url.ends_with(".jpeg") {
            Ok("image/jpeg".to_string())
        } else if self.url.ends_with(".png") {
            Ok("image/png".to_string())
        } else if self.url.ends_with(".gif") {
            Ok("image/gif".to_string())
        } else if self.url.ends_with(".webp") {
            Ok("image/webp".to_string())
        } else {
            Err(PotatoError::Error(format!(
                "Unknown image file extension: {}",
                self.url
            )))
        }
    }

    #[getter]
    fn format(&self) -> Result<String, PotatoError> {
        let media_type = self.media_type()?;
        image_format(&media_type)
    }
}

#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DocumentUrl {
    #[pyo3(get, set)]
    url: String,
    #[pyo3(get)]
    kind: String,
}

#[pymethods]
impl DocumentUrl {
    #[new]
    #[pyo3(signature = (url, kind="document-url"))]
    fn new(url: &str, kind: &str) -> Result<Self, PotatoError> {
        Ok(Self {
            url: url.to_string(),
            kind: kind.to_string(),
        })
    }

    #[getter]
    fn media_type(&self) -> Result<String, PotatoError> {
        guess_type(&self.url)
    }

    #[getter]
    fn format(&self) -> Result<String, PotatoError> {
        let media_type = self.media_type()?;
        document_format(&media_type)
    }
}

#[pyclass]
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BinaryContent {
    #[pyo3(get, set)]
    data: Vec<u8>,
    #[pyo3(get, set)]
    media_type: String,
    #[pyo3(get)]
    kind: String,
}

#[pymethods]
impl BinaryContent {
    #[new]
    #[pyo3(signature = (data, media_type, kind="binary"))]
    fn new(data: Vec<u8>, media_type: &str, kind: &str) -> Result<Self, PotatoError> {
        // assert that media type is valid, must be audio, image, or document

        if get_audio_media_types().contains(media_type)
            || get_image_media_types().contains(media_type)
            || get_document_media_types().contains(media_type)
        {
            return Err(PotatoError::Error(format!(
                "Unknown media type: {}",
                media_type
            )));
        }

        Ok(Self {
            data,
            media_type: media_type.to_string(),
            kind: kind.to_string(),
        })
    }

    #[getter]
    fn is_audio(&self) -> bool {
        get_audio_media_types().contains(self.media_type.as_str())
    }

    #[getter]
    fn is_image(&self) -> bool {
        get_image_media_types().contains(self.media_type.as_str())
    }

    #[getter]
    fn is_document(&self) -> bool {
        get_document_media_types().contains(self.media_type.as_str())
    }

    #[getter]
    fn format(&self) -> Result<String, PotatoError> {
        if self.is_audio() {
            if self.media_type == "audio/mpeg" {
                Ok("mp3".to_string())
            } else if self.media_type == "audio/wav" {
                Ok("wav".to_string())
            } else {
                Err(PotatoError::Error(format!(
                    "Unknown media type: {}",
                    self.media_type
                )))
            }
        } else if self.is_image() {
            image_format(&self.media_type)
        } else if self.is_document() {
            document_format(&self.media_type)
        } else {
            Err(PotatoError::Error(format!(
                "Unknown media type: {}",
                self.media_type
            )))
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum PromptContent {
    Str(String),
    Audio(AudioUrl),
    Image(ImageUrl),
    Document(DocumentUrl),
    Binary(BinaryContent),
}

impl PromptContent {
    pub fn new(prompt: &Bound<'_, PyAny>) -> Result<Self, PotatoError> {
        if prompt.is_instance_of::<AudioUrl>() {
            let audio_url = prompt.extract::<AudioUrl>()?;
            Ok(PromptContent::Audio(audio_url))
        } else if prompt.is_instance_of::<ImageUrl>() {
            let image_url = prompt.extract::<ImageUrl>()?;
            Ok(PromptContent::Image(image_url))
        } else if prompt.is_instance_of::<DocumentUrl>() {
            let document_url = prompt.extract::<DocumentUrl>()?;
            Ok(PromptContent::Document(document_url))
        } else if prompt.is_instance_of::<BinaryContent>() {
            let binary_content = prompt.extract::<BinaryContent>()?;
            Ok(PromptContent::Binary(binary_content))
        } else if prompt.is_instance_of::<PyString>() {
            let user_content = prompt.extract::<String>()?;
            Ok(PromptContent::Str(user_content))
        } else {
            Err(PotatoError::Error("Unsupported prompt content type".into()))
        }
    }

    pub fn to_pyobject<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        match self {
            PromptContent::Str(s) => s.into_bound_py_any(py),
            PromptContent::Audio(audio_url) => {
                // test pydantic module
                match get_pydantic_module(py, "AudioUrl") {
                    Ok(model_class) => {
                        model_class.call1((audio_url.url.clone(), audio_url.kind.clone()))
                    }
                    Err(_) => audio_url.clone().into_bound_py_any(py),
                }
            }
            PromptContent::Image(image_url) => {
                // test pydantic module
                match get_pydantic_module(py, "ImageUrl") {
                    Ok(model_class) => {
                        model_class.call1((image_url.url.clone(), image_url.kind.clone()))
                    }
                    Err(_) => image_url.clone().into_bound_py_any(py),
                }
            }
            PromptContent::Document(document_url) => {
                // test pydantic module
                match get_pydantic_module(py, "DocumentUrl") {
                    Ok(model_class) => {
                        model_class.call1((document_url.url.clone(), document_url.kind.clone()))
                    }
                    Err(_) => document_url.clone().into_bound_py_any(py),
                }
            }
            PromptContent::Binary(binary_content) => {
                // test pydantic module
                match get_pydantic_module(py, "BinaryContent") {
                    Ok(model_class) => model_class.call1((
                        binary_content.data.clone(),
                        binary_content.media_type.clone(),
                        binary_content.kind.clone(),
                    )),
                    Err(_) => binary_content.clone().into_bound_py_any(py),
                }
            }
        }
    }
}

pub fn get_pydantic_module<'py>(py: Python<'py>, module_name: &str) -> PyResult<Bound<'py, PyAny>> {
    py.import("pydantic_ai")?.getattr(module_name)
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Message {
    pub content: PromptContent,
    next_param: usize,
    sanitized_output: Option<SanitizedResult>,
    pub role: String,
}

#[pymethods]
impl Message {
    #[new]
    #[pyo3(signature = (content))]
    pub fn new(content: &Bound<'_, PyAny>) -> PyResult<Self> {
        let content = PromptContent::new(content)?;
        Ok(Self {
            content,
            next_param: 1,
            sanitized_output: None,
            role: Role::User.to_string(),
        })
    }

    pub fn bind(&self, context: &str) -> PyResult<Message> {
        let placeholder = format!("${}", self.next_param);

        let content = match &self.content {
            PromptContent::Str(content) => {
                let new_content = content.replace(&placeholder, context);
                PromptContent::Str(new_content)
            }
            _ => self.content.clone(),
        };

        Ok(Message {
            content,
            next_param: self.next_param + 1,
            sanitized_output: None,
            role: self.role.clone(),
        })
    }

    pub fn sanitize(&self, sanitizer: &PromptSanitizer) -> Result<Message, PotatoError> {
        let (content, sanitized) = match &self.content {
            PromptContent::Str(content) => {
                let sanitized_result = sanitizer.sanitize(content).map_err(|e| {
                    PotatoError::Error(format!("Failed to sanitize content: {}", e))
                })?;
                (
                    PromptContent::Str(sanitized_result.sanitized_text.clone()),
                    Some(sanitized_result),
                )
            }
            _ => (self.content.clone(), None),
        };

        Ok(Message {
            content,
            next_param: self.next_param,
            sanitized_output: sanitized,
            role: self.role.clone(),
        })
    }

    pub fn unwrap<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        self.content.to_pyobject(py)
    }

    pub fn model_dump<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let message = PyDict::new(py);

        message.set_item("role", self.role.clone())?;
        message.set_item("content", self.unwrap(py)?)?;
        Ok(message)
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

impl Message {
    pub fn new_rs(content: PromptContent) -> Self {
        Self {
            content,
            next_param: 1,
            sanitized_output: None,
            role: Role::User.to_string(),
        }
    }
    pub fn from(content: PromptContent, role: Role) -> Self {
        Self {
            content,
            next_param: 1,
            sanitized_output: None,
            role: role.to_string(),
        }
    }

    pub fn is_empty(&self) -> bool {
        match &self.content {
            PromptContent::Str(s) => s.is_empty(),
            _ => false,
        }
    }
}

/// Checks if an object is a subclass of a pydantic BaseModel. This is used when validating structured outputs
/// # Arguments
/// * `py` - The Python interpreter instance
/// * `object` - The object to check
/// # Returns
/// A boolean indicating whether the object is a subclass of pydantic.BaseModel
pub fn check_pydantic_model<'py>(
    py: Python<'py>,
    object: &Bound<'_, PyAny>,
) -> Result<bool, PotatoError> {
    // check pydantic import. Return false if it fails
    let pydantic = match py.import("pydantic").map_err(|e| {
        error!("Failed to import pydantic: {}", e);
        false
    }) {
        Ok(pydantic) => pydantic,
        Err(_) => return Ok(false),
    };

    // get builtin subclass
    let is_subclass = py.import("builtins")?.getattr("issubclass")?;

    // Need to check if provided object is a basemodel
    let basemodel = pydantic.getattr("BaseModel")?;
    let matched = is_subclass.call1((object, basemodel))?.extract::<bool>()?;

    Ok(matched)
}

/// Generate a JSON schema from a pydantic BaseModel object.
/// # Arguments
/// * `object` - The pydantic BaseModel object to generate the schema from.
/// # Returns
/// A JSON schema as a serde_json::Value.
fn get_json_schema_from_basemodel(object: &Bound<'_, PyAny>) -> Result<Value, PotatoError> {
    // call staticmethod .model_json_schema()
    let name = object.getattr("__name__")?.extract::<String>()?;
    let schema = object.getattr("model_json_schema")?.call1(())?;

    let mut schema = pyobject_to_json(&schema).map_err(|e| {
        error!("Failed to convert schema to JSON: {}", e);
        PotatoError::PySerializationError(e.to_string())
    })?;

    // ensure schema as additionalProperties set to false
    if let Some(additional_properties) = schema.get_mut("additionalProperties") {
        *additional_properties = serde_json::json!(false);
    } else {
        schema
            .as_object_mut()
            .unwrap()
            .insert("additionalProperties".to_string(), serde_json::json!(false));
    }

    let json_schema = serde_json::json!({
        "type": "json_schema",
        "json_schema": {
             "name": name,
             "schema": schema,
             "strict": true
        },
    });

    Ok(json_schema)
}

pub fn parse_pydantic_model<'py>(
    py: Python<'py>,
    object: &Bound<'_, PyAny>,
) -> Result<Option<Value>, PotatoError> {
    let is_subclass = check_pydantic_model(py, object)?;
    if is_subclass {
        Ok(Some(get_json_schema_from_basemodel(object)?))
    } else {
        Ok(None)
    }
}
