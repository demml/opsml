use crate::storage::base::{get_files, PathExt, StorageClient};
use crate::storage::filesystem::FileSystem;
use async_trait::async_trait;
use base64::prelude::*;
use futures::stream::Stream;
use futures::StreamExt;
use google_cloud_auth::credentials::CredentialsFile;
use google_cloud_storage::client::{Client, ClientConfig};
use google_cloud_storage::http::objects::delete::DeleteObjectRequest;
use google_cloud_storage::http::objects::download::Range;
use google_cloud_storage::http::objects::get::GetObjectRequest;
use google_cloud_storage::http::objects::list::ListObjectsRequest;
use google_cloud_storage::http::objects::upload::UploadObjectRequest;
use google_cloud_storage::http::objects::upload::UploadType;
use google_cloud_storage::http::objects::Object;
use google_cloud_storage::http::resumable_upload_client::ChunkSize;
use google_cloud_storage::http::resumable_upload_client::ResumableUploadClient;
use google_cloud_storage::http::resumable_upload_client::UploadStatus;
use google_cloud_storage::sign::SignedURLMethod;
use google_cloud_storage::sign::SignedURLOptions;
use indicatif::ProgressBar;
use opsml_error::error::StorageError;
use opsml_settings::config::OpsmlStorageSettings;
use opsml_types::contracts::{FileInfo, UploadPartArgs};
use opsml_types::{StorageType, UPLOAD_CHUNK_SIZE};
use opsml_utils::progress::Progress;
use opsml_utils::FileUtils;
use serde_json::Value;
use std::env;
use std::fs::File;
use std::io::BufReader;
use std::io::Read;
use std::io::Write;
use std::path::Path;
use std::path::PathBuf;

pub struct GcpCreds {
    pub creds: Option<CredentialsFile>,
    pub project: Option<String>,
    pub default_creds: bool,
    pub service_account: Option<Value>,
}

impl GcpCreds {
    pub async fn new() -> Result<Self, StorageError> {
        let mut creds = GcpCreds {
            creds: None,
            project: None,
            default_creds: false,
            service_account: None,
        };
        creds
            .check_model()
            .await
            .map_err(|e| StorageError::Error(format!("Unable to check model: {}", e)))?;
        Ok(creds)
    }

    async fn check_model(&mut self) -> Result<(), StorageError> {
        if let Ok(base64_creds) = env::var("GOOGLE_ACCOUNT_JSON_BASE64") {
            let cred_string = self
                .decode_base64(&base64_creds)
                .map_err(|e| StorageError::Error(format!("Unable to decode base64: {}", e)))?;

            self.creds = Some(
                CredentialsFile::new_from_str(&cred_string)
                    .await
                    .map_err(|e| {
                        StorageError::Error(format!(
                            "Unable to create credentials file from string: {}",
                            e
                        ))
                    })?,
            );
        }

        if let Ok(_service_account_file) = env::var("GOOGLE_APPLICATION_CREDENTIALS_JSON")
            .or_else(|_| env::var("GOOGLE_APPLICATION_CREDENTIALS"))
        {
            self.creds = Some(CredentialsFile::new().await.map_err(|e| {
                StorageError::Error(format!(
                    "Unable to create credentials file from file: {}",
                    e
                ))
            })?);
        }

        Ok(())
    }

    fn decode_base64(&mut self, service_base64_creds: &str) -> Result<String, StorageError> {
        let decoded = BASE64_STANDARD
            .decode(service_base64_creds)
            .map_err(|e| StorageError::Error(format!("Unable to decode base64: {}", e)))?;
        let decoded_str = String::from_utf8(decoded)
            .map_err(|e| StorageError::Error(format!("Unable to convert to string: {}", e)))?;
        Ok(decoded_str)
    }
}

pub struct GoogleMultipartUpload {
    pub upload_client: ResumableUploadClient,
    pub upload_status: UploadStatus,
    file_reader: BufReader<File>,
    file_size: u64,
    filename: String,
}

impl GoogleMultipartUpload {
    pub async fn new(
        upload_client: ResumableUploadClient,
        path: &str,
    ) -> Result<Self, StorageError> {
        let file = File::open(path)
            .map_err(|e| StorageError::Error(format!("Failed to open file: {}", e)))?;

        let metadata = file
            .metadata()
            .map_err(|e| StorageError::Error(format!("Failed to get file metadata: {}", e)))?;

        let file_size = metadata.len();
        let filename = Path::new(path)
            .file_name()
            .unwrap()
            .to_string_lossy()
            .to_string();

        let file_reader = BufReader::new(file);

        Ok(GoogleMultipartUpload {
            upload_client,
            upload_status: UploadStatus::NotStarted,
            file_reader,
            file_size,
            filename,
        })
    }

    pub async fn upload_next_chunk(
        &mut self,
        upload_args: &UploadPartArgs,
    ) -> Result<(), StorageError> {
        let first_byte = upload_args.chunk_index * upload_args.chunk_size;
        let last_byte = first_byte + upload_args.this_chunk_size - 1;

        let size = ChunkSize::new(first_byte, last_byte, Some(self.file_size));

        let mut buffer = vec![0; upload_args.this_chunk_size as usize];
        let bytes_read = self
            .file_reader
            .read(&mut buffer)
            .map_err(|e| StorageError::Error(format!("Failed to read file: {}", e)))?;

        buffer.truncate(bytes_read);

        let result = self
            .upload_client
            .upload_multiple_chunk(buffer, &size)
            .await
            .map_err(|e| {
                StorageError::Error(format!(
                    "Unable to upload multiple chunks to resumable upload: {}",
                    e
                ))
            })?;

        self.upload_status = result;

        Ok(())
    }

    pub async fn upload_file_in_chunks(
        &mut self,
        chunk_count: u64,
        size_of_last_chunk: u64,
        chunk_size: u64,
        bar: &ProgressBar,
    ) -> Result<(), StorageError> {
        for chunk_index in 0..chunk_count {
            let this_chunk = if chunk_count - 1 == chunk_index {
                size_of_last_chunk
            } else {
                chunk_size
            };

            let upload_args = UploadPartArgs {
                presigned_url: None,
                chunk_size,
                chunk_index,
                this_chunk_size: this_chunk,
            };

            self.upload_next_chunk(&upload_args).await?;

            bar.inc(1);
        } // extract the range from the result and update the first_byte and last_byte

        self.complete_upload().await?;
        bar.finish_with_message("Upload complete");

        Ok(())

        // check if enum is Ok
    }

    pub async fn complete_upload(&mut self) -> Result<(), StorageError> {
        match self.upload_status {
            UploadStatus::Ok(_) => {
                // complete the upload
                Ok(())
            }
            _ => Err(StorageError::Error(
                "Failed to upload file in chunks".to_string(),
            )),
        }
    }
}

#[derive(Clone)]
pub struct GoogleStorageClient {
    pub client: Client,
    pub bucket: String,
}

#[async_trait]
impl StorageClient for GoogleStorageClient {
    fn storage_type(&self) -> StorageType {
        StorageType::Google
    }
    async fn bucket(&self) -> &str {
        &self.bucket
    }
    async fn new(settings: &OpsmlStorageSettings) -> Result<Self, StorageError> {
        let creds = GcpCreds::new().await?;
        // If no credentials, attempt to create a default client pulling from the environment

        let config = if creds.creds.is_none() {
            // if using in client_mode, default to anonymous
            let config = if settings.client_mode {
                ClientConfig::default().anonymous()
            } else {
                let config = ClientConfig::default().with_auth().await;

                // default to anonymous if unable to create client with auth
                match config {
                    Ok(config) => config,
                    Err(_) => ClientConfig::default().anonymous(),
                }
            };

            Ok(config)

        // if creds are set (base64 for JSON file)
        } else {
            // try with credentials
            let config = ClientConfig::default()
                .with_credentials(creds.creds.unwrap())
                .await
                .map_err(|e| {
                    StorageError::Error(format!("Unable to create client with credentials: {}", e))
                })?;

            Ok(config)
        };

        let config = config?;

        let client = Client::new(config);

        // strip gs:// from the bucket name if exists
        let bucket = settings
            .storage_uri
            .strip_prefix("gs://")
            .unwrap_or(&settings.storage_uri)
            .to_string();

        Ok(GoogleStorageClient { client, bucket })
    }

    /// Download a remote object as a stream to a local file
    ///
    /// # Arguments
    ///
    /// * `lpath` - The path to the local file
    /// * `rpath` - The path to the remote file
    ///
    async fn get_object(&self, lpath: &str, rpath: &str) -> Result<(), StorageError> {
        let mut stream = self.get_object_stream(rpath).await?;

        // create and open lpath file
        let prefix = Path::new(lpath).parent().unwrap();

        if !prefix.exists() {
            // create the directory if it does not exist and skip errors
            std::fs::create_dir_all(prefix)
                .map_err(|e| StorageError::Error(format!("Unable to create directory: {}", e)))?;
        }

        // create and open lpath file
        let mut file = File::create(lpath)
            .map_err(|e| StorageError::Error(format!("Unable to create file: {}", e)))?;

        while let Some(v) = stream.next().await {
            let chunk = v.map_err(|e| StorageError::Error(format!("Stream error: {}", e)))?;
            file.write_all(&chunk)
                .map_err(|e| StorageError::Error(format!("Unable to write to file: {}", e)))?;
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
        let presigned_url = self
            .client
            .signed_url(
                &self.bucket.clone(),
                path,
                None,
                None,
                SignedURLOptions {
                    method: SignedURLMethod::GET,
                    start_time: None,
                    expires: std::time::Duration::from_secs(expiration),
                    ..Default::default()
                },
            )
            .await
            .map_err(|e| StorageError::Error(format!("Unable to generate presigned url: {}", e)))?;

        Ok(presigned_url)
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
        let result = self
            .client
            .list_objects(&ListObjectsRequest {
                bucket: self.bucket.clone(),
                prefix: Some(path.to_string()),
                ..Default::default()
            })
            .await
            .map_err(|e| StorageError::Error(format!("Unable to list objects: {}", e)))?;

        // return a list of object names if results.items is not None, Else return empty list
        Ok(result
            .items
            .unwrap_or_else(Vec::new)
            .iter()
            .map(|o| o.name.to_owned())
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
        let result = self
            .client
            .list_objects(&ListObjectsRequest {
                bucket: self.bucket.clone(),
                prefix: Some(path.to_string()),
                ..Default::default()
            })
            .await
            .map_err(|e| StorageError::Error(format!("Unable to list objects: {}", e)))?;

        Ok(result
            .items
            .unwrap_or_else(Vec::new)
            .iter()
            .map(|o| FileInfo {
                name: o.name.clone(),
                size: o.size,
                object_type: o.content_type.clone().unwrap_or_default(),
                created: match o.time_created {
                    Some(last_modified) => last_modified.to_string(),
                    None => "".to_string(),
                },
                suffix: o.name.clone().split('.').last().unwrap_or("").to_string(),
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
            .copy_object(
                &google_cloud_storage::http::objects::copy::CopyObjectRequest {
                    source_bucket: self.bucket.clone(),
                    source_object: src.to_string(),
                    destination_bucket: self.bucket.clone(),
                    destination_object: dest.to_string(),
                    ..Default::default()
                },
            )
            .await
            .map_err(|e| StorageError::Error(format!("Unable to copy object: {}", e)))?;

        Ok(true)
    }

    /// Copy objects from one bucket to another without deleting the source objects
    ///
    /// # Arguments
    ///
    /// * `src` - The path to the source object
    /// * `dest` - The path to the destination object
    ///
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
        let request = DeleteObjectRequest {
            bucket: self.bucket.clone(),
            object: path.to_string(),
            ..Default::default()
        };

        self.client
            .delete_object(&request)
            .await
            .map_err(|e| StorageError::Error(format!("Unable to delete object: {}", e)))?;

        Ok(true)
    }

    /// Delete an object from the storage bucket
    ///
    /// # Arguments
    ///
    /// * `path` - The path to the object in the bucket
    ///
    async fn delete_objects(&self, path: &str) -> Result<bool, StorageError> {
        let objects = self.find(path).await?;

        for obj in objects {
            self.delete_object(obj.as_str()).await?;
        }

        Ok(true)
    }
}

impl GoogleStorageClient {
    /// Get an object from the storage bucket and return a stream of bytes to pass to
    /// an async iterator
    ///
    /// # Arguments
    ///
    /// * `rpath` - The path to the object in the bucket
    ///
    /// # Returns
    ///
    /// A stream of bytes
    pub async fn get_object_stream(
        &self,
        rpath: &str,
    ) -> Result<
        impl Stream<Item = Result<bytes::Bytes, google_cloud_storage::http::Error>>,
        StorageError,
    > {
        // open a bucket and blob and return the stream
        let result = self
            .client
            .download_streamed_object(
                &GetObjectRequest {
                    bucket: self.bucket.clone(),
                    object: rpath.to_string(),
                    ..Default::default()
                },
                &Range::default(),
            )
            .await
            .map_err(|e| StorageError::Error(format!("Unable to download object: {}", e)))?;
        Ok(result)
    }

    pub async fn create_multipart_upload(
        &self,
        path: &str,
    ) -> Result<ResumableUploadClient, StorageError> {
        let _filename = path.to_string();

        let metadata = Object {
            name: _filename.clone(),
            content_type: Some("application/octet-stream".to_string()),
            ..Default::default()
        };

        let result = self
            .client
            .prepare_resumable_upload(
                &UploadObjectRequest {
                    bucket: self.bucket.to_string(),
                    ..Default::default()
                },
                &UploadType::Multipart(Box::new(metadata)),
            )
            .await
            .map_err(|e| {
                StorageError::Error(format!("Unable to create resumable session: {}", e))
            })?;

        Ok(result)
    }

    /// Will create a google multipart uploader and return the client
    ///
    /// # Arguments
    ///
    /// * `path` - The path to the object in the bucket
    /// * `session_url` - The session url if it exists
    ///
    /// # Returns
    ///
    /// A GoogleMultipartUpload client
    pub async fn create_multipart_uploader(
        &self,
        lpath: &str,
        rpath: &str,
        session_url: Option<String>,
    ) -> Result<GoogleMultipartUpload, StorageError> {
        let resumable_upload_client = match session_url {
            Some(url) => self.client.get_resumable_upload(url),
            None => self.create_multipart_upload(rpath).await?,
        };
        let client = GoogleMultipartUpload::new(resumable_upload_client, lpath).await?;
        Ok(client)
    }
}

#[derive(Clone)]
pub struct GCSFSStorageClient {
    client: GoogleStorageClient,
}

#[async_trait]
impl FileSystem for GCSFSStorageClient {
    fn name(&self) -> &str {
        "GCSFSStorageClient"
    }

    async fn new(settings: &OpsmlStorageSettings) -> Self {
        let client = GoogleStorageClient::new(settings).await.unwrap();
        GCSFSStorageClient { client }
    }

    fn storage_type(&self) -> StorageType {
        StorageType::Google
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

        let progress = Progress::new();

        if recursive {
            if !stripped_lpath.is_dir() {
                return Err(StorageError::Error(
                    "Local path must be a directory for recursive put".to_string(),
                ));
            }

            let files: Vec<PathBuf> = get_files(&stripped_lpath)?;

            for file in files {
                let (chunk_count, size_of_last_chunk, chunk_size) =
                    FileUtils::get_chunk_count(&file, UPLOAD_CHUNK_SIZE as u64).unwrap();

                let pb = ProgressBar::new(chunk_count);

                let stripped_file_path = file.strip_path(self.client.bucket().await);
                let relative_path = file.relative_path(&stripped_lpath)?;
                let remote_path = stripped_rpath.join(relative_path);

                let mut uploader = self
                    .client
                    .create_multipart_uploader(
                        stripped_file_path.to_str().unwrap(),
                        remote_path.to_str().unwrap(),
                        None,
                    )
                    .await?;

                uploader
                    .upload_file_in_chunks(chunk_count, size_of_last_chunk, chunk_size, &pb)
                    .await?;

                pb.finish_and_clear();
            }
        } else {
            let (chunk_count, size_of_last_chunk, chunk_size) =
                FileUtils::get_chunk_count(&stripped_lpath, UPLOAD_CHUNK_SIZE as u64).unwrap();

            let pb = ProgressBar::new(chunk_count);

            let mut uploader = self
                .client
                .create_multipart_uploader(
                    stripped_lpath.to_str().unwrap(),
                    stripped_rpath.to_str().unwrap(),
                    None,
                )
                .await?;

            uploader
                .upload_file_in_chunks(chunk_count, size_of_last_chunk, chunk_size, &pb)
                .await?;
            pb.finish_and_clear();
        };

        progress.finish();

        Ok(())
    }
}

impl GCSFSStorageClient {
    pub async fn create_multipart_uploader(
        &self,
        lpath: &Path,
        rpath: &Path,
        session_url: Option<String>,
    ) -> Result<GoogleMultipartUpload, StorageError> {
        self.client
            .create_multipart_uploader(
                lpath.to_str().unwrap(),
                rpath.to_str().unwrap(),
                session_url,
            )
            .await
    }

    pub async fn create_multipart_upload(
        &self,
        path: &Path,
    ) -> Result<ResumableUploadClient, StorageError> {
        self.client
            .create_multipart_upload(path.to_str().unwrap())
            .await
    }
}

// tests

#[cfg(test)]
mod tests {
    use super::*;
    use opsml_error::error::StorageError;
    use opsml_settings::config::OpsmlConfig;
    use rand::distributions::Alphanumeric;
    use rand::thread_rng;
    use rand::Rng;
    use std::path::Path;
    use tempfile::TempDir;

    pub fn create_file(name: &str, chunk_size: &u64) {
        let mut file = File::create(name).expect("Could not create sample file.");

        while file.metadata().unwrap().len() <= chunk_size * 2 {
            let rand_string: String = thread_rng()
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
    async fn test_gcs_storage_server() -> Result<(), StorageError> {
        let rand_name = uuid::Uuid::new_v4().to_string();
        let filename = format!("file-{}.txt", rand_name);

        let tmp_dir = TempDir::new().unwrap();
        let tmp_path = tmp_dir.path();

        // write file to temp dir (create_file)
        let lpath = tmp_path.join(&filename);
        create_file(lpath.to_str().unwrap(), &1024);

        let settings = OpsmlConfig::default(); // Adjust settings as needed
        let storage_client = GCSFSStorageClient::new(&settings.storage_settings()).await;

        let rpath_dir = Path::new("test_dir");
        let rpath = rpath_dir.join(&filename);

        if storage_client.exists(rpath_dir).await? {
            storage_client.rm(rpath_dir, true).await?;
        }

        assert!(!storage_client.exists(rpath_dir).await?);

        // put
        storage_client.put(&lpath, &rpath, false).await?;
        assert!(storage_client.exists(&rpath).await?);

        let nested_path = format!("nested/really/deep/file-{}.txt", rand_name);
        let rpath_nested = rpath.parent().unwrap().join(nested_path);

        storage_client.put(&lpath, &rpath_nested, false).await?;

        let path = storage_client.generate_presigned_url(&rpath, 10).await?;
        assert!(!path.is_empty());

        // ls
        assert!(!storage_client
            .find(rpath_nested.parent().unwrap())
            .await?
            .is_empty());

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
    async fn test_gcs_storage_server_trees() -> Result<(), StorageError> {
        let rand_name = uuid::Uuid::new_v4().to_string();

        let tmp_dir = TempDir::new().unwrap();
        let tmp_path = tmp_dir.path();
        let settings = OpsmlConfig::default(); // Adjust settings as needed
        let storage_client = GCSFSStorageClient::new(&settings.storage_settings()).await;

        let child = tmp_path.join("child");
        let grand_child = child.join("grandchild");
        for path in &[tmp_path, &child, &grand_child] {
            std::fs::create_dir_all(path).unwrap();
            let txt_file = format!("file-{}.txt", rand_name);
            let txt_path = path.join(txt_file);
            std::fs::write(&txt_path, "hello, world").unwrap();
        }

        let new_rand_name = uuid::Uuid::new_v4().to_string();
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

        Ok(())
    }
}
