use crate::error::TypeError;
use crate::interfaces::DriftProfileUri;
use crate::RegistryType;
use crate::StorageType;
use chrono::{DateTime, Utc};
use opsml_crypt::decrypt_key;
use opsml_utils::{uid_to_byte_key, PyHelperFuncs};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
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

    pub stripped_path: String,
}

#[pymethods]
impl FileInfo {
    pub fn __str__(&self) -> String {
        // serialize the struct to a string
        PyHelperFuncs::__str__(self)
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct FileTreeNode {
    pub name: String,
    pub created_at: String,
    pub object_type: String,
    pub size: i64,
    pub path: String,
    pub suffix: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FileTreeResponse {
    pub files: Vec<FileTreeNode>,
}

#[derive(Serialize, Deserialize)]
pub struct PresignedUrl {
    pub url: String,
}

#[derive(Serialize, Deserialize)]
pub struct ListFileResponse {
    pub files: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Default)]
pub enum MultipartCompleteParts {
    Aws(CompletedUploadParts),
    Azure(Vec<String>),
    #[default]
    None,
}

#[derive(Debug, Serialize, Deserialize, Default)]
pub struct CompleteMultipartUpload {
    pub path: String,
    pub session_url: String,
    pub parts: MultipartCompleteParts,
    pub cancel: bool,
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

    // only used for aws
    pub bucket: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct StorageSettings {
    pub storage_type: StorageType,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UiSettings {
    pub scouter_enabled: bool,
    pub sso_enabled: bool,
}

#[derive(Serialize, Deserialize)]
pub struct UploadResponse {
    pub uploaded: bool,
    pub message: String,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct CompletedUploadPart {
    pub part_number: i32,
    pub e_tag: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct CompletedUploadParts {
    pub parts: Vec<CompletedUploadPart>,
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
    pub space: String,
    pub registry_type: RegistryType,
    pub encrypted_key: Vec<u8>,
    pub storage_key: String,
}

impl ArtifactKey {
    pub fn get_decrypt_key(&self) -> Result<Vec<u8>, TypeError> {
        // convert uid to byte key (used for card encryption)
        let uid_key = uid_to_byte_key(&self.uid)?;

        Ok(decrypt_key(&uid_key, &self.encrypted_key)?)
    }

    pub fn storage_path(&self) -> PathBuf {
        PathBuf::from(&self.storage_key)
    }
}

// implement Display for ArtifactKey and mask the encrypted_key and storage_key
impl Display for ArtifactKey {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "ArtifactKey {{ uid: {}, registry_type: {}, encrypted_key: <masked>, storage_key: <masked> }}",
            self.uid, self.registry_type
        )
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateArtifactRequest {
    pub uid: String,
    pub created_at: DateTime<Utc>,
    pub app_env: String,
    pub space: String,
    pub name: String,
    pub version: String,
    pub filename: String,
    pub data_type: String,
}

#[derive(Debug, Clone)]
pub enum Operation {
    Create,
    Read,
    Write,
    Delete,
    List,
    Info,
    Encrypt,
    Decrypt,
    Load,
    Check,
    Update,
    Unknown,
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
            Operation::Load => write!(f, "Load"),
            Operation::Check => write!(f, "Check"),
            Operation::Update => write!(f, "Update"),
            Operation::Unknown => write!(f, "Unknown"),
        }
    }
}

#[derive(Debug, Clone)]
pub enum ResourceType {
    File,
    Database,
    Card,
    Drift,
}

impl Display for ResourceType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ResourceType::File => write!(f, "File"),
            ResourceType::Database => write!(f, "Database"),
            ResourceType::Card => write!(f, "Card"),
            ResourceType::Drift => write!(f, "Drift"),
        }
    }
}

#[derive(Debug, Clone)]
pub enum AuditStatus {
    Success,
    Failed,
    Denied,
}

impl Display for AuditStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AuditStatus::Success => write!(f, "Success"),
            AuditStatus::Failed => write!(f, "Failed"),
            AuditStatus::Denied => write!(f, "Denied"),
        }
    }
}

/// Request to get a file from the registry
///
/// # Arguments
/// * `uid` - The unique identifier of card that is requesting the file
/// * `file` - The file tree node
/// * `registry_type` - The type of registry
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct RawFileRequest {
    pub uid: String,
    pub path: String,
    pub registry_type: RegistryType,
}

/// Request to get model drift profiles for ui rendering
///
/// # Arguments
/// * `uid` - The unique identifier of card that is requesting the file
/// * `file` - The file tree node
/// * `registry_type` - The type of registry
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DriftProfileRequest {
    pub uid: String,
    pub drift_profile_uri_map: HashMap<String, DriftProfileUri>,
    pub registry_type: RegistryType,
}

/// Response to get a file from the registry
///
/// # Arguments
/// * `content` - The content of the file
/// * `suffix` - The suffix of the file
/// * `mime_type` - The mime type of the file
///
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct RawFile {
    pub content: String,
    pub suffix: String,
    pub mime_type: String,
}

#[derive(Serialize, Deserialize)]
pub struct UpdatedProfile {
    pub updated: bool,
}
