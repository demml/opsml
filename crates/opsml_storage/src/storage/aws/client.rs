use crate::storage::aws::error::AwsError;
use crate::storage::base::{PathExt, StorageClient, get_files};
use crate::storage::error::StorageError;
use crate::storage::filesystem::FileSystem;
use crate::storage::utils::get_chunk_parts;
use async_trait::async_trait;
use aws_config::BehaviorVersion;
use aws_config::SdkConfig;
use aws_sdk_s3::Client;
use aws_sdk_s3::operation::get_object::GetObjectOutput;
use aws_sdk_s3::presigning::PresigningConfig;
use aws_sdk_s3::primitives::ByteStream;
use aws_sdk_s3::primitives::Length;
use aws_sdk_s3::types::{CompletedMultipartUpload, CompletedPart};
use opsml_settings::config::OpsmlStorageSettings;
use opsml_types::StorageType;
use opsml_types::contracts::{CompleteMultipartUpload, FileInfo, MultipartCompleteParts};
use opsml_utils::ChunkParts;
use reqwest::Client as HttpClient;
use std::fs::File;
use std::io::Write;
use std::path::Path;
use std::path::PathBuf;
use std::time::Duration;
use tracing::{error, instrument};

// Notes:
// For general compatibility with the Pyo3, Rust and generics, we need to define structs with sync in mind.
// Thus, some structs and functions will need to spawn a new runtime to run async functions from a sync context.
// This is handled at the 3rd-party abstraction level, so the user does not need to worry about it.

pub struct AWSCreds {
    pub config: SdkConfig,
}

impl AWSCreds {
    pub async fn new() -> Result<Self, AwsError> {
        let config = aws_config::load_defaults(BehaviorVersion::latest()).await;

        Ok(Self { config })
    }
}

// standalone function for creating a presigned url for a part
pub async fn generate_presigned_url_for_part(
    bucket: &str,
    part_number: i32,
    path: &str,
    upload_id: &str,
    client: &Client,
) -> Result<String, AwsError> {
    let expires_in = Duration::from_secs(600); // Set expiration time for presigned URL

    let presigned_request = client
        .upload_part()
        .bucket(bucket)
        .key(path)
        .upload_id(upload_id)
        .part_number(part_number)
        .presigned(PresigningConfig::expires_in(expires_in)?)
        .await?;

    Ok(presigned_request.uri().to_string())
}

pub struct AWSMulitPartUpload {
    bucket: String,
    client: Client,
    rpath: String,
    lpath: String,
    pub upload_id: String,
    file_size: u64,
    http_client: HttpClient,
}

#[derive(Clone)]
pub struct UploadPart {
    e_tag: String,
    part_number: i32,
}

impl AWSMulitPartUpload {
    pub async fn new(
        bucket: &str,
        lpath: &str,
        rpath: &str,
        upload_id: &str,
    ) -> Result<Self, AwsError> {
        let creds = AWSCreds::new().await?;
        let client = Client::new(&creds.config);
        let file_size = Self::get_file_size(lpath)?;

        Ok(Self {
            client,
            bucket: bucket.to_string(),
            rpath: rpath.to_string(),
            lpath: lpath.to_string(),
            upload_id: upload_id.to_string(),
            file_size,

            http_client: HttpClient::new(),
        })
    }

    fn get_file_size(path: &str) -> Result<u64, AwsError> {
        let metadata = std::fs::metadata(path)?;
        Ok(metadata.len())
    }

    /// Generate a presigned url for a part in the multipart upload
    /// This needs to be a non-self method because it is called from both client or server
    pub async fn upload_part(
        &self,
        part_number: i32,
        body: ByteStream,
        presigned_url: &str,
    ) -> Result<UploadPart, AwsError> {
        let body = body
            .collect()
            .await
            .map_err(|e| AwsError::ByteStreamError(e.to_string()))?;

        let response = self
            .http_client
            .put(presigned_url)
            .body(body.into_bytes())
            .send()
            .await?;

        if response.status().is_success() {
            let e_tag = response
                .headers()
                .get("ETag")
                .ok_or_else(|| AwsError::MissingEtagError)?
                .to_str()
                .map_err(|e| AwsError::InvalidEtagError(e.to_string()))?
                .to_string();

            Ok(UploadPart { e_tag, part_number })
        } else {
            Err(AwsError::UploadError(response.status()))
        }
    }

    pub async fn complete_upload(&self, parts: Vec<UploadPart>) -> Result<(), AwsError> {
        let completed_parts: Vec<CompletedPart> = parts
            .into_iter()
            .map(|part| {
                CompletedPart::builder()
                    .e_tag(part.e_tag)
                    .part_number(part.part_number)
                    .build()
            })
            .collect();

        let completed_multipart_upload = CompletedMultipartUpload::builder()
            .set_parts(Some(completed_parts))
            .build();

        self.client
            .complete_multipart_upload()
            .bucket(&self.bucket)
            .key(&self.rpath)
            .multipart_upload(completed_multipart_upload)
            .upload_id(&self.upload_id)
            .send()
            .await?;

        Ok(())
    }

    pub async fn abort_multipart_upload(&self) -> Result<(), AwsError> {
        let _abort_multipart_upload_res = self
            .client
            .abort_multipart_upload()
            .bucket(&self.bucket)
            .key(&self.rpath)
            .upload_id(&self.upload_id)
            .send()
            .await?;

        Ok(())
    }

    pub async fn get_next_chunk(
        &self,
        path: &Path,
        chunk_size: u64,
        chunk_index: u64,
        this_chunk_size: u64,
    ) -> Result<ByteStream, AwsError> {
        let stream = ByteStream::read_from()
            .path(path)
            .offset(chunk_index * chunk_size)
            .length(Length::Exact(this_chunk_size))
            .build()
            .await
            .map_err(|e| AwsError::NextChunkError(e.to_string()))?;

        Ok(stream)
    }

    pub async fn upload_file_in_chunks(&self, chunk_parts: ChunkParts) -> Result<(), AwsError> {
        let chunk_size = std::cmp::min(self.file_size, chunk_parts.chunk_size);

        let mut upload_parts = Vec::new();

        for chunk_index in 0..chunk_parts.chunk_count {
            let this_chunk = if chunk_parts.chunk_count - 1 == chunk_index {
                chunk_parts.size_of_last_chunk
            } else {
                chunk_size
            };

            let presigned_url = generate_presigned_url_for_part(
                &self.bucket,
                (chunk_index + 1) as i32,
                &self.rpath,
                &self.upload_id,
                &self.client,
            )
            .await?;

            let path = Path::new(&self.lpath);
            let body = ByteStream::read_from()
                .path(path)
                .offset(chunk_index * chunk_size)
                .length(Length::Exact(this_chunk))
                .build()
                .await
                .map_err(|e| AwsError::NextChunkError(e.to_string()))?;

            let part = self
                .upload_part((chunk_index + 1) as i32, body, &presigned_url)
                .await?;
            upload_parts.push(part);
        }

        match self.complete_upload(upload_parts).await {
            Ok(_) => Ok(()),
            Err(e) => {
                error!("Failed to complete upload: {}. Aborting", e);
                self.abort_multipart_upload().await?;
                Err(e)
            }
        }
    }
}

#[derive(Clone)]
pub struct AWSStorageClient {
    pub client: Client,
    pub bucket: String,
}

#[async_trait]
impl StorageClient for AWSStorageClient {
    fn storage_type(&self) -> StorageType {
        StorageType::Aws
    }
    async fn bucket(&self) -> &str {
        &self.bucket
    }
    async fn new(settings: &OpsmlStorageSettings) -> Result<Self, StorageError> {
        // read creds from env
        let creds = AWSCreds::new().await?;
        let client = Client::new(&creds.config);

        let bucket = settings
            .storage_uri
            .strip_prefix("s3://")
            .unwrap_or(&settings.storage_uri)
            .to_string();

        Ok(Self { client, bucket })
    }

    async fn get_object(&self, lpath: &str, rpath: &str) -> Result<(), StorageError> {
        // check if lpath and rpath have suffixes
        let lpath = Path::new(lpath);
        let rpath = Path::new(rpath);

        // fail if lpath and rpath have no suffixes
        if lpath.extension().is_none() || rpath.extension().is_none() {
            return Err(StorageError::LocalAndRemotePathsMustHaveSuffixesError);
        }

        // create and open lpath file
        let prefix = Path::new(lpath).parent().unwrap();

        if !prefix.exists() {
            // create the directory if it does not exist and skip errors
            std::fs::create_dir_all(prefix)?;
        }

        // create and open lpath file
        let mut file = File::create(lpath)?;

        // get stream
        let mut response = self.get_object_stream(rpath.to_str().unwrap()).await?;

        // iterate over the stream and write to the file
        while let Some(v) = response.body.next().await {
            let chunk = v.map_err(|e| AwsError::ByteStreamError(e.to_string()))?;
            file.write_all(&chunk)?;
        }

        Ok(())
    }

    /// Generate a presigned url for an object in the storage bucket
    ///
    /// # Arguments
    ///
    /// * `path` - The path to the object in the bucket
    /// * `expiration` - The time in seconds for the presigned url to expire
    ///
    /// # Returns
    ///
    /// A Result with the presigned url if successful
    ///
    async fn generate_presigned_url(
        &self,
        path: &str,
        expiration: u64,
    ) -> Result<String, StorageError> {
        let expires_in = std::time::Duration::from_secs(expiration);

        let uri = self
            .client
            .get_object()
            .bucket(&self.bucket)
            .key(path)
            .presigned(PresigningConfig::expires_in(expires_in).map_err(AwsError::PresignError)?)
            .await
            .map_err(|e| AwsError::GetObjectError(Box::new(e)))?;

        Ok(uri.uri().to_string())
    }

    /// List all objects in a path
    ///
    /// # Arguments
    ///
    /// * `path` - The path to list objects from
    ///
    /// # Returns
    ///
    /// A list of objects in the path
    async fn find(&self, path: &str) -> Result<Vec<String>, StorageError> {
        // check if path = "/"
        let objects = if path == "/" || path.is_empty() {
            self.client
                .list_objects_v2()
                .bucket(&self.bucket)
                .send()
                .await
                .map_err(|e| AwsError::ListObjectsV2Error(Box::new(e)))?
        } else {
            self.client
                .list_objects_v2()
                .bucket(&self.bucket)
                .prefix(path)
                .send()
                .await
                .map_err(|e| AwsError::ListObjectsV2Error(Box::new(e)))?
        };

        Ok(objects
            .contents
            .unwrap_or_else(Vec::new)
            .iter()
            .filter_map(|o| o.key.clone())
            .collect())
    }

    /// Find object information. Runs the same operation as find but returns more information about each object
    ///
    /// # Arguments
    ///
    /// * `path` - The path to list objects from
    ///
    /// # Returns
    ///
    async fn find_info(&self, path: &str) -> Result<Vec<FileInfo>, StorageError> {
        let response = self
            .client
            .list_objects_v2()
            .bucket(&self.bucket)
            .prefix(path)
            .send()
            .await
            .map_err(|e| AwsError::ListObjectsV2Error(Box::new(e)))?;

        Ok(response
            .contents
            .unwrap_or_else(Vec::new)
            .iter()
            .map(|o| {
                let object_type = match o.storage_class.to_owned() {
                    Some(storage_class) => storage_class.to_string(),
                    None => "".to_string(),
                };
                let key = o.key.as_ref().unwrap_or(&String::new()).to_owned();
                let file = Path::new(&key);

                let size = o.size.unwrap_or_default();

                let created = match o.last_modified {
                    Some(last_modified) => last_modified.to_string(),
                    None => "".to_string(),
                };

                let filepath = key
                    .strip_prefix(&format!("{}/", self.bucket))
                    .unwrap_or(&key);

                let stripped_path = filepath
                    .strip_prefix(path)
                    .unwrap_or(filepath)
                    .strip_prefix("/")
                    .unwrap_or(filepath)
                    .to_string();

                FileInfo {
                    name: filepath.to_string(),
                    size,
                    object_type,
                    created,
                    suffix: file.extension().unwrap().to_str().unwrap().to_string(),
                    stripped_path,
                }
            })
            .collect())
    }

    /// copy object from one bucket to another without deleting the source object
    ///
    /// # Arguments
    ///
    /// * `src` - The path to the source object
    /// * `dest` - The path to the destination object
    ///
    /// # Returns
    ///
    /// A Result with the object name if successful
    async fn copy_object(&self, src: &str, dest: &str) -> Result<bool, StorageError> {
        self.client
            .copy_object()
            .copy_source(format!("{}/{}", self.bucket, src))
            .bucket(&self.bucket)
            .key(dest)
            .send()
            .await
            .map_err(|e| AwsError::CopyObjectError(Box::new(e)))?;

        Ok(true)
    }

    /// Copy objects from the storage bucket
    async fn copy_objects(&self, src: &str, dest: &str) -> Result<bool, StorageError> {
        let objects = self.find(src).await?;
        let dest = Path::new(dest);
        let src = PathBuf::from(src);

        for obj in objects {
            let file_path = Path::new(obj.as_str());
            let relative_path = file_path.relative_path(&src)?;
            let remote_path = dest.join(relative_path);

            self.copy_object(file_path.to_str().unwrap(), remote_path.to_str().unwrap())
                .await?;
        }

        Ok(true)
    }

    /// Delete an object from the storage bucket
    ///
    /// # Arguments
    ///
    /// * `path` - The path to the object in the bucket
    ///
    async fn delete_object(&self, path: &str) -> Result<bool, StorageError> {
        self.client
            .delete_object()
            .bucket(&self.bucket)
            .key(path)
            .send()
            .await
            .map_err(|e| AwsError::DeleteObjectError(Box::new(e)))?;

        Ok(true)
    }

    /// Delete objects from the storage bucket
    ///
    /// # Arguments
    ///
    /// * `path` - Bucket and prefix path to the objects to delete
    ///
    async fn delete_objects(&self, path: &str) -> Result<bool, StorageError> {
        let objects = self.find(path).await?;

        let mut delete_object_ids: Vec<aws_sdk_s3::types::ObjectIdentifier> = vec![];
        for obj in objects {
            let obj_id = aws_sdk_s3::types::ObjectIdentifier::builder()
                .key(obj)
                .build()
                .map_err(|e| AwsError::BuildError(e.to_string()))?;
            delete_object_ids.push(obj_id);
        }

        self.client
            .delete_objects()
            .bucket(&self.bucket)
            .delete(
                aws_sdk_s3::types::Delete::builder()
                    .set_objects(Some(delete_object_ids))
                    .build()
                    .map_err(|e| AwsError::BuildError(e.to_string()))?,
            )
            .send()
            .await
            .map_err(|e| AwsError::DeleteObjectsError(Box::new(e)))?;

        Ok(true)
    }

    // put object stream
}

impl AWSStorageClient {
    /// Get an object stream from the storage bucket
    ///
    /// # Arguments
    ///
    /// * `rpath` - The path to the object in the bucket
    ///
    /// # Returns
    ///
    /// A Result with the object stream if successful
    ///
    pub async fn get_object_stream(&self, rpath: &str) -> Result<GetObjectOutput, AwsError> {
        let response = self
            .client
            .get_object()
            .bucket(&self.bucket)
            .key(rpath)
            .send()
            .await?;
        Ok(response)
    }

    pub async fn create_multipart_upload(&self, path: &str) -> Result<String, AwsError> {
        let response = self
            .client
            .create_multipart_upload()
            .bucket(&self.bucket)
            .key(path)
            .send()
            .await?;

        Ok(response.upload_id.unwrap())
    }

    pub async fn create_multipart_uploader(
        &self,
        lpath: &str,
        rpath: &str,
    ) -> Result<AWSMulitPartUpload, AwsError> {
        let upload_id = self.create_multipart_upload(rpath).await?;
        AWSMulitPartUpload::new(&self.bucket, lpath, rpath, &upload_id).await
    }

    /// Generate a presigned url for a part in the multipart upload
    /// This needs to be a non-self method because it is called from both client or server
    pub async fn generate_presigned_url_for_part(
        &self,
        part_number: i32,
        path: &str,
        upload_id: &str,
    ) -> Result<String, AwsError> {
        let expires_in = Duration::from_secs(600); // Set expiration time for presigned URL

        let presigned_request = self
            .client
            .upload_part()
            .bucket(&self.bucket)
            .key(path)
            .upload_id(upload_id)
            .part_number(part_number)
            .presigned(PresigningConfig::expires_in(expires_in)?)
            .await?;

        Ok(presigned_request.uri().to_string())
    }

    /// Helper function to complete an upload from parts
    /// This is use by the server to complete a client multipart upload
    ///
    /// # Arguments
    ///
    /// * `upload_id` - The upload id of the multipart upload
    /// * `parts` - The completed parts of the upload
    /// * `path` - The path to the object in the bucket
    ///
    #[instrument(skip_all)]
    pub async fn complete_upload_from_parts(
        &self,
        upload_id: &str,
        parts: MultipartCompleteParts,
        path: &str,
    ) -> Result<(), AwsError> {
        // convert the parts to CompletedPart
        let parts = match parts {
            MultipartCompleteParts::Aws(parts) => parts,
            _ => return Err(AwsError::InvalidPartsTypeError),
        };

        let upload_parts = parts
            .parts
            .iter()
            .map(|part| {
                CompletedPart::builder()
                    .e_tag(part.e_tag.clone())
                    .part_number(part.part_number)
                    .build()
            })
            .collect();

        let completed_multipart_upload: CompletedMultipartUpload =
            CompletedMultipartUpload::builder()
                .set_parts(Some(upload_parts))
                .build();

        let _upload_response = self
            .client
            .complete_multipart_upload()
            .bucket(&self.bucket)
            .key(path)
            .multipart_upload(completed_multipart_upload)
            .upload_id(upload_id)
            .send()
            .await?;

        Ok(())
    }
}

// For both python and rust, we need to define 2 structs: one for rust that supports async and one for python that does not
#[derive(Clone)]
pub struct S3FStorageClient {
    client: AWSStorageClient,
}

#[async_trait]
impl FileSystem for S3FStorageClient {
    fn name(&self) -> &str {
        "S3FStorageClient"
    }

    fn bucket(&self) -> &str {
        &self.client.bucket
    }

    async fn new(settings: &OpsmlStorageSettings) -> Self {
        let client = AWSStorageClient::new(settings).await.unwrap();
        Self { client }
    }

    fn storage_type(&self) -> StorageType {
        StorageType::Aws
    }

    async fn find(&self, path: &Path) -> Result<Vec<String>, StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);
        self.client.find(stripped_path.to_str().unwrap()).await
    }

    async fn find_info(&self, path: &Path) -> Result<Vec<FileInfo>, StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);
        self.client.find_info(stripped_path.to_str().unwrap()).await
    }

    async fn get(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        // strip the paths
        let stripped_rpath = rpath.strip_path(self.client.bucket().await);
        let stripped_lpath = lpath.strip_path(self.client.bucket().await);

        if recursive {
            // list all objects in the path
            let objects = self.client.find(stripped_rpath.to_str().unwrap()).await?;

            // iterate over each object and get it
            for obj in objects {
                let file_path = Path::new(obj.as_str());
                let stripped_path = file_path.strip_path(self.client.bucket().await);
                let relative_path = file_path.relative_path(&stripped_rpath)?;
                let local_path = stripped_lpath.join(relative_path);

                self.client
                    .get_object(
                        local_path.to_str().unwrap(),
                        stripped_path.to_str().unwrap(),
                    )
                    .await?;
            }
        } else {
            self.client
                .get_object(
                    stripped_lpath.to_str().unwrap(),
                    stripped_rpath.to_str().unwrap(),
                )
                .await?;
        }

        Ok(())
    }

    async fn copy(&self, src: &Path, dest: &Path, recursive: bool) -> Result<(), StorageError> {
        let stripped_src = src.strip_path(self.client.bucket().await);
        let stripped_dest = dest.strip_path(self.client.bucket().await);

        if recursive {
            self.client
                .copy_objects(
                    stripped_src.to_str().unwrap(),
                    stripped_dest.to_str().unwrap(),
                )
                .await?;
        } else {
            self.client
                .copy_object(
                    stripped_src.to_str().unwrap(),
                    stripped_dest.to_str().unwrap(),
                )
                .await?;
        }

        Ok(())
    }

    async fn rm(&self, path: &Path, recursive: bool) -> Result<(), StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);

        if recursive {
            self.client
                .delete_objects(stripped_path.to_str().unwrap())
                .await?;
        } else {
            self.client
                .delete_object(stripped_path.to_str().unwrap())
                .await?;
        }

        Ok(())
    }
    async fn exists(&self, path: &Path) -> Result<bool, StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);
        let objects = self.client.find(stripped_path.to_str().unwrap()).await?;

        Ok(!objects.is_empty())
    }

    async fn generate_presigned_url(
        &self,
        path: &Path,
        expiration: u64,
    ) -> Result<String, StorageError> {
        let stripped_path = path.strip_path(self.client.bucket().await);
        self.client
            .generate_presigned_url(stripped_path.to_str().unwrap(), expiration)
            .await
    }

    async fn put(&self, lpath: &Path, rpath: &Path, recursive: bool) -> Result<(), StorageError> {
        let stripped_lpath = lpath.strip_path(self.client.bucket().await);
        let stripped_rpath = rpath.strip_path(self.client.bucket().await);

        if recursive {
            if !stripped_lpath.is_dir() {
                return Err(StorageError::PathMustBeDirectoryError);
            }

            let files: Vec<PathBuf> = get_files(&stripped_lpath)?;

            for file in files {
                let chunk_parts = get_chunk_parts(&file)?;

                let stripped_file_path = file.strip_path(self.client.bucket().await);
                let relative_path = file.relative_path(&stripped_lpath)?;
                let remote_path = stripped_rpath.join(relative_path);

                let uploader = self
                    .client
                    .create_multipart_uploader(
                        stripped_file_path.to_str().unwrap(),
                        remote_path.to_str().unwrap(),
                    )
                    .await?;

                uploader.upload_file_in_chunks(chunk_parts).await?;
            }
        } else {
            let chunk_parts = get_chunk_parts(&stripped_lpath)?;

            let uploader = self
                .client
                .create_multipart_uploader(
                    stripped_lpath.to_str().unwrap(),
                    stripped_rpath.to_str().unwrap(),
                )
                .await?;

            uploader.upload_file_in_chunks(chunk_parts).await?;
        }

        Ok(())
    }

    async fn complete_multipart_upload(
        &self,
        request: CompleteMultipartUpload,
    ) -> Result<(), StorageError> {
        let parts = request.parts;
        Ok(self
            .client
            .complete_upload_from_parts(&request.session_url, parts, &request.path)
            .await?)
    }
}

impl S3FStorageClient {
    pub async fn create_multipart_upload(&self, path: &Path) -> Result<String, AwsError> {
        self.client
            .create_multipart_upload(path.to_str().unwrap())
            .await
    }

    pub async fn create_multipart_uploader(
        &self,
        rpath: &Path,
        lpath: &Path,
    ) -> Result<AWSMulitPartUpload, AwsError> {
        let upload_id = self
            .client
            .create_multipart_upload(rpath.to_str().unwrap())
            .await?;

        let bucket = self.client.bucket().await.to_string();

        AWSMulitPartUpload::new(
            &bucket,
            lpath.to_str().unwrap(),
            rpath.to_str().unwrap(),
            &upload_id,
        )
        .await
    }

    pub async fn generate_presigned_url_for_part(
        &self,
        part_number: i32,
        path: &Path,
        upload_id: &str,
    ) -> Result<String, AwsError> {
        self.client
            .generate_presigned_url_for_part(part_number, path.to_str().unwrap(), upload_id)
            .await
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::storage::error::StorageError;
    use opsml_settings::config::OpsmlConfig;
    use opsml_utils::create_uuid7;
    use rand::Rng;
    use rand::distr::Alphanumeric;
    use rand::rng;
    use std::path::Path;
    use tempfile::TempDir;

    pub fn create_file(name: &str, chunk_size: &u64) {
        let mut file = File::create(name).expect("Could not create sample file.");

        while file.metadata().unwrap().len() <= chunk_size * 2 {
            let rand_string: String = rng()
                .sample_iter(&Alphanumeric)
                .take(256)
                .map(char::from)
                .collect();
            let return_string: String = "\n".to_string();
            file.write_all(rand_string.as_ref())
                .expect("Error writing to file.");
            file.write_all(return_string.as_ref())
                .expect("Error writing to file.");
        }
    }

    #[tokio::test]
    async fn test_aws_storage_server() -> Result<(), StorageError> {
        let rand_name = create_uuid7();
        let filename = format!("file-{rand_name}.txt");

        let tmp_dir = TempDir::new().unwrap();
        let tmp_path = tmp_dir.path();

        // write file to temp dir (create_file)
        let lpath = tmp_path.join(&filename);
        create_file(lpath.to_str().unwrap(), &1024);

        let settings = OpsmlConfig::default(); // Adjust settings as needed
        let storage_client = S3FStorageClient::new(&settings.storage_settings().unwrap()).await;

        let rpath_dir = Path::new("test_dir");
        let rpath = rpath_dir.join(&filename);

        if storage_client.exists(rpath_dir).await? {
            storage_client.rm(rpath_dir, true).await?;
        }

        assert!(!storage_client.exists(rpath_dir).await?);

        // put
        storage_client.put(&lpath, &rpath, false).await?;
        assert!(storage_client.exists(&rpath).await?);

        let nested_path = format!("nested/really/deep/file-{rand_name}.txt");
        let rpath_nested = rpath.parent().unwrap().join(nested_path);

        storage_client.put(&lpath, &rpath_nested, false).await?;

        let path = storage_client.generate_presigned_url(&rpath, 10).await?;
        assert!(!path.is_empty());

        // ls
        assert!(
            !storage_client
                .find(rpath_nested.parent().unwrap())
                .await?
                .is_empty()
        );

        // find
        let blobs = storage_client.find(rpath_dir).await?;

        assert_eq!(
            blobs,
            vec![
                rpath.to_str().unwrap().to_string(),
                rpath_nested.to_str().unwrap().to_string()
            ]
        );

        // create new temp dir
        let new_tmp_dir = TempDir::new().unwrap();

        let new_lpath = new_tmp_dir.path().join(&filename);

        // get
        storage_client.get(&new_lpath, &rpath, false).await?;
        assert!(new_lpath.exists());

        // rm
        storage_client.rm(&rpath, false).await?;
        assert!(!storage_client.exists(&rpath).await?);

        // rm recursive
        storage_client.rm(rpath_dir, true).await?;
        assert!(!storage_client.exists(rpath_dir).await?);

        Ok(())
    }

    #[tokio::test]
    async fn test_aws_storage_server_trees() -> Result<(), StorageError> {
        let rand_name = create_uuid7();

        let tmp_dir = TempDir::new().unwrap();
        let tmp_path = tmp_dir.path();
        let settings = OpsmlConfig::default(); // Adjust settings as needed
        let storage_client = S3FStorageClient::new(&settings.storage_settings().unwrap()).await;

        let child = tmp_path.join("child");
        let grand_child = child.join("grandchild");
        for path in &[tmp_path, &child, &grand_child] {
            std::fs::create_dir_all(path).unwrap();
            let txt_file = format!("file-{rand_name}.txt");
            let txt_path = path.join(txt_file);
            std::fs::write(&txt_path, "hello, world").unwrap();
        }

        let new_rand_name = create_uuid7();
        let rpath_root = Path::new(&new_rand_name);

        if storage_client.exists(rpath_root).await? {
            storage_client.rm(rpath_root, true).await?;
        }

        // put
        storage_client.put(tmp_path, rpath_root, true).await?;
        assert_eq!(storage_client.find(rpath_root).await?.len(), 3);

        // copy
        let copy_dir = rpath_root.join("copy");
        storage_client
            .copy(&rpath_root.join("child"), &copy_dir, true)
            .await?;
        assert_eq!(storage_client.find(&copy_dir).await?.len(), 2);

        // put
        let put_dir = rpath_root.join("copy2");
        storage_client.put(&child, &put_dir, true).await?;
        assert_eq!(storage_client.find(&put_dir).await?.len(), 2);

        // rm
        storage_client.rm(&put_dir, true).await?;
        assert_eq!(storage_client.find(&put_dir).await?.len(), 0);

        storage_client.rm(rpath_root, true).await?;

        Ok(())
    }
}
