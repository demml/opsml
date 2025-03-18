use crate::error::PotatoHeadError;
use mime_guess;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::sync::OnceLock;

static DOCUMENT_MEDIA_TYPES: OnceLock<HashSet<&'static str>> = OnceLock::new();

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

fn image_format(media_type: &str) -> PyResult<String> {
    let format = match media_type {
        "image/jpeg" => "jpeg",
        "image/png" => "png",
        "image/gif" => "gif",
        "image/webp" => "webp",
        _ => {
            return Err(PotatoHeadError::new_err(format!(
                "Unknown image media type: {}",
                media_type
            )))
        }
    };

    Ok(format.to_string())
}

fn document_format(media_type: &str) -> PyResult<String> {
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
            return Err(PotatoHeadError::new_err(format!(
                "Unknown document media type: {}",
                media_type
            )))
        }
    };
    Ok(format.to_string())
}

fn guess_type(url: &str) -> PyResult<String> {
    // fail if mime type is not found
    let mime_type = mime_guess::from_path(url).first().ok_or_else(|| {
        PotatoHeadError::new_err(format!("Failed to guess mime type for {}", url))
    })?;

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
    url: String,
    #[pyo3(get)]
    kind: String,
}

#[pymethods]
impl ImageUrl {
    #[new]
    fn new(url: String) -> PyResult<Self> {
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
            url,
            kind: "image-url".to_string(),
        })
    }

    #[getter]
    fn media_type(&self) -> PyResult<String> {
        if self.url.ends_with(".jpg") || self.url.ends_with(".jpeg") {
            Ok("image/jpeg".to_string())
        } else if self.url.ends_with(".png") {
            Ok("image/png".to_string())
        } else if self.url.ends_with(".gif") {
            Ok("image/gif".to_string())
        } else if self.url.ends_with(".webp") {
            Ok("image/webp".to_string())
        } else {
            Err(PotatoHeadError::new_err(format!(
                "Unknown image file extension: {}",
                self.url
            )))
        }
    }

    #[getter]
    fn format(&self) -> PyResult<String> {
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
    #[pyo3(signature = (url, kind=None))]
    fn new(url: &str, kind: Option<&str>) -> PyResult<Self> {
        Ok(Self {
            url: url.to_string(),
            kind: kind.unwrap_or("document-url").to_string(),
        })
    }

    #[getter]
    fn media_type(&self) -> PyResult<String> {
        guess_type(&self.url)
    }

    #[getter]
    fn format(&self) -> PyResult<String> {
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
    fn new(data: Vec<u8>, media_type: String) -> PyResult<Self> {
        // assert that media type is valid, must be audio, image, or document

        if get_audio_media_types().contains(media_type.as_str())
            || get_image_media_types().contains(media_type.as_str())
            || get_document_media_types().contains(media_type.as_str())
        {
            PotatoHeadError::new_err(format!("Unknown media type: {}", media_type));
        }

        Ok(Self {
            data,
            media_type,
            kind: "binary".to_string(),
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
    fn format(&self) -> PyResult<String> {
        if self.is_audio() {
            if self.media_type == "audio/mpeg" {
                Ok("mp3".to_string())
            } else if self.media_type == "audio/wav" {
                Ok("wav".to_string())
            } else {
                Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "Unknown media type: {}",
                    self.media_type
                )))
            }
        } else if self.is_image() {
            image_format(&self.media_type)
        } else if self.is_document() {
            document_format(&self.media_type)
        } else {
            Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Unknown media type: {}",
                self.media_type
            )))
        }
    }
}
