use crate::RegistryType;
use crate::StorageType;
use opsml_crypt::decrypt_key;
use opsml_error::TypeError;
use opsml_utils::{uid_to_byte_key, PyHelperFuncs};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::fmt::Display;
use std::path::PathBuf;

#[derive(Serialize, Deserialize)]
pub struct MultiPartQuery {
    pub path: String,
}

#[derive(Serialize, Deserialize, Default)]
pub struct PresignedQuery {
    pub path: String,
    pub session_url: Option<String>,
    pub part_number: Option<i32>,
    pub for_multi_part: Option<bool>,
}

#[derive(Serialize, Deserialize)]
pub struct UploadPartArgParser {}

#[derive(Serialize, Deserialize)]
pub struct ListFileQuery {
    pub path: String,
}

#[derive(Serialize, Deserialize)]
pub struct DeleteFileQuery {
    pub path: String,
    pub recursive: bool,
}

#[derive(Serialize, Deserialize)]
pub struct DownloadFileQuery {
    pub path: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct FileInfo {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub size: i64,
    #[pyo3(get)]
    pub object_type: String,
    #[pyo3(get)]
    pub created: String,
    #[pyo3(get)]
    pub suffix: String,
}

#[pymethods]
impl FileInfo {
    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }
}

#[derive(Serialize, Deserialize)]
pub struct PresignedUrl {
    pub url: String,
}

#[derive(Serialize, Deserialize)]
pub struct ListFileResponse {
    pub files: Vec<String>,
}

#[derive(Serialize, Deserialize)]
pub struct ListFileInfoResponse {
    pub files: Vec<FileInfo>,
}

#[derive(Serialize, Deserialize)]
pub struct DeleteFileResponse {
    pub deleted: bool,
}

#[derive(Serialize, Deserialize)]
pub struct MultiPartSession {
    pub session_url: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct StorageSettings {
    pub storage_type: StorageType,
}

#[derive(Serialize, Deserialize)]
pub struct UploadResponse {
    pub uploaded: bool,
    pub message: String,
}

#[derive(Serialize, Deserialize)]
pub struct DownloadResponse {
    pub exists: bool,
}

#[derive(Serialize, Deserialize)]
pub struct PermissionDenied {
    pub error: String,
}

pub struct UploadPartArgs {
    pub presigned_url: Option<String>,
    pub chunk_size: u64,
    pub chunk_index: u64,
    pub this_chunk_size: u64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ArtifactKeyRequest {
    pub uid: String,
    pub registry_type: RegistryType,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ArtifactKey {
    pub uid: String,
    pub registry_type: RegistryType,
    pub encrypted_key: Vec<u8>,
    pub storage_key: String,
}

impl ArtifactKey {
    pub fn get_decrypt_key(&self) -> Result<Vec<u8>, TypeError> {
        // convert uid to byte key (used for card encryption)
        let uid_key = uid_to_byte_key(&self.uid)?;

        decrypt_key(&uid_key, &self.encrypted_key).map_err(|e| TypeError::Error(format!("{}", e)))
    }

    pub fn storage_path(&self) -> PathBuf {
        PathBuf::from(&self.storage_key)
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub enum Operation {
    Create,
    Read,
    Write,
    Delete,
    List,
    Info,
    Encrypt,
    Decrypt,
}

impl Display for Operation {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Operation::Read => write!(f, "Read"),
            Operation::Write => write!(f, "Write"),
            Operation::Delete => write!(f, "Delete"),
            Operation::List => write!(f, "List"),
            Operation::Info => write!(f, "Info"),
            Operation::Encrypt => write!(f, "Encrypt"),
            Operation::Decrypt => write!(f, "Decrypt"),
            Operation::Create => write!(f, "Create"),
        }
    }
}
